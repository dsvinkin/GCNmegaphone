# -*- coding: utf-8 -*-

from __future__ import print_function

import logging as log
import numpy as np
import os
import re

from astropy.io import fits

import clock
import path_utils
import config
info = config.read_config('config.yaml')

import setlog
setlog.set_log()


def equat2eclipt(fRA, fDec):
    """
    Function converts equatorial coordinate to ecliptical.
    fRA - Right ascension, deg
    fDec - declination, deg
    fL - ecliptic longitude, deg
    fB - ecliptic latitude, deg

    expression were taken from "Physics of Space, a little encyclopaedia" page 316
    """

    # inclination angle of the Earth spin axes to the ecliptic plane
    eps = 23.43929 # degrees = 23o27' 23.43929

    cosEps = np.cos(np.deg2rad(eps))
    sinEps = np.sin(np.deg2rad(eps))

    cosRA = np.cos(np.deg2rad(fRA))
    sinRA = np.sin(np.deg2rad(fRA))
    cosDec = np.cos(np.deg2rad(fDec))
    sinDec = np.sin(np.deg2rad(fDec))

    fL = np.rad2deg(np.arctan2(cosDec * sinRA * cosEps + sinDec * sinEps, cosDec * cosRA))
    fB = np.rad2deg(np.arcsin(-cosDec * sinRA * sinEps + sinDec * cosEps))
    
    if (fL < 0):
        fL += 360

    return fL, fB


def get_RA_Dec_from_log(path, file_name):

    with open(os.path.join(path, file_name), 'r') as f:
        lines = f.read().split('\n')

    str_ = " ".join(lines)
    lst_m = re.findall(r'GRB_RA\s*(\d+\.\d+)\s*GRB_DEC\s*([+-]?\d+\.\d+)', str_)
    
    if len(lst_m) == 0:
        raise ValueError('No localization info is found in {:s}!'.format(file_name))

    return float(lst_m[-1][0]), float(lst_m[-1][1])


def get_RA_Dec(folder, file_name):

    hdul = fits.open("{:s}/{:s}".format(folder, file_name))
    RA = hdul[0].header['RA_OBJ']
    Dec = hdul[0].header['DEC_OBJ']

    return RA, Dec


