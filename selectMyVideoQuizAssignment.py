import re

def selectMyVideoQuizAssignment(thisCourse, assignments, kalturaUrl):
    thisQuiz = None
    videoQuizzes=[]
    ii = 0
    for asgn in assignments:
        if hasattr(asgn, 'external_tool_tag_attributes'):
            url = asgn.external_tool_tag_attributes['url']
            result = re.search(kalturaUrl, url)
            if result != None:
                idSearch = re.search(r'\/media\/entryid\/(\w*)', url)
                if idSearch != None:
                    entryId = idSearch.group(1)
                    tt = (asgn.name, asgn.id, entryId, ii)
                    videoQuizzes.append(tt)
        ii += 1
    ii = 0
    print("Select a video quiz:")
    for quiz in videoQuizzes:
        print ('{0})  {1}'.format(ii, quiz[0]))
        ii += 1

    selectedVideoQuiz = int(input())
    if (selectedVideoQuiz > -1) and (selectedVideoQuiz < len(videoQuizzes)):
        thisQuiz = videoQuizzes[selectedVideoQuiz]
        print ("Fetching grades for quiz {0}:".format(thisQuiz[0]))
    else:
        print("Invalid selection:  {0}.".format(selectedVideoQuiz))
        exit(3)

    return thisQuiz
