# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import logging as log

import ftplib
from ftplib import FTP, FTP_TLS

import datetime
from time import sleep
import re

from astropy.io import fits

import clock
import tle
import gbm_tte
import gbm_map
import path_utils

data_download_delay = 1200 # s 
number_of_tte_min = 6

import config
info = config.read_config('config.yaml')

log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u"{:s}/{:s}".format(info['log_dir'], 'log.txt'))

def eph(list_trigdat, path):

    hdul = fits.open("{:s}/{:s}".format(path, list_trigdat[0]))
    trigtime = hdul[0].header['TRIGTIME']
    dateutc = clock.fermi2utc(trigtime)
    ms = str(round(dateutc.microsecond/1e6, 3))
    time2sec = dateutc.hour*3600+dateutc.minute*60+dateutc.second

    str_datetime1 = dateutc.strftime("%Y-%m-%d %H:%M:%S")+ms[1:]
    str_datetime2 = dateutc.strftime("%Y%m%d")+' '+str(time2sec)+ms[1:]
    str_out = 'TRIGTIME={:f}\n{:s}\n{:s}'.format(trigtime, str_datetime1, str_datetime2)
        

    with open("{:s}/{:s}".format(path, 'fermi_date_time.txt'),'w') as out_file:
        out_file.write(str_out)
    
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
    #print(path, file_folder)
    #print(file_ftp)

    if file_ftp != file_folder:
        for file_ftp in sorted(set(file_ftp) - set(file_folder)):
            log.info("Downloading {:s}".format(file_ftp))
            ftp.retrbinary('RETR ' + file_ftp, open(path+'/'+file_ftp,'wb').write)
    else:
        log.info ("No new files in format -> {:s}".format(str_pattern))

def all_files_are_downloaded(path):

    check = False
    file_folder = path_utils.get_files(path, 'glg_tte_n', prefix=True, all=True)
    file_trigdat = path_utils.get_files(path, 'glg_trigdat_all', prefix=True, all=True)
    file_loc = path_utils.get_files(path, 'glg_loclist_all', prefix=True, all=True)

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
            ftp = FTP_TLS('heasarc.gsfc.nasa.gov')
            ftp.login()
            ftp.prot_p()
            log.info("Connected")

            ftp.cwd(ftp_dir)
            log.info("Path of the ftp directory {:s}".format(ftp_dir))
      
            lc_tot_ftp = nlst(ftp, 'glg_lc_tot*pdf')
            trigdat_all_ftp = nlst(ftp, 'glg_trigdat_all*fit')
            loclist_all_ftp = nlst(ftp, 'glg_loclist_all*txt')
            healpix_ftp = nlst(ftp, 'glg_healpix_all*fit')
            tte_n_ftp = nlst(ftp, 'glg_tte_n*fit')
            glg_tcat_all_ftp = nlst(ftp, 'glg_tcat_all*fit')
           
            download(ftp, path, lc_tot_ftp, 'glg_lc_tot')
            download(ftp, path, trigdat_all_ftp, 'glg_trigdat_all')
            download(ftp, path, loclist_all_ftp, 'glg_loclist_all')
            download(ftp, path, glg_tcat_all_ftp, 'glg_tcat_all')
            download(ftp, path, tte_n_ftp, 'glg_tte_n')
            download(ftp, path, healpix_ftp, 'glg_healpix_all')

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

        file_trigdat = path_utils.get_files(path, 'glg_trigdat', prefix=True, all=True)   
        file_hpx = path_utils.get_files(path, 'glg_healpix_all', prefix=True, all=True)
     
        if len(file_hpx) >0:
            hpx_path = os.path.join(path, file_hpx[0])
            gbm_map.get_contours(hpx_path)

        eph(file_trigdat, path)
        gbm_tte.tte_to_ascii(path)

if __name__ == '__main__':

    date = '20200826'
    time = 79782.72

    path = "data/GRB{:s}_T{:05d}".format(date, int(time))
    fod = "{:03.0f}".format(time/86400.0 * 1000)
    event_gbm_name = "{:s}{:s}".format(date[2:], fod)

    print("Downloading data for {:s} to {:s}".format(event_gbm_name, path))

    if not os.path.isdir(path):
        os.makedirs(path)
    
    #exit()

    download_fermi(event_gbm_name, path)
    #eph(('glg_trigdat_all_bn181222841_v00.fit',''), path)