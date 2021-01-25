import canvasapi
import logging
import os
import re

logger = logging.getLogger()

try:
    targetUserId = os.environ['CANVAS_USER_ID']
    canvasToken = os.environ['CANVAS_USER_TOKEN']
    canvasUrl = os.environ['CANVAS_URL']
    kalturaUrl = os.environ['KALTURA_URL']
except Exception as ex:
    logger.error("Error getting environment variables.")
    logger.exception(ex)
    exit(1)

try:
    client = canvasapi.Canvas(canvasUrl, canvasToken)
except:
    logger.exception("Error getting Canvas API client.")

ii = 0
print("Select a course:")
try:
    user = client.get_user(targetUserId, 'sis_login_id')
    courses = client.get_courses()
    for course in courses:
        if hasattr(course, 'course_code'):
            print('{0}) {1}'.format(ii, course))
        else:
            print('{0}) unavailable {1}'.format(ii, course.id))
        ii += 1
except canvasapi.exceptions.ResourceDoesNotExist as ex:
    logger.exception(ex)
    exit(1)

selectedCourse = int(input())
if (selectedCourse > -1) and (selectedCourse < ii):
    thisCourse = courses[selectedCourse]
    print ("Fetching video quizzes for course {0}:".format(thisCourse.name))
else:
    print("Invalid selection:  {0}.".format(selectedCourse))

assignments = thisCourse.get_assignments()
videoQuizzes=[]
ii = 0
for asgn in assignments:
    if hasattr(asgn, 'external_tool_tag_attributes'):
        #print(asgn)
        url = asgn.external_tool_tag_attributes['url']
        result = re.search(kalturaUrl, url)
        if result != None:
            idSearch = re.search(r'\/media\/entryid\/(\w*)', url)
            if idSearch != None:
                entryId = idSearch.group(1)
                #print('\tEntry Id:  \t' + entryId)
                #print('\tAssignment Id:  ' + str(asgn.id))
                tt = (asgn.name, asgn.id, entryId, ii)
                videoQuizzes.append(tt)
    ii += 1
ii = 0
print("Select a video quiz:")
for quiz in videoQuizzes:
    print ('{0})  {1}'.format(ii, quiz[0]))
    #print("\t" + str(quiz[1]))
    #print("\t" + quiz[2])
    ii += 1

selectedVideoQuiz = int(input())
if (selectedVideoQuiz > -1) and (selectedVideoQuiz < len(videoQuizzes)):
    thisQuiz = videoQuizzes[selectedVideoQuiz]
    print ("Fetching grades for quiz {0}:".format(thisQuiz[0]))
else:
    print("Invalid selection:  {0}.".format(selectedVideoQuiz))

assgn = assignments[thisQuiz[3]]
students = assgn.get_gradeable_students()
submissions = assgn.get_submissions()
filename = 'CanvasQuizTool.out.txt'
handle = open(filename, "wt")
handle.write('Course\t{0}\n'.format(thisCourse.name))
handle.write('Assignment\t{0}\n'.format(thisQuiz[0]))
handle.write('Due Date\t{0}\n'.format(asgn.due_at))
handle.write('Grade Type\t{0}\n'.format(asgn.grading_type))
handle.write('Allowed Attempts\t{0}\n'.format(asgn.allowed_attempts))
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
    print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format(subm.assignment_id, name, uid, subm.grade, assgn.points_possible, subm.attempt, subm.submitted_at))
    handle.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(subm.assignment_id, name, uid, subm.grade, assgn.points_possible, subm.attempt, subm.submitted_at))


handle.close()
print("Output written to {0}".format(filename))
print("done")