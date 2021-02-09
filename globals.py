import os

try:
    targetUserId = os.environ['CANVAS_USER_ID']
except:
    print('/n/nOops!  You forgot to set the CANVAS_USER_ID environment variable./n/n')
    exit(1)

try:
    canvasToken = os.environ['CANVAS_USER_TOKEN']
except:
    print('/n/nOops!  You forgot to set the CANVAS_USER_ID environment variable./n/n')
    exit(2)

try:
    canvasUrl = os.environ['CANVAS_URL']
except:
    print('/n/nOops!  You forgot to set the CANVAS_URL environment variable./n/n')
    exit(3)

try:
    kalturaUrl = os.environ['KALTURA_URL']
except:
    print('/n/nOops!  You forgot to set the KALTURA_URL environment variable./n/n')
    exit(4)

try:
    value = os.environ['CANVAS_USERS_TO_IGNORE']
    ignoreUids = value.split(',')
except:
    ignoreUids = []     # Empty list

try:
    kalturaPid = os.environ['KALTURA_PID']
except:
    print('/n/nOops!  You forgot to set the KALTURA_PID environment variable./n/n')
    exit(5)

try:
    kalturaSecret = os.environ['KALTURA_SECRET']
except:
    print('/n/nOops!  You forgot to set the KALTURA_SECRET environment variable./n/n')
    exit(6)

try:
    kalturaUser = os.environ['KALTURA_USER']
except:
    print('/n/nOops!  You forgot to set the KALTURA_USER environment variable./n/n')
    exit(7)