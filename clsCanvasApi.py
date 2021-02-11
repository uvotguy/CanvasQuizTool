import canvasapi
import globals
import re
import kochUtilities

class clsCanvasApi:
    # Class variables shared by all instances of the class
    # In C/C++ these are known as "static variables".
    client = None
    selectedCourse = None
    assignments = None
    teachers = []
    students = []
    studentInfo = []
    submissions = []

    def __init__(self):
        try:
            self.client = canvasapi.Canvas(globals.canvasUrl, globals.canvasToken)
        except:
            print("Error connection to the Canvas API.")
            exit(10)
    
    def selectMyCourse(self):
        index = 0
        print("Select a course:")
        try:
            courses = self.client.get_courses()
            for course in courses:
                if hasattr(course, 'course_code'):
                    print('{0}) {1}'.format(index, course))
                else:
                    print('{0}) unavailable {1}'.format(index, course.id))
                index += 1
        except canvasapi.exceptions.ResourceDoesNotExist as ex:
            print(ex)
            exit(11)

        selectedIndex = int(input())
        if (selectedIndex > -1) and (selectedIndex < index):
            self.selectedCourse = courses[selectedIndex]
            # print ("Fetching video quizzes for course {0}:".format(self.selectedCourse.name))
            self.getVideoQuizAssignments()
        else:
            print("Invalid selection:  {0}.".format(selectedIndex))
            exit(12)
        
        allTeachers = self.selectedCourse.get_users(enrollment_type='teacher')
        for teacher in allTeachers:
            if teacher.sis_user_id in globals.ignoreUids:
                continue
            self.teachers.append(teacher)

    def getVideoQuizAssignments(self):
        # Make a list of all assignments
        self.assignments = self.selectedCourse.get_assignments()
    
    def isVideoQuizAssignment(self, asgn):
        if hasattr(asgn, 'external_tool_tag_attributes'):
            url = asgn.external_tool_tag_attributes['url']
            result = re.search(globals.kalturaUrl, url)
            if result != None:
                idSearch = re.search(r'\/media\/entryid\/(\w*)', url)
                if idSearch != None:
                    return idSearch.group(1)
        return None
    
    def getCanvasVideoQuizSubmissions(self, asgn):
        self.studentInfo.clear()
        self.submissions = []
        self.students = asgn.get_gradeable_students()
        for st in self.students:
            self.studentInfo.append((st.display_name, st.id))
        self.studentInfo.sort()
        submissions = asgn.get_submissions()
        for subm in submissions:
            self.submissions.append(subm)
        print('\t\t\tGot {0} grades'.format(len(self.submissions)))

    def saveSubmissions(self, assgn, quizEntryId):
        filename = kochUtilities.makeQuizFilename(str(self.selectedCourse.id), quizEntryId, 'CanvasQuizGrades', 'tsv')
        handle = open(filename, "wt")
        handle.write('Course\t{0}\n'.format(self.selectedCourse.name))
        handle.write('Teacher(s)\n')
        for teacher in self.teachers:
            handle.write('\t{0}\t{1}\n'.format(teacher.short_name, teacher.sis_user_id))
        handle.write('Assignment\t{0}\n'.format(assgn.name))
        handle.write('Quiz Entry ID:\t{0}\n'.format(quizEntryId))
        handle.write('Due Date\t{0}\n'.format(assgn.due_at))
        handle.write('Grade Type\t{0}\n'.format(assgn.grading_type))
        handle.write('Allowed Attempts\t{0}\n'.format(assgn.allowed_attempts))
        msg = 'Assignment ID\tName\tUser ID\tGrade\tPoints Possible\tAttempt\tSubmitted At\n'
        #print(msg)
        handle.write(msg)
        for subm in self.submissions:
            # Find this student info
            name = ''
            uid = ''
            for st in self.students:
                if st.id == subm.user_id:
                    name = st.display_name
                    uid = st.id
                    break
            if name == '':
                print("Student not found:  {0}".format(subm.user_id))
                continue
            #print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format(subm.assignment_id, name, uid, subm.entered_grade, assgn.points_possible, subm.attempt, subm.submitted_at))
            handle.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(subm.assignment_id, name, uid, subm.entered_grade, assgn.points_possible, subm.attempt, subm.submitted_at))
        handle.close()
    
