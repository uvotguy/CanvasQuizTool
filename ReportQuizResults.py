from logging import fatal
import canvasapi
import CanvasQuizTool
import FetchKalturaQuizGrades
import kochUtilities

canvasQuizData = CanvasQuizTool.CanvasQuizTool()
students = canvasQuizData[4]
quizId = canvasQuizData[2]

canvasQuizOutputFilename = kochUtilities.makeFilename('ReportQuizResults-' + quizId, 'tsv')
kalturaSubmissionData = FetchKalturaQuizGrades.FetchKalturaQuizGrades(quizId)
handle = open(canvasQuizOutputFilename, 'wt')

msg = "Course:  \t{0}".format(canvasQuizData[0].name)
print(msg)
handle.write(msg + '\n')

msg = "Instructor(s)"
print(msg)
handle.write(msg + '\n')

for per in canvasQuizData[1]:
    msg = "\t{0}".format(per.name)
    print(msg)
    handle.write(msg + '\n')

msg = "Assignment\t{0}".format(canvasQuizData[3].name) 
print(msg)
handle.write(msg + '\n')

points_possible = canvasQuizData[3].points_possible
msg = "Points Possible\t{0}".format(points_possible)
print(msg)
handle.write(msg + '\n')

msg = "Due Date\t{0}".format(canvasQuizData[3].due_at)
print(msg)
handle.write(msg + '\n')

for st in students:
    canvasFullName = st[0]
    canvasUid = st[1]
    for kalSubm in kalturaSubmissionData[1:]:
        if kalSubm[0] == canvasFullName:
            kalturaFullName = kalSubm[0]
            kalturaPercent = kalSubm[2]
            kalturaPoints = kalSubm[2] * points_possible
            #print("{0}\t{1}\t{2}".format(studentFullName, subm[2], subm[4])
            # Find corresponding Canvas grade(s)
            canvasGrade = ''
            diff = ''
            for canvasSubm in canvasQuizData[5]:
                if canvasSubm.user_id == canvasUid:
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

            msg = '{0}\t{1}\t{2}\t{3:.0%}\t{4:.2f}\t{5}'.format(
                                                canvasFullName,
                                                canvasGrade,
                                                kalturaFullName,
                                                kalturaPercent,
                                                kalturaPoints,
                                                diff)
            print(msg)
            handle.write(msg + '\n')

# sanity check.  See if there are any submissions by non-students
# for subm in kalturaSubmissionData[1:]:
#     found = False
#     for st in students:
#         if st[0] == subm[0]:
#             found = True
#     if found == False:
#         print("Unknown student:  {0}\t{1}".format(subm[0],subm[4]))

handle.close()
print('\nOutput written to ' + str(canvasQuizOutputFilename))
print('done')