from datetime import datetime
from pathlib import Path

# Generate a filename of the following form:
#
#   {User Home Directory}/{Today's Date}_{rootFilename}.{extension}
#
def makeFilename(rootFilename, extension):
    datestr = datetime.today().strftime('%Y-%m-%d')
    home = Path.home().absolute()
    filename = Path.joinpath(home, datestr + '_' + rootFilename + '.' + extension)
    return filename
