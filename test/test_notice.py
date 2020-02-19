import sys
sys.path.append('../')

from lxml import etree
#from lxml.etree import fromstring
import notice_filter


fermi_gnd_pos = """\
<?xml version = '1.0' encoding = 'UTF-8'?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/Fermi#GBM_Gnd_Pos_2020-02-19T09:54:14.68_603798859_59-498"
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
    <Date>2020-02-19T09:54:56</Date>
    <Description>This VOEvent message was created with GCN VOE version: 1.46 12jan20</Description>
  </Who>
  <What>
    <Param name="Packet_Type"           value="112" />
    <Param name="Pkt_Ser_Num"           value="5" />
    <Param name="TrigID"                value="603798859" ucd="meta.id" />
    <Param name="Sequence_Num"          value="59" ucd="meta.id.part" />
    <Param name="Burst_TJD"             value="18898" unit="days" ucd="time" />
    <Param name="Burst_SOD"             value="35654.68" unit="sec" ucd="time" />
    <Param name="Burst_Inten"           value="0" unit="cts" ucd="phot.count" />
    <Param name="Data_Integ"            value="4.096" unit="sec" ucd="time.interval" />
    <Param name="Burst_Signif"          value="21.30" unit="sigma" ucd="stat.snr" />
    <Param name="Phi"                   value="331.00" unit="deg" ucd="pos.az.azi" />
    <Param name="Theta"                 value="44.00" unit="deg" ucd="pos.az.zd" />
    <Param name="Algorithm"             value="4173" unit="dn" />
    <Param name="Lo_Energy"             value="44032" unit="keV"  />
    <Param name="Hi_Energy"             value="279965" unit="keV"  />
    <Param name="SC_Geo_X"              value="21940"   />
    <Param name="SC_Geo_Y"              value="-97124"   />
    <Param name="SC_Geo_Z"              value="47552"   />
    <Param name="Trigger_ID"            value="0x1" />
    <Param name="Misc_flags"            value="0x40000000" />
    <Group name="Trigger_ID" >
      <Param name="Def_NOT_a_GRB"         value="false" />
      <Param name="Target_in_Blk_Catalog" value="false" />
      <Param name="Spatial_Prox_Match"    value="false" />
      <Param name="Long_short"            value="unknown" />
      <Param name="Temporal_Prox_Match"   value="false" />
      <Param name="Test_Submission"       value="false" />
    </Group>
    <Group name="Misc_Flags" >
      <Param name="Values_Out_of_Range"   value="false" />
      <Param name="Flt_Generated"         value="false" />
      <Param name="Gnd_Generated"         value="true" />
      <Param name="CRC_Error"             value="false" />
    </Group>
    <Param name="LightCurve_URL" value="http://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2020/bn200219413/quicklook/glg_lc_medres34_bn200219413.gif" ucd="meta.ref.url" >
      <Description> The LC_URL file will not be created/available until ~15 min after the trigger.</Description>
    </Param>
    <Param name="LocationMap_URL" value="http://gcn.gsfc.nasa.gov/notices_f/gbm_gnd_loc_map_603798859.fits" ucd="meta.ref.url" >
      <Description>The LocationMap_URL file will not be created/available until ~4 min after the notice.</Description>
    </Param>
    <Param name="Coords_Type"           value="1" unit="dn" />
    <Param name="Coords_String"         value="source_object" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="332.29" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="-11.40" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="39.25" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="2.27" unit="hr" />
      <Param name="Moon_RA"       value="283.39" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="-23.34" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="35.09" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="16.55" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="47.62" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="-9.40" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="302.11" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="28.88" unit="deg" ucd="pos.ecliptic.lat" />
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
              <ISOTime>2020-02-19T09:54:14.68</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>298.0700</C1>
              <C2>8.5200</C2>
            </Value2>
            <Error2Radius>4.7000</Error2Radius>
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
  <Why importance="0.95">
    <Inference probability="0.5">
      <Concept>process.variation.burst;em.gamma</Concept>
    </Inference>
  </Why>
  <Citations>
    <EventIVORN cite="followup">ivo://nasa.gsfc.gcn/Fermi#GBM_Alert_2020-02-19T09:54:14.68_603798859_1-493</EventIVORN>
    <Description>This is an updated position to the original trigger.</Description>
  </Citations>
  <Description>
  </Description>
</voe:VOEvent>"""

