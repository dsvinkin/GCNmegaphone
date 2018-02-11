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
import get_temporal_history


log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u'log.txt')

def eph(list_tcat, name):
  with open(os.getcwd()+'/'+name+'/'+list_tcat[0], 'r') as in_file, open(os.getcwd()+'/'+name+'/'+'fermi_date_time.txt','w') as out_file:
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

  tle.get_ephemeris(sc_name, str_date, str_time, name)

def nlst(ftp, str_pattern):
  files = []
  try:
    files = sorted(ftp.nlst(str_pattern))
  except ftplib.error_temp:
      log.info ("No {:s} files in directory".format(str_pattern))
  return files

def download(ftp, name, file_ftp, str_pattern):
  path_folder = os.listdir(os.getcwd()+'/'+name)
  file_folder = list(filter(lambda x: x.startswith(str_pattern), path_folder))
  if file_ftp != file_folder:
    for file_ftp in sorted(set(file_ftp) - set(file_folder)):
      log.info ("Downloading {:s}".format(file_ftp))
      ftp.retrbinary('RETR ' + file_ftp, open(name+'/'+file_ftp,'wb').write)
  else:
    log.info ("No new files in format -> {:s}".format(str_pattern))

def check(name, date):
  check = True
  path_folder = os.listdir(os.getcwd()+'/'+name)
  file_folder = list(filter(lambda x: x.startswith('glg_tte_n'), path_folder))
  file_tcat = list(filter(lambda x: x.startswith('glg_tcat_all'), path_folder))
  if (len(file_folder) >= 12 and len(file_tcat) >= 1):
    eph(file_tcat, name)
    get_temporal_history.delimitation(name, file_folder[0])
    check = False
    log.info ("The thread {:s} finale!".format(date+'_FER'))
  return check

def download_fermi(date, name):
  ftp_dir = "fermi/data/gbm/triggers/20{:s}/bn{:s}/current".format(date[0:2], date)
  k = 0
  while check(name, date):
    sleep(1200)
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

      download(ftp, name, lc_tot_ftp, 'glg_lc_tot')
      download(ftp, name, trigdat_all_ftp, 'glg_trigdat_all')
      download(ftp, name, loclist_all_ftp, 'glg_loclist_all')
      download(ftp, name, glg_tcat_all_ftp, 'glg_tcat_all')
      download(ftp, name, tte_n_ftp, 'glg_tte_n')

      ftp.quit()
      log.info ("Disconnect")
    except ftplib.error_perm:
      log.info ("Maybe the folder bn{:s} is not created! Wait ...".format(date))
      ftp.quit()
      log.info ("Disconnect")
      k += 1
      if k > 2:
        log.info("Failed to download data from the folder bn{:s}".format(date))
        break

if __name__ == '__main__':

  Date_event = '171025416'
  Name_event = 'GRB171025_35940'

  download_fermi(Date_event, Name_event)