class GBMTTEFile(object):
    """
     GBMTTEFile class was adopted from threeML https://github.com/giacomov/3ML
    """

    def __init__(self, ttefile):
        """
        A simple class for opening and easily accessing Fermi GBM
        TTE Files.
        :param ttefile: The filename of the TTE file to be stored
        """

        tte = fits.open(ttefile)

        self._events = tte['EVENTS'].data['TIME']
        self._pha = tte['EVENTS'].data['PHA']

        try:
            self._trigger_time = tte['PRIMARY'].header['TRIGTIME']

        except:

            # For continuous data
            warnings.warn("There is no trigger time in the TTE file. Must be set manually or using MET relative times.")

            self._trigger_time = 0

        self._src_name = tte['PRIMARY'].header['OBJECT']

        self._start_events = tte['PRIMARY'].header['TSTART']
        self._stop_events = tte['PRIMARY'].header['TSTOP']

        self._utc_start = tte['PRIMARY'].header['DATE-OBS']
        self._utc_stop = tte['PRIMARY'].header['DATE-END']

        self._n_channels = tte['EBOUNDS'].header['NAXIS2']

        self._det_name = "%s_%s" % (tte['PRIMARY'].header['INSTRUME'], tte['PRIMARY'].header['DETNAM'])

        self._telescope = tte['PRIMARY'].header['TELESCOP']

        self._emin = tte['EBOUNDS'].data['E_MIN']
        self._emax = tte['EBOUNDS'].data['E_MAX']

        self._calculate_deadtime()

    @property
    def trigger_time(self):

        return self._trigger_time

    @trigger_time.setter
    def trigger_time(self, val):

        assert self._start_events <= val <= self._stop_events, "Trigger time must be within the interval (%f,%f)" % (
            self._start_events, self._stop_events)

        self._trigger_time = val

    @property
    def tstart(self):
        return self._start_events

    @property
    def tstop(self):
        return self._stop_events

    @property
    def arrival_times(self):
        return self._events

    @property
    def n_channels(self):
        return self._n_channels

    @property
    def energies(self):
        return self._pha

    @property
    def mission(self):
        """
        Return the name of the mission
        :return:
        """
        return self._telescope

    @property
    def det_name(self):
        """
        Return the name of the instrument and detector
        :return:
        """
        return self._det_name

    @property
    def emin(self):
        return self._emin

    @property
    def emax(self):
        return self._emax

    @property
    def deadtime(self):
        return self._deadtime

    def _calculate_deadtime(self):
        """
        Computes an array of deadtimes following the perscription of Meegan et al. (2009).
        The array can be summed over to obtain the total dead time
        """
        self._deadtime = np.zeros_like(self._events)
        overflow_mask = self._pha == self._n_channels  # specific to gbm! should work for CTTE

        # From Meegan et al. (2009)
        # Dead time for overflow (note, overflow sometimes changes)
        self._deadtime[overflow_mask] = 10.E-6  # s

        # Normal dead time
        self._deadtime[~overflow_mask] = 2.E-6  # s

    def get_info(self, bounds):
        """
        Make header for ascii lc file
        """
    
        date_utc = clock.fermi2utc(self._trigger_time)
        frac_s = date_utc.microsecond/1e6
        time2sec = date_utc.hour*3600 + date_utc.minute*60 + date_utc.second
        sod = time2sec + frac_s
        date = date_utc.strftime("%Y%m%d")
    
        str_info = "SrcName: {:s}\nT0 = {:.3f} MET\n".format(self._src_name, self._trigger_time)
        str_info += "{:>11s}".format('Emin (keV):')
        for i in range(len(bounds)):
            str_info += "{:>6.1f}".format(self._emin[bounds[i][0]])
    
        str_info +="\n{:>11s}".format('Emax (keV):')
        for i in range(len(bounds)):
            str_info +="{:>6.1f}".format(self._emax[bounds[i][1]])
    
        return str_info, date, sod

    def get_tte_lc(self, start=-10, stop=100, dt=1, channel_start=0, channel_end=127):
        """
        Get single channel lightcurve from TTE
        """
        
        bins = np.arange(start, stop+1.5*dt, step=dt)
        interval_deadtime = np.zeros_like(bins[1:])
        interval_corr = np.zeros_like(bins[1:])
        
        """
        for i, (t_beg, t_end) in enumerate(zip(bins[:-1]+self._trigger_time, bins[1:]+self._trigger_time)):

            mask = np.logical_and(t_beg <= self._events, self._events<=t_end)
            interval_deadtime[i] = (self._deadtime[mask]).sum()
            interval_corr[i] = 1.0 / (1.0 - interval_deadtime[i]/(t_end-t_beg))
            #print("{:d} {:.3f} {:.1e}".format(i, t_beg-self._trigger_time,  interval_deadtime[i]))
        """

        arrival_times = []
        for i in range(len(self._pha)):
            if self._pha[i] >= channel_start and self._pha[i] <= channel_end:
                arrival_times.append(self._events[i] - self._trigger_time)
        
        counts, bins = np.histogram(np.array(arrival_times), bins=bins)
        #time_bins = np.array(list(zip(bins[:-1], bins[1:])))
        
        #return counts*interval_corr, bins[:-1]
        return counts, bins[:-1]


    def get_multichannel_lc(self, resolution, bounds):
        """
        Get multi-channel lightcurve.
    
        bounds - list of low and hi channel tuples
        """
    
        lst_counts = []
        lst_bins = [] # for consistency with counts
        for b in range(len(bounds)):
            counts, bins = self.get_tte_lc(start=resolution[0], stop=resolution[1], dt=resolution[2]/1000., 
                     channel_start=bounds[b][0], channel_end=bounds[b][1])
    
            lst_counts.append(counts)
            lst_bins.append(bins)
    
        return lst_bins[0], np.vstack(lst_counts)


class light_curve:

    def __init__(self):
        self.lst_det = []
        self.lst_res = []
        self.dict_lc = {}
        self.dict_info = {}

    def add_info(self, det, str_info):
        self.dict_info[det] = str_info

    def add_lc(self, det, res, bins, counts):

        #print("Appending: ", det, res)
        if (det, res) in self.dict_lc.keys():
            print("Duplicate det and res: ", det, res)

        self.lst_det.append(det)
        self.lst_res.append(res)
        self.dict_lc[(det,res)] = (bins, counts)

    def get_sum_det_lc(self, res):
        set_det = set(self.lst_det)

        bins = self.dict_lc[(self.lst_det[0], res)][0]
        lc_size_res = len(bins)
        n_bounds = len(self.dict_lc[(self.lst_det[0], res)][1])
        lc_res = np.zeros((n_bounds, lc_size_res),dtype=int)

        for det in set_det:
            #print(res, det)
            #print(lc_res)
            #print(self.dict_lc[(det, res)][1])
            lc_res = lc_res + self.dict_lc[(det, res)][1]

        return np.array(bins), lc_res, self.dict_info[self.lst_det[0]]