fermi_fin_pos = """\
<?xml version = '1.0' encoding = 'UTF-8'?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/Fermi#GBM_Fin_Pos2020-02-19T09:54:14.68_603798859_0-524"
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
    <Date>2020-02-19T10:03:34</Date>
    <Description>This VOEvent message was created with GCN VOE version: 1.46 12jan20</Description>
  </Who>
  <What>
    <Param name="Packet_Type"    value="115" />
    <Param name="Pkt_Ser_Num"    value="5" />
    <Param name="TrigID"         value="603798859" ucd="meta.id" />
    <Param name="Sequence_Num"   value="0" ucd="meta.id.part" />
    <Param name="Burst_TJD"      value="18898" unit="days" ucd="time" />
    <Param name="Burst_SOD"      value="35654.68" unit="sec" ucd="time" />
    <Param name="Burst_Inten"    value="0" unit="cts" ucd="phot.count" />
    <Param name="Data_Integ"     value="0.000" unit="sec" ucd="time.interval" />
    <Param name="Burst_Signif"   value="0.00" unit="sigma" ucd="stat.snr" />
    <Param name="Phi"            value="332.00" unit="deg" ucd="pos.az.azi" />
    <Param name="Theta"          value="46.00" unit="deg" ucd="pos.az.zd" />
    <Param name="Algorithm"      value="41731" unit="dn" />
    <Param name="Lo_Energy"      value="44032" unit="keV"  />
    <Param name="Hi_Energy"      value="279965" unit="keV"  />
    <Param name="Trigger_ID"     value="0x8000001" />
    <Param name="Misc_flags"     value="0x40000000" />
    <Group name="Trigger_ID" >
      <Param name="Def_NOT_a_GRB"         value="false" />
      <Param name="Target_in_Blk_Catalog" value="false" />
      <Param name="Human_generated"       value="true" />
      <Param name="Robo_generated"        value="false" />
      <Param name="LAT_FoV"               value="true" />
      <Param name="Long_short"            value="Long" />
      <Param name="Spatial_Prox_Match"    value="false" />
      <Param name="Temporal_Prox_Match"   value="false" />
      <Param name="Test_Submission"       value="false" />
    </Group>
    <Group name="Misc_Flags" >
      <Param name="Values_Out_of_Range"   value="false" />
      <Param name="Flt_Generated"         value="false" />
      <Param name="Gnd_Generated"         value="true" />
      <Param name="CRC_Error"             value="false" />
    </Group>
    <Param name="LightCurve_URL" value="http://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2020/bn200219413/quicklook/glg_lc_medres34_bn200219413.gif" ucd="meta.ref.url" />
    <Param name="LocationMap_URL" value="http://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2020/bn200219413/quicklook/glg_locplot_all_bn200219413.png" ucd="meta.ref.url" />
    <Param name="Coords_Type"    value="1" unit="dn" />
    <Param name="Coords_String"  value="source_object" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="332.30" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="-11.39" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="37.42" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="2.19" unit="hr" />
      <Param name="Moon_RA"       value="283.47" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="-23.34" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="33.83" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="16.50" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="46.49" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="-11.24" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="302.81" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="26.83" unit="deg" ucd="pos.ecliptic.lat" />
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
              <ISOTime>2020-02-19T09:54:14.68</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>299.1300</C1>
              <C2>6.6500</C2>
            </Value2>
            <Error2Radius>3.9800</Error2Radius>
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
  <Why importance="0.95">
    <Inference probability="1.0">
      <Concept>process.variation.burst;em.gamma</Concept>
    </Inference>
  </Why>
  <Citations>
    <EventIVORN cite="followup">ivo://nasa.gsfc.gcn/Fermi#GBM_Alert_2020-02-19T09:54:14.68_603798859_1-493</EventIVORN>
    <Description>This is an updated position to the original trigger.</Description>
  </Citations>
  <Description>
  </Description>
</voe:VOEvent>"""


def xstr(s):
    if s is None:
        return 'None'
    return str(s)

def main():

    payload = fermi_gnd_pos
    payload = payload.encode('UTF-8')
    data = notice_filter.notice(payload)

    for key in sorted(notice_filter.notice_parameters.keys()):
        name = notice_filter.notice_parameters[key]
        print( "{:25s} {:25s} {:s}".format(key, name, xstr(data.get_value(key))) )

if __name__ == "__main__":
    main()
