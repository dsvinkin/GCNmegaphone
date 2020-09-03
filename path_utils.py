import os
import logging as log

import config
info = config.read_config('config.yaml')

log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u"{:s}/{:s}".format(info['log_dir'], 'log.txt'))


def get_files(path, pattern='', prefix=True, all=False):
    """
    Find file with specific prefix (prefix=True) or suffix (prefix=False) 
    """

    list_files = os.listdir(path)

    if len(list_files) == 0:
        print("Directory {:s} is empty!".format(path))
        return []

    if prefix:
        file_folder = list(filter(lambda x: x.startswith(pattern), list_files))
    else:
        file_folder = list(filter(lambda x: x.endswith(pattern), list_files))

    if len(file_folder) == 0:
        print("No required file with pattern: {:s}".format(pattern))
        if all:
           return []
        else:
           return None

    #print(file_folder)

    if all:
        return file_folder
    else:
        return file_folder[0]