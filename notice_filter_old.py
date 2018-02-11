# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import gcn
import telebot
import datetime
import threading
import get_fermi
import get_integral 
import gcn.handlers
import logging as log
import xml.dom.minidom
import gcn.notice_types

token = '408065188:AAGqxghhuzEBZUj-l17KNrBw7dAsbAOHLGE'
chat_id = 235646475
bot = telebot.TeleBot(token)

Temp_date_fermi_integral = None
Temp_date_integral = None

ArrayType = {'31': 'IPN RAW', '111': 'FERMI GBM FLT POS',
  '112': 'FERMI GBM GND POS', '115': 'FERMI GBM FIN POS',
  '61': 'SWIFT BAT GRB POS ACK', '84': 'SWIFT BAT TRANS',
  '52': 'INTEGRAL SPIACS'}

ArrayParam = {
  'Packet_Type': 'NOTICE_TYPE:', 'TrigID': 'TRIGGER_NUM:',
  'Sun_Distance': 'SUN_DIST:', 'Sun_Hr_Angle': 'SUN_ANGLE:',
  'Galactic_Long': 'GAL_LONG:', 'Galactic_Lat': 'GAL_LAT:',
  'Ecliptic_Long': 'ECL_LONG:', 'Ecliptic_Lat': 'ECL_LAT:',
  'Burst_Inten': 'BURST_INTEN:', 'Trig_Timescale': 'TRIG_TIMESCALE:',
  'Data_Timescale': 'DATA_TIMESCALE:', 'Data_Signif': 'DATA_SIGNIF:',
  'Most_Likely_Index': 'MOST_LIKELY:', 'Most_Likely_Prob': 'MOST_LIKELY_PROB',
  'Sec_Most_Likely_Index': '2nd_MOST_LIKELY:', 'MOON_Distance': 'MOON_DIST'}

ArrayVar = (
  'C1', 'GRB_RA:', 'C2', 'GRB_DEC:',
  'Error2Radius', 'GRB_ERROR:', 'ISOTime', 'GRB_TIME:')

# Most_Likely_Ind
GoodIndex = {'4': '4  GRB', '5': '5  GENERIC_SGR', '6': '6  GENERIC_TRANSIENT',
	'7': '7  DISTANT_PARTICLES', '10': '10  SGR_1806_20', '11': '11  GROJ_0422_32'}

# Sec_Most_Likely_Index
AllIndex = {'0': '0 ERROR', '1': '1 UNRELIABLE_LOCATION', '2': '2 LOCAL_PARTICLES', '3': '3 BELOW_HORIZON', '4': '4 GRB',
  '5': '5 GENERIC_SGR', '5': '6 GENERIC_TRANSIENT', '7': '7 DISTANT_PARTICLES', '8': '8 SOLAR_FLARE', '9': '9 CYG_X1',
  '10': '10 SGR_1806_20 ', '11': '11 GROJ_0422_32', '12': '12 undefined', '13': '13 undefined', '14': '14 undefined',
  '15': '15 undefined', '16': '16 undefined', '17': '17 undefined', '18': '18 undefined', '19': '19 TGF'}

# Convert date and name
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

def recording_Param(child, el, filename):

	key, parametr = el

	if (child.getAttribute('name') == key and child.getAttribute('name') == 'Packet_Type'):
		value = ArrayType.get(child.getAttribute('value'))
                print("{:21s} {:s}".format(parametr, value), file = filename)

	elif (child.getAttribute('name') == key and child.getAttribute('name') == 'Most_Likely_Index'):
		value = GoodIndex.get(child.getAttribute('value'))
		print("{:21s} {:s}".format(parametr, value), file = filename)

  	elif (child.getAttribute('name') == key and child.getAttribute('name') == 'Sec_Most_Likely_Index'):
    		value = AllIndex.get(child.getAttribute('value'))
    		print("{:21s} {:s}".format(parametr, value), file = filename)

	elif (child.getAttribute('name') == key):
		value = child.getAttribute('value')
		print("{:21s} {:s}".format(parametr, value), file = filename)

def recording_Var(root, el, next_el, filename):

  key = el
  parametr = next_el
  value = root.getElementsByTagName(key)[0].firstChild.data
  print("{:21s} {:s}".format(parametr, value), file = filename)

# Function to call every time a GCN is received.
@gcn.handlers.include_notice_types(
     gcn.notice_types.IPN_RAW,
     gcn.notice_types.FERMI_GBM_FLT_POS,
     gcn.notice_types.FERMI_GBM_GND_POS,
     gcn.notice_types.FERMI_GBM_FIN_POS,
     gcn.notice_types.INTEGRAL_SPIACS)

#-----------------------------------------------------------------------------------------

