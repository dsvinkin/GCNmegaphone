# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import datetime
import threading
import logging as log
import re
from collections import OrderedDict

#import xml.dom.minidom
from lxml import etree

import gcn
import gcn.handlers
import gcn.notice_types

import telebot

import get_fermi
import get_integral

# Parameters of the log file
#log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u'log.txt')
log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.DEBUG, filename = u'log.txt')

# Telegram parameters
token = '408065188:AAGqxghhuzEBZUj-l17KNrBw7dAsbAOHLGE'
chat_id = 235646475
bot = telebot.TeleBot(token)

current_event_fermi_integral = None
current_event_integral = None

ArrayType = {
    '31': 'IPN RAW', 
    '111': 'FERMI GBM FLT POS',
    '112': 'FERMI GBM GND POS', 
    '115': 'FERMI GBM FIN POS',
    '61': 'SWIFT BAT GRB POS ACK', 
    '84': 'SWIFT BAT TRANS',
    '52': 'INTEGRAL SPIACS'
     }

ArrayParam = {
    'Packet_Type': 'NOTICE_TYPE', 
    'TrigID': 'TRIGGER_NUM',
    'Sun_Distance': 'SUN_DIST', 
    'Sun_Hr_Angle': 'SUN_ANGLE',
    'Galactic_Long': 'GAL_LONG', 
    'Galactic_Lat': 'GAL_LAT',
    'Ecliptic_Long': 'ECL_LONG', 
    'Ecliptic_Lat': 'ECL_LAT',
    'Burst_Inten': 'BURST_INTEN', 
    'Trig_Timescale': 'TRIG_TIMESCALE',
    'Data_Timescale': 'DATA_TIMESCALE', 
    'Data_Signif': 'DATA_SIGNIF',
    'Most_Likely_Index': 'MOST_LIKELY', 
    'Most_Likely_Prob': 'MOST_LIKELY_PROB',
    'Sec_Most_Likely_Index': '2nd_MOST_LIKELY',
    'Sec_Most_Likely_Prob': '2nd_MOST_LIKELY_PROB',
    'MOON_Distance': 'MOON_DIST',
    'C1':'GRB_RA',
    'C2':'GRB_DEC',
    'Error2Radius': 'GRB_ERROR',
    'ISOTime':'GRB_TIME'
    }

# Most_Likely_Ind
GoodIndex = {
    '4': '4  GRB', 
    '5': '5  GENERIC_SGR', 
    '6': '6  GENERIC_TRANSIENT',
    '7': '7  DISTANT_PARTICLES', 
    '10': '10  SGR_1806_20', 
    '11': '11  GROJ_0422_32'
    }

