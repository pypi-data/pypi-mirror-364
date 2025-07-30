import numpy as np
from numpy import linalg
import scipy as sc

from .mwahpy_glob import solar_ps

#TODO: Make sure all transformations have inverse transformations
#TODO: Make sure all transormations have unit tests
#TODO: (low priority) Allow certain quantities (like galactocentric phi/theta) to be expressed/input in radians
#TODO: (low priority) add left-handed versions to all galactic cartesian transformations

#===============================================================================
#TEMPLATE
#===============================================================================
#this generically allows functions to take in either arrays or single values
# and turns everything into arrays behind the scenes

def fix_arrays(func, *args, **kwargs):
    def wrapper(*args, **kwargs):

        use_array = True
        if not(isinstance(args[0], np.ndarray)): #check whether the first input is an array (assume all inputs are symmetric)
            use_array = False
            args = tuple([np.array([args[i]]) for i in range(len(args))]) #if they aren't, convert the args to arrays

        ret = func(*args) #catches the output from the function

        if not use_array: #convert them back if necessary
            if not(isinstance(ret, tuple)): #check whether we can actually iterate on the returned values (i.e. whether the func returns a single value or multiple)
                ret = ret[0]
            else:
                ret = tuple([ret[i][0] for i in range(len(ret))])

        return ret
    return wrapper

#===============================================================================
#HELPER FUNCTIONS
#===============================================================================
#These functions aren't meant to be accessed by outside files or by end users,
#and as such they are not well documented, named, or tested

@fix_arrays
def wrap_long(lon, rad=False):

    if rad:
        lon = lon * 180/np.pi

    for i in range(len(lon)):
        if lon[i] < 0:
            lon[i] += 360
        elif lon[i] > 360:
            lon[i] -= 360

    if rad:
        lon = lon * np.pi/180

    return lon

#rotate the given data around the provided axis
#TODO: Allow array-like input
def rot_around_arb_axis(x, y, z, ux, uy, uz, theta):
    #TODO: Allow radians or degrees
    #x, y, z: 3D cartesian coordinates of the data
    #ux, uy, uz: 3d cartesian coordinates of the axis vector u = (ux, uy, uz)
    #theta: angle to rotate data counter-clockwise around axis (rad)

    #make sure that u is normalized
    norm_u = (ux**2 + uy**2 + uz**2)**0.5
    if round(norm_u, 8) != 1.:
        ux /= norm_u
        uy /= norm_u
        uz /= norm_u

    xyz = np.array([x, y, z])

    cos = np.cos(theta)
    sin = np.sin(theta)
    R = np.array([[cos+ux**2*(1-cos),    ux*uy*(1-cos)-uz*sin, ux*uz*(1-cos)+uy*sin],
                  [uy*ux*(1-cos)+uz*sin, cos+uy**2*(1-cos),    uy*uz*(1-cos)-ux*sin],
                  [uz*ux*(1-cos)-uy*sin, uz*uy*(1-cos)+ux*sin, cos+uz**2*(1-cos)   ]])

    xyz = np.matmul(R, xyz)
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    return x, y, z

@fix_arrays
def long_lat_to_unit_vec(l, b, left_handed=False, rad=False):

    if not rad:
        l = l*np.pi/180
        b = b*np.pi/180

    if left_handed:
        #left-handed
        x = -1 * np.cos(l)*np.cos(b)
    else:
        #right-handed
        x = np.cos(l)*np.cos(b)

    y = np.sin(l)*np.cos(b)
    z = np.sin(b)

    return x, y, z

def comp_wise_dot(M, v, normalize=False):
    #performs a component-wise dot product for matrix M of vectors, with vector v
    #if normalize == True, normalize v and each component of M
    tol = 1e-6

    out = np.zeros(len(M))

    if normalize:
        v = v / linalg.norm(v)

    for i in range(len(M)):
        if normalize:
            if linalg.norm(M[i]) < tol: #required to handle singularities
                out[i] = 0
            else:
                out[i] = np.dot(M[i], v) / linalg.norm(M[i])
        else:
            out[i] = np.dot(M[i], v)

    return out

#===============================================================================
#FIRST ORDER COORDINATE/POSITION TRANSFORMATIONS
#===============================================================================

