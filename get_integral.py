# -*- coding: utf-8 -*-

import logging as log
import requests
import re
import os
from time import sleep

timeout = 30 # s
log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u'log.txt')

def GetInHMS(seconds, use_codes=False):
    hours = int(seconds / 3600)
    seconds -= 3600.0 * hours
    minutes = int(seconds / 60.0)
    seconds -= int(60.0 * minutes)
    if use_codes:
        return "{:02d}%3A{:02d}%3A{:02.0f}".format(hours, minutes, seconds)
    else:
        return "{:02d}:{:02d}:{:02.0f}".format(hours, minutes, seconds)

def check (Name_event, k):
    check = True
    if k > 1:
        size = os.path.getsize(os.getcwd()+'/'+Name_event+'/'+'20'+Name_event[3:]+'_INT.thr')
    if (size >= 120000) or (k > 24):
            check = False
            log.info ("The thread {:s} finale!".format(Name_event[3:]+'_INT'))
    return check

def download_integral(Name_event, interval):
    url_lc =  'http://isdc.unige.ch/~savchenk/spiacs-online/spiacs.pl'
    m = re.search('(\d{4})(\d{2})(\d{2})', '20'+Name_event[3:9])
    date_dashed = "{:s}-{:s}-{:s}".format(m.group(1), m.group(2), m.group(3))
    time_hhmmss = GetInHMS(int(Name_event[10:]), use_codes=False)

    proxy = {'http': 'http://www-proxy:3128'}
    k = 0
    while check(Name_event, k):
        k += 1
        sleep(2400)
        # get lc
        utc = "{:s}T{:s} {:d}".format(date_dashed, time_hhmmss, int(interval))
        log.info (utc)
        data = {'requeststring': utc, 'submit':'Submit', 'generate':'ipnlc'}
        req = requests.post(url_lc, data=data, proxies=proxy)
        text = re.sub("<br>","", req.text)
        text = re.sub("\r","", text)

        file_name = "{:s}_{:s}_INT.thr".format('20'+Name_event[3:9], Name_event[10:])
        with open(Name_event+'/'+file_name, 'w') as f:
            f.write(text)
        log.info (Name_event+" thr has been downloaded")
        
    # get eph
        utc = "{:s}T{:s}".format(date_dashed, time_hhmmss, int(interval))
        data = {'requeststring': utc, 'submit':'Submit', 'generate':'ephs'}
        req = requests.post(url_lc, data=data, proxies=proxy)
        text = re.sub("<br>","", req.text)
        text = re.sub("\r","", text)

        file_name = "{:s}_{:s}_INT.eph".format('20'+Name_event[3:9], Name_event[10:])
        with open(Name_event+'/'+file_name, 'w') as f:
            f.write("%s %s\n" %(date_dashed, Name_event[10:]))
            f.write(text)
        log.info (Name_event+" eph has been downloaded")

def test():
    Name_event = 'GRB171029_39512'
    interval = 200

    download_integral(Name_event, interval)

if __name__ == "__main__":
    test()