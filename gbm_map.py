
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

import contour

def print_contour(lst_cont, levels, file):

    n_lev = len(lst_cont)
    for i_lev in range(n_lev):

        n_poly = len(lst_cont[i_lev])
        #file.write("Conf level {:8.3f}\nNumber of polygon: {:d}\n".format(levels[i_lev], n_poly))
        file.write("-- --\n")
        
        for i_poly in range(n_poly):
            n_vert = len(lst_cont[i_lev][i_poly])
            #file.write("Number of vertices: {:d}\n".format(n_vert))
            file.write("-- --\n")
            for i_ver in range(n_vert):
                file.write("{:8.3f} {:8.3f}\n".format(lst_cont[i_lev][i_poly][i_ver][0], lst_cont[i_lev][i_poly][i_ver][1]))

def get_area(hpx, prob):
   print ("Calculate sky area for given prob.")
   arr_idx = None
   for i in range(8000, len(hpx)):
       idx = hpx.argsort()[-i:][::-1]
       prob_curr = hpx[idx].sum()
       #print idx, prob_curr
       if(prob<prob_curr):
           arr_idx = idx
           break

   if arr_idx is None:
       print ("Fail")
       return None

   npix = len(hpx)
   sky_area = 4 * 180**2 / np.pi
   pix_area = sky_area / npix 
   
   
   print(pix_area, len(arr_idx))
   print("Sky area:", pix_area * len(arr_idx))
   return pix_area * len(arr_idx)

def get_contours(path):
    """
    NSIDE = 128
    ORDERING = NESTED in fits file
    INDXSCHM = IMPLICIT
    Ordering converted to RING

    
    """
   
    p_1sigma = 0.682689492137
    p_2sigma = 0.954499736104
    p_3sigma = 0.997300203937
    levels = (1-p_1sigma, 1-p_2sigma, 1-p_3sigma)
    #levels = (1-p_1sigma, 1-p_2sigma)
    

    data = hp.read_map(path, field=1)
    
    print(data)
    print(np.sum(data))

    npix = len(data)
    sky_area = 4 * 180**2 / np.pi
    print (npix, sky_area, sky_area / npix)

    #hpx = hp.read_map(file_name, field=0)
    #get_area(hpx, p_2sigma)
    #exit()
    
    #lst_cont = contour.contour(data, levels, nest=False, degrees=True, simplify=True)
    lst_cont = contour.contour(data, levels, nest=False, degrees=True)

    file_name = os.path.splitext(path)[0] + '_cont.txt'
    with open(file_name, 'w') as file:
        print_contour(lst_cont, levels, file)

if __name__ == '__main__':

    path = '../GRB20200224_T35924/glg_healpix_all_bn200224416_v00.fit'
    get_contours(path)