@fix_arrays
def cart_to_gal(x, y, z, left_handed=False):
    #get l, b, r (helio) from galactocentric X, Y, Z coords

    if left_handed:
        r = ((x+solar_ps.x)**2 + y**2 + z**2)**0.5
        l = np.arctan2(y,-1*(x-8))*180/np.pi
    else:
        r = ((x-solar_ps.x)**2 + y**2 + z**2)**0.5
        l = np.arctan2(y,(x+8))*180/np.pi
    b = np.arcsin(z/r)*180/np.pi

    return l, b, r

#-------------------------------------------------------------------------------

@fix_arrays
def gal_to_cart(l, b, r, left_handed=False, rad=False):

    if not rad:
        l = l*np.pi/180
        b = b*np.pi/180

    if left_handed:
        #left-handed
        x = -1*solar_ps.x - r*np.cos(l)*np.cos(b)
    else:
        #right-handed
        x = r*np.cos(l)*np.cos(b) + solar_ps.x

    y = r*np.sin(l)*np.cos(b)
    z = r*np.sin(b)

    return x, y, z

#-------------------------------------------------------------------------------

#input: x[kpc], y[kpc], z[kpc]
#output: Cylindrical coordinates (R, [kpc], Z [kpc], Phi [deg])
#phi = 0 when oriented along the positive x-axis
@fix_arrays
def cart_to_cyl(x, y, z):

    R = (x**2 + y**2)**0.5
    phi = np.arctan2(y, x)*180/np.pi

    return R, z, phi

#-------------------------------------------------------------------------------

@fix_arrays
def cyl_to_cart(R, z, phi):

    phi = phi*np.pi/180

    x = R*np.cos(phi)
    y = R*np.sin(phi)

    return x, y, z

#-------------------------------------------------------------------------------

@fix_arrays
def cart_to_sph(x, y, z):

    r = (x**2 + y**2 + z**2)**0.5

    phi = np.arctan2(y, x)*180/np.pi
    theta = np.arcsin(z/r)*180/np.pi

    return phi, theta, r

#-------------------------------------------------------------------------------

@fix_arrays
def sph_to_cart(phi, theta, r):

    phi = phi*np.pi/180
    theta = theta*np.pi/180

    x = r*np.cos(phi)*np.cos(theta)
    y = r*np.sin(phi)*np.cos(theta)
    z = r*np.sin(theta)

    return x, y, z

#===============================================================================
#SECOND ORDER COORDINATE/POSITION TRANSFORMATIONS
#===============================================================================

@fix_arrays
def cyl_to_gal(R, z, phi):
    x, y, z = cyl_to_cart(R, z, phi)
    l, b, r = cart_to_gal(x, y, z)
    return l, b, r

#-------------------------------------------------------------------------------

@fix_arrays
def gal_to_cyl(l, b, r):
    x, y, z = gal_to_cart(l, b, r)
    R, z, phi = cart_to_cyl(x, y, z)
    return R, z, phi

#===============================================================================
#VELOCITY TRANSFORMATIONS
#===============================================================================

# Input: distance [kpc], radial velocity [km/s], RA/DEC [degrees], and pmRA/pmDEC [mas/yr]
# Returns: Galactic vx, vy, vz velocities [km/s]
# NOTE: pmRA = d/dt(RA) * cos(DEC)
# Adapted from code written by Alan Pearl
@fix_arrays
def get_uvw(ra, dec, dist, rv, pmra, pmde):

    # Conversion from Equatorial (J2000) Cartesian to Galactic Cartesian
    EQ2GC = np.array( [[-0.05487572, -0.87343729, -0.48383453],
                      [  0.49410871, -0.44482923,  0.7469821 ],
                      [ -0.86766654, -0.19807649,  0.45598456]], dtype=np.float32 )

    ra_rad = ra * (np.pi/180.0)
    dec_rad = dec * (np.pi/180.0)

    sina = np.sin(ra_rad)
    cosa = np.cos(ra_rad)
    sind = np.sin(dec_rad)
    cosd = np.cos(dec_rad)

    vra =  4.741067035842384 * pmra * dist
    vdec = 4.741067035842384 * pmde * dist

    vx_Eq = rv * cosd * cosa   -   vdec * sind * cosa   -   vra * sina
    vy_Eq = rv * cosd * sina   -   vdec * sind * sina   +   vra * cosa
    vz_Eq = rv * sind          +   vdec * cosd

    vel_Eq = np.array([ vx_Eq, vy_Eq, vz_Eq ])
    U, V, W = np.dot(EQ2GC, vel_Eq)

    return U, V, W

