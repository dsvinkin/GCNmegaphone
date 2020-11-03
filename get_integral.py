# -*- coding: utf-8 -*-

import logging as log
import requests
import re
import os
from time import sleep

from path_utils import file_is_ok
from clock import sod_to_hhmmss

import config

info = config.read_config('config.yaml')

timeout = 30 # s
data_download_delay = 1200 # s
max_number_of_requests = 60
min_size_kb = 120
 
import setlog
setlog.set_log()


def request_data(data):

    url_lc =  'http://isdc.unige.ch/~savchenk/spiacs-online/spiacs.pl'
    proxy = {'http': info['http_proxy']}

    try: 
        req = requests.post(url_lc, data=data, proxies=proxy)
    except requests.exceptions.RequestException as e:
        log.info("Got error {:s} for {:s}.".format(str(e), data['requeststring']))
        return None
    else:
        return req.text

def download_integral(date, time, interval, path):

    m = re.search('(\d{4})(\d{2})(\d{2})', date)
    date_dashed = "{:s}-{:s}-{:s}".format(m.group(1), m.group(2), m.group(3))
    time_hhmmss = sod_to_hhmmss(time, use_codes=False)

    utc = "{:s}T{:s} {:d}".format(date_dashed, time_hhmmss, int(interval))
    log.info("Geting SPI-ACS data for {:s}".format(utc))
    data = {'requeststring': utc, 'submit':'Submit', 'generate':'ipnlc'}

    thr_file = "{:s}_{:05d}_INT.thr".format(date, time)
    eph_file = "{:s}_{:05d}_INT.eph".format(date, time)

    thr_file = os.path.join(path, thr_file)
    eph_file = os.path.join(path, eph_file)

    text = request_data(data)

    if text is not None:    
        text = re.sub("<br>","", text)
        text = re.sub("\r","", text)
    
        with open(thr_file, 'w') as f:
            f.write(text)
        log.info("INTEGRAL {:s} has been downloaded.".format(thr_file))
    
    # get eph
    utc = "{:s}T{:s}".format(date_dashed, time_hhmmss, int(interval))
    data = {'requeststring': utc, 'submit':'Submit', 'generate':'ephs'}
    
    text = request_data(data)

    if text is not None:         
        text = re.sub("<br>","", text)
        text = re.sub("\r","", text)
    
        with open(eph_file, 'w') as f:
            f.write("%s %s\n" %(date_dashed, time))
            f.write(text)
        log.info("INTEGRAL ephemeris {:s} has been downloaded.".format(thr_file))

    return thr_file, eph_file


def download_integral_loop(date, time, interval, path):
    """
    date - YYYYMMDD [str] 
    time - integer seonds, UT [int]
    interval - integer seconds [int]
    """
 
    thr_file, eph_file = None, None

    request_count = 0

    while (not file_is_ok(thr_file, min_size_kb) and request_count <= max_number_of_requests):
        request_count += 1
        
        thr_file, eph_file = download_integral(date, time, interval, path)

        if request_count > 1:
            sleep(data_download_delay)

    if file_is_ok(thr_file, min_size_kb):
        log.info("The {:s} has good size.".format(thr_file))
        log.info ("The thread {:s}_{:s}_INT is finished.".format(date, str(time) ))
    else:
        log.info ("Failed to download SPI-ACS data for {:s} {:s}.".format(date, str(time)))

def test():
    date = '20181222'
    time = 68000
    interval = 200
    path = '.'

    download_integral(date, time, interval, path)

if __name__ == "__main__":
    test()