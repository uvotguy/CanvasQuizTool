# ReportCourseQuizResults
We occasionally see differences between grades in a course gradebook (for a Canvas course)
and grades submitted to the gradebook via the Kaltura KAF module.  This is a known problem
which has yet to be solved.  This tool can be used to compare Canvas gradebook grades to 
the grade(s) submitted by Kaltura when a student takes, and possible re-takes a video quiz.

The main output file is a table of grades as submitted by Kalura and the corresponding grade
recorded by Canvas.  An asterisk in the last column indicates a difference between grades.
Some courses have many students and many video quizzes.  To simplify comparison, the program
loops over all results for a user-selected course.  For a class of 160 students given about
20 video quizzes (some with multiple attempts enabled), the program takes about 20 minutes
to generate a report.

# Taking Quizzes
A basic knowledge of how quizzing works might be helpful in understading the program -
especially if you intend to modify it for your own purposes.

Video quizzes are created in Kaltura.  Instructors use the *Assignments* inteface in Canvas to
associate a Kaltura Video Quiz with a course assignment.  Video quizzes are delivered by
Kaltura.  When a student takes a video quiz, Kaltura gathers student responses and stores them
in a Kalura database.  Upon submission, Kaltura saves the score and computes an *effective*
score, and sends the results to Canvas via the Kaltura KAF module.  If everything works 
properly, quiz results appear automatically in the course gradebook.

Note that a quiz score may be different than the computed *effective* score if muliple attempts
are allows.  Based upon how the instuctor chooses (in Kaltura) to handle multiple attempts, the
two scores may differ.  See the definition of **scoreType** in the Kaltura API documentation:
https://developer.kaltura.com/api-docs/service/quiz/action/get.

# Program Output
The main output files is saved to a standard output folder:  ~/CanvasQuizResults/{Canvas Course ID}/.
Raw output files for a given quiz are written to a sub-folder named by its Kaltura Entry Id.  Raw
Kaltura output contains all quiz submissions, so multiple submissions and scores are shown.  Raw
Canvas files contain useful header information such as course instructor(s), scoring method, and
allowed number of attempts.


## Setup
Only teachers have permission to view course grades.  Canvas administrators
at your institution can grant you access.  When presented with a list of courses to
select, you will only see courses you teach (or at least have *Teacher* privilege).

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
|:----------------------	|:-------------------------------------------------------------------------------------------------------------------	|
| CANVAS_USER_ID         	| your Canvas login (e.g. AustinPowers@mi6.gov)                                                                       	|
| CANVAS_USER_TOKEN      	| the token you just created                                                                                          	|
| CANVAS_URL             	| URL of your Canvas instance (e.g. https://mi6.instructure.com)                                                      	|
| KALTURA_URL            	| URL of your Canvas KAF instance (e.g. https://mi6canvas-prod.kaf.kaltura.com)                                       	|
| CANVAS_USERS_TO_IGNORE 	| Comma separated list of **teachers** to ignore (e.g. AustinPowers@mi6.gov,MrBigglesworth@mi6.gov,NumberTwo@mi6.gov) 	|
| KALTURA_PID            	| Kaltura Partner ID                                                                                                  	|
| KALTURA_SECRET         	| Administrative secret                                                                                               	|
| KALTURA_USER           	| Kaltura User Id must have administrative privilege to dump scores                                                   	|
| KALTURA_EMAIL_DOMAIN      | Kaltura User IDs end in this value, e.g. "@abc.edu"         |

If any of these is not set, the code program will give an error message and exit.  If your login
and/or token are incorrect, the program will print a message and exit.

### Python Setup
Install the Python Canvas API module:

*pip install canvasapi*

Also install the Kaltura API Client for python:

*pip install KalturaApiClient*

If you have to install additional modules, please submit an issue.  We will add it/them here.

## Run the Program
The top level python program *ReportCourseQuizResults.py* prompts the user to select a course from
a list of Canvas courses he/she teaches.  It queries Canvas for a list of assignments, and filters
out those assignments not associated with a Kaltura video quiz.

The program loops over video quiz assignments, gathers Canvas quiz grades, gathers Kaltura submissions, and
compares the two datasets.

*python3 ReportCourseQuizResults.py*

On windows:

*py ReportCourseQuizResults.py*

## Debugging
Edit the **args** parameter in *launch.json*.  The first (and only)
argument is the target Entry ID.  Run the code in debug mode.

## Deleting Quiz Submissions
Use the *ClearStudentQuizSubmissions* utility to remove quiz submissions for a given quiz for a given student.
The program **DOES NOT** check submission date.  It will *delete* entry submissions from your Kaltura instance.
Use it carefully.