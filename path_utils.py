import os

import setlog
setlog.set_log()

def get_files(path, pattern='', prefix=True, all=False):
    """
    Find file with specific prefix (prefix=True) or suffix (prefix=False) 
    """

    list_files = os.listdir(path)

    if len(list_files) == 0:
        log.error("Directory {:s} is empty!".format(path))
        return []

    if prefix:
        file_folder = list(filter(lambda x: x.startswith(pattern), list_files))
    else:
        file_folder = list(filter(lambda x: x.endswith(pattern), list_files))

    if len(file_folder) == 0:
        log.error("No required file with pattern: {:s}".format(pattern))
        if all:
           return []
        else:
           return None

    if all:
        return file_folder
    else:
        return file_folder[0]