#-------------------------------------------------------------------------------

@fix_arrays
def get_vxvyvz(ra, dec, dist, rv, pmra, pmde):

    U, V, W = get_uvw(ra, dec, dist, rv, pmra, pmde)

    # add Sun's velocity
    vx = U + solar_ps.vx
    vy = V + solar_ps.vy
    vz = W + solar_ps.vz

    return vx, vy, vz

#-------------------------------------------------------------------------------

#TODO: Do the linear algebra to avoid a inv calculation, since that's huge time waste
#solar reflex motion will be already removed if UVW are galactocentric
@fix_arrays
def get_rvpm(ra, dec, dist, U, V, W):

    k = 4.74057
    rv = np.array([0.0]*len(ra))
    pmra = np.array([0.0]*len(ra))
    pmdec = np.array([0.0]*len(ra))

    i = 0
    while i < len(ra):

        ra_rad = ra[i] * np.pi/180
        dec_rad = dec[i] * np.pi/180

        T = np.array( [[-0.05487572, -0.87343729, -0.48383453],
                      [  0.49410871, -0.44482923,  0.7469821 ],
                      [ -0.86766654, -0.19807649,  0.45598456]], dtype=np.float32 )
        A = np.array([[np.cos(ra_rad)*np.cos(dec_rad), -1*np.sin(ra_rad), -1*np.cos(ra_rad)*np.sin(dec_rad)], [np.sin(ra_rad)*np.cos(dec_rad), np.cos(ra_rad), -1*np.sin(ra_rad)*np.sin(dec_rad)], [np.sin(dec_rad), 0, np.cos(dec_rad)]])
        B = np.matmul(T,A)
        B_inv = np.linalg.inv(B)

        uvw = np.array([[U[i]], [V[i]], [W[i]]])
        rvpm = np.matmul(B_inv, uvw)

        rv[i] = rvpm[0][0]
        pmra[i] = rvpm[1][0]/dist[i]/k
        pmdec[i] = rvpm[2][0]/dist[i]/k

        i += 1

    return rv, pmra, pmdec

#-------------------------------------------------------------------------------

@fix_arrays
def remove_sol_mot_from_pm(ra, dec, dist, pmra, pmdec):

    vx = np.array([-solar_ps.vx] * len(ra))
    vy = np.array([-solar_ps.vy] * len(ra))
    vz = np.array([-solar_ps.vz] * len(ra))

    rv, mura, mudec = get_rvpm(ra, dec, dist, vx, vy, vz)

    #don't directly modify pmra and pmdec
    pmra_new = pmra - mura
    pmdec_new = pmdec - mudec

    return pmra_new, pmdec_new

#-------------------------------------------------------------------------------

@fix_arrays
def add_sol_mot_to_pm(ra, dec, dist, pmra, pmdec):

    vx = np.array([-solar_ps.vx] * len(ra))
    vy = np.array([-solar_ps.vy] * len(ra))
    vz = np.array([-solar_ps.vz] * len(ra))

    rv, mura, mudec = get_rvpm(ra, dec, dist, vx, vy, vz)

    #don't directly modify pmra and pmdec
    pmra_new = pmra + mura
    pmdec_new = pmdec + mudec

    return pmra_new, pmdec_new

#-------------------------------------------------------------------------------

