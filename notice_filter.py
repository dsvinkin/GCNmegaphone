# -*- coding: utf-8 -*-


import os
import datetime
import threading
import logging as log
import re
from collections import OrderedDict

from lxml import etree

import gcn
import gcn.handlers
import gcn.notice_types

import config
import telegram_api
import get_fermi
#import get_integral


info = config.read_config('config.yaml')

# Parameters of the log file
import setlog
setlog.set_log()


current_event_fermi = None
current_event_integral = None
#current_event_hend = None

# See https://gcn.gsfc.nasa.gov/filtering.html
good_notice_types = {
    '31': 'IPN RAW', 
    '52': 'INTEGRAL SPIACS',
    '59': 'KONUS LC', 
    '60': 'SWIFT BAT GRB ALERT',
    '61': 'SWIFT BAT GRB POS ACK', 
    '84': 'SWIFT BAT TRANS',
    '111': 'FERMI GBM FLT POS',
    '112': 'FERMI GBM GND POS', 
    '115': 'FERMI GBM FIN POS',
    '150': 'LVC_PRELIM',
    '151': 'LVC_INITIAL',
    '152': 'LVC_UPDATE',
    '154': 'LVC_CNTRPART',
     }

notice_parameters = {
    'Packet_Type':    'NOTICE_TYPE', 
    'TrigID':         'TRIGGER_NUM', 
    'Sun_Distance':   'SUN_DIST',    
    'Sun_Hr_Angle':   'SUN_ANGLE',   
    'Galactic_Long':  'GAL_LONG',    
    'Galactic_Lat':   'GAL_LAT',     
    'Ecliptic_Long':  'ECL_LONG',    
    'Ecliptic_Lat':   'ECL_LAT',     
    'Burst_Inten':    'BURST_INTEN', 
    'Burst_Signif':   'BURST_SIGNIF',
    'Trig_Timescale': 'TRIG_TIMESCALE',
    'Data_Timescale': 'DATA_TIMESCALE', 
    'Data_Signif':    'DATA_SIGNIF',
    'Data_Integ':     'DATA_INTEG',  
    'Most_Likely_Index': 'MOST_LIKELY', 
    'Most_Likely_Prob':  'MOST_LIKELY_PROB',
    'Sec_Most_Likely_Index': '2nd_MOST_LIKELY',
    'Sec_Most_Likely_Prob': '2nd_MOST_LIKELY_PROB',
    'MOON_Distance':  'MOON_DIST',
    'C1':             'GRB_RA', 
    'C2':             'GRB_DEC',
    'Error2Radius':   'GRB_ERROR',
    'ISOTime':        'GRB_TIME',
    'Long_short':     'LONG_OR_SHORT'
    }

# See https://gcn.gsfc.nasa.gov/sock_pkt_def_doc.html
# for most_likely and 2most_likely definitions 

# Most_Likely_Ind
GoodIndex = {
    '4': '4  GRB', 
    '5': '5  GENERIC_SGR', 
    '6': '6  GENERIC_TRANSIENT',
    '7': '7  DISTANT_PARTICLES', 
    '10':'10  SGR_1806_20', 
    '11':'11  GROJ_0422_32'
    }

# Sec_Most_Likely_Index
AllIndex = {
    '0': '0 ERROR', 
    '1': '1 UNRELIABLE_LOCATION', 
    '2': '2 LOCAL_PARTICLES', 
    '3': '3 BELOW_HORIZON', 
    '4': '4 GRB',
    '5': '5 GENERIC_SGR', 
    '6': '6 GENERIC_TRANSIENT', 
    '7': '7 DISTANT_PARTICLES', 
    '8': '8 SOLAR_FLARE', 
    '9': '9 CYG_X1',
    '10': '10 SGR_1806_20 ', 
    '11': '11 GROJ_0422_32', 
    '12': '12 undefined', 
    '13': '13 undefined', 
    '14': '14 undefined',
    '15': '15 undefined', 
    '16': '16 undefined', 
    '17': '17 undefined', 
    '18': '18 undefined', 
    '19': '19 TGF'
    }

def qw(s):
    return s.split()


def run_download_gbm_thread(event_name, event_gbm_name, path):

    global current_event_fermi
    thread_fermi = threading.Thread(target = get_fermi.download_fermi, args = (event_gbm_name, path))
  
    if (current_event_fermi != event_name and not thread_fermi.is_alive()):
        thread_fermi.start()
        log.info("The thread {:s} started".format(event_name+'_FER'))
        current_event_fermi = event_name
    else:
        log.info ("The thread {:s} is already working".format(event_name+'_FER'))

