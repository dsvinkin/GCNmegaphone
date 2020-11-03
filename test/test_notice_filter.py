
""" 
Test for notice_filter.py
"""

from __future__ import print_function

import sys
sys.path.append('../')

from lxml.etree import fromstring

import gcn
import notice_filter

payload_gbm_flt1 = '''\
<?xml version = '1.0' encoding = 'UTF-8'?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/Fermi#GBM_Flt_Pos_2018-02-25T10:00:54.18_541245659_44-006"
      role="observation" version="2.0"
      xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" >
  <Who>
    <AuthorIVORN>ivo://nasa.gsfc.tan/gcn</AuthorIVORN>
    <Author>
      <shortName>Fermi (via VO-GCN)</shortName>
      <contactName>Julie McEnery</contactName>
      <contactPhone>+1-301-286-1632</contactPhone>
      <contactEmail>Julie.E.McEnery@nasa.gov</contactEmail>
    </Author>
    <Date>2018-02-25T10:01:17</Date>
    <Description>This VOEvent message was created with GCN VOE version: 1.25 07feb18</Description>
  </Who>
  <What>
    <Param name="Packet_Type"    value="111" />
    <Param name="Pkt_Ser_Num"    value="4" />
    <Param name="TrigID"         value="541245659" ucd="meta.id" />
    <Param name="Sequence_Num"   value="44" ucd="meta.id.part" />
    <Param name="Burst_TJD"      value="18174" unit="days" ucd="time" />
    <Param name="Burst_SOD"      value="36054.18" unit="sec" ucd="time" />
    <Param name="Burst_Inten"    value="299" unit="cts" ucd="phot.count" />
    <Param name="Trig_Timescale" value="0.256" unit="sec" ucd="time.interval" />
    <Param name="Data_Timescale" value="0.256" unit="sec" ucd="time.interval" />
    <Param name="Data_Signif"    value="8.00" unit="sigma" ucd="stat.snr" />
    <Param name="Phi"            value="130.00" unit="deg" ucd="pos.az.azi" />
    <Param name="Theta"          value="45.00" unit="deg" ucd="pos.az.zd" />
    <Param name="SC_Long"        value="96.04" unit="deg" ucd="pos.earth.lon" />
    <Param name="SC_Lat"         value="0.00" unit="deg" ucd="pos.earth.lat" />
    <Param name="Algorithm"             value="3" unit="dn" />
    <Param name="Most_Likely_Index"     value="4" unit="dn" />
    <Param name="Most_Likely_Prob"      value="96" />
    <Param name="Sec_Most_Likely_Index" value="6" unit="dn" />
    <Param name="Sec_Most_Likely_Prob"  value="3" />
    <Param name="Hardness_Ratio"        value="0.64" ucd="arith.ratio" />
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
    <Param name="LightCurve_URL" value="http://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2018/bn180225417/quicklook/glg_lc_medres34_bn180225417.gif" ucd="meta.ref.url" />
    <Param name="Coords_Type"   value="1" unit="dn" />
    <Param name="Coords_String" value="source_object" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="338.48" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="-9.03" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="142.07" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="10.71" unit="hr" />
      <Param name="Moon_RA"       value="94.59" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="20.06" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="92.16" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="73.14" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="285.37" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="37.03" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="187.79" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="-22.63" unit="deg" ucd="pos.ecliptic.lat" />
    </Group>
    <Description>The Fermi-GBM location of a transient.</Description>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="GEOLUN" />
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO" />
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2018-02-25T10:00:54.18</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>177.6000</C1>
              <C2>-23.7500</C2>
            </Value2>
            <Error2Radius>14.9833</Error2Radius>
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
    <EventIVORN cite="followup">ivo://nasa.gsfc.gcn/Fermi#GBM_Alert_2018-02-25T10:00:54.18_541245659_1-005</EventIVORN>
    <Description>This is an updated position to the original trigger.</Description>
  </Citations>
  <Description>
  </Description>
</voe:VOEvent>
'''