@fix_arrays
def get_uvw_errors(dist, ra, dec, pmra, pmdec, err_pmra, err_pmdec, err_rv, err_dist):
    #distance in pc
    k = 4.74057

    ra_rad = ra * np.pi/180
    dec_rad = dec * np.pi/180

    T = np.array([[-0.05487572,-0.87343729, -0.48383453], [0.49410871, -0.44482923,  0.7469821], [-0.86766654, -0.19807649,  0.45598456]])
    A = np.array([[np.cos(ra_rad)*np.cos(dec_rad), -1*np.sin(ra_rad), -1*np.cos(ra_rad)*np.sin(dec_rad)], [np.sin(ra_rad)*np.cos(dec_rad), np.cos(ra_rad), -1*np.sin(ra_rad)*np.sin(dec_rad)], [np.sin(dec_rad), 0, np.cos(dec_rad)]])
    B = np.matmul(T,A)
    C = B**2

    M = np.array([[err_rv**2],
                  [(k*dist)**2 * (err_pmra**2 + (pmra*err_dist/dist)**2)],
                  [(k*dist)**2 * (err_pmdec**2 + (pmdec*err_dist/dist)**2)]])
    N = 2*pmra*pmdec*k**2*err_dist**2*np.array([[B[0][1]*B[0][2]],
                                               [B[1][1]*B[1][2]],
                                               [B[2][1]*B[2][2]]])

    uvw_var = np.matmul(C,M) + N

    err_u = (uvw_var[0][0])**0.5
    err_v = (uvw_var[1][0])**0.5
    err_w = (uvw_var[2][0])**0.5

    return err_u, err_v, err_w

#remove solar reflex motion from line of sight velocity
@fix_arrays
def vlos_to_vgsr(l, b, vlos):
    #TODO: Allow ra, dec as inputs

    l = l * np.pi/180
    b = b * np.pi/180

    vgsr = vlos + solar_ps.vx*np.cos(l)*np.cos(b) + solar_ps.vy*np.sin(l)*np.cos(b) + solar_ps.vz*np.sin(b)

    return vgsr

#add solar reflex motion back into GSR line of sight velocity
@fix_arrays
def vgsr_to_vlos(l, b, vgsr):
    #TODO: Allow ra, dec as inputs

    l = l * np.pi/180
    b = b * np.pi/180

    vlos = vgsr - solar_ps.vx*np.cos(l)*np.cos(b) - solar_ps.vy*np.sin(l)*np.cos(b) - solar_ps.vz*np.sin(b)

    return vlos

#=====================================
#MISC TOOLS
#=====================================

#-------------------------------------------------------------------------------

#this is more or less meant to be a helper function, I think.
#I won't add it to the documentation for that reason.
#borrowed from NewbyTools
def plane_dist(x,y,z, params):
    a,b,c = params
    return (a*x + b*y + c*z)

#-------------------------------------------------------------------------------

#x, y, z should be numpy arrays
#takes in galactocentric x, y, z data and outputs parameters for the best fit plane to those points incident the galactic center
#adapted from NewbyTools
def plane_OLS(x,y,z, print_distances=False):
    """ Solves for the best-fit plane to a set of x,y,z data using ordinary least-squares.
        Equation is of form z = Ax + By.
        DIFFERENT FROM NEWBY TOOLS plane_OLS() IN THAT WE CONSTRAIN THE PLANE THROUGH GALACTIC CENTER
        Output is normalized a,b,c of a plane of the form ax+by+cz=0"""
    A = np.array([x, y]).T
    B = z.T

    #solve Ax=B
    p = np.matmul(np.matmul(linalg.inv(np.matmul(A.T, A)), A.T), B.T) #uses left pseudo-inverse {(A^T * A)^-1 * A^T} due to system being overconstrained (A doesn't have a true inverse)
    params = [-float(p[0]), -float(p[1]), 1.0]  #c=1.0 by default
    bottom = np.sqrt(params[0]*params[0] + params[1]*params[1] + params[2]*params[2])
    for i in range(len(params)):  params[i] = params[i]/bottom
    print("# - Normalized best-fit plane parameters: {0}".format(params))
    if print_distances:
        for i in range(len(x)):
            print(plane_dist(x[i], y[i], z[i], params))
    return params

#-------------------------------------------------------------------------------

#get_plane_normal: [float, float, float, float] --> np.array([float, float, float])
#takes in parameters that define a plane in 3D and returns a normalized normal vector to that plane
def get_plane_normal(params):
    #params ([a, b, c]) corresponding to the equation for a plane ax + by + cz = 0
    #comes from the plan fitting method above

    #definition of a normal vector, given equation of a plane
    normal = np.array([params[0], params[1], params[2]])

    #normalize the normal vector
    len_normal = (normal[0]**2 + normal[1]**2 + normal[2]**2)**0.5
    normal = (normal[0]/len_normal, normal[1]/len_normal, normal[2]/len_normal)

    return normal

