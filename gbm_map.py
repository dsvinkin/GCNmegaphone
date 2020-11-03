
"""
TO check near circular contours. The radii of 1, 2 , and 3 sigma
localizations must scale as r2/r1 and r3/r2

p1 = 3.173105E-1
r1 = sqrt(-2*ln(p1))

p2 =  4.550025E-2
r2 = np.sqrt(-2*np.log(p2))

p3 = 2.699796E-3
r3 = sqrt(-2*ln(p3))

"""
import os
import numpy as np
import healpy as hp

import ligo.skymap.postprocess.contour as contour
from ligo.skymap.io import fits


def get_pos_center(prob):

    # Most probable sky location
    ipix_max = np.argmax(prob)

    npix = len(prob)
    nside = hp.npix2nside(npix)
    theta, phi = hp.pix2ang(nside, ipix_max, nest=True)
    

    ra = np.rad2deg(phi)
    dec = np.rad2deg(0.5 * np.pi - theta)

    return ra, dec

def print_contour(lst_cont, levels, file_name):

    n_lev = len(lst_cont)
    #print(lst_cont)
    #exit()

    f = open(file_name, 'w')
    for i_lev in range(n_lev):

        n_poly = len(lst_cont[i_lev])
        print("\nConf level {:8.3f}\nNumber of polygon: {:d}".format(levels[i_lev], n_poly))
        
        for i_poly in range(n_poly):
            n_vert = len(lst_cont[i_lev][i_poly])
            print("Polygon {:d}: Number of vertices: {:d}".format(i_poly, n_vert))

            ra_prev = lst_cont[i_lev][i_poly][0][0]
            for i_ver in range(n_vert):
                ra = lst_cont[i_lev][i_poly][i_ver][0]
                dec = lst_cont[i_lev][i_poly][i_ver][1]
       
                if np.abs(ra - ra_prev) >=270.0:
                    f.write("-- --\n")

                f.write("{:8.3f} {:8.3f}\n".format(ra, dec))
                ra_prev = ra

            f.write("-- --\n")

    f.close()

def get_contours(path):
    """
    See https://github.com/lpsinger/ligo.skymap/blob/master/ligo/skymap/tool/ligo_skymap_contour.py
    
    """
   
    p_1sigma = 0.682689492137
    p_2sigma = 0.954499736104
    p_3sigma = 0.997300203937
    levels = np.array([p_1sigma, p_2sigma, p_3sigma]) * 100
 
    prob, _ = fits.read_sky_map(path, nest=True)

    # Find credible levels
    i = np.flipud(np.argsort(prob))
    cumsum = np.cumsum(prob[i])
    cls = np.empty_like(prob)
    cls[i] = cumsum * 100
    
    lst_cont = contour(cls, levels, degrees=True, nest=True, simplify=False)
    print(levels, len(lst_cont[0]))
    #exit()

    ra, dec = get_pos_center(prob)
    print("Max prob position: {:.3f} {:.3f}".format(ra, dec))

    lst_cont = [[[[ra, dec]]]] + lst_cont # [lev[polys[points[ra, dec]]]]
    levels = np.append([0], levels)

    file_name = os.path.splitext(path)[0] + '_cont.txt'
    print_contour(lst_cont, levels, file_name)

if __name__ == '__main__':

    path = '../GRB20201103_T22389/glg_healpix_all_bn201103259_v00.fit'
    get_contours(path)