from os import write
from clsKalturaApi import clsKalturaApi
from clsCanvasApi import clsCanvasApi
import globals
import util

def getProperKalturaSubmission(userFullName,
                               keepGrade,
                               kalturaSubmissions,
                               kalturaSubmissionUids):
    ret = None
    index = 0
    for kalSubm in kalturaSubmissions:
        if kalturaSubmissionUids[index][0] == userFullName:
            if ret == None:
                ret = kalSubm
                index += 1
                continue
            if keepGrade == 'Highest':
                if kalSubm.calculatedScore > ret.calculatedScore:
                    ret = kalSubm
            elif keepGrade == 'Lowest':
                if kalSubm.calculatedScore < ret.calculatedScore:
                    ret = kalSubm
            elif keepGrade == 'Latest':
                if kalSubm.createdAt > ret.createdAt:
                    ret = kalSubm
            elif keepGrade == 'First':
                if kalSubm.createdAt < ret.createdAt:
                    ret = kalSubm
            elif keepGrade == 'Average':
                # I'm guessing this is equivalent to 'Latest' since averaging is done by Kaltura quiz engine.
                if kalSubm.createdAt > ret.createdAt:
                    ret = kalSubm
            else:
                print("\n\nUnknown 'keepGrade' type:  " + keepGrade)
                exit(14)   
        index += 1
    return ret

def writeGradeResults(fileHandle,
                      thisAssignment,
                      entryId,
                      canvasStudentsInfo,
                      kalturaSubmissions,
                      kalturaSubmissionUids,
                      keepGrade,
                      canvasSubmissions):
    print('\t\tSaving results ...')
    # We want the results to be sorted in order of student name.
    for si in canvasStudentsInfo:
        canvasStudentFullName = si[0]
        canvasStudentUid = si[1]
        # print(canvasStudentFullName, canvasStudentUid)
        # Loop through Kaltura submission data and process all for this student
        kalSubm = getProperKalturaSubmission(canvasStudentFullName,
                                             keepGrade,
                                             kalturaSubmissions,
                                             kalturaSubmissionUids)
        if kalSubm == None:
            # Student has no Kaltura submissions.  He/she hasn't taken the video quiz.
            # Onto next student ...
            continue
        kalturaPercent = kalSubm.calculatedScore
        kalturaPoints = kalturaPercent * assgn.points_possible
        # Find corresponding Canvas grade
        canvasGrade = ''
        diff = ''
        for canvasSubm in canvasSubmissions:
            if canvasSubm.points_deducted is None:
                deduction = 0.0
            else:
                deduction = canvasSubm.points_deducted
            late = ''
            if canvasSubm.late == True:
                late = 'LATE'
            if canvasSubm.user_id == canvasStudentUid:
                if (canvasSubm.entered_score == None):
                    canvasGrade = ''
                    diff = '*'
                elif (type(canvasSubm.entered_score) is float):
                    if (round(canvasSubm.entered_score,2) != round(kalturaPoints,2)):
                        diff = '*'
                    canvasGrade = '{0:.2f}'.format(canvasSubm.entered_score)
                else:
                    canvasGrade = canvasSubm.entered_score
                    diff = '*'
                # If there is no matching Canvas submission, the Canvas data will be blank.
                msg = '{0}\t{1}\t{2}\t{3}\t{4:.0%}\t{5:.2f}\t{6}\t{7}\t{8}\t{9}\t{10:.2f}\n'.format(
                                assgn.name,
                                entryId, 
                                str(assgn.due_at),
                                canvasStudentFullName,
                                kalturaPercent,
                                kalturaPoints,
                                assgn.points_possible,
                                canvasGrade,
                                diff,
                                late,
                                deduction)
                fileHandle.write(msg)
                break
        fileHandle.flush()

myCanvas = clsCanvasApi()
myCanvas.selectMyCourse()
myKaltura = clsKalturaApi()

print('\n\n' + myCanvas.selectedCourse.name)

ReportFilename = util.makeFilename(myCanvas.selectedCourse.id, 'ReportCourseQuizResults', 'tsv')
reportFileHandle = open(ReportFilename, "wt")
msg = "Course:  \t{0}".format(myCanvas.selectedCourse.name)
print(msg)
reportFileHandle.write(msg + '\n')

msg = "Instructor(s)\n"
reportFileHandle.write(msg)

for teach in myCanvas.teachers:
    msg = "\t{0}\n".format(teach.name)
    reportFileHandle.write(msg)

msg = 'Assignment\tEntry Id\tDue Date\tStudent\tKaltura Score\tKaltura Points\tPoints Possible\tCanvas Grade\tDifferent\tLate\tDeduction\n'
reportFileHandle.write(msg)

# Loop over all course assignments
# nn = "Video Quiz 05-03 Microbial Growth and Its Control"
# skipping = True 
for assgn in myCanvas.assignments:
    entryId = myCanvas.isVideoQuizAssignment(assgn)
    if entryId != None:
        print('\t' + assgn.name)
        # if assgn.name == nn:
        #     skipping = False
        # elif skipping == True:
        #     continue

        print('\t\tFetching Canvas quiz submissions ...')
        myCanvas.getCanvasVideoQuizSubmissions(assgn)
        myCanvas.saveSubmissions(assgn, entryId)

        print('\t\tFetching Kaltura quiz submissions ...')
        myKaltura.getKalturaQuizEntry(entryId)
        if myKaltura.kalturaEntry is None:
            continue
        myKaltura.getKalturaQuizSubmissions()
        myKaltura.saveSubmissions(myCanvas.selectedCourse.id)

        # Output results.
        writeGradeResults(reportFileHandle,
                          assgn,
                          entryId,
                          myCanvas.studentInfo,
                          myKaltura.submissions,
                          myKaltura.submissionUids,
                          myKaltura.keepGrade,
                          myCanvas.submissions)

reportFileHandle.close()
print('\nOutput written to ' + str(ReportFilename))
print('done')