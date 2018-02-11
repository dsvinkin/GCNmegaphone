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
log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u'log.txt')

# Telegram parameters
token = '408065188:AAGqxghhuzEBZUj-l17KNrBw7dAsbAOHLGE'
chat_id = 235646475
bot = telebot.TeleBot(token)

Temp_date_fermi_integral = None
Temp_date_integral = None

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
    'Packet_Type': 'NOTICE_TYPE:', 
    'TrigID': 'TRIGGER_NUM:',
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


def get_folder_name(dt_str):

    dt, _, us = dt_str.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    part_day = int(round((dt.hour*60+dt.minute+dt.second/60.0)/1.44))
  
    # date - format yymmddttt
    date = "{:s}{:03d}".format(dt.strftime('%y%m%d'), part_day)
    time_sec = dt.hour*3600+dt.minute*60+dt.second
  
    # name - format GRByymmdd_sssss
    name = "GRB{:s}_{:05d}".format(dt.strftime('%y%m%d'), time_sec)
  
    return date, name


def send_to_telegram(text):

    bot.send_message(chat_id, text)

def run_download_gbm_thread(Date_event, Name_event):

    global Temp_date_fermi_integral
      
    thread_fermi = threading.Thread(target = get_fermi.download_fermi, args = (Date_event, Name_event,))
    thread_integral = threading.Thread(target = get_integral.download_integral, args = (Name_event, 200,))
  
    if (Temp_date_fermi_integral != Date_event and not thread_fermi.is_alive()):
  
        thread_fermi.start()
        log.info ("The thread {:s} started".format(Date_event+'_FER'))
  
        if (Temp_date_fermi_integral != Date_event and not thread_integral.is_alive()):
            thread_integral.start()
            log.info("The thread {:s} started".format(Date_event+'_INT'))
            Temp_date_fermi_integral = Date_event

        else:
            log.info ("The thread {:s} is already working".format(Date_event+'_INT'))
    else:
        log.info ("The thread {:s} is already working".format(Date_event+'_FER'))

def run_download_int_thread(Date_event, Name_event):
  
    global Temp_date_integral
    thread_integral = threading.Thread(target = get_integral.download_integral, args = (Name_event, 200,))
    
    if (Temp_date_integral != Date_event and not thread_integral.is_alive()):
        thread_integral.start()
        log.info ("The thread {:s} started".format(Date_event+'_INT'))
        Temp_date_integral = Date_event
    
    else:
        log.info ("The thread {:s} is already working".format(Date_event+'_INT'))


class notice:

    def __init__(self, payload):
        tree = etree.XML(payload) 

        self.dict_par = OrderedDict()
        self._update_dict(tree, self.dict_par)

        self.role = self.dict_par['role']

    def _update_dict(self, element, my_dict):
        """
        Code from https://stackoverflow.com/questions/28503666/python-parsing-xml-autoadd-all-key-value-pairs
        """
        # lxml defines "length" of the element as number of its children.
        if len(element):  # If "length" is other than 0.
            for subelement in element:
                # That's where the recursion happens. We're calling the same
                # function for a subelement of the element.
                update_dict(subelement, my_dict)
    
        else:  # Otherwise, subtree is a leaf.
            #print (element.tag,':', element.text, element.attrib)
    
            if element.text:
                name = element.tag
                name = re.sub(r"{.+?}","",name)
                my_dict[name] = element.text
                print (name,':', element.text)
            elif element.attrib:
                name = element.attrib.get('name',None)
                val = element.attrib.get('value',None)
                if name and val:
                    print (name,':', val)
                    my_dict[name] = val

    def _qw(self, s):
        return s.split()

    def get_value(self, key):
        self.dict_par.get(key, None)

    def get_event_time(self):
        self.dict_par.get('ISOTime', None)

    def print_param(self, key, f):

        name = ArrayParam[key]
        val = self.dict_par[key]

        if (key == 'Most_Likely_Index'):
            print("{:21s} {:s}".format(name, GoodIndex[val]), file=f)
    
        elif (key == 'Sec_Most_Likely_Index'):
            print("{:21s} {:s}".format(name, AllIndex[val]), file=f)
    
        else:
            print("{:21s} {:s}".format(name, val), file=f)
    
    def append_info_to_file(self, file_name):

       lst_to_print = self._qw('Packet_Type TrigID  ISOTime '+ 
            'Trig_Timescale Data_Timescale Data_Signif '+
            'Most_Likely_Index Most_Likely_Prob Sec_Most_Likely_Index '+
            'C1 C2 Error2Radius '+
            'Sun_Distance Galactic_Long Galactic_Lat Ecliptic_Long Ecliptic_Lat'
             )

       with open(file_name, 'a') as f:
          print(" --- The begin message --- ", file=f)
      
          for key in lst_to_print:
              print_param(key, f)
      
          print(" --- The end message --- \n", file=f)
    