#===============================================================================
#NONSTANDARD/UNIQUE COORDINATE TRANFORMATIONS
#===============================================================================

#gal2plane: np.array(floats), np.array(floats), np.array(floats), (float, float, float), (float, float, float) --> np.array(floats), np.array(floats), np.array(floats)
#takes in galactic coordinates for a star(s) and returns their x,y,z coordinates with respect to a rotated plane with the normal vector provided
#Newby 2013 et al, appendix
def cart_to_plane(x, y, z, normal, point):

    #construct a 3D frame in the current long/lat frame
    xyz = np.array([x, y, z])

    #build the change of basis matrix
    r_pole = np.array(list(normal))
    r_origin = np.array(list(point))
    r_newy = np.cross(r_pole, r_origin)

    cob_mat = np.array([r_origin, r_newy, r_pole])

    #compute the new values
    xyz = np.matmul(cob_mat, xyz)
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    return x, y, z

#gal2plane: np.array(floats), np.array(floats), np.array(floats), (float, float, float), (float, float, float) --> np.array(floats), np.array(floats), np.array(floats)
#takes in galactic coordinates for a star(s) and returns their x,y,z coordinates with respect to a rotated plane with the normal vector provided
#Newby 2013 et al, appendix
def gal_to_plane(l, b, d, normal, point):

    x, y, z = gal_to_cart(l, b, d)
    x, y, z = cart_to_plane(x, y, z, normal, point)

    return x, y, z

#-------------------------------------------------------------------------------

#kind of a helper function for the gal_to_lambet and cart_to_lambet functions,
#although it just finds longitude and latitude of any cartesian system
@fix_arrays
def cart_to_lonlat(x, y, z):
    Lam = np.arctan2(y, x)*180/np.pi #convert to degrees

    #correct Lam to be between 0 and 360 instead of -180 to 180
    i = 0
    while i < len(Lam):
        if Lam[i] < 0:
            Lam[i] += 360
        i += 1

    Bet = np.arcsin(z/(x**2 + y**2 + z**2)**0.5)*180/np.pi #convert to degrees

    return Lam, Bet

#-------------------------------------------------------------------------------

def gal_to_lambet(l, b, d, normal, point):

    x_prime, y_prime, z_prime = gal_to_plane(l, b, d, normal, point)
    Lam, Bet = cart_to_lonlat(x_prime, y_prime, z_prime)

    return Lam, Bet

#-------------------------------------------------------------------------------

#this may just go away. Not sure how useful it really is
def gal_to_lambet_galcentric(l, b, d, normal, point):

    galcx, galcy, galcz = gal_to_cart(l, b, d)
    x_prime, y_prime, z_prime = cart_to_plane(galcx, galcy, galcz, normal, point)
    Lam, Bet = cart_to_lonlat(x_prime, y_prime, z_prime)

    return Lam, Bet

#-------------------------------------------------------------------------------

def cart_to_lambet(x,y,z, normal, point):

    x_prime, y_prime, z_prime = cart_to_plane(x,y,z, normal=normal, point=point)
    Lam, Bet = cart_to_lonlat(x_prime, y_prime, z_prime)

    return Lam, Bet

#-------------------------------------------------------------------------------

# I believe x, y, z can be arrays
def cart_to_sgr(x,y,z):

    x_prime = x_prime - solar_ps.x
    xyz = np.array([x, y, z])

    #Euler rotation matrix from Solar frame into Sgr
    phi = 183.8 * np.pi/180
    theta = 76.5 * np.pi/180
    psi = 194.1 * np.pi/180
    cphi = np.cos(phi)
    sphi = np.sin(phi)
    ctheta = np.cos(theta)
    stheta = np.sin(theta)
    cpsi= np.cos(psi)
    spsi= np.sin(psi)

    R = np.array([[cpsi*cphi-ctheta*sphi*spsi, cpsi*sphi+ctheta*cphi*spsi, spsi*stheta],
                   [-1*spsi*cphi-ctheta*sphi*cpsi, -1*spsi*sphi+ctheta*cphi*cpsi, cpsi*stheta],
                   [stheta*sphi, -1*stheta*cphi, ctheta]])

    xyz = np.matmul(R, xyz)
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    Lam = np.arctan2(y, x)*180/np.pi
    Bet = np.arcsin(z/(x**2 + y**2 + z**2)**0.5)*180/np.pi

    return Lam, Bet

