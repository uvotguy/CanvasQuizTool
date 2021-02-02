import canvasapi
import logging
import os
import re
import selectMyCourse
import selectMyVideoQuizAssignment
from pathlib import Path

logger = logging.getLogger()
try:
    targetUserId = os.environ['CANVAS_USER_ID']
    canvasToken = os.environ['CANVAS_USER_TOKEN']
    canvasUrl = os.environ['CANVAS_URL']
    kalturaUrl = os.environ['KALTURA_URL']
    try:
        value = os.environ['CANVAS_USERS_TO_IGNORE']
        ignoreUids = value.split(',')
    except:
        ignoreUids = []     # Empty list
except Exception as ex:
    logger.error("Error getting environment variables.")
    logger.exception(ex)
    exit(1)

try:
    client = canvasapi.Canvas(canvasUrl, canvasToken)
except:
    logger.exception("Error getting Canvas API client.")

user = client.get_user(targetUserId, 'sis_login_id')

# Prompt user to select one of his/her courses.
thisCourse = selectMyCourse.selectMyCourse(client)
allTeachers = thisCourse.get_users(enrollment_type='teacher')
teachers = []
for teacher in allTeachers:
    if teacher.sis_user_id in ignoreUids:
        continue
    teachers.append(teacher)

# Make a list of all assignments
assignments = thisCourse.get_assignments()

# Filter the list of assignments to select ones that are Kaltura video quizzes.
# Prompt user to select one
thisQuiz = selectMyVideoQuizAssignment.selectMyVideoQuizAssignment(thisCourse, assignments, kalturaUrl)
thisAssignment = assignments[thisQuiz[3]]

students = thisAssignment.get_gradeable_students()
submissions = thisAssignment.get_submissions()

home = Path.home().absolute()
filename = Path.joinpath(home, 'CanvasQuizTool.out.txt')
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
    print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format(subm.assignment_id, name, uid, subm.grade, thisAssignment.points_possible, subm.attempt, subm.submitted_at))
    handle.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(subm.assignment_id, name, uid, subm.grade, thisAssignment.points_possible, subm.attempt, subm.submitted_at))

handle.close()
print("\n\nOutput written to {0}".format(filename))
print("done")