# -*- coding: utf-8 -*-

"""
    GBMTTEFile class was implemented by M. Burgess
    in https://github.com/giacomov/3ML
"""

from __future__ import print_function

import astropy.io.fits as fits
import logging as log
import numpy as np
import os
import re

log.basicConfig(format = u'[%(asctime)s]  %(message)s', level = log.INFO, filename = u'log.txt')


class GBMTTEFile(object):

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


def deg2rad(deg):
     return deg*np.pi/180.0


def rad2deg(rad):
     return rad*180.0/np.pi


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

    cosEps = np.cos(deg2rad(eps))
    sinEps = np.sin(deg2rad(eps))

    cosRA = np.cos(deg2rad(fRA))
    sinRA = np.sin(deg2rad(fRA))
    cosDec = np.cos(deg2rad(fDec))
    sinDec = np.sin(deg2rad(fDec))

    fL = rad2deg(np.arctan2(cosDec * sinRA * cosEps + sinDec * sinEps, cosDec * cosRA))
    fB = rad2deg(np.arcsin(-cosDec * sinRA * sinEps + sinDec * cosEps))
    
    if (fL < 0):
        fL += 360

    return fL, fB


# Create a temporary history file .thr
def print_data(folder, file, bins, mas, bounds, resolution):

    tte = GBMTTEFile(ttefile = folder+file)

    with open(folder+'GRB'+file[13:19]+'_GBM_'+resolution+'ms.thr', 'w') as f:

        print("SrcName: GRB{}".format(file[13:22]), file = f)
        print("T0 = {:.3f} MET".format(tte.trigger_time), file = f)
        print("{:>11} {:>6.1f} {:>6.1f} {:>6.1f}".format('Emin (keV):', tte.emin[bounds[0][0]],
                                      tte.emin[bounds[1][0]], tte.emin[bounds[2][0]]), file = f)
        print("{:>11} {:>6.1f} {:>6.1f} {:>6.1f}".format('Emax (keV):', tte.emax[bounds[0][1]],
                                      tte.emax[bounds[1][1]], tte.emax[bounds[2][1]]), file = f)

        for el in range(len(mas[0])):
            print("{:<11.3f} {:>6} {:>6} {:>6}".format(bins[el], mas[0][el], mas[1][el], mas[2][el]), file = f)

    print('File GRB'+file[13:19]+'_GBM_'+resolution+'ms.thr is created!')


def tte_lightcurve(folder, file, start = -10, stop = 100, dt = 1, channel_start = 0, channel_end = 127):

    tte = GBMTTEFile(ttefile = folder+file)
    bins = np.arange(start, stop, step = dt)
    arrival_times = []

    for i in range(len(tte.energies)):

        if channel_start <= tte.energies[i] <= channel_end:
            arrival_times.append(tte.arrival_times[i] - tte.trigger_time)

    counts, bins = np.histogram(np.array(arrival_times), bins = bins)
    width = np.diff(bins)
    time_bins = np.array(list(zip(bins[:-1], bins[1:])))

    return counts, bins


def temporal_history(folder, file, detectors, resolution, bounds):

    for r in range(len(resolution)):
        all_mas = []

        for d in detectors:
            current_file = file[0:9]+d+file[10:]
            mas = []

            for b in range(len(bounds)):
                counts, bins = tte_lightcurve(folder, current_file, start = resolution[r][0], stop = resolution[r][1],
                              dt = resolution[r][2]/1000., channel_start = bounds[b][0], channel_end = bounds[b][1])

                mas.append([0] * len(counts))
                mas[b] = counts

            all_mas.extend(mas)

        for el in range(len(all_mas[0])):
            for l in range(3, len(all_mas), 3):
                all_mas[0][el] += all_mas[l][el]
                all_mas[1][el] += all_mas[l+1][el]
                all_mas[2][el] += all_mas[l+2][el]

        mas = []

        for i in range(3):
            mas.append(all_mas[i])

        print_data(folder, file, bins, mas, bounds, str(resolution[r][2]))

