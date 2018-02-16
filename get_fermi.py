# -*- coding: utf-8 -*-

import logging as log
import ftplib
from ftplib import FTP
import os
import datetime
from time import sleep
import re

import clock
import tle
import gbm_tte

data_download_delay = 600 # s = 10 min

log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u'log.txt')

def eph(list_tcat, path):

    with open(path+'/'+list_tcat[0], 'r') as in_file,\
        open(path+'/'+'fermi_date_time.txt','w') as out_file:
        text = in_file.read()
        trigtime = re.findall(r'\d{9}.\d{6}', text)

        dateutc = clock.fermi2utc(float(trigtime[2]))
        ms = str(round(dateutc.microsecond/1e6, 3))
        time2sec = dateutc.hour*3600+dateutc.minute*60+dateutc.second
        a = 'TRIGTIME='+str(trigtime[2])
        b = dateutc.strftime("%Y-%m-%d %H:%M:%S")+ms[1:]
        c = dateutc.strftime("%Y%m%d")+' '+str(time2sec)+ms[1:]

        out_file.write(a+'\n'+b+'\n'+c+'\n')
        log.info ("File fermi_data_time.txt is created!")

    sc_name = 'Fermi'
    str_date = dateutc.strftime("%Y%m%d")
    str_time = str(time2sec)+ms[1:]

    tle.get_ephemeris(sc_name, str_date, str_time, path)

def nlst(ftp, str_pattern):

    files = []
    try:
        files = sorted(ftp.nlst(str_pattern))
    except ftplib.error_temp:
        log.info("No {:s} files in directory".format(str_pattern))
    return files

def download(ftp, path, file_ftp, str_pattern):

    file_folder = list(filter(lambda x: x.startswith(str_pattern), path))
    if file_ftp != file_folder:
        for file_ftp in sorted(set(file_ftp) - set(file_folder)):
            log.info ("Downloading {:s}".format(file_ftp))
            ftp.retrbinary('RETR ' + file_ftp, open(path+'/'+file_ftp,'wb').write)
    else:
        log.info ("No new files in format -> {:s}".format(str_pattern))

def all_files_are_downloaded(path):

    check = False
    path_folder = os.listdir(path)
    file_folder = list(filter(lambda x: x.startswith('glg_tte_n'), path_folder))
    file_tcat = list(filter(lambda x: x.startswith('glg_tcat_all'), path_folder))

    print(file_folder, file_tcat)
    
    if (len(file_folder) >= 12 and len(file_tcat) >= 1):
        check = True
    return check

def download_fermi(date, name, path):
    print(date, name, path)
    ftp_dir = "fermi/data/gbm/triggers/{:s}/bn{:s}/current".format(date[0:4], name)
    k = 0
    while not all_files_are_downloaded(path):
        sleep(data_download_delay)
        log.info ("Connecting ...")
        ftp = FTP('legacy.gsfc.nasa.gov')
        ftp.login()
        log.info ("Connected")

        try:
            ftp.cwd(ftp_dir)
            log.info("Path of the directory = {:s}".format(ftp_dir))
      
            lc_tot_ftp = nlst(ftp, 'glg_lc_tot*pdf')
            trigdat_all_ftp = nlst(ftp, 'glg_trigdat_all*fit')
            loclist_all_ftp = nlst(ftp, 'glg_loclist_all*txt')
            tte_n_ftp = nlst(ftp, 'glg_tte_n*fit')
            glg_tcat_all_ftp = nlst(ftp, 'glg_tcat_all*fit')

            download(ftp, path, lc_tot_ftp, 'glg_lc_tot')
            download(ftp, path, trigdat_all_ftp, 'glg_trigdat_all')
            download(ftp, path, loclist_all_ftp, 'glg_loclist_all')
            download(ftp, path, glg_tcat_all_ftp, 'glg_tcat_all')
            download(ftp, path, tte_n_ftp, 'glg_tte_n')

            ftp.quit()
            log.info ("Disconnect")

        except ftplib.error_perm:
            log.info ("Maybe the folder {:s} is not created! Wait ...".format(date))
            ftp.quit()
            log.info ("Disconnect")
        k += 1
        if k > 2:
            log.info("Failed to download data from the folder bn{:s}".format(name))
            break

    if all_files_are_downloaded(path):
        log.info ("The thread bn{:s} finale!".format(name))
        path_folder = os.listdir(path)
        file_folder = list(filter(lambda x: x.startswith('glg_tte_n'), path_folder))
        file_tcat = list(filter(lambda x: x.startswith('glg_tcat_all'), path_folder))

        eph(file_tcat, path)
        gbm_tte.tte_to_ascii(path, file_folder[0])

if __name__ == '__main__':

    event_gbm_name = '171025416'
    event_name = 'GRB171025_35940'

    download_fermi(event_gbm_name, event_name)