# ReportCourseQuizResults
We occasionally see differences between grades in a course gradebook (for a Canvas course)
and grades submitted to the gradebook via the Kaltura KAF module.  This is a known problem
which has yet to be solved.  This tool can be used to compare Canvas gradebook grades to 
the grades submitted by Kaltura when a student takes an Interactive Video Quiz (IVQ).

Access to your Canvas quiz data is granted via an Access Token.  Access to Kaltura quiz
data is granted via your instance administrative secret.


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
are allowed.  Based upon how the instuctor chooses (in Kaltura) to handle multiple attempts, the
two scores may differ.  See the definition of **scoreType** in the Kaltura API documentation:
https://developer.kaltura.com/api-docs/service/quiz/action/get.  Grades can also differ if a
deduction is applied in Canvas.  Instructors can manually adjust a grade.  Grades can also differ
because of a late submission.  *Canvas Quiz Tool* takes deductions into account.

**As of this writing, *Canvas Quiz Tool* only handles the *Latest* and *Highest* grade types.**

## Setup

### Canvas Access Token
Access to your Canvas course is granted via a Canvas API token.  Tokens are easily created in Canvas:

1. Log into Canvas
2. Select *Account*
3. Select *Settings*
4. Click the **+ New Access Token** button

Be sure to save your token in a secure place.  Canvas will not allow you to view it again.  Of course,
you can always create another.

### Kaltura Secret
Kaltura administrators (with KMC access) should have access to your institution's data.
The Partner Id and Administrative Secret are shown on the *Account > Integration* tab.  Be sure to safeguard
them.

### Environment Variables
The quiz tool reads sensitive variables from your environment.  Set the following environment variables:

|        Variable       |                    Description |
|---------------------- | ------------------------------------------------------------------------------------|
|CANVAS_USER_ID         | your Canvas login (e.g. AustinPowers@mi6.gov)|
|CANVAS_USER_TOKEN      | the token you just created |
|CANVAS_URL             | URL of your Canvas instance (e.g. https://mi6.instructure.com)|
|KALTURA_URL            | URL of your Canvas KAF instance (e.g. https://mi6canvas-prod.kaf.kaltura.com)|
|CANVAS_USERS_TO_IGNORE | Comma separated list of UserIds to ignore (e.g. AustinPowers@mi6.gov,MrBigglesworth@mi6.gov,NumberTwo@mi6.gov)|
|KALTURA_PID            | Kaltura Partner ID|
|KALTURA_SECRET         | Administrative secret|
|KALTURA_USER           | Kaltura User Id must have administrative privilege to dump scores|
|KALTURA_EMAIL_DOMAIN   | Kaltura User IDs end in this value, e.g. "@abc.edu"|
|KALTURA_KAF_URL        | The URL for your KAF module, e.g. 'https://acme.kaf.kaltura.com/browseandembed/index/media/entryid/'|

If any of these is not set, the code program will give an error message and exit.  If your login
and/or token are incorrect, the program will print a message and exit.

### Configuration File
Set your desired output folder by editing 
The following items can be set in the application configuration file:  *config.json*.
Variable | Description            |

| OutputFolder | blah |
| EmailDomain  | This parameter is currently not used. |
| IgnoreNames  | A comma-separated list of User IDs to ignore.  This may be useful for ignoring system administrators who take exams for test purposes. |
| KalturaUrl   | The base URL for access to the Kaltura API. |

### Python Setup
Install the Python Canvas API module:

*pip install canvasapi*

Also install the Kaltura API Client for python:

*pip install KalturaApiClient*

If you have to install additional modules, please submit an issue.  We will add it/them here.

## Run the Program
*Canvas Quiz Tool* prompts you with
a list of Canvas courses you teach (i.e. you are enrolled as *Teacher*).
*Canvas Quiz Tool* queries your selection for a list of assignments, and filters
out those assignments not associated with a Kaltura video quiz.

It loops over video quiz assignments, gathering Canvas quiz grades and Kaltura submissions.
Finally it compares the two datasets and writes out the results.

From a MacOS or Linux command prompt:

    > python3 CanvasQuizTool.py

From a Windows command prompt:

    > py CanvasQuizTool.py

# Program Output
Output files are written to $HOME/{OutputFolder}.  Output for each IVQ is written to
a sub-folder bearing the "slugified" version of the course name.  Three files are written:
| Filename | Description |
| -------- | ----------- |
| gradebook.tsv          | A list of Canvas gradebook entries.  The table has one row for every (assignment, student) tuple. |
| kalturaSubmissions.tsv | A tab-separated text file containing a full list of Kaltura submissions for all IVQ's used in the selected course.  **NOTE**:  Kaltura is a media platform, not an LMS.  As such, it has no concept of course, terms, enrollments, etc.  If a given quiz is used across semesters, this list will contain submissions by students who are not currently enrolled.  Inactive students will be ignored in the merged results.|
| QuizDifferences.tsv    | This list is the main output file.  It contains the proper Kaltura grade and the corrected Canvas gradebook grade.  If they differ, the *Different* column will contain an asterisk.  If a submission is marked "Late", the record will indicate so.  If a deduction was applied, the deduction will also be shown. |

Should you have problems running the code, or if you find errors in the output, please contact me.  The preferred contact method is to enter an issue on the GitHub project site.

Thank you, and have fun!!!  We hope you find this tool useful.