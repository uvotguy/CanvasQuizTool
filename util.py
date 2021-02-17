from datetime import datetime
from pathlib import Path

# Generate a filename of the following form:
#
#   {User Home Directory}/CanvasQuizResults/{canvasCourseId}/{quizEntryId}/{Today's Date}_{rootFilename}.{extension}
#
# Create the folder if needed.
#
def makeQuizFilename(canvasCourseId, quizEntryId, rootFilename, extension):
    if type(canvasCourseId) == int:
        canvasCourseId = str(canvasCourseId)
    datestr = datetime.today().strftime('%Y-%m-%d')
    home = Path.home().absolute()
    targetFolder = Path.joinpath(home, 'CanvasQuizResults', canvasCourseId, quizEntryId)
    Path(targetFolder).mkdir(parents=True, exist_ok=True)
    filename = Path.joinpath(targetFolder, datestr + '_' + rootFilename + '.' + extension)
    return filename

# Generate a filename of the following form:
#
#   {User Home Directory}/CanvasQuizResults/{canvasCourseId}/{Today's Date}_{rootFilename}.{extension}
# 
# Create the folder if needed.
# 
def makeFilename(canvasCourseId, rootFilename, extension):
    if type(canvasCourseId) == int:
        canvasCourseId = str(canvasCourseId)
    datestr = datetime.today().strftime('%Y-%m-%d')
    home = Path.home().absolute()
    targetFolder = Path.joinpath(home, 'CanvasQuizResults', canvasCourseId)
    Path(targetFolder).mkdir(parents=True, exist_ok=True)
    filename = Path.joinpath(targetFolder, datestr + '_' + rootFilename + '.' + extension)
    return filename
