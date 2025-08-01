import os
import logging as log
import asyncio

from telegram.request import HTTPXRequest
import telegram

import config
info = config.read_config('config.yaml')

import setlog
setlog.set_log()

os.environ['HTTP_PROXY'] = os.environ['http_proxy'] = info['telegram_proxy']
os.environ['HTTPS_PROXY'] = os.environ['https_proxy'] = info['telegram_proxy']

lst_par = """\
 Trig_Timescale 
 Data_Timescale 
 Data_Integ 
 Data_Signif 
 Burst_Signif
 Long_short 
 Sun_Distance 
 MOON_Distance 
 Galactic_Lat
""".split()

lst_par_lvc = """\
 GraceID
 Instruments 
 FAR 
 BNS 
 NSBH 
 BBH 
 MassGap
 Terrestrial 
 HasNS 
 HasRemnant
""".split()

set_par_lvc_float = set("BNS  NSBH  BBH  MassGap  Terrestrial  HasNS HasRemnant".split())

def send_to_telegram(data, notice_type, event_date_time, event_name):

    text= "Recieved notice: {:s}\nTrig. time: {:s}\nBurst name: {:s}\n".format(
        notice_type, event_date_time, event_name)

    for s in lst_par + lst_par_lvc:
        val = data.get_value(s)
        if val is not None:
            if s in set_par_lvc_float:
                text += "{:16s} {:.3f}\n".format(s+':', float(val))
            elif s=='FAR':
                text += "{:16s} {:.2e}\n".format(s+':', float(val))
            else:
                text += "{:16s} {:s}\n".format(s+':', val)

    log.info(text)

    trequest = HTTPXRequest(connection_pool_size=20)
    bot = telegram.Bot(token=info['bot_token'], request=trequest)
    
    asyncio.run(bot.send_message(chat_id=info['chat_id'], text=text))