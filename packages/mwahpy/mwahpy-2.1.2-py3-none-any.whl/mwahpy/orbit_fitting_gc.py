'''
This is a self-contained orbit fitting routine.

This orbit fitter is unique compared to other common orbit fitters in that it
uses a galactocentric generalized plane coordinate system when fitting data
'''

#TODO: Allow different coordinate systems input
#TODO: Allow vlos/vgsr input for optimization

import numpy as np
import scipy as sc
import scipy.optimize as scopt
import matplotlib.pyplot as plt

from astropy import units as u
from astropy.coordinates import SkyCoord

import galpy
from galpy.orbit import Orbit

from .coords import get_plane_normal, plane_OLS, cart_to_lambet, gal_to_lambet_galcentric
from .flags import verbose
from .pot import mwahpy_default_pot

'''
================================================================================
 FLAGS
================================================================================
'''

#-------------------------------------------------------------------------------
#DO NOT TOUCH
#Any routine meant to be used by an end user will configure this from input data
vx_flag = 0
vy_flag = 0
vz_flag = 0
vgsr_flag = 0
#-------------------------------------------------------------------------------

'''
================================================================================
 PARAMETERS FOR OPTIMIZATION
================================================================================
'''
t_length = 0.5 #Gyr
resolution = 1000
ts = np.linspace(0, t_length, num=resolution)*u.Gyr

deg_sep_pun = 1000 #multiplier for every degree that the lambda fitting function is off
#this can be tweaked based on how many degrees of freedom you have - fewer DOF
#means punishment can/should be smaller

loop_pun = 10000 #punishment for every time that the orbit has to loop around in Lam

'''
================================================================================
 CLASSES
================================================================================
'''

class OrbitData():
    #all of these parameters can be np.arrays of floats
    def __init__(self, l, b, d, vx, vy, vz, vgsr, b_err, d_err, vx_err, vy_err, vz_err, vgsr_err):
        self.l = l
        self.b = b
        self.d = d #heliocentric distance
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.vgsr = vgsr

        self.b_err = b_err
        self.d_err = d_err
        self.vx_err = vx_err
        self.vy_err = vy_err
        self.vz_err = vz_err
        self.vgsr_err = vgsr_err

        self.x = self.d*np.cos(self.l*np.pi/180)*np.cos(self.b*np.pi/180) - 8
        self.y = self.d*np.sin(self.l*np.pi/180)*np.cos(self.b*np.pi/180)
        self.z = self.d*np.sin(self.b*np.pi/180)

        self.r = (self.x**2 + self.y**2 + self.z**2)**0.5

    def calc_lam_bet(self, normal, point):
        #normal: the normal vector to the plane of the Great Circle we are estimating for the orbit
        #point: parameter for the axis generation of the Great Circle coordinates
        self.L, self.B = cart_to_lambet(self.x, self.y, self.z, normal, point)
        self.B_err = self.b_err #should be error propogated (Newby et al. 2013) but is not yet

'''
================================================================================
 HELPER FUNCTIONS FOR OPTIMIZATION
================================================================================
'''

#do this in one place so it's uniform across the file and easily changeable
def make_orbit(params):

    #negate the x velocity because galpy is in left-handed frame and we aren't barbarians
    o = Orbit(vxvv=[params[0]*u.deg, params[1]*u.deg, params[2]*u.kpc, -1*params[3]*u.km/u.s, params[4]*u.km/u.s, params[5]*u.km/u.s], uvw=True, lb=True, ro=8., vo=220., zo=0., solarmotion=[0, -220, 0])
    o.integrate(ts, mwahpy_default_pot)

    return o

#-------------------------------------------------------------------------------

#this function just makes a few places in the code cleaner
def get_OrbitData_from_orbit(o, o_rev):
    #o: the orbit
    #o: the reversed orbit
    #both of these should be integrated prior to calling this function

    #don't think that the velocities need obs=[8., 0., etc] except the vlos (to make it vgsr)
    data_orbit = OrbitData(np.array(o.ll(ts)), np.array(o.bb(ts)), np.array(o.dist(ts)), np.array(o.vx(ts)), np.array(o.vy(ts)), np.array(o.vz(ts)), np.array(o.vlos(ts, obs=[8., 0., 0., 0., 0., 0.])), np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([]))
    data_orbit_rev = OrbitData(np.array(o_rev.ll(ts)), np.array(o_rev.bb(ts)), np.array(o_rev.dist(ts)), np.array(o_rev.vx(ts))*-1, np.array(o_rev.vy(ts))*-1, np.array(o_rev.vz(ts))*-1, np.array(o.vlos(ts, obs=[8., 0., 0., 0., 0., 0.]))*-1, np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([]))

    return data_orbit, data_orbit_rev