# Reading of detectors
def get_detectors(path, file_name):

    detectors = []

    det_file = os.path.join(path,'detectors.dat')
    fits_file = os.path.join(path, file_name)

    if os.path.exists(det_file): 

        with open(det_file, 'r') as det:
            text = det.read()
            text = ''.join(text.split())
            for s in text:
                detectors.append(s)

    else:
        hdul = fits.open(fits_file)
        DET_MASK = hdul[0].header['DET_MASK']

        for el in range(len(DET_MASK) - 2):
            if DET_MASK[el] == '0':
                continue

            if el == 10:
                detectors.append('a')
            elif el == 11:
                detectors.append('b')
            else:
                detectors.append(str(el))
 

        with open(det_file, 'w') as out:        
            for el in detectors:
                out.write(el+' ')

    print("Detectors: ", detectors)
    return detectors

def get_resolution():
    """
    Make list of desired lightcurve resolutions (in ms) and start, end times (relative to the trigger time).
    resolution = [[t_start_1, t_end_1, res_1],...]
    """

    resolution = [[-1, 10, 2], [-5, 50, 16], [-10, 100, 64], [-20, 150, 256]]
    #resolution = [ [-10, 50, 16], [-10, 100, 64], [-20, 400, 256]]
    #resolution = [[126,134,2], [50, 150, 16], [40, 160, 64], [-20, 160, 256]]
    #resolution = [[5, 10, 2]]

    return resolution

def get_channel_bounds(Dec):
    """
    Make three channel groups approximately corresponding Konus-Wind S1 and S2 channel bounderies.
    """

    if Dec >= 0:
        bounds = [[15, 42], [43, 85], [86, 126]]
    else:
        bounds = [[16, 45], [46, 91], [92, 126]]

    return bounds


def print_data(path, date, sod, res, bins, counts, str_info):
    """
    Create a lightcurve file
    """

    #file_name = os.path.join(path, "GRB{:s}_GBM_{:d}ms_dt.thr".format(date[2:], int(res)))
    file_name = os.path.join(path, "GRB{:s}_GBM_{:d}ms.thr".format(date[2:], int(res)))

    with open(file_name, 'w') as f:

        f.write("{:s}".format(str_info))

        for i_time in range(len(bins)):
            f.write("\n{:<11.5f}".format(bins[i_time]))
            for i_ch in range(counts.shape[0]):
                f.write(" {:>5d}".format(counts[i_ch,i_time]))
                #f.write(" {:9.3f}".format(counts[i_ch,i_time]))

    print('File {:s} has been created.'.format(file_name))

def get_trigger_name(trig_dat):

    m = re.search(r'(bn\d{9})', trig_dat)
    return m.group(1)

def get_tte_ver(lst_tte):

    lst_ver = []
    for s in lst_tte:
        lst_ver.append(s[-6:-4])

    ver = sorted(list(set(lst_ver)))[-1]
    #print("TTE ver: ", ver)
    return ver

def tte_to_ascii(path):

    trig_dat = path_utils.get_files(path, pattern='glg_trigdat_all_bn', prefix=True, all=False)
    lst_tte = path_utils.get_files(path, pattern='glg_tte_n', prefix=True, all=True)
    tte_ver = get_tte_ver(lst_tte)
    trigger_name = get_trigger_name(trig_dat)
    GRB_data = path_utils.get_files(path, pattern='_FER.txt', prefix=False, all=False)

    detectors = get_detectors(path, trig_dat)
    resolution = get_resolution()

    if GRB_data is not None:
        RA, Dec = get_RA_Dec_from_log(path, GRB_data)
        str_src = GRB_data
    elif trig_dat is not None:
        RA, Dec = get_RA_Dec(path, trig_dat)
        str_src = trig_dat
    else:
        raise ValueError('No localization info is available!')
        

    print("RA, Dec  are from {:s}: {:8.3f} {:8.3f}".format(str_src, RA, Dec))
    RA, Dec = equat2eclipt(RA, Dec)

    e_bounds = get_channel_bounds(Dec)


    lc = light_curve()
    for det in detectors:
        tte_file = os.path.join(path, "glg_tte_n{:s}_{:s}_v{:s}.fit".format(det, trigger_name, tte_ver))
        tte = GBMTTEFile(ttefile=tte_file)

        str_info, date, sod = tte.get_info(e_bounds)

        lc.add_info(det, str_info)
        for res in resolution:
            bins, counts = tte.get_multichannel_lc(res, e_bounds)
            #print("Det, res: ", det, res[2])
            lc.add_lc(det, res[2], bins, counts)
    
    for res in resolution:
        bins, counts, str_info = lc.get_sum_det_lc(res[2])
        print_data(path, date, sod, res[2], bins, counts, str_info)


if __name__ == "__main__":

    path = '../GRB20201016_T01669'

    tte_to_ascii(path)
