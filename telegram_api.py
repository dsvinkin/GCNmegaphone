
import logging as log

import telegram

import config
info = config.read_config('config.yaml')

log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u"{:s}/{:s}".format(info['log_dir'], 'log.txt'))

# Telegram parameters
chat_id = info['chat_id']

pp = telegram.utils.request.Request(proxy_url=info['telegram_proxy'])
bot = telegram.Bot(token=info['bot_token'], request=pp)

lst_par = """\
 Trig_Timescale 
 Data_Timescale 
 Data_Integ 
 Data_Signif 
 Burst_Signif 
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

def send_to_telegram(data, notice_type, event_date_time, event_name):

    text= "Recieved notice: {:s}\nTrig. time: {:s}\nBurst name: {:s}\n".format(notice_type, event_date_time, event_name)

    for s in lst_par + lst_par_lvc:
        val = data.get_value(s)
        if val is not None:
            text += "{:16s} {:s}\n".format(s+':', val)

    log.info(text)
    bot.send_message(chat_id=chat_id, text=text)