payload_gbm_flt2 = """\
<?xml version = '1.0' encoding = 'UTF-8'?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/Fermi#GBM_Flt_Pos_2020-02-04T12:25:17.16_602511922_46-343"
      role="observation" version="2.0"
      xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" >
  <Who>
    <AuthorIVORN>ivo://nasa.gsfc.tan/gcn</AuthorIVORN>
    <Author>
      <shortName>Fermi (via VO-GCN)</shortName>
      <contactName>Julie McEnery</contactName>
      <contactPhone>+1-301-286-1632</contactPhone>
      <contactEmail>Julie.E.McEnery@nasa.gov</contactEmail>
    </Author>
    <Date>2020-02-04T12:25:41</Date>
    <Description>This VOEvent message was created with GCN VOE version: 1.46 12jan20</Description>
  </Who>
  <What>
    <Param name="Packet_Type"    value="111" />
    <Param name="Pkt_Ser_Num"    value="11" />
    <Param name="TrigID"         value="602511922" ucd="meta.id" />
    <Param name="Sequence_Num"   value="46" ucd="meta.id.part" />
    <Param name="Burst_TJD"      value="18883" unit="days" ucd="time" />
    <Param name="Burst_SOD"      value="44717.16" unit="sec" ucd="time" />
    <Param name="Burst_Inten"    value="678" unit="cts" ucd="phot.count" />
    <Param name="Trig_Timescale" value="0.016" unit="sec" ucd="time.interval" />
    <Param name="Data_Timescale" value="0.016" unit="sec" ucd="time.interval" />
    <Param name="Data_Signif"    value="3.90" unit="sigma" ucd="stat.snr" />
    <Param name="Phi"            value="60.00" unit="deg" ucd="pos.az.azi" />
    <Param name="Theta"          value="30.00" unit="deg" ucd="pos.az.zd" />
    <Param name="SC_Long"        value="125.05" unit="deg" ucd="pos.earth.lon" />
    <Param name="SC_Lat"         value="0.00" unit="deg" ucd="pos.earth.lat" />
    <Param name="Algorithm"             value="3" unit="dn" />
    <Param name="Most_Likely_Index"     value="4" unit="dn" />
    <Param name="Most_Likely_Prob"      value="30" />
    <Param name="Sec_Most_Likely_Index" value="8" unit="dn" />
    <Param name="Sec_Most_Likely_Prob"  value="28" />
    <Param name="Hardness_Ratio"        value="8.49" ucd="arith.ratio" />
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
    <Param name="LightCurve_URL" value="http://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2020/bn200204518/quicklook/glg_lc_medres34_bn200204518.gif" ucd="meta.ref.url" />
    <Param name="Coords_Type"   value="1" unit="dn" />
    <Param name="Coords_String" value="source_object" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="317.61" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="-16.29" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="79.99" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="6.67" unit="hr" />
      <Param name="Moon_RA"       value="72.07" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="20.27" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="131.18" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="73.55" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="313.68" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="-2.17" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="239.13" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="-45.12" unit="deg" ucd="pos.ecliptic.lat" />
    </Group>
    <Description>The Fermi-GBM location of a transient.</Description>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="GEOLUN" />
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO" />
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2020-02-04T12:25:17.16</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>217.1000</C1>
              <C2>-63.0000</C2>
            </Value2>
            <Error2Radius>28.9833</Error2Radius>
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
    <EventIVORN cite="followup">ivo://nasa.gsfc.gcn/Fermi#GBM_Alert_2020-02-04T12:25:17.16_602511922_1-342</EventIVORN>
    <Description>This is an updated position to the original trigger.</Description>
  </Citations>
  <Description>
  </Description>
</voe:VOEvent>"""