# Sec_Most_Likely_Index
AllIndex = {
    '0': '0 ERROR', 
    '1': '1 UNRELIABLE_LOCATION', 
    '2': '2 LOCAL_PARTICLES', 
    '3': '3 BELOW_HORIZON', 
    '4': '4 GRB',
    '5': '5 GENERIC_SGR', 
    '5': '6 GENERIC_TRANSIENT', 
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


def get_event_name(str_date_time):

    time = datetime.datetime.strptime(str_date_time, "%Y-%m-%dT%H:%M:%S.%f")
    part_day = int(round((time.hour*60 + time.minute + time.second/60.0) / 1.44))
  
    # gbm_name - format yymmddttt
    gbm_name = "{:s}{:03d}".format(time.strftime('%y%m%d'), part_day)
    date = time.strftime('%Y%m%d')
    time_sec = time.hour * 3600 + time.minute * 60 + time.second + time.microsecond/1e6
  
    # name - format GRByymmdd_sssss
    name = "GRB{:s}_T{:05d}".format(time.strftime('%Y%m%d'), int(time_sec))
  
    return name, gbm_name, date, time_sec

def send_to_telegram(text):

    bot.send_message(chat_id, text)

def run_download_gbm_thread(event_name, event_gbm_name, date, time, path):

    global current_event_fermi_integral
      
    thread_fermi = threading.Thread(target = get_fermi.download_fermi, args = (event_name, event_gbm_name, path))
    thread_integral = threading.Thread(target = get_integral.download_integral, args = (date, time, 200, path))

    get_fermi.download_fermi(date, event_gbm_name, path)
    get_integral.download_integral(date, time, 200, path)
    return
  
    if (current_event_fermi_integral != event_name and not thread_fermi.is_alive()):
        thread_fermi.start()
        log.info ("The thread {:s} started".format(event_name+'_FER'))
  
        if (current_event_fermi_integral != event_name and not thread_integral.is_alive()):
            thread_integral.start()
            log.info("The thread {:s} started".format(event_name+'_INT'))
            current_event_fermi_integral = event_name

        else:
            log.info ("The thread {:s} is already working".format(event_name+'_INT'))
    else:
        log.info ("The thread {:s} is already working".format(event_name+'_FER'))

def run_download_int_thread(event_name, date, time, path):
  
    global current_event_integral
    thread_integral = threading.Thread(target = get_integral.download_integral, args=(date, time, 200, path))

    if (current_event_integral != event_name and not thread_integral.is_alive()):
        thread_integral.start()
        log.info ("The thread {:s} started".format(event_name + '_INT'))
        current_event_integral = event_name
    
    else:
        log.info ("The thread {:s} is already working".format(Date_event+'_INT'))


class notice:

    def __init__(self, payload):
        self.payload = payload
        tree = etree.XML(payload) 

        self.dict_par = OrderedDict()
        self._update_dict(tree, self.dict_par)
        #print (self.dict_par)

        self.role = tree.attrib['role']

    def append_payload_to_file(self,file_name):
        with open(file_name, 'a') as f:
          print("-------------------------------", file=f)
          print(self.payload, file=f)

    def _update_dict(self, element, my_dict):
        """
        Code from https://stackoverflow.com/questions/28503666/python-parsing-xml-autoadd-all-key-value-pairs
        """
        # lxml defines "length" of the element as number of its children.
        if len(element):  # If "length" is other than 0.
            for subelement in element:
                # That's where the recursion happens. We're calling the same
                # function for a subelement of the element.
                self._update_dict(subelement, my_dict)
    
        else:  # Otherwise, subtree is a leaf.
            #print (element.tag,':', element.text, element.attrib)
    
            if element.text:
                name = element.tag
                name = re.sub(r"{.+?}","",name)
                my_dict[name] = element.text
                #print (name,':', element.text)
            elif element.attrib:
                name = element.attrib.get('name',None)
                val = element.attrib.get('value',None)
                if name and val:
                    #print (name,':', val)
                    my_dict[name] = val

    def _qw(self, s):
        return s.split()

    def get_value(self, key):
        return self.dict_par.get(key, None)

    def get_event_time(self):
        return self.dict_par.get('ISOTime', None)

    def print_param(self, key, f):

        name = ArrayParam[key]
        val = self.dict_par[key]
        
        if (key == 'Packet_Type'):
            print("{:22s} {:s}".format(name, ArrayType[val]), file=f)

        elif (key == 'Most_Likely_Index'):
            print("{:22s} {:s}".format(name, GoodIndex[val]), file=f)
    
        elif (key == 'Sec_Most_Likely_Index'):
            print("{:22s} {:s}".format(name, AllIndex[val]), file=f)
    
        else:
            print("{:22s} {:s}".format(name, val), file=f)
    
    def append_info_to_file(self, file_name):

       lst_to_print = self._qw('Packet_Type TrigID  ISOTime '+ 
            'Trig_Timescale Data_Timescale Data_Signif '+
            'Most_Likely_Index Most_Likely_Prob Sec_Most_Likely_Index Sec_Most_Likely_Prob '+
            'C1 C2 Error2Radius '+
            'Sun_Distance Galactic_Long Galactic_Lat Ecliptic_Long Ecliptic_Lat'
             )

       with open(file_name, 'a') as f:
          now = datetime.utcnow()
          print("{:22s} {:s}".format('Timestamp', now), file=f)
      
          for key in lst_to_print:
              self.print_param(key, f)
      
          print("-----------------------------\n", file=f)

    
# Function to call every time a GCN is received.
@gcn.handlers.include_notice_types(
    gcn.notice_types.IPN_RAW,
    gcn.notice_types.FERMI_GBM_FLT_POS,
    gcn.notice_types.FERMI_GBM_GND_POS,
    gcn.notice_types.FERMI_GBM_FIN_POS,
    gcn.notice_types.INTEGRAL_SPIACS)

def process_gcn(payload, root):

    data = notice(payload)
    data.append_payload_to_file('raw_notices.txt')

    # Respond to only real 'observation' events
    if (data.role != 'observation'):
        #print ("data.role != observation")
        return
  
    notice_type = ArrayType[data.get_value('Packet_Type')]
    event_date_time = data.get_event_time()

    event_name, event_gbm_name, event_date, event_time = get_event_name(event_date_time)
    print(event_name, event_gbm_name, event_date, event_time)
    log.info("Received message info: {:s} {:s} {:s} {:s} {:8.3f}".format(notice_type, event_name, event_gbm_name, event_date, event_time))

    # Respond to only Most_Likely_Index = GoodIndex
    MOST_LIKELY_IND = data.get_value('Most_Likely_Index')
    if MOST_LIKELY_IND and MOST_LIKELY_IND not in GoodIndex:
        log.info ("MOST_LIKELY_IND is {:s} ({:s}), skip this event!".format(MOST_LIKELY_IND, AllIndex.get(MOST_LIKELY_IND, 'N/A')))
        return
    else:
        log.info ("MOST_LIKELY_IND is {:s} ({:s}), write event info to a file.".format(MOST_LIKELY_IND, AllIndex.get(MOST_LIKELY_IND, 'N/A')))
  
    path = "../{:s}".format(event_name)
    if not os.path.exists(path):
        os.mkdir(path)
        log.info ("The folder {:s} is created".format(event_name))
  
    # Create file with all notices and parse the message
    file_name = "{:s}/{:s}_{:s}.txt".format(path, event_name, notice_type[:3])
    data.append_info_to_file(file_name)

    #Download data and send Telegram notification
    if notice_type in ('FERMI GBM FLT POS', 'FERMI GBM GND POS', 'FERMI GBM FIN POS'):
        DATA_TIMESCALE = float(data.get_value('Data_Timescale'))
        DATA_SIGNIF = float(data.get_value('Data_Signif'))
        log.info("{:s} DATA_TIMESCALE: {:.3f} DATA_SIGNIF: {:.3f}".format(notice_type, DATA_TIMESCALE, DATA_SIGNIF))
        run_download_gbm_thread(event_name, event_gbm_name, event_date, int(event_time), path)

        if (DATA_SIGNIF > 20.0 or DATA_TIMESCALE < 1.024):
            send_to_telegram("Message type: {:s}\n{:s}\nDATA_TIMESCALE: {:8.3f}\nDATA_SIGNIF: {:8.1f}".format(
                notice_type, event_date_time, DATA_TIMESCALE, DATA_SIGNIF))
    elif notice_type == 'INTEGRAL SPIACS':
        run_download_int_thread(event_name, event_date, int(event_time), path)
        

if __name__ == "__main__":
    # Listen for GCNs until the program is interrupted (killed or interrupted with control-C).
    gcn.listen(handler=process_gcn)