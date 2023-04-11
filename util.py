from datetime import datetime
from pathlib import Path

def makeCourseFolder(rootFolder, courseSlug):
    home = Path.home().absolute()
    targetFolder = Path.joinpath(home, rootFolder, courseSlug)
    Path(targetFolder).mkdir(parents=True, exist_ok=True)
    return targetFolder

def makeQuizFolder(rootFolder, courseFolder, quizSlug):
    home = Path.home().absolute()
    targetFolder = Path.joinpath(home, rootFolder, courseFolder, quizSlug)
    Path(targetFolder).mkdir(parents=True, exist_ok=True)
    return targetFolder

def unixTimeToDateString(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def stripArray(arr):
    st = str(arr)
    st.replace('[', '')
    st.replace(']', '')
    st.replace('\'', '')
    st.replace(',', ' ')

# def makeQuizFilename(canvasCourseName, quizEntryId, rootFilename, extension):
#     datestr = datetime.today().strftime('%Y-%m-%d')
#     home = Path.home().absolute()
#     targetFolder = Path.joinpath(home, 'CanvasQuizResults', canvasCourseName, quizEntryId)
#     Path(targetFolder).mkdir(parents=True, exist_ok=True)
#     filename = Path.joinpath(targetFolder, datestr + rootFilename + '.' + extension)
#     return filename

# Generate a filename of the following form:
#
#   {User Home Directory}/CanvasQuizResults/{canvasCourseId}/{Today's Date}_{rootFilename}.{extension}
# 
# Create the folder if needed.
# 
# def makeFilename(canvasCourseId, rootFilename, extension):
#     if type(canvasCourseId) == int:
#         canvasCourseId = str(canvasCourseId)
#     datestr = datetime.today().strftime('%Y-%m-%d')
#     home = Path.home().absolute()
#     targetFolder = Path.joinpath(home, 'CanvasQuizResults', canvasCourseId)
#     Path(targetFolder).mkdir(parents=True, exist_ok=True)
#     filename = Path.joinpath(targetFolder, datestr + rootFilename + '.' + extension)
#     return filename