payload_lvc = """\
<?xml version="1.0" ?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
 version="2.0" role="observation" ivorn="ivo://gwnet/LVC#MS190225l-1-Preliminary">
    <Who>
        <Date>2019-02-25T11:59:29</Date>
        <Author>
            <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
        </Author>
    </Who>
    <What>
        <Param name="Packet_Type" dataType="int" value="150">
            <Description>The Notice Type number is assigned/used within GCN, eg type=150 is an LVC_PRELIMINARY notice</Description>
        </Param>
        <Param name="internal" dataType="int" value="0">
            <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
        </Param>
        <Param name="Pkt_Ser_Num" dataType="string" value="1"/>
        <Param name="GraceID" dataType="string" value="MS190225l" ucd="meta.id">
            <Description>Identifier in GraceDB</Description>
        </Param>
        <Param name="AlertType" dataType="string" value="Preliminary" ucd="meta.version">
            <Description>VOEvent alert type</Description>
        </Param>
        <Param name="HardwareInj" dataType="int" value="0" ucd="meta.number">
            <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
        </Param>
        <Param name="OpenAlert" dataType="int" value="1" ucd="meta.number">
            <Description>Indicates that this event is an open alert if 1, no if 0</Description>
        </Param>
        <Param name="EventPage" dataType="string" value="https://gracedb.ligo.org/superevents/MS190225l/view/" ucd="meta.ref.url">
            <Description>Web page for evolving status of this GW candidate</Description>
        </Param>
        <Param name="Instruments" dataType="string" value="H1,L1,V1" ucd="meta.code">
            <Description>List of instruments used in analysis to identify this event</Description>
        </Param>
        <Param name="FAR" dataType="float" value="5.17695487734e-16" ucd="arith.rate;stat.falsealarm" unit="Hz">
            <Description>False alarm rate for GW candidates with this strength or greater</Description>
        </Param>
        <Param name="Group" dataType="string" value="CBC" ucd="meta.code">
            <Description>Data analysis working group</Description>
        </Param>
        <Param name="Pipeline" dataType="string" value="gstlal" ucd="meta.code">
            <Description>Low-latency data analysis pipeline</Description>
        </Param>
        <Param name="Search" dataType="string" value="MDC" ucd="meta.code">
            <Description>Specific low-latency search</Description>
        </Param>
        <Group type="GW_SKYMAP" name="bayestar">
            <Param name="skymap_fits" dataType="string" value="https://gracedb.ligo.org/api/superevents/MS190225l/files/bayestar.fits.gz" ucd="meta.ref.url">
                <Description>Sky Map FITS</Description>
            </Param>
        </Group>
        <Group type="Classification">
            <Param name="BNS" dataType="float" value="0.99991250894" ucd="stat.probability">
                <Description>Probability that the source is a binary neutron star merger</Description>
            </Param>
            <Param name="NSBH" dataType="float" value="0.0" ucd="stat.probability">
                <Description>Probability that the source is a neutron star - black hole merger</Description>
            </Param>
            <Param name="BBH" dataType="float" value="0.0" ucd="stat.probability">
                <Description>Probability that the source is a binary black hole merger</Description>
            </Param>
            <Param name="Terrestrial" dataType="float" value="8.74910603082e-05" ucd="stat.probability">
                <Description>Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)</Description>
            </Param>
            <Description>Source classification: binary neutron star (BNS), neutron star-blackhole (NSBH), binary black hole (BBH), or terrestrial (noise)</Description>
        </Group>
        <Group type="Properties">
            <Param name="HasNS" dataType="float" value="1.0" ucd="stat.probability">
                <Description>Probability that at least one object in the binary has a mass that is less than 3 solar masses</Description>
            </Param>
            <Param name="HasRemnant" dataType="float" value="1.0" ucd="stat.probability">
                <Description>Probability that a nonzero mass was ejected outside the central remnant object</Description>
            </Param>
            <Description>Qualitative properties of the source, conditioned on the assumption that the signal is an astrophysical compact binary merger</Description>
        </Group>
    </What>
    <WhereWhen>
        <ObsDataLocation>
            <ObservatoryLocation id="LIGO Virgo"/>
            <ObservationLocation>
                <AstroCoordSystem id="UTC-FK5-GEO"/>
                <AstroCoords coord_system_id="UTC-FK5-GEO">
                    <Time>
                        <TimeInstant>
                            <ISOTime>2019-02-25T11:52:17.151336</ISOTime>
                        </TimeInstant>
                    </Time>
                </AstroCoords>
            </ObservationLocation>
        </ObsDataLocation>
    </WhereWhen>
    <How>
        <Description>Candidate gravitational wave event identified by low-latency analysis</Description>
        <Description>H1: LIGO Hanford 4 km gravitational wave detector</Description>
        <Description>L1: LIGO Livingston 4 km gravitational wave detector</Description>
        <Description>V1: Virgo 3 km gravitational wave detector</Description>
    </How>
    <Description>Report of a candidate gravitational wave event</Description>
</voe:VOEvent>
"""