"""
def run_download_int_thread(event_name, date, time, path):
  
    global current_event_integral
    thread_integral = threading.Thread(target = get_integral.download_integral_loop, args=(date, time, 200, path))

    if (current_event_integral != event_name and not thread_integral.is_alive()):
        thread_integral.start()
        log.info ("The thread {:s} started".format(event_name + '_INT'))
        current_event_integral = event_name
    else:
        log.info ("The thread {:s} is already working".format(event_name+'_INT'))
"""
"""
def run_download_hend_thread(event_name, date, time, path):

    global current_event_hend
    thread_hend = threading.Thread(target = get_hend.download_hend_loop, args = (date, time, path))
  
    if (current_event_hend != event_name and not thread_hend.is_alive()):
        thread_hend.start()
        log.info("The thread {:s} started".format(event_name+'_HEND'))
        current_event_hend = event_name
    else:
        log.info("The thread {:s} is already working".format(event_name+'_HEND'))
"""

class notice:

    def __init__(self, payload):
        self.payload = payload
        tree = etree.XML(payload) 

        self.dict_par = OrderedDict()
        #self._update_dict(tree, self.dict_par) 
        self._update_dict_lxml(tree, self.dict_par)
        #print (self.dict_par)

        self.role = tree.attrib['role']

        self.gw_packets = qw('150 151 152 154')

    def append_payload_to_file(self, file_name):
        with open(file_name, 'ab') as f:
          f.write("------------------------------\n".encode('UTF-8'))
          f.write(self.payload)

    def _update_dict(self, element, my_dict):
        """
        Code from https://stackoverflow.com/questions/28503666/python-parsing-xml-autoadd-all-key-value-pairs

        TODO: add dataType to my_dict
        """
        # lxml defines "length" of the element as number of its children.
        if len(element):  # If "length" is other than 0.
            for subelement in element:
                # That's where the recursion happens. We're calling the same
                # function for a subelement of the element.
                self._update_dict(subelement, my_dict)
    
        else:  # Otherwise, subtree is a leaf.
            print (element.tag,':', element.text, element.attrib)
    
            if element.text:
                name = element.tag
                name = re.sub(r"{.+?}","",name)
                my_dict[name] = element.text
                #print (name,':', element.text)
            elif element.attrib:
                name = element.attrib.get('name',None)
                val = element.attrib.get('value',None)
                if name is not None and val is not None:
                    print (name,':', val)
                    my_dict[name] = val

    def _update_dict_lxml(self, root, my_dict):

        lst_par = root.findall('.//Param')
        for param in lst_par:
            name = param.attrib.get('name', None)
            value = param.attrib.get('value', None)
            if name and value:
                #print (name,':', val)
                my_dict[name] = value

        # Get text parameters
        lst_gbm_par_names = ['ISOTime', 'C1', 'C2', 'Error2Radius']
        for name in lst_gbm_par_names:
            lst_par = root.findall('.//{:s}'.format(name))
            if len(lst_par):
                my_dict[name] = lst_par[0].text
            

    def get_value(self, key):
        return self.dict_par.get(key, None)

    def get_event_time(self):
        return self.dict_par.get('ISOTime', None)

    def get_event_type(self):
        if self.get_value('Packet_Type') in self.gw_packets:
            return 'GW'
        else:
            return 'GRB'

    def get_event_name(self):
        """
        Returns:  
        name      GW/GRByyyymmdd_Tsssss 
        gbm_name  yymmddfff
        date      yyyymmdd
        time_sec  float seconds of day
        """

        str_date_time = self.dict_par.get('ISOTime', None)
       
        time = datetime.datetime.strptime(str_date_time.replace('Z', ''), "%Y-%m-%dT%H:%M:%S.%f")
        part_day = int(round((time.hour*60 + time.minute + time.second/60.0) / 1.44))
      
        # gbm_name - format yymmddttt
        gbm_name = "{:s}{:03d}".format(time.strftime('%y%m%d'), part_day)
        date = time.strftime('%Y%m%d')
        time_sec = time.hour * 3600 + time.minute * 60 + time.second + time.microsecond/1e6                                            
                                             
        # name - format GRByymmdd_sssss
        name = "{:s}{:s}_T{:05d}".format(self.get_event_type(), time.strftime('%Y%m%d'), int(time_sec))
      
        return name, gbm_name, date, time_sec

    def print_param(self, key, f):

        name = notice_parameters.get(key, 'None')
        val = self.dict_par.get(key, 'None')

        if name=='None' or val=='None':
             log.error("name {:s} is {:s}; val {:s} is {:s}".format(key ,name, key, val))
             return
        
        if (key == 'Packet_Type'):
            print("{:22s} {:s}".format(name, good_notice_types[val]), file=f)

        elif (key == 'Most_Likely_Index'):
            print("{:22s} {:s}".format(name, GoodIndex[val]), file=f)
    
        elif (key == 'Sec_Most_Likely_Index'):
            print("{:22s} {:s}".format(name, AllIndex[val]), file=f)
    
        else:
            print("{:22s} {:s}".format(name, val), file=f)
    
    def append_info_to_file(self, file_name):

       lst_to_print = qw("""Packet_Type TrigID  ISOTime  
            Trig_Timescale Data_Timescale Data_Signif 
            Most_Likely_Index Most_Likely_Prob Sec_Most_Likely_Index Sec_Most_Likely_Prob 
            C1 C2 Error2Radius
            Sun_Distance Galactic_Long Galactic_Lat Ecliptic_Long Ecliptic_Lat""")

       with open(file_name, 'a') as f:
          now = datetime.datetime.utcnow()
          print("{:22s} {:s}".format('Timestamp', now.strftime("%Y-%m-%d %H:%M:%S")), file=f)
      
          for key in lst_to_print:
              self.print_param(key, f)
      
          print("-----------------------------\n", file=f)