# Function to call every time a GCN is received.
@gcn.handlers.include_notice_types(
	gcn.notice_types.IPN_RAW,
	gcn.notice_types.FERMI_GBM_FLT_POS,
	gcn.notice_types.FERMI_GBM_GND_POS,
	gcn.notice_types.FERMI_GBM_FIN_POS,
	gcn.notice_types.INTEGRAL_SPIACS)
	
def process_gcn(payload, root):

    data = notice(payload)
  
    # Respond to only real 'observation' events
    if (data.role != 'observation'):
        return
  
    # Respond to only Most_Likely_Index = GoodIndex, Data_Timescale > 1.024, Data_Signif > 20.
    MOST_LIKELY_IND = data.get_value('Most_Likely_Index')
    if MOST_LIKELY_IND not in GoodIndex:
        log.info ("Most_Likely_Index = {:s}, folder not created!".format(MOST_LIKELY_IND))
        return
    else:
        log.info ("Most_Likely_Index = {:s}".format(MOST_LIKELY_IND))
  
    Notice_type = data.get_value('Packet_Type')
    event_date_time = data.get_event_time()

    #Download data and send Telegram notification for bright events only
    if Notice_type == 'FERMI GBM FLT POS':
        DATA_TIMESCALE = float(data.get_value('Data_Timescale'))
        DATA_SIGNIF = float(data.get_value('Data_Signif'))
  
        if (DATA_SIGNIF < 20.00 and DATA_TIMESCALE > 1.024):
            log.info ("Data_Timescale = {:.3f}, Data_Signif = {:.3f} folder not created!".format(DATA_TIMESCALE, DATA_SIGNIF))
            return
        else:
            log.info ("Data_Timescale = {:.3f}, Data_Signif = {:.3f}".format(DATA_TIMESCALE, DATA_SIGNIF))
            send_to_telegram("Message type: {:s}, {:s}, data timescale = {:8.3f}, data signif = {:8.1f}".format(
              Notice_type, event_date_time, DATA_TIMESCALE, DATA_SIGNIF))
    else:
        send_to_telegram("Type of received messages is {:s}, {:s}".format(Notice_type, event_date_time))
  
    Date_event, Name_event = get_folder_name(event_date_time)
    log.info("Type of received messages is {:s}, {:s}".format(Notice_type, Name_event))
  
    path = "./{:s}".format(Name_event)
  
    if not os.path.exists(Path):
        os.mkdir(Path)
        log.info ("The folder {:s} is created".format(Name_event))
  
    # Creating file with all notices and parse the message
    file_name = "{:s}/{:s}_{:s}.txt".format(Path, Name_event, Notice_type[:3])
    append_info_to_file(file_name, data.lst_par)

    # Download data
    if (Notice_type == ('FERMI GBM FLT POS' or 'FERMI GBM GND POS' or 'FERMI GBM FIN POS')):
        run_download_gbm_thread(Date_event, Name_event)
    
    elif (Notice_type == 'INTEGRAL SPIACS'):
        run_download_int_thread(Date_event, Name_event)


if __name__ == "__main__":    
    # Listen for GCNs until the program is interrupted (killed or interrupted with control-C).
    gcn.listen(handler=process_gcn)