payload_lvc_initial = """\
<?xml version="1.0" ?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
 version="2.0" role="observation" ivorn="ivo://gwnet/LVC#MS190225m-2-Initial">
    <Who>
        <Date>2019-02-25T13:00:27</Date>
        <Author>
            <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
        </Author>
    </Who>
    <What>
        <Param name="Packet_Type" dataType="int" value="151">
            <Description>The Notice Type number is assigned/used within GCN, eg type=151 is an LVC_INITIAL notice</Description>
        </Param>
        <Param name="internal" dataType="int" value="0">
            <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
        </Param>
        <Param name="Pkt_Ser_Num" dataType="string" value="2"/>
        <Param name="GraceID" dataType="string" value="MS190225m" ucd="meta.id">
            <Description>Identifier in GraceDB</Description>
        </Param>
        <Param name="AlertType" dataType="string" value="Initial" ucd="meta.version">
            <Description>VOEvent alert type</Description>
        </Param>
        <Param name="HardwareInj" dataType="int" value="0" ucd="meta.number">
            <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
        </Param>
        <Param name="OpenAlert" dataType="int" value="1" ucd="meta.number">
            <Description>Indicates that this event is an open alert if 1, no if 0</Description>
        </Param>
        <Param name="EventPage" dataType="string" value="https://gracedb.ligo.org/superevents/MS190225m/view/" ucd="meta.ref.url">
            <Description>Web page for evolving status of this GW candidate</Description>
        </Param>
        <Param name="Instruments" dataType="string" value="H1,L1" ucd="meta.code">
            <Description>List of instruments used in analysis to identify this event</Description>
        </Param>
        <Param name="FAR" dataType="float" value="9.11069936486e-14" ucd="arith.rate;stat.falsealarm" unit="Hz">
            <Description>False alarm rate for GW candidates with this strength or greater</Description>
        </Param>
        <Param name="Group" dataType="string" value="CBC" ucd="meta.code">
            <Description>Data analysis working group</Description>
        </Param>
        <Param name="Pipeline" dataType="string" value="gstlal" ucd="meta.code">
            <Description>Low-latency data analysis pipeline</Description>
        </Param>
        <Param name="Search" dataType="string" value="MDC" ucd="meta.code">
            <Description>Specific low-latency search</Description>
        </Param>
        <Group type="GW_SKYMAP" name="bayestar">
            <Param name="skymap_fits" dataType="string" value="https://gracedb.ligo.org/api/superevents/MS190225m/files/bayestar.fits.gz" ucd="meta.ref.url">
                <Description>Sky Map FITS</Description>
            </Param>
        </Group>
        <Group type="Classification">
            <Param name="BNS" dataType="float" value="0.995705026421" ucd="stat.probability">
                <Description>Probability that the source is a binary neutron star merger</Description>
            </Param>
            <Param name="NSBH" dataType="float" value="0.0" ucd="stat.probability">
                <Description>Probability that the source is a neutron star - black hole merger</Description>
            </Param>
            <Param name="BBH" dataType="float" value="0.0" ucd="stat.probability">
                <Description>Probability that the source is a binary black hole merger</Description>
            </Param>
            <Param name="Terrestrial" dataType="float" value="0.0042949735787" ucd="stat.probability">
                <Description>Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)</Description>
            </Param>
            <Description>Source classification: binary neutron star (BNS), neutron star-blackhole (NSBH), binary black hole (BBH), or terrestrial (noise)</Description>
        </Group>
        <Group type="Properties">
            <Param name="HasNS" dataType="float" value="1.0" ucd="stat.probability">
                <Description>Probability that at least one object in the binary has a mass that is less than 3 solar masses</Description>
            </Param>
            <Param name="HasRemnant" dataType="float" value="1.0" ucd="stat.probability">
                <Description>Probability that a nonzero mass was ejected outside the central remnant object</Description>
            </Param>
            <Description>Qualitative properties of the source, conditioned on the assumption that the signal is an astrophysical compact binary merger</Description>
        </Group>
    </What>
    <WhereWhen>
        <ObsDataLocation>
            <ObservatoryLocation id="LIGO Virgo"/>
            <ObservationLocation>
                <AstroCoordSystem id="UTC-FK5-GEO"/>
                <AstroCoords coord_system_id="UTC-FK5-GEO">
                    <Time>
                        <TimeInstant>
                            <ISOTime>2019-02-25T12:56:16.153666</ISOTime>
                        </TimeInstant>
                    </Time>
                </AstroCoords>
            </ObservationLocation>
        </ObsDataLocation>
    </WhereWhen>
    <How>
        <Description>Candidate gravitational wave event identified by low-latency analysis</Description>
        <Description>H1: LIGO Hanford 4 km gravitational wave detector</Description>
        <Description>L1: LIGO Livingston 4 km gravitational wave detector</Description>
    </How>
    <Citations>
        <EventIVORN cite="supersedes">ivo://gwnet/LVC#MS190225m-1-Preliminary</EventIVORN>
        <Description>Initial localization is now available</Description>
    </Citations>
    <Description>Report of a candidate gravitational wave event</Description>
</voe:VOEvent>

"""