#-------------------------------------------------------------------------------

#takes in galactic coordinates for a star(s) and returns their Lambda, Beta coordinates with respect to the Sgr stream plane
def gal_to_sgr(l, b):
    #l, b: Galactic coordinates (can be arrays)

    x = np.cos(l*np.pi/180)*np.cos(b*np.pi/180)
    y = np.sin(l*np.pi/180)*np.cos(b*np.pi/180)
    z = np.sin(b*np.pi/180)
    xyz = np.array([x, y, z])

    #Euler rotation matrix from Solar frame into Sgr
    phi = 183.8 * np.pi/180
    theta = 76.5 * np.pi/180
    psi = 194.1 * np.pi/180
    cphi = np.cos(phi)
    sphi = np.sin(phi)
    ctheta = np.cos(theta)
    stheta = np.sin(theta)
    cpsi= np.cos(psi)
    spsi= np.sin(psi)

    R = np.array([[   cpsi*cphi-ctheta*sphi*spsi,    cpsi*sphi+ctheta*cphi*spsi, spsi*stheta],
                  [-1*spsi*cphi-ctheta*sphi*cpsi, -1*spsi*sphi+ctheta*cphi*cpsi, cpsi*stheta],
                  [   stheta*sphi,                -1*stheta*cphi,                ctheta     ]])

    xyz = np.matmul(R, xyz)
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    Lam = wrap_long(np.arctan2(y, x)*180/np.pi)
    Bet = np.arcsin(z/(x**2 + y**2 + z**2)**0.5)*180/np.pi

    return Lam, Bet

#-------------------------------------------------------------------------------

#takes in Lambda, Beta coordinates for a star(s) and returns their Galactic coordinates with respect to the Sgr stream plane
def sgr_to_gal(Lam, Bet):

    x = np.cos(Lam*np.pi/180)*np.cos(Bet*np.pi/180)
    y = np.sin(Lam*np.pi/180)*np.cos(Bet*np.pi/180)
    z = np.sin(Bet*np.pi/180)
    xyz = np.array([x, y, z])

    #Euler rotation matrix from Solar frame into Sgr
    phi = 183.8 * np.pi/180
    theta = 76.5 * np.pi/180
    psi = 194.1 * np.pi/180
    cphi = np.cos(phi)
    sphi = np.sin(phi)
    ctheta = np.cos(theta)
    stheta = np.sin(theta)
    cpsi= np.cos(psi)
    spsi= np.sin(psi)

    R = np.array([[   cpsi*cphi-ctheta*sphi*spsi,    cpsi*sphi+ctheta*cphi*spsi, spsi*stheta],
                  [-1*spsi*cphi-ctheta*sphi*cpsi, -1*spsi*sphi+ctheta*cphi*cpsi, cpsi*stheta],
                  [   stheta*sphi,                -1*stheta*cphi,                ctheta     ]])
    R_inv = np.linalg.inv(R)

    xyz = np.matmul(R_inv, xyz)
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    l = wrap_long(np.arctan2(y, x)*180/np.pi)
    b = np.arcsin(z/(x**2 + y**2 + z**2)**0.5)*180/np.pi

    return l, b

#-------------------------------------------------------------------------------

#pole_rotation: array(float), array(float), tuple(float, float), tuple(float, float) -> array(float), array(float)
#rotate the positions on the sky (sky1, sky2) into a new frame determined by
#the pole of the new frame (pole1, pole2) and the origin of the new frame (origin1, origin2)
#The output is the longitude and latitude in the new coordinate frame

#NOTE: Inputs can be any spherical geometry, as long as the pole & origin arguments
#are in the same coordinate system as the (sky1, sky2) coordinates.
#e.g. if sky1 is a list of RAs and sky2 is a list of Decs, then
#the pole and origin arguments must also be specified in RA Dec.

#sky_to_pole() is deprecated but it is an alias of this function