#-------------------------------------------------------------------------------

#given the full list of Lambdas, outputs the indices of the points within that list closest to our data's Lambdas
#(while keeping in mind that it may wrap from 0 to 360 degrees and vice versa)
def get_point_list(vals, Lam):
    #vals: the Lambda values that you want to find the closest indices to
    #Lam: the array of Lambda values that you are searching through

    #---------------------------------------------------------------------------
    #grabs the index of the value in Lam with the closest value to val
    def get_closest_index(val, Lam):
        Lam = np.abs(Lam - val)
        m = np.min(Lam)

        try: #another race condition?
            ind = np.where(Lam == m)[0][0]
        except IndexError:
            ind = -1

        return ind, m*deg_sep_pun
    #---------------------------------------------------------------------------

    point_list = []
    Lam_list = []
    costs = 0

    for val in vals:

        #within that segment, find the index which produces the value closest to val
        point, c = get_closest_index(val, Lam)
        costs += c

        #toss it in the list
        point_list.append(point)
        Lam_list.append(Lam[point])

    return point_list, costs

#-------------------------------------------------------------------------------

#take in data, orbit, and plane info: Output model data corresponding to each data point
def get_model_from_params(data, params, normal, point):

    #initialize the orbit we are fitting
    o = make_orbit(params)

    #we flip it around so that we are fitting both the forwards and the backwards orbit
    o_rev = o.flip()
    o_rev.integrate(ts, mwahpy_default_pot)

    data_orbit, data_orbit_rev = get_OrbitData_from_orbit(o, o_rev)
    data_orbit.calc_lam_bet(normal, point)
    data_orbit_rev.calc_lam_bet(normal, point)

    #grab full lists so that we can select the closest points once we get a list
    Lam = np.append(np.flip(data_orbit_rev.L), data_orbit.L)

    #get the list of points closest to each data point in Lambda
    point_list, costs = get_point_list(data.L, Lam)

    #grab the model points from the point list we grabbed
    Bet = np.append(np.flip(data_orbit_rev.B), data_orbit.B)
    B_model = np.array([Bet[p] for p in point_list]).flatten()

    D = np.append(np.flip(data_orbit_rev.d), data_orbit.d)
    D_model = np.array([D[p] for p in point_list]).flatten()

    if vx_flag:
        vx = np.append(np.flip(data_orbit_rev.vx), data_orbit.vx)
        vx_model = np.array([vx[p] for p in point_list]).flatten()
    else:
        vx_model = np.zeros(len(B_model))

    if vy_flag:
        vy = np.append(np.flip(data_orbit_rev.vy), data_orbit.vy)
        vy_model = np.array([vy[p] for p in point_list]).flatten()
    else:
        vy_model = np.zeros(len(B_model))

    if vz_flag:
        vz = np.append(np.flip(data_orbit_rev.vz), data_orbit.vz)
        vz_model = np.array([vz[p] for p in point_list]).flatten()
    else:
        vz_model = np.zeros(len(B_model))

    if vgsr_flag:
        vgsr = np.append(np.flip(data_orbit_rev.vlos), data_orbit.vlos)
        vgsr_model = np.array([vgsr[p] for p in point_list]).flatten()
    else:
        vgsr_model = np.zeros(len(B_model))

    return B_model, D_model, vx_model, vy_model, vz_model, vgsr_model, costs

#-------------------------------------------------------------------------------

