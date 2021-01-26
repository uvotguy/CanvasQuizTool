# Canvas Quiz Tool
This tool can be used to dump student assignment grades for your course.

## Setup
Access to your Canvas course is granted via a Canvas API token.  Tokens are easily created in Canvas:

1. Log into Canvas
2. Select *Account*
3. Select *Settings*
4. Click the **+ New Access Token** button

Be sure to save your token in a secure place.  Canvas will not allow you to view it again.  Of course,
you can always create another.

The quiz tool reads sensitive variables from your environment.  Set the following environment variables:

CANVAS_USER_ID - your Canvas login (e.g. AustinPowers@mi6.gov)
CANVAS_USER_TOKEN - the token you just created
CANVAS_URL - URL of your Canvas instance (e.g. https://mi6.instructure.com)
KALTURA_URL = URL of your Canvas KAF instance (e.g. https://mi6canvas-prod.kaf.kaltura.com)
CANVAS_USERS_TO_IGNORE - Comma separated list of **teachers** to ignore (e.g. AustinPowers@mi6.gov,MrBigglesworth@mi6.gov,NumberTwo@mi6.gov)

If any of these is not set, the code program will give an error message and exit.  If your login
and / or token are incorrect, the program will print a message and exit.

### Python Setup
You will need to install the Python Canvas API module:

*pip install canvasapi*

## Run the Program

*python3 CanvasQuizTool.py*

on Windows:

*py CanvasQuizTool.py*

Select a course from the menu.

Select a video quiz from the menu.
