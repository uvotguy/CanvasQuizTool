from os import write
from clsKalturaApi import clsKalturaApi
from clsCanvasApi import clsCanvasApi
import globals
import kochUtilities

def writeGradeResults(fileHandle,
                      thisAssignment,
                      entryId,
                      canvasStudentsInfo,
                      kalturaSubmissions,
                      kalturaSubmissionUids,
                      canvasSubmissions):
    print('\t\tSaving results ...')
    # We want the results to be sorted in order of student name.
    for si in canvasStudentsInfo:
        canvasStudentFullName = si[0]
        canvasStudentUid = si[1]
        # print(canvasStudentFullName, canvasStudentUid)
        # Loop through Kaltura submission data and process all for this student
        index = 0
        for kalSubm in kalturaSubmissions:
            kalturaFullName = kalturaSubmissionUids[index][0]
            kalturaUid = kalturaSubmissionUids[index][1]
            if kalturaFullName == canvasStudentFullName:
                studentSubmissionFound = True
                kalturaPercent = kalSubm.calculatedScore
                kalturaPoints = kalturaPercent * assgn.points_possible
                # Find corresponding Canvas grade(s)
                canvasGrade = ''
                diff = ''
                for canvasSubm in canvasSubmissions:
                    if canvasSubm.user_id == canvasStudentUid:
                        if (canvasSubm.entered_score == None):
                            canvasGrade = ''
                            diff = '*'
                        elif (type(canvasSubm.entered_score) is float):
                            if (canvasSubm.entered_score != kalturaPoints):
                                diff = '*'
                            canvasGrade = '{0:.2f}'.format(canvasSubm.entered_score)
                        else:
                            canvasGrade = canvasSubm.entered_score
                            diff = '*'
                # If there is no matching Canvas submission, the Canvas data will be blank.
                msg = '{0}\t{1}\t{2}\t{3:.0%}\t{4:.2f}\t{5}\t{6}\t{7}\n'.format(
                                assgn.name, 
                                str(assgn.due_at),
                                canvasStudentFullName,
                                kalturaPercent,
                                kalturaPoints,
                                assgn.points_possible,
                                canvasGrade,
                                diff)
                fileHandle.write(msg)
            index += 1

myCanvas = clsCanvasApi()
myCanvas.selectMyCourse()
myKaltura = clsKalturaApi()

print('\n\n' + myCanvas.selectedCourse.name)

ReportFilename = kochUtilities.makeFilename(myCanvas.selectedCourse.id, 'ReportCourseQuizResults', 'tsv')
reportFileHandle = open(ReportFilename, "wt")
msg = "Course:  \t{0}".format(myCanvas.selectedCourse.name)
print(msg)
reportFileHandle.write(msg + '\n')

msg = "Instructor(s)\n"
reportFileHandle.write(msg)

for teach in myCanvas.teachers:
    msg = "\t{0}\n".format(teach.name)
    reportFileHandle.write(msg)

msg = 'Assignment\tEntry Id\tDue Date\tStudent\tKaltura Score\tKaltura Points\tPoints Possible\tCanvas Grade\tDifferent\n'
reportFileHandle.write(msg)

# Loop over all course assignments
for assgn in myCanvas.assignments:
    entryId = myCanvas.isVideoQuizAssignment(assgn)
    if entryId != None:
        print('\t' + assgn.name)
        print('\t\tFetching Canvas quiz submissions ...')
        myCanvas.getCanvasVideoQuizSubmissions(assgn)
        myCanvas.saveSubmissions(assgn, entryId)

        print('\t\tFetching Kaltura quiz submissions ...')
        myKaltura.getKalturaQuizEntry(entryId)
        myKaltura.getKalturaQuizSubmissions()
        myKaltura.saveSubmissions(myCanvas.selectedCourse.id)

        # Output results.
        writeGradeResults(reportFileHandle,
                          assgn,
                          entryId,
                          myCanvas.studentInfo,
                          myKaltura.submissions,
                          myKaltura.submissionUids,
                          myCanvas.submissions)

reportFileHandle.close()
print('\nOutput written to ' + str(ReportFilename))
print('done')