"""
LVC parameters description

Packet_Type: The Notice Type number is assigned/used within GCN, eg type=151 is an LVC_INITIAL notice
internal: Indicates whether this event should be distributed to LSC/Virgo members only
GraceID: Identifier in GraceDB
AlertType: VOEvent alert type
HardwareInj: Indicates that this event is a hardware injection if 1, no if 0
OpenAlert: Indicates that this event is an open alert if 1, no if 0
EventPage: Web page for evolving status of this GW candidate
Instruments: List of instruments used in analysis to identify this event
FAR: False alarm rate for GW candidates with this strength or greater
Group: Data analysis working group
Pipeline: Low-latency data analysis pipeline
Search: Specific low-latency search
skymap_fits: Sky Map FITS
BNS: Probability that the source is a binary neutron star merger
NSBH: Probability that the source is a neutron star - black hole merger
BBH: Probability that the source is a binary black hole merger
Terrestrial: Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)
HasNS: Probability that at least one object in the binary has a mass that is less than 3 solar masses
HasRemnant: Probability that a nonzero mass was ejected outside the central remnant object

"""

def test_gbm():

    file_name = 'gbm_test_notices/gbm_200228A.txt'
    with open(file_name) as f:
        payload = f.read()

    payload = payload.encode('UTF-8')
      
    root = fromstring(payload)
    notice_filter.process_gcn(payload, root)

def test_lvc():

    payload = payload_lvc.encode('UTF-8')
    root = fromstring(payload)
    notice_filter.process_gcn(payload, root)


#test_lvc()
test_gbm()