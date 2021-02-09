import sys
import os
from datetime import datetime
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Quiz import *
import kochUtilities

def FetchKalturaQuizGrades(quizId):
    # Python arrays are not fixed type.  Each element can be a completely different
    # data type:  string, int, or even object.  We use that language property here.
    # The output arry contains the following information:
    #
    #   outData[0]: A copy of the Kaltura quiz media entry
    #   outData[1]: A quiz submission tuple:
    #               - User full name
    #               - User Kaltura login
    #               - Calculated score
    #               - Date submitted
    #   ...
    #   ...
    #   outData[n]: More qis submission tuples
    #
    outData = []
    print("Entry:  {0}".format(quizId))


    config = KalturaConfiguration(kalturaPid)
    config.serviceUrl = "https://www.kaltura.com/"
    kalClient = KalturaClient(config)
    ks = kalClient.session.start(
        kalturaSecret,
        kalturaUser,
        KalturaSessionType.ADMIN,
        kalturaPid)
    kalClient.setKs(ks)

    result = kalClient.media.get(quizId)
    if result == None:
        print("\n\nEntry not found:  {0}\n\n".format(quizId))
        exit(6)

    if result.capabilities == 'quiz.quiz':
        print("Title:\t{0}".format(result.name))
    else:
        print("\n\nEntry is not a quiz.\n\n")
        exit(7)

    if result.views == 0:
        print("\n\nQuiz has zero views\n\n")
        exit(8)
    else:
        print("Views:\t{0}".format(result.views))

    if result.plays == 0:
        print("\n\nQuiz has zero plays\n\n")
        exit(9)
    else:
        print("Plays:\t{0}".format(result.plays))

    filename = kochUtilities.makeFilename('FetchKalturaQuizGrades-' + quizId, 'tsv')
    handle = open(filename, "wt")

    outData.append(result)

    pager = KalturaFilterPager()
    pager .pageIndex = 1
    pager.pageSize = 500

    quizFilter = KalturaQuizUserEntryFilter()
    quizFilter.userIdEqualCurrent = KalturaNullableBoolean.FALSE_VALUE
    quizFilter.entryIdEqual = quizId
    quizFilter.statusEqual = KalturaUserEntryStatus.QUIZ_SUBMITTED
    msg = 'Entry ID\tName\tUser Id\tCalculated Score\tSubmitted At'
    print(msg)
    handle.write(msg + '\n')

    done = False
    while done == False:
        quizSubmissions = kalClient.userEntry.list(quizFilter, pager)
        if len(quizSubmissions.objects) ==0:
            done = True
            continue
        else:
            pager.pageIndex += 1

        for subm in quizSubmissions.objects:
            intDate = subm.updatedAt
            dt = datetime.fromtimestamp(intDate)
            kalturaUser = kalClient.user.get(subm.userId)
            outData.append((kalturaUser.fullName, kalturaUser.id, subm.calculatedScore, dt))
            msg = '{0}\t{1}\t{2}\t{3}\t{4}Z'.format(subm.entryId, kalturaUser.fullName, kalturaUser.id, subm.calculatedScore, dt)
            handle.write(msg + '\n')
            print(msg)
    handle.close()

    print("\n\nOutput written to {0}".format(filename))
    print('done')

    return outData

if __name__ == "__main__":
    if len(sys.argv) > 1:
        quizId = sys.argv[1]
    else:
        print("Usage:  {0} EntryId UserId".format(sys.argv[0]))
        exit(1)

    FetchKalturaQuizGrades(quizId)