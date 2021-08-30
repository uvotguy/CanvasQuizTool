from clsKalturaApi import clsKalturaApi
import globals

myKaltura = clsKalturaApi()

done = False
while done == False:
    print("\nEnter a Quiz ID ([Enter] to quit):")
    quizId = input()
    if quizId == "":
        exit(0)
    print("\n\tChecking ...")
    try:
        myKaltura.getKalturaQuizEntry(quizId)
        print("\tQuiz found.  Title=", myKaltura.kalturaEntry.name)
        print("\n\tEnter a student User Id ([Enter] to quit):")
        uid = input()
        if uid == '':
            exit(0)
        if uid.endswith("@psu.edu") == False:
            uid += "@psu.edu"

        myKaltura.getKalturaQuizUserSubmissions(uid)

        if len(myKaltura.submissions) > 0:
            print("\n\tDelete submissions [y/n]?")
            answer = input()
            if answer == 'y':
                for subm in myKaltura.submissions:
                    print('\tDeleting quiz submission:  UserId={0}; Submission Id={1};'.format(uid, subm.id))
                    myKaltura.deleteSubmission(subm.id)
                print("done")
    except:
        print("\nQuiz not found.  Try again.")
    