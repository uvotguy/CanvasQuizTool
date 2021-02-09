from os import O_APPEND
import os
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Quiz import *
import kochUtilities
import globals
from datetime import datetime

class clsKalturaApi:
    # Class variables shared by all instances of the class
    # In C/C++ these are known as "static variables".
    client = None
    kalturaEntry = None
    submissions = None
    submissionUids = None

    def __init__(self):
        config = KalturaConfiguration(globals.kalturaPid)
        config.serviceUrl = "https://www.kaltura.com/"
        self.client = KalturaClient(config)
        ks = self.client.session.start(
                    globals.kalturaSecret,
                    globals.kalturaUser,
                    KalturaSessionType.ADMIN,
                    globals.kalturaPid)
        self.client.setKs(ks)

    def getKalturaQuizEntry(self, quizId):
        result = self.client.media.get(quizId)
        if result == None:
            print("\n\nEntry not found:  {0}\n\n".format(quizId))
            exit(6)
        if result.capabilities != 'quiz.quiz':
            print("\n\nEntry is not a quiz.\n\n")
            exit(7)
        if result.views == 0:
            print("\n\nQuiz has zero views\n\n")
            exit(8)
        if result.plays == 0:
            print("\n\nQuiz has zero plays\n\n")
            exit(9)
        self.kalturaEntry = result

    def getKalturaQuizSubmissions(self):
        self.submissions = []
        self.submissionUids = []
        pager = KalturaFilterPager()
        pager .pageIndex = 1
        pager.pageSize = 500

        quizFilter = KalturaQuizUserEntryFilter()
        quizFilter.userIdEqualCurrent = KalturaNullableBoolean.FALSE_VALUE
        quizFilter.entryIdEqual = self.kalturaEntry.id
        quizFilter.statusEqual = KalturaUserEntryStatus.QUIZ_SUBMITTED
        done = False
        while done == False:
            quizSubmissions = self.client.userEntry.list(quizFilter, pager)
            if len(quizSubmissions.objects) == 0:
                done = True
                continue
            else:
                pager.pageIndex += 1
            for subm in quizSubmissions.objects:
                self.submissions.append(subm)
    
    def saveSubmissions(self, canvasCourseId):
        filename = kochUtilities.makeFilename(str(canvasCourseId), 'KalturaQuizSubmissions_' + self.kalturaEntry.id, 'tsv')
        handle = open(filename, "wt")
        msg = 'Entry ID\tName\tUser Id\tCalculated Score\tSubmitted At'
        handle.write(msg + '\n')
        for subm in self.submissions:
            intDate = subm.updatedAt
            dt = datetime.fromtimestamp(intDate)
            kalturaUser = self.client.user.get(subm.userId)
            self.submissionUids.append((kalturaUser.fullName, kalturaUser.id))
            msg = '{0}\t{1}\t{2}\t{3}\t{4}Z'.format(subm.entryId, kalturaUser.fullName, kalturaUser.id, subm.calculatedScore, dt)
            handle.write(msg + '\n')
        handle.close()