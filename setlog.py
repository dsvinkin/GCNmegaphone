import logging
import config
info = config.read_config('config.yaml')

def set_log():
    logging.basicConfig(format = u'[%(asctime)s]  %(message)s', level = logging.INFO, filename = u"{:s}/{:s}".format(info['log_dir'], 'log.txt'))