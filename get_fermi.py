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

data_download_delay = 1200 # s 
number_of_tte_min = 6

log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u'log.txt')

def eph(list_trigdat, path):

    with open(path+'/'+list_trigdat[0], 'r') as in_file,\
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
    except Exception as e:
        log.error("Got error in nlst: {:s} for {:s}.".format(str(e), str_pattern))
    return files

def download(ftp, path, file_ftp, str_pattern):

    path_folder = os.listdir(path)
    file_folder = list(filter(lambda x: x.startswith(str_pattern), path_folder))
    #print path, file_folder
    #print file_ftp
    if file_ftp != file_folder:
        for file_ftp in sorted(set(file_ftp) - set(file_folder)):
            log.info("Downloading {:s}".format(file_ftp))
            ftp.retrbinary('RETR ' + file_ftp, open(path+'/'+file_ftp,'wb').write)
    else:
        log.info ("No new files in format -> {:s}".format(str_pattern))

def all_files_are_downloaded(path):

    check = False
    path_folder = os.listdir(path)
    file_folder = list(filter(lambda x: x.startswith('glg_tte_n'), path_folder))
    file_trigdat = list(filter(lambda x: x.startswith('glg_trigdat_all'), path_folder))
    file_loc = list(filter(lambda x: x.startswith('glg_loclist_all'), path_folder))

    print("TTE: ", file_folder)
    print("trigdat: ", file_trigdat)
    print("loclist: ", file_loc)
    
    if (len(file_folder) >= number_of_tte_min and len(file_trigdat) >= 1): # and len(file_loc)>=1):
        check = True
    return check

def download_fermi(name, path):

    ftp_dir = "fermi/data/gbm/triggers/20{:s}/bn{:s}/current".format(name[0:2], name)
    
    k = 0
    k_max = 40

    while not all_files_are_downloaded(path):
        k += 1
        if k > k_max:
            log.info("Failed to download data from the folder bn{:s}".format(name))
            break

        log.info ("Connecting to legacy.gsfc.nasa.gov ...")

        try:
            ftp = FTP('legacy.gsfc.nasa.gov')
            ftp.login()
            log.info("Connected")

            ftp.cwd(ftp_dir)
            log.info("Path of the ftp directory {:s}".format(ftp_dir))
      
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
            log.info("Disconnect")

        except ftplib.error_perm as e:
            log.error("Got error {:s}. Maybe the folder bn{:s} is not created! Wait ...".format(str(e), name))
            ftp.quit()

        except Exception as e:
            log.error("Got error {:s} during GBM data downloading.".format(str(e), name))

        if k > 1:
            sleep(data_download_delay)

    if all_files_are_downloaded(path):
        log.info ("The thread bn{:s} finale!".format(name))
        path_folder = os.listdir(path)
        file_folder = list(filter(lambda x: x.startswith('glg_tte_n'), path_folder))
        file_trigdat = list(filter(lambda x: x.startswith('glg_trigdat'), path_folder))

        eph(file_trigdat, path)
        print file_folder
        gbm_tte.tte_to_ascii(path, file_folder[0])

if __name__ == '__main__':

    event_gbm_name = '190222312'
    path = '../GRB20190222_T26975'

    download_fermi(event_gbm_name, path)
    #eph(('glg_trigdat_all_bn181222841_v00.fit',''), path)