#takes in the observed data and a test orbit and calculates the goodness-of-fit using a chi-squared method
def chi_squared(params, data=[], normal=(0, 0, 0), point=(1, 0, 0)):

    B_model, d_model, vx_model, vy_model, vz_model, vgsr_model, costs = get_model_from_params(data, params, normal, point) #get model data from orbit

    x2_B = sum(((B_model - data.B)/data.B_err)**2)
    x2_d = sum(((d_model - data.d)/data.d_err)**2)

    #this is the main chi squared that we are minimizing
    x2 = x2_B + x2_d + costs

    if vx_flag:
        x2_vx = sum(((vx_model - data.vx)/data.vx_err)**2)
        x2 += x2_vx

    if vy_flag:
        x2_vy = sum(((vy_model - data.vy)/data.vy_err)**2)
        x2 += x2_vy

    if vz_flag:
        x2_vz = sum(((vz_model - data.vz)/data.vz_err)**2)
        x2 += x2_vz

    if vgsr_flag:
        x2_vgsr = sum(((vgsr_model - data.vgsr)/data.vgsr_err)**2)
        x2 += x2_vgsr

    #there's a weird edge case where occasionally x2 is a short array of floats
    #this bit prevents scipy from throwing an error
    #no idea what causes that
    if type(x2) == type(np.array([])):
        x2 = x2[0]

    if verbose:
        print('X^2: ' + str(x2))

    return x2

#-------------------------------------------------------------------------------

#takes in data, then fits a Great Circle to that data and
#minimizes the chi_squared to fit an orbit to the data
def optimize(data_opt, max_it, bounds, **kwargs):

    #compute the preferred galactocentric spherical frame to fit this orbit in
    #(should be close to the orbital plane of the observed data)
    normal = get_plane_normal(plane_OLS(data_opt.x, data_opt.y, data_opt.z)) #get normal vector for fit Great Circle
    point = (1, 0, 0) #not currently fitting this, but this can be changed or fit at a later date

    data_opt.calc_lam_bet(normal, point)

    '''
    ============================================================================
    DIFFERENTIAL EVOLUTION CONSTANTS
    ============================================================================
    '''
    #DO NOT TOUCH
    pop_size = 50 #10 times number of parameters
    diff_scaling_factor = 0.8
    crossover_rate = 0.9
    '''
    ============================================================================
    '''

    #the actual bulk of the optimization
    params = scopt.differential_evolution(chi_squared, bounds, args=(data_opt, normal, point), maxiter=max_it, popsize=pop_size, mutation=diff_scaling_factor, recombination=crossover_rate, workers=-1, disp=not(verbose), **kwargs).x

    x2 = chi_squared(params, data_opt, normal, point)

    return params, normal, point, x2

'''
================================================================================
 FUNCTIONS
================================================================================
'''

#pass in l, b, d values (and optional vx, vy, vz, vlos velocities)
#computes the best orbit fit to those parameters
#outputs the parameters for that best orbit fit
#also need to pass in errors for each value used (except l)

#additional kwargs are passed to scipy.optimize.differential_evolution()
def fit_orbit(l, b, b_err, d, d_err, vx=None, vy=None, vz=None, vgsr=None, \
              vx_err=None, vy_err=None, vz_err=None, vgsr_err=None, max_it=100, \
              bounds=[(0, 360), (-90, 90), (0, 100), (-1000, 1000), (-1000, 1000), (-1000, 1000)], \
              t_len=None, **kwargs):

    #construct data
    #set proper flags based on input data
    if vx:
        global vx_flag
        vx_flag = 1
    if vy:
        global vy_flag
        vy_flag = 1
    if vz:
        global vz_flag
        vz_flag = 1
    if vgsr:
        global vgsr_flag
        vgsr_flag = 1

    #update t_length if necessary
    if t_len:
        global t_length
        t_length = t_len
        global ts
        ts = np.linspace(0, t_length, num=resolution)*u.Gyr

    if verbose:
        print('Building orbit data...')

    data_opt = OrbitData(l, b, d, vx, vy, vz, vgsr, b_err, d_err, vx_err, vy_err, vz_err, vgsr_err)

    if verbose:
        print('===================================')
        print('Optimizing:')
        print('===================================')

    #optimization
    params, normal, point, x2 = optimize(data_opt, max_it, bounds, **kwargs)

    if verbose:
        print('===================================')
        print('Params: l, b, d, vx, vy, vz')
        print(params)
        print()
        print('Normal Vector:')
        print(normal)
        print()
        print('Point Vector:')
        print(point)
        print()
        print('Chi Squared:')
        print(x2)
        print('===================================')

    return params, normal, point, x2

