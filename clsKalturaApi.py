from os import O_APPEND
import os
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Quiz import *
import util
import globals
from datetime import datetime

class clsKalturaApi:
    # Class variables shared by all instances of the class
    # In C/C++ these are known as "static variables".
    client = None
    kalturaEntry = None
    submissions = None
    submissionUids = None
    keepGrade = None

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
            exit(13)
        if result.capabilities != 'quiz.quiz':
            print("\n\nEntry is not a quiz.\n\n")
            exit(14)
        if result.views == 0:
            print("\n\nQuiz has zero views\n\n")
            self.submissions = []
            return
        if result.plays == 0:
            self.submissions = []
            return
        self.kalturaEntry = result

        quiz = self.client.quiz.quiz.get(quizId)

        if quiz.scoreType.value == 1:
            self.keepGrade = 'Highest'
        elif quiz.scoreType.value == 2:
            self.keepGrade = 'Lowest'
        elif quiz.scoreType.value == 3:
            self.keepGrade = 'Latest'
        elif quiz.scoreType.value == 4:
            self.keepGrade = 'First'
        elif quiz.scoreType.value == 5:
            self.keepGrade = 'Average'
        else:
            print("\n\nScore type not set on Kaltura Quiz.  Don't know which to keep.")
            exit(15)

    def getKalturaQuizSubmissions(self):
        self.submissions = []
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
        print("\t\t\tGot {0} quiz submissions".format(len(self.submissions)))
    
    def saveSubmissions(self, canvasCourseId):
        self.submissionUids = []
        filename = util.makeQuizFilename(str(canvasCourseId), self.kalturaEntry.id, 'KalturaQuizSubmissions', 'tsv')
        handle = open(filename, "wt")
        msg = 'Score Type\t{0}'.format(self.keepGrade)
        handle.write(msg + '\n')
        msg = 'Entry ID\tName\tUser Id\tCalculated Score\tSubmitted At'
        handle.write(msg + '\n')
        for subm in self.submissions:
            intDate = subm.updatedAt
            dt = datetime.fromtimestamp(intDate)
            # We need to save the full name of the user who submitted this kaltura quiz.  It's what we use
            # later to compare results to canvas scores.
            kalturaUser = self.client.user.get(subm.userId)
            self.submissionUids.append((kalturaUser.fullName, kalturaUser.id))
            msg = '{0}\t{1}\t{2}\t{3}\t{4}Z'.format(subm.entryId, kalturaUser.fullName, kalturaUser.id, subm.calculatedScore, dt)
            handle.write(msg + '\n')
        handle.close()