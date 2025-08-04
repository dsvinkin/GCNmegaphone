
import os
import datetime
import threading
import logging as log

from gcn_kafka import Consumer

import config
import telegram_api
import get_fermi
#import get_integral

from notice import notice, check_gbm_classification

info = config.read_config('config.yaml')

# Parameters of the log file
import setlog
setlog.set_log()


current_event_fermi = None
current_event_integral = None
#current_event_hend = None

os.environ['HTTP_PROXY'] = os.environ['http_proxy'] = 'socks5h://konus:wind@159.253.20.56:8989'
os.environ['HTTPS_PROXY'] = os.environ['https_proxy'] = 'socks5h://konus:wind@159.253.20.56:8989'
os.environ['NO_PROXY'] = os.environ['no_proxy'] = '127.0.0.1,localhost,.local'

lst_notices ="""\
    gcn.classic.voevent.FERMI_GBM_ALERT
    gcn.classic.voevent.FERMI_GBM_FIN_POS
    gcn.classic.voevent.FERMI_GBM_FLT_POS
    gcn.classic.voevent.FERMI_GBM_GND_POS
    gcn.classic.voevent.GECAM_FLT
    gcn.classic.voevent.GECAM_GND
    gcn.classic.voevent.IPN_RAW
    gcn.classic.voevent.LVC_INITIAL
    gcn.classic.voevent.LVC_PRELIMINARY
    gcn.classic.voevent.LVC_UPDATE
    gcn.classic.voevent.SWIFT_BAT_GRB_POS_ACK
    gcn.classic.voevent.KONUS_LC
    gcn.notices.svom.voevent.grm
    gcn.notices.svom.voevent.eclairs
    igwn.gwalert
    gcn.notices.swift.bat.guano
    gcn.notices.einstein_probe.wxt.alert
""".split()

"""
Remobed notices 

gcn.heartbeat - https://gcn.nasa.gov/docs/faq#how-can-i-tell-that-my-kafka-client-is-working
"""

def run_download_gbm_thread(event_name, event_gbm_name, path):

    global current_event_fermi
    thread_fermi = threading.Thread(target = get_fermi.download_fermi, args = (event_gbm_name, path))
  
    if (current_event_fermi != event_name and not thread_fermi.is_alive()):
        thread_fermi.start()
        log.info("The thread {:s} started".format(event_name+'_FER'))
        current_event_fermi = event_name
    else:
        log.info ("The thread {:s} is already working".format(event_name+'_FER'))


# Function to call every time a GCN is received.

def process_gcn(message):

    #set_roles_to_respond = set(['observation', 'test'])
    set_roles_to_respond = set(['observation',])

    print(f'topic={message.topic()}, offset={message.offset()}')
    payload = message.value()
    #print(payload)
    
    if '.voevent' in message.topic():
        print('voevent')
    else:
        print('not voevent skipping')
        return

    data = notice(payload)
    data.append_payload_to_file("{:s}/{:s}".format(info['log_dir'], 'raw_notices.txt'))

    notice_type = good_notice_types.get(data.get_value('Packet_Type'), None)
    print("Recieved Packet_Type: {:s} - {:s}".format(data.get_value('Packet_Type'), notice_type)) 
    print (f"{data.role=}")

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

    str_class, is_good = check_gbm_classification(data):
        
    if is_good:
        log.info("MOST_LIKELY_IND is {:s}, write event info to a file.".format(str_class))
    else:
        log.info("MOST_LIKELY_IND is {:s}, skip this event!".format(str_class))
            return
  
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

    

if __name__ == "__main__":

    consumer = Consumer(
        client_id='7ui8eap5h755rodgdlr8k2jeij',
        client_secret='1u1rg3rpuhepnhp0kvp942l2hfe9njle2hsfbmgs9lboti7896dt')

    # Subscribe to topics and receive alerts
    consumer.subscribe(lst_notices)

    while True:
        for message in consumer.consume(timeout=1):
            if message.error():
                print(message.error())
                continue
            # Print the topic and message ID
            print(f'topic={message.topic()}, offset={message.offset()}')
            value = message.value()
            print(value)

            process_gcn(message)
