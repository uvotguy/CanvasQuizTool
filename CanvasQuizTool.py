from pathlib import Path
from clsKalturaApi import clsKalturaApi
from clsCanvasApi import clsCanvasApi
from config import config
from KalturaClient.exceptions import (KalturaException, KalturaClientException)

appConfig = config()
myCanvas = clsCanvasApi(appConfig)
myCanvas.selectMyCourse()
myCanvas.makeCourseGradebook()
myCanvas.saveCourseGradebook()

# Gather Kaltura information for each assignment
print('\tFeching Kaltura quiz submissions')
myKaltura = clsKalturaApi(appConfig)
for entryId in myCanvas.assignmentEntryIds:
    # clsKalturaApi is set up to save information **for a single quiz**.
    # It does not save a list of submission object across all quizzes,
    # like a gradebook.
    try:
        myKaltura.getKalturaQuizEntry(entryId)
    except Exception:
        print(r"\t\Ignoring quiz.")
        continue

    # Fetch all Kaltura submissions for this quiz.  Note that Kaltura has
    # no concept of semesters - it's not an LMS.  The resulting list will
    # contain quiz submissions for ALL semesters.  Only the ones for
    # current students will be considered below.
    myKaltura.getKalturaQuizSubmissions(entryId)   
myKaltura.saveSubmissions(myCanvas.courseFolder)

# At this point, we've gathered all the Canvas and Kaltura data for this
# course.  Now print out the merged results.
#filename = Path.joinpath(myCanvas.courseFolder, 'QuizResultsMerged-Full.tsv')
filename = Path.joinpath(myCanvas.courseFolder, 'QuizDifferences.tsv')
diffFile = open(filename, 'wt')
diffFile.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n'
               .format('Assignment',
                       'User Name',
                       'User ID',
                       'Kaltura Points',
                       'Gradebook Points',
                       'Points Possible',
                       'Different',
                       'Late'))
ii = -1
for asgn in myCanvas.assignments:
    ii += 1
    print('\n{0}'.format(asgn.name))

    # For each clsCanvasApi assignment object, there is a corresponding
    # entryId, stored in a simple array.
    entryId = myCanvas.assignmentEntryIds[ii]
    entry = myKaltura.getEntry(entryId)
    quiz = myKaltura.getQuiz(entryId)

    # Fetch all Kaltura submissions for this quiz.  Note that Kaltura has
    # no concept of semesters - it's not an LMS.  The resulting list will
    # contain quiz submissions for ALL semesters.  Only the ones for
    # current students will be considered below.
    #kalSubmissions = myKaltura.getKalturaQuizSubmissions(entryId)
   
    # We will use the Canvas gradebook as a master for determining which
    # students to report on.  There should be one gradebook record for
    # each (assignment, student) tuple.  Get a list of gradebook records
    # for this quiz.
    #
    # This list should contain one entry for every gradeable student.
    # Loop over each student and compare their correct Kaltura submission
    # (based on the KeepGrade setting on the Kaltura quiz entry) to the
    # gradebook entry.
    quizGradebook = myCanvas.getQuizGradebook(asgn)
    for gradebook in quizGradebook:
        if hasattr(quiz, 'scoreType'):
            keepGrade = myKaltura.keepGradeToText(quiz.scoreType.value)
        else:
            keepGrade = 'Latest'

        kalturaSubmission = myKaltura.getCorrectQuizSubmission(entryId, 
                                                               gradebook.userId, 
                                                               keepGrade)
        if kalturaSubmission == None:
            continue
        
        kalturaPercent = kalturaSubmission.calculatedScore
        kalturaPoints = round(kalturaPercent * asgn.points_possible,2)

        if len(gradebook.grades) == 0:
            grade = None
        elif len(gradebook.grades) > 1:
            raise ("Canvas gradebook has multiple grades for user.  Assignment={0};UserId={1};".format(asgn.name, gradebook.userId))
        else:
            if gradebook.grades[0] == '':
                grade = None
            else:
                grade = round(gradebook.grades[0],2)

        if len(gradebook.late) == 0:
            late = ''
        elif len(gradebook.grades) > 1:
            raise ("Canvas gradebook has multiple LATEs for user.  Assignment={0};UserId={1};".format(asgn.name, gradebook.userId))
        else:
            if gradebook.late[0] == '':
                late = ''
            else:
                late = gradebook.late[0]

        if len(gradebook.deductions) == 0:
            deduction = ''
        elif len(gradebook.grades) > 1:
            raise ("Canvas gradebook has multiple DEDUCTIONs for user.  Assignment={0};UserId={1};".format(asgn.name, gradebook.userId))
        else:
            if gradebook.deductions[0] == '':
                strDeduction = ''
                deduction = 0.0
            elif gradebook.deductions[0] == 0.0:
                strDeduction = ''
                deduction = 0.0
            else:
                deduction = round(gradebook.deductions[0],2)
                strDeduction = str(deduction)

        diff = ''
        if (grade == None):
            # Since there's a Kaltura submission and the Canvas grade is blank
            # the grades are obviously different.
            grade = ''
            diff = '*'
        elif (round(kalturaPoints - deduction,2)  != round(grade, 2)):
                grade = round(grade,2)
                diff = '*'

        diffFile.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n'
                        .format(asgn.name, 
                                gradebook.sortableName,
                                kalturaSubmission.userId,
                                kalturaPoints,
                                grade,
                                asgn.points_possible,
                                diff,
                                late,
                                strDeduction))
        diffFile.flush()
diffFile.close()
print('\nOutput saved in {0}\n'.format(myCanvas.courseFolder))