def process_gcn(payload, root):

  root = xml.dom.minidom.parseString(payload)
  root.normalize()

  # Respond to only real 'observation' events
  if (root.getElementsByTagName('voe:VOEvent')[0].getAttribute('role') != 'observation'):
  	return

  # Respond to only Most_Likely_Index = GoodIndex, Data_Timescale > 1.024, Data_Signif > 20.
  childList = root.getElementsByTagName('Param')

  for child in childList:
  	if (child.getAttribute('name') == 'Most_Likely_Index'):
  		MOST_LIKELY_IND = child.getAttribute('value')
  		if MOST_LIKELY_IND not in GoodIndex:
			log.info ("Most_Likely_Index = {:s}, folder not created!".format(MOST_LIKELY_IND))
  			return
		else:
			log.info ("Most_Likely_Index = {:s}".format(MOST_LIKELY_IND))

  for child in childList:
    if (child.getAttribute('name') == 'Packet_Type'):
      Notice_type = ArrayType.get(child.getAttribute('value'))
      break

  if Notice_type == 'FERMI GBM FLT POS':
    for child in childList:
      if (child.getAttribute('name') == 'Data_Timescale'):
        DATA_TIMESCALE = float(child.getAttribute('value'))

      elif (child.getAttribute('name') == 'Data_Signif'):
        DATA_SIGNIF = float(child.getAttribute('value'))

    if (DATA_SIGNIF < 20.00 and  DATA_TIMESCALE > 1.024):
      log.info ("Data_Timescale = {:.3f}, Data_Signif = {:.3f} folder not created!".format(DATA_TIMESCALE, DATA_SIGNIF))
      return

    else:
      log.info ("Data_Timescale = {:.3f}, Data_Signif = {:.3f}".format(DATA_TIMESCALE, DATA_SIGNIF))

  Date_event, Name_event = get_folder_name(root.getElementsByTagName('ISOTime')[0].firstChild.data)

  Path = './'+Name_event+'/'

  if not os.path.exists(Path):
  	os.mkdir(Path)

  	log.info ("The folder {:s} is created".format(Name_event))

  # Creating file and parse the message
  with open(Path+Name_event+'_'+Notice_type[:3]+'.txt', "a") as Nf:

  	print(" --- The begin message --- ", file = Nf)

  	for child in childList:

  		for el in ArrayParam.items():

  			recording_Param(child, el, Nf)

  	for el in ArrayVar[::2]:

  		next_el = ArrayVar[ArrayVar.index(el) + 1]

  		recording_Var(root, el, next_el, Nf)

  	print(" --- The end message --- \n",  file = Nf)
  
  # Send a message to Telegram
  if Notice_type == 'FERMI GBM FLT POS':

    bot.send_message(chat_id, "Type of received messages is {:s}, {:s}, data timescale = {:8.3f}, data signif = {:8.1f}".format(Notice_type, Name_event, DATA_TIMESCALE, DATA_SIGNIF))
  
  else:

    bot.send_message(chat_id, "Type of received messages is {:s}, {:s}".format(Notice_type, Name_event))

  log.info("Type of received messages is {:s}, {:s}".format(Notice_type, Name_event))

  if (Notice_type == ('FERMI GBM FLT POS' or 'FERMI GBM GND POS' or 'FERMI GBM FIN POS')):

  	global Temp_date_fermi_integral

  	thread_fermi = threading.Thread(target = get_fermi.download_fermi, args = (Date_event, Name_event,))
  	thread_integral = threading.Thread(target = get_integral.download_integral, args = (Name_event, 200,))

  	if (Temp_date_fermi_integral != Date_event) and (thread_fermi.is_alive() == False):

  		thread_fermi.start()

  		log.info ("The thread {:s} started".format(Date_event+'_FER'))

		if (Temp_date_fermi_integral != Date_event) and (thread_integral.is_alive() == False):
        	  thread_integral.start()
  		  log.info("The thread {:s} started".format(Date_event+'_INT'))
  		  Temp_date_fermi_integral = Date_event
      		else:
                  log.info ("The thread {:s} is already working".format(Date_event+'_INT'))
  	else:

  		log.info ("The thread {:s} is already working".format(Date_event+'_FER'))

  elif (Notice_type == 'INTEGRAL SPIACS'):

    thread_integral = threading.Thread(target = get_integral.download_integral, args = (Name_event, 200,))

    global Temp_date_integral

    if (Temp_date_integral != Date_event) and (thread_integral.is_alive() == False):

      thread_integral.start()

      log.info ("The thread {:s} started".format(Date_event+'_INT'))

      Temp_date_integral = Date_event

    else:

      log.info ("The thread {:s} is already working".format(Date_event+'_INT'))

# Parameters of the log file
log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u'log.txt')

# Listen for GCNs until the program is interrupted (killed or interrupted with control-C).
gcn.listen(handler=process_gcn)


