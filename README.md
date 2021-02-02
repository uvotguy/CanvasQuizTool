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

# Fetch Kaltura Quiz Grade Tool

This tool will dump a list of quiz submissions for a given quiz.

## Setup

Set the following environment variables:

KALTURA_PID - Kaltura Partner ID
KALTURA_SECRET - Administrative secret
KALTURA_USER - Kaltura User Id must have administrative privilege to dump scores

Install the Kaltura API Client for python:

*pip install KalturaApiClient*

## Run the program

*py FetchKalturaQuizGrade {Quiz ID}*

Output is printed to the console and written to a file.

## Debugging

Edit the **args** parameter in *launch.json*.  The first (and only)
argument it the target Entry ID.  Run the code in debug mode.