'''
================================================================================
 PLOTTING
================================================================================
'''

def plot_orbit_lam_bet(L, B, params, normal, point):

    o = make_orbit(params)

    o_rev = o.flip()
    o_rev.integrate(ts, mwahpy_default_pot)

    #sign swap on vx because galpy is left-handed, and we are inputting data in a right-handed coordinate system
    data_orbit, data_orbit_rev = get_OrbitData_from_orbit(o, o_rev)
    data_orbit.calc_lam_bet(normal, point)
    data_orbit_rev.calc_lam_bet(normal, point)

    fig = plt.figure(figsize=(9, 6))

    plt.plot(data_orbit.L, data_orbit.B, c='b')
    plt.plot(data_orbit_rev.L, data_orbit_rev.B, c='r')
    plt.scatter(L, B, c='k')

    plt.xlim(0, 360)
    plt.ylim(-90, 90)
    plt.xlabel('$\\Lambda$')
    plt.ylabel('$\\beta$')

    plt.show()

def plot_orbit_gal(l, b, d, params):

    o = make_orbit(params)

    o_rev = o.flip()
    o_rev.integrate(ts, mwahpy_default_pot)

    #sign swap on vx because galpy is left-handed, and we are inputting data in a right-handed coordinate system
    data_orbit, data_orbit_rev = get_OrbitData_from_orbit(o, o_rev)

    fig = plt.figure(figsize=(18, 8))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.plot(data_orbit.l, data_orbit.b, c='b')
    ax1.plot(data_orbit_rev.l, data_orbit_rev.b, c='r')
    ax1.scatter(l, b, c='k')

    ax1.set_xlim(0, 360)
    ax1.set_ylim(-90, 90)
    ax1.set_xlabel('l')
    ax1.set_ylabel('b')

    ax2.plot(data_orbit.l, data_orbit.d, c='b')
    ax2.plot(data_orbit_rev.l, data_orbit_rev.d, c='r')
    ax2.scatter(l, d, c='k')

    ax2.set_xlim(0, 360)
    ax2.set_xlabel('l')
    ax2.set_ylabel('d (helio)')

    plt.show()

'''
================================================================================
 TESTING
================================================================================
'''

def test():
    test_o_l = 90
    test_o_b = 20
    test_o_d = 25
    test_o_vx = 150
    test_o_vy = -200
    test_o_vz = 100

    ts = np.linspace(0, 0.25, 1000)*u.Gyr
    sample = np.array([100, 250, 400, 500, 600, 750, 850])

    o = make_orbit([test_o_l, test_o_b, test_o_d, test_o_vx, test_o_vy, test_o_vz])
    o.integrate(ts, mwahpy_default_pot)
    l = np.take(o.ll(ts), sample)
    b = np.take(o.bb(ts), sample)
    d = np.take(o.dist(ts), sample)

    plt.scatter(l, b, s=5)
    plt.scatter(o.ll(ts), o.bb(ts), s=1)
    plt.show()

    plt.scatter(l, d, s=5)
    plt.scatter(o.ll(ts), o.dist(ts), s=1)
    plt.show()

    b_err = np.zeros(len(b)) + 0.05
    d_err = np.zeros(len(d)) + 1

    test_orbit_data = OrbitData(l, b, d, None, None, None, None, b_err, d_err, None, None, None, None)
    test_orbit_data.calc_lam_bet((0, 0, 1), (1, 0, 0))

    print('Chi Squared of actual values:')
    print(chi_squared([test_o_l, test_o_b, test_o_d, test_o_vx, test_o_vy, test_o_vz], data=test_orbit_data, normal=(0, 0, 1), point=(1, 0, 0)))

    params, normal, point, x2 = fit_orbit(l, b, b_err, d, d_err)
    L, B = gal_to_lambet_galcentric(l, b, d, normal, point)
    plot_orbit_lam_bet(L, B, params, normal, point)
    plot_orbit_gal(l, b, d, params)

'''
================================================================================
 RUNTIME
================================================================================
'''

if __name__ == "__main__":
    test()
