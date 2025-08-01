
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
import meander


def get_most_prob_loc(probs):

    ipix_max = np.argmax(probs)
    nside = hp.pixelfunc.get_nside(probs)

    theta, phi = hp.pix2ang(nside, ipix_max)
    ra = np.rad2deg(phi)
    dec = np.rad2deg(0.5 * np.pi - theta)
    return ra, dec

def compute_contours(proportions, samples):
    r''' Plot containment contour around desired level.
    E.g 90% containment of a PDF on a healpix map

    Parameters:
    -----------
    proportions: list
        list of containment level to make contours for.
        E.g [0.68,0.9]
    samples: array
        array of values read in from healpix map
        E.g samples = hp.read_map(file)
    Returns:
    --------
    theta_list: list
        List of arrays containing theta values for desired contours
    phi_list: list
        List of arrays containing phi values for desired contours
    '''

    levels = []
    sorted_samples = list(reversed(list(sorted(samples))))
    nside = hp.pixelfunc.get_nside(samples)
    sample_points = np.array(hp.pix2ang(nside,np.arange(len(samples)))).T
    for proportion in proportions:
        level_index = (np.cumsum(sorted_samples) > proportion).tolist().index(True)
        level = (sorted_samples[level_index] + (sorted_samples[level_index+1] if level_index+1 < len(samples) else 0)) / 2.0
        levels.append(level)
    contours_by_level = meander.spherical_contours(sample_points, samples, levels)

    theta_list = []; phi_list=[]
    for contours in contours_by_level:
        for contour in contours:
            theta, phi = contour.T
            phi[phi<0] += 2.0*np.pi
            theta_list.append(theta)
            phi_list.append(phi)

    return theta_list, phi_list

def print_contours(phi_contour, theta_contour, ra, dec, file_name):

    with open(file_name, 'w') as f:
        f.write("RA   Dec\n")
        f.write("{:8.3f}  {:8.3f}\n--  --\n".format(ra, dec))

        for arr_phi, arr_theta in zip(phi_contour, theta_contour):
            ra = np.rad2deg(arr_phi)
            dec = 90 - np.rad2deg(arr_theta)
            for i in range(ra.size):
                f.write("{:8.3f}  {:8.3f}\n".format(ra[i], dec[i]))

            f.write("--  --\n")

def get_contours(path):
    """
        
    """
   
    p_1sigma = 0.682689492137
    p_2sigma = 0.954499736104
    p_3sigma = 0.997300203937
    levels = np.array([p_1sigma, p_2sigma, p_3sigma])
 
    probs = hp.read_map(path)

    ra, dec = get_most_prob_loc(probs)
    print("Max prob position: {:.3f} {:.3f}".format(ra, dec))

    theta_contour, phi_contour = compute_contours(levels, probs)

    file_name = os.path.splitext(path)[0] + '_cont.txt'
    print_contours(phi_contour, theta_contour, ra, dec, file_name)

if __name__ == '__main__':

    path = '../GRB20250620_T58029/glg_healpix_all_bn250620672_v00.fit'
    get_contours(path)