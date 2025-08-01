# -*- coding: utf-8 -*-

"""
Approximate channel boundaries from ctime
 CHANNEL E_MIN  E_MAX
  none   keV    keV
     0   4      12
     1   12     26
     2   26     50
     3   50     102
     4   102    290
     5   290    542
     6   542    1000
     7   1000   2000

TTE to ctime channel correspondence
TRIGDAT TTE
CHANNEL CHANNEL
     0   0-7
     1   8-19
     2   20-32
     3   33-50
     4   51-84
     5   85-105
     6   106-126
     7   127-127

"""

import datetime
import os
import re

import numpy as np

import astropy
import astropy.io.fits as fits
from astropy.time import Time

import clock

class trig_dat:

    n_det = 12 # number of detectors
    N_chan = 8 # number of channels 
    lst_res = [64, 256, 1024, 8192] # integer ms

    e_bounds = ((4, 12), (12, 26), (26, 50), (50, 102), (102, 290), 
             (290, 542), (542, 1000), (1000, 2000)) # approximate boundaries keV

    i_e_min = 4 # min channel index 
    i_e_max = 6 # max channel index 

    def __init__(self, fits_name):

        self.fits_name = fits_name

        self.hdu_list = fits.open(fits_name)
        
        self.trig_time = self.hdu_list['PRIMARY'].header['TRIGTIME']
        self.det_mask = self.hdu_list['PRIMARY'].header['DET_MASK']
    
        self.ti = self.hdu_list['EVNTRATE'].data['TIME']
        self.tf = self.hdu_list['EVNTRATE'].data['ENDTIME']
        self.rate = self.hdu_list['EVNTRATE'].data['RATE'] / 1.024

        self.size = self.ti.size

        self.detectors = self.get_det_num(self.det_mask)

        self.date, self.date_ipn, self.sod, self.time_info = self.get_date_time()

        self.e_min = self.e_bounds[self.i_e_min][0] # keV
        self.e_max = self.e_bounds[self.i_e_max][1] # keV

    def show_info(self,):

        print("FITS info:")
        self.hdu_list.info()
        print("EVNTRATE shape:", self.hdu_list['EVNTRATE'].header['TDIM5'])
        print("TIME shape: ", self.ti.shape)
        print("RATE shape: ", self.rate.shape)
        print("Triggered detectors:", self.detectors)

        print("Trigger info:\n{:s}".format(self.time_info))      
        
    def get_date_time(self):

        date_utc = clock.fermi2utc(self.trig_time)
        frac_s = date_utc.microsecond/1e6
        time2sec = date_utc.hour*3600 + date_utc.minute*60 + date_utc.second
        sod = time2sec + frac_s
        date = date_utc.strftime("%Y%m%d")
        date_ipn = date_utc.strftime("%d/%m/%y")

        full_info = 'TRIGTIME={:10.4f}'.format(self.trig_time) + '\n'
        full_info += date_utc.strftime("%Y-%m-%d %H:%M:%S.%f") + '\n'
        full_info += date_utc.strftime("%Y%m%d")+" {:9.4f}".format(time2sec+frac_s)

        return date, date_ipn, sod, full_info

    def get_det_num(self, det_mask):

        lst_det =[i for i in range(len(det_mask)) if det_mask[i] == '1']
        return lst_det

    def get_bg_rate(self, ti, tf, rate): # TODO: test

        ti_bg = -50.0
        tf_bg = -10.0

        arr_dt = self.tf - self.ti
        arr_bool = np.around(arr_dt*1000) == self.lst_res[-1]
        arr_bool = np.logical_and(arr_bool, ti-self.trig_time >= ti_bg)
        arr_bool = np.logical_and(arr_bool, tf-self.trig_time <= tf_bg)

        bg_rate = np.mean(rate[arr_bool])
        return bg_rate        

    def _test_rate(self, arr_dt, rate):

        arr_bool = np.around(arr_dt*1000) == 64
        rate = np.around(rate[arr_bool, :, :]*0.064).astype(int)
        print(rate)
        rate = np.sum(rate[:, :, self.i_e_min:self.i_e_max+1], axis=2)
        print(rate)
        print(rate[:, self.detectors])
        print(np.sum(rate[:, self.detectors], axis=1))
        exit()

    def print_thr(self, path, lst_det=None):
 
        if lst_det:
            self.detectors = lst_det

        arr_dt = self.tf - self.ti
        rate = np.reshape(self.rate, (self.size, 14, 8))
        
        # test block
        #test = True
        test = False
        if test:
            self._test_rate(arr_dt, rate)

        rate = np.sum(rate[:, :, self.i_e_min:self.i_e_max+1], axis=2)
        rate = np.sum(rate[:, self.detectors], axis=1)
        
        bg_rate = self.get_bg_rate(self.ti, self.tf, rate)

        lst_names = self.get_thr_names(self.lst_res)
        str_header = "'Fermi-GBM '  '{:s}'  {:8.3f}\n".format(self.date_ipn, self.sod)
        str_header += "{:.1f} {:6.1f}\n".format(self.e_min, self.e_max)

        for name, res in zip(lst_names, self.lst_res):
            res_s = res/1000.0
            with open(os.path.join(path, name), 'w') as f:
                str_h = str_header + "{:.1f} {:5.3f}\n".format(bg_rate*res_s, res_s) 
                f.write(str_h)
                for i in range(self.ti.size):
                    if(np.around(arr_dt[i]*1000) != res):
                        continue
                    #f.write("{:8.3f} {:8.3f} {:8.1f}\n".format(self.ti[i]-self.trig_time, arr_dt[i], rate[i]*res_s))
                    f.write("{:8.3f} {:8.1f}\n".format(self.ti[i]-self.trig_time, rate[i]*res_s))


    def get_thr_names(self, lst_res):

        return ["gbm_tdat_{:s}_{:05d}_{:d}ms.thr".format(self.date, int(self.sod), res) for res in lst_res]

def trigdat2ascii(fits_name):

    t_dat = trig_dat(fits_name)
    t_dat.print_thr(os.path.dirname(fits_name))

if __name__ == '__main__':
    """
    10000100010000
    0123456789ab
    """

    path = '../GRB20220426_T24591' 
    trigger_name = 'bn220426285'
    lst_det = [0,1,2,5,10]
    ver ='01'


    fits_name = os.path.join(path, "glg_trigdat_all_{:s}_v{:s}.fit".format(trigger_name, ver))
    t_dat = trig_dat(fits_name)
    t_dat.show_info()
    t_dat.print_thr(path, lst_det)
