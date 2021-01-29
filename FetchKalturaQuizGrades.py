import sys
import os
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Quiz import *
from datetime import datetime
from pathlib import Path

if len(sys.argv) > 1:
    quizId = sys.argv[1]
else:
    print("Usage:  {0} EntryId UserId".format(sys.argv[0]))
    exit(1)

print("Entry:  {0}".format(quizId))

try:
    kalturaPid = os.environ['KALTURA_PID']
except:
    print('/n/nOops!  You forgot to set the KALTURA_PID environment variable./n/n')
    exit(3)

try:
    kalturaSecret = os.environ['KALTURA_SECRET']
except:
    print('/n/nOops!  You forgot to set the KALTURA_SECRET environment variable./n/n')
    exit(4)

try:
    kalturaUser = os.environ['KALTURA_USER']
except:
    print('/n/nOops!  You forgot to set the KALTURA_USER environment variable./n/n')
    exit(5)

config = KalturaConfiguration(kalturaPid)
config.serviceUrl = "https://www.kaltura.com/"
client = KalturaClient(config)
ks = client.session.start(
      kalturaSecret,
      kalturaUser,
      KalturaSessionType.ADMIN,
      kalturaPid)
client.setKs(ks)

result = client.media.get(quizId)
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

datestr = datetime.today().strftime('%Y-%m-%d')
home = Path.home().absolute()
filename = Path.joinpath(home, datestr + '_FetchKalturaQuizGrades-' + quizId + '.tsv')
handle = open(filename, "wt")

pager = KalturaFilterPager()

quizFilter = KalturaQuizUserEntryFilter()
quizFilter.userIdEqualCurrent = KalturaNullableBoolean.FALSE_VALUE
quizFilter.entryIdEqual = quizId
quizFilter.statusEqual = KalturaUserEntryStatus.QUIZ_SUBMITTED
quizSubmissions = client.userEntry.list(quizFilter, pager)
msg = 'Entry ID\tName\tUser Id\tCalculated Score\tSubmitted At'
print(msg)
handle.write(msg + '\n')
for subm in quizSubmissions.objects:
    intDate = subm.updatedAt
    dt = datetime.fromtimestamp(intDate)
    kalturaUser = client.user.get(subm.userId)
    msg = '{0}\t{1}\t{2}\t{3}\t{4}Z'.format(subm.entryId, kalturaUser.fullName, kalturaUser.id, subm.calculatedScore, dt)
    handle.write(msg + '\n')
    print(msg)

handle.close()
print("\n\nOutput written to {0}".format(filename))
print('done')