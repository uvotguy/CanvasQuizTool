from datetime import datetime
from pathlib import Path

# Generate a filename of the following form:
#
#   {User Home Directory}/{Today's Date}_{rootFilename}.{extension}
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
