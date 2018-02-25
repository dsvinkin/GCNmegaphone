
""" 
Test for notice_filter.py
"""
import gcn
import notice_filter

payload = '''\
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

date_time = '2018-02-10T12:24:38.55' 
payload = payload.format(date_time)
payload = payload.encode('UTF-8')

root = gcn.voeventclient.parse_from_string(payload)
notice_filter.process_gcn(payload, root)