# Function to call every time a GCN is received.

@gcn.handlers.include_notice_types(
    gcn.notice_types.IPN_RAW,
    gcn.notice_types.FERMI_GBM_FLT_POS,
    gcn.notice_types.FERMI_GBM_GND_POS,
    gcn.notice_types.FERMI_GBM_FIN_POS,
    gcn.notice_types.INTEGRAL_SPIACS,
    gcn.notice_types.KONUS_LC,
    gcn.notice_types.SWIFT_BAT_GRB_ALERT,
    gcn.notice_types.SWIFT_BAT_GRB_POS_ACK,
    gcn.notice_types.LVC_PRELIMINARY,
    gcn.notice_types.LVC_INITIAL,
    gcn.notice_types.LVC_UPDATE
    )

def process_gcn(payload, root):

    data = notice(payload)
    data.append_payload_to_file("{:s}/{:s}".format(info['log_dir'], 'raw_notices.txt'))

    notice_type = good_notice_types.get(data.get_value('Packet_Type'), None)
    print("Recieved Packet_Type: {:s} - {:s}".format(data.get_value('Packet_Type'), notice_type)) 
    print (f"{data.role=}")

    #set_roles_to_respond = set(['observation', 'test'])
    set_roles_to_respond = set(['observation',])

    # Respond to only real 'observation' events
    if data.role not in set_roles_to_respond:
        print (f"Skip notice with role {data.role=}")
        return
  
    if not notice_type:
        return

    event_date_time = data.get_event_time()
    event_name, event_gbm_name, event_date, event_time = data.get_event_name()
    print(event_name, event_gbm_name, event_date, event_time)
    
    log.info("Received message info: {:s} {:s} {:s} {:s} {:8.3f}".format(notice_type, event_name, event_gbm_name, event_date, event_time))

    # Respond to only GBM triggers where Most_Likely_Index in GoodIndex
    MOST_LIKELY_IND = data.get_value('Most_Likely_Index')

    if MOST_LIKELY_IND is not None:
        if MOST_LIKELY_IND not in GoodIndex:
            log.info("MOST_LIKELY_IND is {:s} ({:s}), skip this event!".format(MOST_LIKELY_IND, AllIndex.get(MOST_LIKELY_IND, 'N/A')))
            return
        else:
            log.info("MOST_LIKELY_IND is {:s} ({:s}), write event info to a file.".format(MOST_LIKELY_IND, AllIndex.get(MOST_LIKELY_IND, 'N/A')))
  
    if data.get_event_type() == 'GW':
        #Send Telegram notification and download data
        #print(data.get_value(Terrestrial))
        telegram_api.send_to_telegram(data, notice_type, event_date_time, event_name)
        return

    telegram_api.send_to_telegram(data, notice_type, event_date_time, event_name)

    path = "{:s}/{:s}".format(info['data_dir'], event_name)
    if not os.path.exists(path):
        os.mkdir(path)
        log.info ("The folder {:s} is created".format(event_name))
  
    # Create file with all notices and parse the message
    file_name = "{:s}/{:s}_{:s}.txt".format(path, event_name, notice_type[:3])
    data.append_info_to_file(file_name)

    if notice_type in ('FERMI GBM FLT POS', 'FERMI GBM GND POS', 'FERMI GBM FIN POS'):
        run_download_gbm_thread(event_name, event_gbm_name, path)
        #run_download_int_thread(event_name, event_date, int(event_time), path)
        #run_download_hend_thread(event_name, event_date, int(event_time), path)

    #elif notice_type in ('INTEGRAL SPIACS', 'IPN RAW', 'LVC_PRELIM'):
        #run_download_int_thread(event_name, event_date, int(event_time), path)
        #run_download_hend_thread(event_name, event_date, int(event_time), path)

if __name__ == "__main__":
    # Listen for GCNs until the program is interrupted (killed or interrupted with control-C).
    gcn.listen(handler=process_gcn)