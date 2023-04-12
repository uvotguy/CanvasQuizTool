import os
import json
from pathlib import Path

class config:
    outputFolder = ''
    ignoreNames = []
    emailDomain = ''

    canvasUserId = ''
    canvasToken = ''
    canvasUrl = ''

    kalturaUrl = ''
    kalturaPid = ''
    kalturaSecret = ''
    kalturaUser = ''

    def __init__(self):
        configFile = 'config.json'
        try:      
            # Opening JSON file
            f = open(configFile, "r")
            config_data = json.load(f)
        except:
            print('\n\nError parsing config file:  {0}\n'.format(configFile))
            exit(8)
        finally:
            f.close()

        home = Path.home().absolute()
        self.outputFolder = Path.joinpath(home, config_data["OutputFolder"])
        print('Output folder is {0}\n'.format(self.outputFolder))
     
        self.emailDomain = config_data["EmailDomain"]

        lst = config_data["IgnoreNames"].split(',')
        for nn in lst:
            thisName = nn.strip()
            #thisName = thisName.replace(self.emailDomain, '')
            self.ignoreNames.append(thisName)
        print("Ignoring quiz submissions from these people:  {0}\n".format(self.ignoreNames))

        self.kalturaUrl = config_data["KalturaUrl"]
        
        try:
            self.canvasUserId = os.environ['CANVAS_USER_ID']
        except:
            print('\n\nOops!  You forgot to set the CANVAS_USER_ID environment variable.\n\n')
            exit(1)

        try:
            self.canvasToken = os.environ['CANVAS_USER_TOKEN']
        except:
            print('\n\nOops!  You forgot to set the CANVAS_USER_ID environment variable.\n\n')
            exit(2)

        try:
            self.canvasUrl = os.environ['CANVAS_URL']
        except:
            print('\n\nOops!  You forgot to set the CANVAS_URL environment variable.\n\n')
            exit(3)

        try:
            self.kalturaPid = os.environ['KALTURA_PID']
        except:
            print('\n\nOops!  You forgot to set the KALTURA_PID environment variable.\n\n')
            exit(5)

        try:
            self.kalturaSecret = os.environ['KALTURA_SECRET']
        except:
            print('\n\nOops!  You forgot to set the KALTURA_SECRET environment variable.\n\n')
            exit(6)

        try:
            self.kalturaUser = os.environ['KALTURA_USER']
        except:
            print('\n\nOops!  You forgot to set the KALTURA_USER environment variable.\n\n')
            exit(7)