def pole_rotation(sky1, sky2, pole, origin, wrap=False, rad=False):
    #sky1, sky2: positions of the data on the sky (e.g. sky1 = array(RA), sky2 = array(Dec), etc.)
    #pole: position of the pole of the new coordinate system, tuple
    #origin: position of the origin of the new coordinate system, tuple
    #wrap: if True, Lam is constrained to only positive values. Otherwise, Lam is in [-180,180]
    #rad: is True, ALL inputs are in radians. ALL inputs should be in degrees if rad=False

    use_array = True
    if not(isinstance(sky1, np.ndarray)):
        use_array = False
        sky1 = np.array([sky1])
        sky2 = np.array([sky2])

    sky1 = sky1.copy() #fix aliasing
    sky2 = sky2.copy()
    pole1 = pole[0] #separate tuples for readability
    pole2 = pole[1] #and easy scalability
    origin1 = origin[0]
    origin2 = origin[1]

    if not rad:
        sky1 *= np.pi/180
        sky2 *= np.pi/180
        pole1 *= np.pi/180
        pole2 *= np.pi/180
        origin1 *= np.pi/180
        origin2 *= np.pi/180

    #construct a 3D frame in the current long/lat frame
    #all points have unit distance
    x = np.cos(sky1)*np.cos(sky2)
    y = np.sin(sky1)*np.cos(sky2)
    z = np.sin(sky2)
    xyz = np.array([x, y, z])

    #build the change of basis matrix
    r_pole = np.array([np.cos(pole1)*np.cos(pole2), np.sin(pole1)*np.cos(pole2), np.sin(pole2)])
    r_origin = np.array([np.cos(origin1)*np.cos(origin2), np.sin(origin1)*np.cos(origin2), np.sin(origin2)])
    r_newy = np.cross(r_pole, r_origin)

    cob_mat = np.array([r_origin, r_newy, r_pole])

    #compute the new values
    xyz = np.matmul(cob_mat, xyz)
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    #calculate Lam, Bet in new frame
    Lam = np.arctan2(y, x)
    Bet = np.arcsin(z/(x**2 + y**2 + z**2)**0.5)

    #---------------------------

    if not rad:
        Lam *= 180/np.pi
        Bet *= 180/np.pi

    if wrap:
        Lam = wrap_long(Lam) #TODO: wrap_long should allow for radians

    if not use_array:
        Lam = Lam[0]
        Bet = Bet[0]

    return Lam, Bet

#given the origin and pole for a pole_rotation (in Eq, galactic, etc.), and the new Lambda/Beta,
#returns the sky coordinates in whatever coordinates pole and origin were specified in
def pole_rotation_inv(Lam, Bet, pole, origin, **kwargs):

    new_lon, new_lat = pole_rotation(np.array([0., 0.]), np.array([90., 0.]), pole, origin, **kwargs)
    new_pole = (new_lon[0], new_lat[0])
    new_origin = (new_lon[1], new_lat[1])
    sky1, sky2 = pole_rotation(Lam, Bet, new_pole, new_origin, **kwargs)

    return sky1, sky2

def sky_to_pole(sky1, sky2, pole, origin, wrap=False, rad=False):

    print(DeprecationWarning('sky_to_pole() is deprecated as of mwahpy v1.4.5. Please use pole_rotation() instead (sky_to_pole is now an alias for this). In future updates, this function may be removed.'))

    return pole_rotation(sky1, sky2, pole, origin, wrap=False, rad=False)

#===============================================================================
#EXTRA UTILITIES
#===============================================================================

#euler angle rotation matrix
#too long to format like I normally would
#out here because it's used for the transform and inverse transform
#is it bad to do this outside because it utilizes memory even without using the relevant functions? Probably. It can't be that bad though, right?
phi = 128.79*np.pi/180
theta = 54.39*np.pi/180
psi = 90.70*np.pi/180

newberg2010_ERM = np.array([[(np.cos(psi)*np.cos(phi))-(np.cos(theta)*np.sin(phi)*np.sin(psi)),
                             (np.cos(psi)*np.sin(phi))+(np.cos(theta)*np.cos(phi)*np.sin(psi)),
                             np.sin(psi)*np.sin(theta)],
                            [(-np.sin(psi)*np.cos(phi))-(np.cos(theta)*np.sin(phi)*np.cos(psi)),
                             (-np.sin(psi)*np.sin(phi))+(np.cos(theta)*np.cos(phi)*np.cos(psi)),
                             np.cos(psi)*np.sin(theta)],
                            [np.sin(theta)*np.sin(phi),
                             -np.sin(theta)*np.cos(phi),
                             np.cos(theta)]])

