from slugify import slugify

class clsGradebookEntry:
    course = ''
    courseSlug = ''
    assignment = ''
    assignmentSlug = ''
    userId = ''
    canvasId = -1
    name = ''
    sortableName = ''
    canvasGrade = -1.0
    allowedAttempts = 0
    submittedAt = []
    grades = []
    late = []
    deductions = []

    def __init__(self, crsNam, assgn, allowedAtt, uid, canvId, nam, sortName):
        self.course = crsNam
        self.courseSlug = slugify(self.course)
        self.assignment = assgn
        self.allowedAttempts = allowedAtt
        self.assignmentSlug = slugify(self.assignment)
        self.userId = uid
        self.canvasId = canvId
        self.name = nam
        self.sortableName = sortName
        self.canvasGrade = -1.0
        self.grades = []
        self.submittedAt = []
        self.late = []
        self.deductions = []

    def addSubmission(self, grade, submitDate, late, deduction):
        self.grades.append(round(grade,2))
        self.submittedAt.append(submitDate)
        if late:
            ll = 'Late'
        else:
            ll = ''
        self.late.append(ll)
        self.deductions.append(deduction)
