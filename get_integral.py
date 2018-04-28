# -*- coding: utf-8 -*-

import logging as log
import requests
import re
import os
from time import sleep

timeout = 30 # s
data_download_delay = 2400 # s
 
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

def thr_is_ok(file_name):

    size = 0
    if os.path.isfile(file_name): 
        size = os.path.getsize(file_name)
    
    log.info("File {:s} has size: {:d} B".format(file_name, size))

    if (size >= 120 * 1024):
        return True
    else:
        return False

def download_integral(date, time, interval, path):
    """
    date - YYYYMMDD [str] 
    time - integer seonds, UT [int]
    interval - integer seconds [int]
    """

    url_lc =  'http://isdc.unige.ch/~savchenk/spiacs-online/spiacs.pl'
    m = re.search('(\d{4})(\d{2})(\d{2})', date)
    date_dashed = "{:s}-{:s}-{:s}".format(m.group(1), m.group(2), m.group(3))
    time_hhmmss = GetInHMS(time, use_codes=False)
    Name_event = "GRB{:s}_T{:05d}".format(date,time)

    proxy = {'http': 'http://www-proxy:3128'}

    k = 0
    k_max = 30

    thr_file = "{:s}_{:05d}_INT.thr".format(date, time)
    eph_file = "{:s}_{:05d}_INT.eph".format(date, time)

    while (not thr_is_ok(path+'/'+thr_file) and k <= k_max):
        k += 1
        # get lc
        #print ('get lc')
        utc = "{:s}T{:s} {:d}".format(date_dashed, time_hhmmss, int(interval))
        log.info (utc)
        data = {'requeststring': utc, 'submit':'Submit', 'generate':'ipnlc'}
        req = requests.post(url_lc, data=data, proxies=proxy)
        text = re.sub("<br>","", req.text)
        text = re.sub("\r","", text)

        with open(path+'/'+thr_file, 'w') as f:
            f.write(text)
        log.info(thr_file+" has been downloaded")
        
        # get eph
        utc = "{:s}T{:s}".format(date_dashed, time_hhmmss, int(interval))
        data = {'requeststring': utc, 'submit':'Submit', 'generate':'ephs'}
        req = requests.post(url_lc, data=data, proxies=proxy)
        text = re.sub("<br>","", req.text)
        text = re.sub("\r","", text)

        with open(path+'/'+eph_file, 'w') as f:
            f.write("%s %s\n" %(date_dashed, time))
            f.write(text)
        log.info (eph_file+" has been downloaded")

        if k > 1:
            sleep(data_download_delay)

    if thr_is_ok(path+'/'+thr_file):
        log.info("The {:s} has good size.".format(thr_file))
        log.info ("The thread {:s}_INT finale!".format(Name_event))
    else:
        log.info ("Failed to download SPI-ACS data for {:s}.".format(Name_event))

def test():
    date = '20171029'
    time = 39512
    interval = 200
    path = '.'

    download_integral(date, time, interval, path)

if __name__ == "__main__":
    test()