import re
from slugify import slugify
from pathlib import Path
import canvasapi
from config import config
from clsGradebookEntry import clsGradebookEntry

import util
class clsCanvasApi:
    # Class variables shared by all instances of the class
    # In C/C++ these are known as "static variables".
    appConfig = None
    client = None
    selectedCourse = None
    courseFolder = ''
    courseSlug = ''
    assignments = []
    assignmentEntryIds = []
    quizFolder = ''
    teachers = []
    submissions = []
    gradebook = []
    # Keep track of students as we query them.  No sense beating the
    # heck out of the Canvas API.
    activeStudents = []

    def __init__(self, cc):
        self.appConfig = cc

        try:
            self.client = canvasapi.Canvas(self.appConfig.canvasUrl, self.appConfig.canvasToken)            
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
                    print('{0}) {1}'.format(index, course.name))
                else:
                    print('{0}) unavailable {1}'.format(index, course.id))
                index += 1
        except canvasapi.exceptions.ResourceDoesNotExist as ex:
            print(ex)
            exit(11)

        selectedIndex = int(input())
        if (selectedIndex > -1) and (selectedIndex < index):
            self.selectedCourse = courses[selectedIndex]
            self.courseSlug = slugify(self.selectedCourse.name)
            self.courseFolder = util.makeCourseFolder(self.appConfig.outputFolder, self.courseSlug)
            print('\n{0}'.format(self.selectedCourse.name))
            # print ("Fetching video quizzes for course {0}:".format(self.selectedCourse.name))
            self.getIvqAssignments()
        else:
            print("Invalid selection:  {0}.".format(selectedIndex))
            exit(12)
        
        print('\tFetching teachers')
        print('\t\t', end='')
        allTeachers = self.selectedCourse.get_users(enrollment_type='teacher')
        for teacher in allTeachers:
            print('.', end='')
            if teacher.name in self.appConfig.ignoreNames:
                continue
            self.teachers.append(teacher)
        print('\n\t\tFound {0} teachers'.format(len(self.teachers)))

        print('\tFetching student records')
        enrollments = self.selectedCourse.get_enrollments()
        print('\t\t', end='')
        for enr in enrollments:
            if enr.user_id in self.appConfig.ignoreNames:
                continue
            print('.', end='')
            if enr.enrollment_state == 'active':
                usr = self.selectedCourse.get_user(enr.user_id)
                self.activeStudents.append(usr)
        print('\n\t\tFound {0} active students'.format(len(self.activeStudents)))

    def makeCourseGradebook(self):
        # Loop over assignmens and make a gradebook.  It is possible that
        # not all students are required to complete all assignments, so get a
        # list of gradeable students for each one.  The gradebook will have an
        # entry for each (assignment, gradeable student) tuple.
        print("\tQuerying Canvas assignments for this course")
        print('\tWARNING!!!  Ignoring students without sis_user_id.')
        for asgn in self.assignments:
            #print('\t{0}'.format(asgn.name))
            print('\n\t.', end='')
            #self.quizFolder = util.makeQuizFolder(self.appConfig.outputFolder, self.courseSlug, slugify(asgn.name))

            # Get a list of submissions for this assignment.
            # Since this is a paginated list, we have to loop through and append
            # to a local array.
            self.submissions = []
            submissions = asgn.get_submissions()
            for subm in submissions:
                self.submissions.append(subm)
            #print('\t\tGot {0} submissions to Canvas'.format(len(self.submissions)))

            if (asgn.allowed_attempts == -1):
                allowedAttempts = "Unlimited"
            else:
                allowedAttempts = str(asgn.allowed_attempts)
            #print('\t\t{0} allowed attempts'.format(allowedAttempts))

            gradeableStudents = asgn.get_gradeable_students()
            nGradeable = 0
            for st in gradeableStudents:
                usr = self.getStudent(st.id)
                if usr == None:
                    # Student no longer enrolled
                    # usr = self.selectedCourse.get_user(st.id)
                    #print("x", end='')
                    continue
                elif (usr.sis_user_id == None):
                    # Ignore users without an sis_user_id
                    #print('\tWARNING!!!  Ignoring student without sis_user_id.  Name={0}'.format(st.display_name))
                    #print('?', end='')
                    continue
                else:
                    print('.', end='')

                nGradeable += 1
                #print('\t\t\t{0}'.format(usr.sis_user_id))
                thisGradebookEntry = clsGradebookEntry(self.selectedCourse.name,
                                                       asgn.name,
                                                       allowedAttempts,
                                                       usr.sis_user_id,
                                                       usr.id,
                                                       usr.name,
                                                       usr.sortable_name)
                thisStudentSubmissions = []
                for subm in self.submissions:
                    if (subm.assignment_id == asgn.id) and (subm.user_id == st.id):
                        if subm.grade == None:
                            continue
                        if subm.grade == '':
                            continue

                        if subm.points_deducted == None:
                            deduction = 0.00
                        else:
                            deduction = round(subm.points_deducted, 2)

                        thisStudentSubmissions.append(subm)
                        thisGradebookEntry.addSubmission(float(subm.grade), subm.submitted_at, subm.late, deduction)
                #print('\t\t\t\t{0} submissions'.format(len(thisStudentSubmissions)))

                self.gradebook.append(thisGradebookEntry)
            #print('\t\tGot {0} gradeable students'.format(nGradeable))  
        print('\n')

    def saveCourseGradebook(self):
        gradebookFilename = Path.joinpath(self.courseFolder, 'gradebook.tsv')
        filehandle = open(gradebookFilename, 'wt')
        filehandle.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\n'
                            .format('Assignment',
                                    'Entry ID',
                                    'User ID', 
                                    'Canvas User ID', 
                                    'Name', 
                                    'Grade', 
                                    'Allowed Attempts',
                                    'Submitted At',
                                    'Grades',
                                    'Late',
                                    'Deduction'))
        for rec in self.gradebook:
            entryId = self.getAssignmentEntryId(rec.assignment)
            filehandle.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'
                             .format(rec.assignment,
                                     entryId,
                                     rec.userId, 
                                     rec.canvasId, 
                                     rec.sortableName, 
                                     rec.canvasGrade, 
                                     rec.allowedAttempts,
                                     rec.submittedAt,
                                     util.stripArray(rec.grades),
                                     util.stripArray(rec.late),
                                     util.stripArray(rec.deductions)))
        filehandle.close()

    def getStudent(self, canvasUserId):
        for st in self.activeStudents:
            if (st.id == canvasUserId):
                return st
        return None

    def getAssignmentEntryId(self, searchValue):
        ii = 0
        for asgn in self.assignments:
            if asgn.name == searchValue:
                return self.assignmentEntryIds[ii]
            ii += 1
        return ''

    def getIvqAssignments(self):
        # Make a list of all assignments
        allAssignments = self.selectedCourse.get_assignments(order_by="due_at")
        for asgn in allAssignments:
            entryId = self.getIvqAssignmentEntryId(asgn)
            if entryId != None:
                # According to the Canvas API docs, "grading_type" is one of 'pass_fail',
                # 'percent', 'letter_grade', 'gpa_scale', 'points'.  This algorithm
                # only supports the 'points' type.
                if asgn.grading_type != 'points':
                    print('WARNING!!!  Unsupported grading type:  {0}.  Skipping ...'
                          .format(asgn.grading_type))
                self.assignments.append(asgn)
                self.assignmentEntryIds.append(entryId)

    def getQuizGradebook(self, asgn):
        records = []
        for rec in self.gradebook:
            if rec.assignment == asgn.name:
                records.append(rec)
        return records

    def getIvqAssignmentEntryId(self, asgn):
        if hasattr(asgn, 'external_tool_tag_attributes'):
            url = asgn.external_tool_tag_attributes['url']
            result = re.search(self.appConfig.kalturaUrl, url)
            if result != None:
                idSearch = re.search(r'\/media\/entryid\/(\w*)', url)
                if idSearch != None:
                    return idSearch.group(1)
            # Some video quiz URIs might begin with this:    
            result = re.search('https://psucanvas-prod.kaf.kaltura.com/browseandembed/index/media/entryid/', url)
            if result != None:
                idSearch = re.search(r'\/media\/entryid\/(\w*)', url)
                if idSearch != None:
                    return idSearch.group(1) 
        return None