k19_rotmat = np.array([[-0.44761231, -0.08785756, -0.88990128],
                       [-0.84246097,  0.37511331,  0.38671632],
                       [ 0.29983786,  0.92280606, -0.24192190]])

#-------------------------------------------------------------------------------

#coordinate transform from (l,b) to Orphan-Chenab Stream (Lambda,Beta) from Newberg et al. (2010)
#adapted from code by Hiroka Warren
@fix_arrays
def gal_to_lambet_newberg2010(l, b):

    l_rad = l*np.pi/180
    b_rad = b*np.pi/180

    M2 = np.array([np.cos(b_rad)*np.cos(l_rad),
                   np.cos(b_rad)*np.sin(l_rad),
                   np.sin(b_rad)])

    M3 = np.matmul(newberg2010_ERM,M2)

    lam = np.arctan2(M3[1], M3[0])*180/np.pi
    bet = np.arcsin(M3[2])*180/np.pi

    return lam, bet

#-------------------------------------------------------------------------------

#(inverse) coordinate transform from Orphan-Chenab Stream (Lambda,Beta) to (l,b) from Newberg et al. (2010)
#adapted from code by Hiroka Warren
@fix_arrays
def lambet_to_gal_newberg2010(lam, bet):

    inv_M1 = np.linalg.inv(newberg2010_ERM)

    lam_rad = lam*np.pi/180
    bet_rad = bet*np.pi/180

    M2 = np.array([np.cos(bet_rad)*np.cos(lam_rad),
                   np.cos(bet_rad)*np.sin(lam_rad),
                   np.sin(bet_rad)])

    M3 = np.matmul(inv_M1,M2)

    l = np.arctan2(M3[1],M3[0])*180/np.pi
    b = np.arcsin(M3[2])*180/np.pi

    return l, b

#-------------------------------------------------------------------------------

#Conversion from (ra, dec) to (phi1, phi2) for Orphan-Chenab stream as per Koposov et al. (2019)
@fix_arrays
def eq_to_OC_koposov2019(ra, dec):

    ra_rad = ra*np.pi/180
    dec_rad = dec*np.pi/180

    M2 = np.array([np.cos(ra_rad)*np.cos(dec_rad),
                   np.sin(ra_rad)*np.cos(dec_rad),
                   np.sin(dec_rad)])

    M3 = np.matmul(k19_rotmat,M2)

    phi1 = np.arctan2(M3[1],M3[0])*180/np.pi
    phi2 = np.arcsin(M3[2])*180/np.pi

    return phi1, phi2

#-------------------------------------------------------------------------------

#Inverse conversion from (phi1, phi2) to (ra, dec) for Orphan-Chenab stream as per Koposov et al. (2019)
@fix_arrays
def OC_to_eq_koposov2019(phi1, phi2):

    M1 = np.linalg.inv(k19_rotmat)

    phi1_rad = phi1*np.pi/180
    phi2_rad = phi2*np.pi/180

    M2 = np.array([np.cos(phi1_rad)*np.cos(phi2_rad),
                   np.sin(phi1_rad)*np.cos(phi2_rad),
                   np.sin(phi2_rad)])

    M3 = np.matmul(M1,M2)

    ra = np.arctan2(M3[1],M3[0])*180/np.pi
    dec = np.arcsin(M3[2])*180/np.pi

    return ra, dec

#-------------------------------------------------------------------------------
#hard-coded pole_rotation transformations

oc_pole = (72, -14) #koposov et al. (2019) Orphan-Chenab stream transformation (ra, dec)
oc_origin = (191.10487, 62.86084)

def eq_to_OC(ra, dec, **kwargs):
    return pole_rotation(ra, dec, oc_pole, oc_origin, **kwargs)

def OC_to_eq(Lam, Bet, **kwargs):
    return pole_rotation_inv(Lam, Bet, oc_pole, oc_origin, **kwargs)

#===============================================================================
# RUNTIME
#===============================================================================
