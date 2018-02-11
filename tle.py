"""
Download TLE from www.space-track.org

Perl code for the same task
`curl -c cookies.txt -b cookies.txt -k https://www.space-track.org/ajaxauth/login -d 'identity=$Login&password=$Pass'`;
my $response = `curl --limit-rate 100K --cookie cookies.txt $args`;

Name         ID
Fermi     33053
Swift     28485
ISS(MAXI) 25544
AGILE     31135
RHESSI    27370

c:\work\\Utilities\GetSCEphemeris\GetSCEphemeris4List.exe

"""

import sys
import re
import os
import subprocess
import logging
from datetime import datetime, timedelta


def get_tle(str_date, sc_id):

    import requests

    login = 'dmitrysvinkin@gmail.com'
    password = 'MityaSpb1234567'

    date_eph = datetime.strptime(str_date, "%Y%m%d").date()
    date_start = (date_eph - timedelta(days=2)).strftime("%Y-%m-%d")
    date_end = (date_eph + timedelta(days=1)).strftime("%Y-%m-%d")

    args = "https://www.space-track.org/basicspacedata/query/class/tle/EPOCH/" +\
       "{0}--{1}/NORAD_CAT_ID/{2}/orderby/TLE_LINE1%20ASC/format/tle".format(date_start, date_end, sc_id);

    url = 'https://www.space-track.org/ajaxauth/login'

    s = requests.Session()

    payload = {'identity': login, 'password': password}
    try:
        s.post(url, data=payload)
        response = s.get(args)
    except:
        logging.error("Request to {:s} was failed.".format(url))
        return None

    return response.text

def get_ephemeris(str_sc_name, str_date, str_time, fl_name):

    dic_sc = {
        'Fermi': '33053', 
        'Swift':'28485', 
        'ISS':'25544', 
        'Tg-2':'41765',
        'AGILE':'31135',
         'RHESSI':'27370'
    }

    if not str_sc_name in dic_sc:
        logging.info("No NORAD ID for {:s}".format(str_sc_name))
        return None, None, None 

    sc_id = dic_sc[str_sc_name]

    tle_file_name = "{:s}_{:s}.tle".format(str_date, str_sc_name)
    eph_file_name = "{:s}_{:s}.eph".format(str_date, str_sc_name)
    list_file_name = "{:s}_list.txt".format(str_sc_name)

    with open(os.getcwd()+'/'+fl_name+'/'+list_file_name,'w') as f:
        f.write("%s %s\n" % (str_date, str_time))

    text_tle = get_tle(str_date, sc_id)
    if not text_tle:
        return (list_file_name, None, None)

    with open(os.getcwd()+'/'+fl_name+'/'+tle_file_name,'w') as f:
        f.write(text_tle)

    #str_run = 'c:/work/Utilities/GetSCEphemeris/GetSCEphemeris4List.exe'
    #str_run = "{:s} {:s} {:s} {:s}".format(str_run, tle_file_name, list_file_name, eph_file_name)
    #logging.info(str_run)
    #subprocess.call(str_run, shell=True)

    return list_file_name, tle_file_name, eph_file_name

def test():
    
    sc_name = 'AGILE'
    str_date = '20170817'
    str_time = '45666.475'
    fl_name = 'GRB170817_45666'
    
    get_ephemeris(sc_name, str_date, str_time, fl_name)
    
if __name__ == "__main__":
    test()