# For testing
"""
payload = '''<?xml version = '1.0' encoding = 'UTF-8'?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/Fermi#GBM_Flt_Pos_2011-09-04T03:54:36.02_336801278_45-956"
      role="observation" version="1.1"
      xmlns:voe="http://www.ivoa.net/xml/VOEvent/v1.1"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v1.1 http://www.ivoa.net/xml/VOEvent/VOEvent-v1.1.xsd" >
  <Who>
    <AuthorIVORN>ivo://nasa.gsfc.tan/gcn</AuthorIVORN>
    <Author>
      <shortName>Fermi (via VO-GCN)</shortName>
      <contactName>Julie Mcenery</contactName>
      <contactPhone>+1-301-286-1632</contactPhone>
      <contactEmail>Julie.E.McEnery@nasa.gov</contactEmail>
    </Author>
    <Date>2011-09-04T03:54:51</Date>
    <Description>This VOEvent message was created with GCN VOE version: 1.4 04jun11</Description>
  </Who>
  <What>
    <Param name="Packet_Type"    value="111" />
    <Param name="Pkt_Ser_Num"    value="10" />
    <Param name="TrigID"         value="336801278" ucd="meta.id" />
    <Param name="Sequence_Num"   value="45" ucd="meta.id.part" />
    <Param name="Burst_TJD"      value="15808" unit="days" ucd="time" />
    <Param name="Burst_SOD"      value="14076.02" unit="sec" ucd="time" />
    <Param name="Burst_Inten"    value="117" unit="cts" ucd="phot.count" />
    <Param name="Trig_Timescale" value="8.192" unit="sec" ucd="time.interval" />
    <Param name="Data_Timescale" value="8.192" unit="sec" ucd="time.interval" />
    <Param name="Data_Signif"    value="21.00" unit="sigma" ucd="stat.snr" />
    <Param name="Phi"            value="55.00" unit="deg" ucd="pos.az.azi" />
    <Param name="Theta"          value="65.00" unit="deg" ucd="pos.az.zd" />
    <Param name="SC_Long"        value="115.18" unit="deg" ucd="pos.earth.lon" />
    <Param name="SC_Lat"         value="0.00" unit="deg" ucd="pos.earth.lat" />
    <Param name="Algorithm"             value="3" unit="dn" />
    <Param name="Most_Likely_Index"     value="4" unit="dn" />
    <Param name="Most_Likely_Prob"      value="93" />
    <Param name="Sec_Most_Likely_Index" value="8" unit="dn" />
    <Param name="Sec_Most_Likely_Prob"  value="5" />
    <Param name="Hardness_Ratio"        value="1.39" ucd="arith.ratio" />
    <Param name="Trigger_ID"            value="0x0" />
    <Param name="Misc_flags"            value="0x1000000" />
    <Group name="Trigger_ID" >
      <Param name="Def_NOT_a_GRB"         value="false" />
      <Param name="Target_in_Blk_Catalog" value="false" />
      <Param name="Spatial_Prox_Match"    value="false" />
      <Param name="Temporal_Prox_Match"   value="false" />
      <Param name="Test_Submission"       value="false" />
    </Group>
    <Group name="Misc_Flags" >
      <Param name="Values_Out_of_Range"   value="false" />
      <Param name="Delayed_Transmission"  value="true" />
      <Param name="Flt_Generated"         value="true" />
      <Param name="Gnd_Generated"         value="false" />
    </Group>
    <Param name="Coords_Type"   value="1" unit="dn" />
    <Param name="Coords_String" value="source_object" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="162.74" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="7.33" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="48.74" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="-2.03" unit="hr" />
      <Param name="Moon_RA"       value="241.71" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="-22.42" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="43.86" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="43.70" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="303.07" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="31.12" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="204.91" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="-24.00" unit="deg" ucd="pos.ecliptic.lat" />
    </Group>
    <Description>The Fermi-GBM location of a transient.</Description>
  </What>
  <WhereWhen>
    <ObsDataLocation xmlns="http://www.ivoa.net/xml/STC/stc-v1.30.xsd">
      <ObservatoryLocation xlink:href="ivo://STClib/Observatories#GEOLUN/" xlink:type="simple" id="GEOLUN" />
      <ObservationLocation>
        <AstroCoordSystem xlink:href="ivo://STClib/CoordSys#UTC-FK5-GEO/" xlink:type="simple" id="FK5-UTC-GEO" />
        <AstroCoords coord_system_id="FK5-UTC-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2017-10-04T20:33:35.38</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1 pos_unit="deg">193.0000</C1>
              <C2 pos_unit="deg">-31.7500</C2>
            </Value2>
            <Error2Radius>17.4333</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  <Description>The RA,Dec coordinates are of the type: source_object.</Description>
  </WhereWhen>
  <How>
    <Description>Fermi Satellite, GBM Instrument</Description>
    <Reference uri="http://gcn.gsfc.nasa.gov/fermi.html" type="url" />
  </How>
  <Why importance="0.5">
    <Inference probability="0.5">
      <Concept>process.variation.burst;em.gamma</Concept>
    </Inference>
  </Why>
  <Citations>
    <EventIVORN cite="followup">ivo://nasa.gsfc.gcn/Fermi#GBM_Alert_2011-09-04T03:54:36.02_336801278_1-954</EventIVORN>
    <Description>This is an updated position to the original trigger.</Description> 
  </Citations>
  <Description>
  </Description>
</voe:VOEvent>
'''.encode('UTF-8')

root = gcn.voeventclient.parse_from_string(payload)
process_gcn(payload, root)
"""