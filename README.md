# Canvas Quiz Tool
This tool can be used to dump student assignment grades for a course.  The tool consists
of three parts:  a part to gather information from Canvas, a part to gather quiz submissions
from Kaltura, and a third part to compare the results.

Video quizzes are delivered by Kaltura.  When a student takes a video quiz, Kaltura gathers
student responses, computes a grade, and sends the results to Canvas via the Kaltura KAF
module.  If everything works properly, quiz results appear automatically in the course
gradebook.

Only teachers have permission to view course grades.  Canvas administrators
at your institution can grant you access.  When presented with a list of courses to
select, you will only see courses you teach (or at least have *Teacher* privilege).

## Setup
### Canvas Access Token
Access to your Canvas course is granted via a Canvas API token.  Tokens are easily created in Canvas:

1. Log into Canvas
2. Select *Account*
3. Select *Settings*
4. Click the **+ New Access Token** button

Be sure to save your token in a secure place.  Canvas will not allow you to view it again.  Of course,
you can always create another.

### Environment Variables
The quiz tool reads sensitive variables from your environment.  Set the following environment variables:
|        Variable        	|                                                     Description                                                     	|
|:----------------------:	|:-------------------------------------------------------------------------------------------------------------------:	|
| CANVAS_USER_ID         	| your Canvas login (e.g. AustinPowers@mi6.gov)                                                                       	|
| CANVAS_USER_TOKEN      	| the token you just created                                                                                          	|
| CANVAS_URL             	| URL of your Canvas instance (e.g. https://mi6.instructure.com)                                                      	|
| KALTURA_URL            	| URL of your Canvas KAF instance (e.g. https://mi6canvas-prod.kaf.kaltura.com)                                       	|
| CANVAS_USERS_TO_IGNORE 	| Comma separated list of **teachers** to ignore (e.g. AustinPowers@mi6.gov,MrBigglesworth@mi6.gov,NumberTwo@mi6.gov) 	|
| KALTURA_PID            	| Kaltura Partner ID                                                                                                  	|
| KALTURA_SECRET         	| Administrative secret                                                                                               	|
| KALTURA_USER           	| Kaltura User Id must have administrative privilege to dump scores                                                   	|
If any of these is not set, the code program will give an error message and exit.  If your login
and/or token are incorrect, the program will print a message and exit.

### Python Setup
You will need to install the Python Canvas API module:

*pip install canvasapi*

Also install the Kaltura API Client for python:

*pip install KalturaApiClient*

## Run the Program
The top level python program *ReportQuizResults.py* calls python scripts to do parts 1 and 2 as described
above.  It then compares Kalura quiz submission data with the grades in the course gradebook.

*python3 ReportQuizResults.py*

On windows:

*py ReportQuizResults.py*

The call to *CanvasQuizTool.py* prompts you to select a course.  Only courses for which you are a *Teacher*
are shown.  Select a course.  It then displays a list of course assignments that are associated with a
Kaltura video quiz.  Select a quiz.

A table of grades is printed to the screen AND written to an output file.

*ReportQuizGrades.py* then calls the script to gather Kaltura video quiz submissions for the selected
Canvas assignment.  The script prints out a table of quiz submissions AND writes the table to an output
file.

Finally, *ReportQuizResults.py* compares the two tables.  The results table is printed to the screen
AND written to an output file.  An asterisk appears in the last column when the Canvas grade does
not match the Kaltura grade.

# Additional Information
## Running Scripts Separately
Both scripts *CanvasQuizTool.py* and *FetchKalturaQuizGrades.py* may be run separately.

*python3 CanvasQuizTool.py*

*python3 FetchKalturaQuizGrade.py {Quiz ID}*

## Debugging
Edit the **args** parameter in *launch.json*.  The first (and only)
argument is the target Entry ID.  Run the code in debug mode.