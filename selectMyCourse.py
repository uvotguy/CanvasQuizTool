import canvasapi

def selectMyCourse(client):
    ii = 0
    thisCourse = None
    print("Select a course:")
    try:
        courses = client.get_courses()
        for course in courses:
            if hasattr(course, 'course_code'):
                print('{0}) {1}'.format(ii, course))
            else:
                print('{0}) unavailable {1}'.format(ii, course.id))
            ii += 1
    except canvasapi.exceptions.ResourceDoesNotExist as ex:
        print(ex)
        exit(8)

    selectedCourse = int(input())
    if (selectedCourse > -1) and (selectedCourse < ii):
        thisCourse = courses[selectedCourse]
        print ("Fetching video quizzes for course {0}:".format(thisCourse.name))
    else:
        print("Invalid selection:  {0}.".format(selectedCourse))
        exit(9)

    return(thisCourse)