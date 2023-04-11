from os import O_APPEND
import os
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Quiz import *
import util
from config import config
from datetime import datetime
from pathlib import Path

class clsKalturaApi:
    # Class variables shared by all instances of the class
    # In C/C++ these are known as "static variables".
    client = None
    appConfig = None
    entries = []        # List of Kaltura entries already queried.
    quizzes = []        # List of Kaltura quiz objects, one per entry
    submissions = []    # Master list of all submissions for all quizzes in this course

    def __init__(self, cc):
        self.appConfig = cc
        kalConfig = KalturaConfiguration()
        self.client = KalturaClient(kalConfig)
        ks = self.client.session.start(
                    self.appConfig.kalturaSecret,
                    self.appConfig.kalturaUser,
                    KalturaSessionType.ADMIN,
                    self.appConfig.kalturaPid)
        self.client.setKs(ks)

    def getKalturaQuizEntry(self, entryId):
        result = self.client.media.get(entryId)
        if result == None:
            print("\t\tEntry not found:  {0}".format(entryId))
            exit(13)
        if result.capabilities != 'quiz.quiz':
            print("\t\tEntry is not a quiz.")
            exit(14)
        self.entries.append(result)
      
        # Got the Kaltura entry object.  Now fetch the corresponding
        # quiz object.
        quiz = self.client.quiz.quiz.get(entryId)
        if quiz == None:  
            print("\t\tKaltura quiz object not found for entry")
            exit(15)
        self.quizzes.append(quiz)

    # Fetch a Kaltura entry object for a given Entry ID. 
    def getEntry(self, id):
        for entr in self.entries:
            if entr.id == id:
                return entr
        print ("Uh oh!  Entry not found in list.  This shouldn't happen.")
        exit(16)

    # Fetch a Kaltura quiz object for a given Entry ID.  Quiz objects do not
    # have the entry ID of the quiz.  Whaaaa??  Get the index of the entry
    # and use that.
    def getQuiz(self, id):
        ii = 0
        entry = None
        for entr in self.entries:
            if entr.id == id:
                entry = entr
                break
            ii += 1
        if entry == None:
            print ("Uh oh!  Quiz object not found in list.  This shouldn't happen.")
            exit(17)
        return self.quizzes[ii]

    def getKalturaQuizSubmissions(self, entryId):
        pager = KalturaFilterPager()
        pager .pageIndex = 1
        pager.pageSize = 500

        quizFilter = KalturaQuizUserEntryFilter()
        quizFilter.userIdEqualCurrent = KalturaNullableBoolean.FALSE_VALUE
        quizFilter.entryIdEqual = entryId
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
        print("\t\tGot {0} Kaltura quiz submissions".format(len(self.submissions)))

    def getCorrectQuizSubmission(self, entryId, userId, keepGrade):
        userRecords = []
        for subm in self.submissions:
            if (subm.entryId == entryId) and (subm.userId == userId):
                userRecords.append(subm)

        if keepGrade == 'Latest':
            latestDate = 0
            keepRecord = None
            for subm in userRecords:
                if subm.updatedAt >= latestDate:
                    keepRecord = subm
                    latestDate = subm.updatedAt
        elif keepGrade == 'Highest':
            highest = -1.0
            keepRecord = None
            for subm in userRecords:
                if subm.calculatedScore  >= highest:
                    keepRecord = subm
                    highest = subm.calculatedScore
        else:
            raise "Uh oh!  Grade type not handled."
        
        return keepRecord

    def saveSubmissions(self, courseFolder): 
        filename = Path.joinpath(courseFolder, 'kalturaSubmissions.tsv')
        kalturaFile = open(filename, 'wt')
        kalturaFile.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'
                                .format('Assignment', 
                                        'Entry ID', 
                                        'User ID',
                                        'Keep Grade',
                                        'Calculated Score',
                                        'Created At',
                                        'Update At'))
        handle = open(filename, "wt")
        for subm in self.submissions:
            entry = self.getEntry(subm.entryId)
            quiz = self.getQuiz(subm.entryId)
            keepGrade = self.keepGradeToText(quiz.scoreType.value)
            kalturaFile.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'
                            .format(entry.name, 
                                    subm.entryId, 
                                    subm.userId,
                                    keepGrade,
                                    round(subm.score,2),
                                    util.unixTimeToDateString(subm.createdAt),
                                    util.unixTimeToDateString(subm.updatedAt)))
        handle.close()

    def keepGradeToText(self, value):
        if value == 1:
            return 'Highest'
        elif value == 2:
            return 'Lowest'
        elif value == 3:
            return'Latest'
        elif value == 4:
            return 'First'
        elif value == 5:
            return 'Average'
        else:
            print("\n\nScore type not set on Kaltura Quiz.  Don't know which to keep.")
            exit(18)
