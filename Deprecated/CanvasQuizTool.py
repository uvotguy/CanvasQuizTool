import canvasapi
import logging
import os
import re
import selectMyCourse
import selectMyVideoQuizAssignment
import kochUtilities
import getEnvironmentVariables

def CanvasQuizTool(client):
    global targetUserId, canvasToken, canvasUrl, kalturaUrl, ignoreUids

    # Python arrays are not fixed type.  Each element can be a completely different
    # data type:  string, int, or even object.  We use that language property here.
    # The output arry contains the following information:
    #
    #   outData[0]: A Course object
    #               - name
    #   outData[1]: A list of teachers 
    #               - User[x].login_id
    #               - User[x].name
    #               - User[x].sortable_name
    #   outData[2]: - Kaltura EntryId of video quiz
    #   outData[3]: Assignment object
    #               - due_at
    #               - external_tool_tag_attributes.url  (contains video quiz entry id)
    #               - name
    #               - points_possible
    #   outData[4]: A list of (student name, canvas_id) tuples sorted by name
    #   outData[5]: A PaginatedList of quiz submissions (presumably the best score)
    #               - _elements[x].attempt
    #               - _elements[x].entered_grade
    #               - _elements[x].entered_score
    #               - _elements[x].grade
    #               - _elements[x].graded_at
    #               - _elements[x].late
    #               - _elements[x].points_deducted
    #               - _elements[x].score            (entered_score minus points_deducted?)
    #               - _elements[x].user_id
    #
   outData = []

    user = client.get_user(targetUserId, 'sis_login_id')

    # Prompt user to select one of his/her courses.
    thisCourse = selectMyCourse.selectMyCourse(client)
    outData.append(thisCourse)
    allTeachers = thisCourse.get_users(enrollment_type='teacher')
    teachers = []
    for teacher in allTeachers:
        if teacher.sis_user_id in ignoreUids:
            continue
        teachers.append(teacher)
    outData.append(teachers)


    # Filter the list of assignments to select ones that are Kaltura video quizzes.
    # Prompt user to select one
    thisQuiz = selectMyVideoQuizAssignment.selectMyVideoQuizAssignment(thisCourse, assignments, kalturaUrl)
    outData.append(thisQuiz[2])
    thisAssignment = assignments[thisQuiz[3]]
    outData.append(thisAssignment)

    students = thisAssignment.get_gradeable_students()
    studentNames = []
    for st in students:
        studentNames.append((st.display_name, st.id))
    studentNames.sort()
    outData.append(studentNames)

    submissions = thisAssignment.get_submissions()
    outData.append(submissions)

    filename = kochUtilities.makeFilename('CanvasQuizTool', 'tsv')
    handle = open(filename, "wt")
    handle.write('Course\t{0}\n'.format(thisCourse.name))
    handle.write('Teacher(s)\n')
    for teacher in teachers:
        handle.write('\t{0}\t{1}\n'.format(teacher.short_name, teacher.sis_user_id))
    handle.write('Assignment\t{0}\n'.format(thisQuiz[0]))
    handle.write('Quiz Entry ID:\t{0}\n'.format(thisQuiz[2]))
    handle.write('Due Date\t{0}\n'.format(thisAssignment.due_at))
    handle.write('Grade Type\t{0}\n'.format(thisAssignment.grading_type))
    handle.write('Allowed Attempts\t{0}\n'.format(thisAssignment.allowed_attempts))
    msg = 'Assignment ID\tName\tUser ID\tGrade\tPoints Possible\tAttempt\tSubmitted At\n'
    print(msg)
    handle.write(msg)
    for subm in submissions:
        # Find this student info
        name = ''
        for st in students:
            if st.id == subm.user_id:
                name = st.display_name
                uid = st.id
                break
        if name == '':
            logger.warn("Student not found:  {0}".format(subm.user_id))
            continue
        print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format(subm.assignment_id, name, uid, subm.entered_grade, thisAssignment.points_possible, subm.attempt, subm.submitted_at))
        handle.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(subm.assignment_id, name, uid, subm.entered_grade, thisAssignment.points_possible, subm.attempt, subm.submitted_at))
    handle.close()

    print("\n\nOutput written to {0}".format(filename))
    print("done")
    #return outData

if __name__ == "__main__":
    CanvasQuizTool(client)