def get_RA_Dec(folder, file_name):

    RA = None
    Dec = None
    with open(folder+file_name, 'r') as inp:
        text = inp.read()
        m = re.search(r'RA_OBJ\s*=\s*(\d+\.\d+)', text)
        if m:
            RA = float(m.group(1))

        m = re.search(r'DEC_OBJ\s*=\s*([+-]?\d+\.\d+)', text)
        if m:
            Dec = float(m.group(1))

    return RA, Dec

# Reading of detectors
def get_detectors(folder, file_name):

    detectors = []

    if os.path.exists(folder+'detectors.dat'): 

        with open(folder+'detectors.dat', 'r') as det:
            text = det.read()
            text = ''.join(text.split())
            for s in text:
                detectors.append(s)

    else:
        with open(folder+file_name, 'r') as inp, open(folder+'detectors.dat', 'w') as out:
            text = inp.read()
            DET_MASK = re.findall(r'\d{14}', text)
            DET_MASK = DET_MASK[1]
            for el in range(len(DET_MASK) - 2):
                if DET_MASK[el] != '0':
                    if el == 10:
                        detectors.append('a')
                    elif el == 11:
                        detectors.append('b')
                    else:
                        detectors.append(str(el))

            for el in detectors:
                out.write(el+' ')

    return detectors

def tte_to_ascii(folder, file):

    if folder != '':
        folder = folder + '/'

    file_detectors = get_files(folder)
    detectors = get_detectors(folder, file_detectors)
    resolution = [[-1, 1, 2], [-5, 50, 16], [-10, 100, 64], [-20, 150, 256]]
    #resolution = [[-10, 60, 16], [-20, 80, 64], [-20, 100, 256]]
    #resolution = [[-1, 1, 2],]

    GRB_data = get_files(folder, pattern='_FER.txt', switch=1)
    trig_dat = get_files(folder, pattern='glg_trigdat_all_bn', switch=0)

    str_src = ''
    if GRB_data is None and trig_dat is None:
        RA = data_input('RA')
        Dec = data_input('Dec')
        str_src = 'User'
    elif GRB_data is not None:
        RA, Dec = get_coordinates(folder, GRB_data)
        str_src = GRB_data
    elif trig_dat is not None:
        RA, Dec = get_RA_Dec(folder, trig_dat)
        str_src = trig_dat

    print("RA, Dec from {:s}: {:8.3f} {:8.3f}".format(str_src, RA, Dec))
    RA, Dec = equat2eclipt(RA, Dec)

    if Dec >= 0:
        bounds = [[15, 42], [43, 85], [86, 126]]
    else:
        bounds = [[16, 45], [46, 91], [92, 126]]

    temporal_history(folder, file, detectors, resolution, bounds)


def get_files(path, pattern='glg_trigdat_all', switch = 0):

    list_files = os.listdir(path)

    if not len(list_files):
        print("Directory does not exist!")
        exit(0)

    if switch != 0:
        file_folder = list(filter(lambda x: x.endswith(pattern), list_files))

    else:
        file_folder = list(filter(lambda x: x.startswith(pattern), list_files))

    if len(file_folder) != 0:
        print(file_folder)
        return file_folder[0]
    else:
        print("No required file with pattern: {:s}".format(pattern))
        return None

def data_input(x):

    while True:

        try:
            text = "Enter values for " + x +': '
            y = float(input(text))
            return y

        except ValueError:
            print("The number is not correct, please repeat!")


def get_coordinates(folder, file):

    with open(folder+file, 'r') as f:

        grb_ra = 'GRB_RA'
        grb_dec = 'GRB_DEC'

        try:
            for line in f:
                if grb_ra in line:
                    RA = re.findall(r'\S\d+.\d+', line)[0]

                elif grb_dec in line:
                    Dec = re.findall(r'\S\d+.\d+', line)[0]

            return float(RA), float(Dec)

        except:
            print('No data for RA and Dec in '+file+'!')
            RA = data_input('RA')
            Dec = data_input('Dec')
            return RA, Dec


if __name__ == "__main__":

    folder_path = '../GRB20181111_T56534'

    first_tte_file = get_files(folder_path, pattern='glg_tte_n')

    tte_to_ascii(folder_path, first_tte_file)
