 MILKYWAY@HOME PYTHON PACKAGE (MWAHPY)
========================================

NOTE: MWAHPY HAS ENTERED LONG-TERM LEGACY SUPPORT (V2.0.0+). PULL REQUESTS WILL BE REVIEWED AND MERGED IF POSSIBLE, BUT I AM NO LONGER PLANNING ON IMPLEMENTING NEW FEATURES FOR THE CODE BASE. 

Copyright Tom Donlon, 2020 RPI

github user: thomasdonlon

Requires Python v.>3.6.0

-----------------------------------------

MilkyWay@home is a computational astrophysics project located at RPI and run by Dr. Heidi Newberg. The project contains two main components, (i) the Separation Application and (ii) the N-body Application. I have worked with both, and over a few years have developed several useful bits of python code to supplement analysis and usage of MilkyWay@home. This code has been cleaned and organized here, so that others can avoid having to constantly reinvent the wheel.

The purpose of the mwahpy package is to provide a collection of useful tools for people working with/on the MilkyWay@home N-body project at RPI.

In practice it would be good for this package to be updated along with the MilkyWay@home project and/or python updates after I'm gone. No clue if that's going to happen, but I plan on maintaining support at least through the spring of 2023 (while I'm in grad school).

Issues with the package can be directed to my github profile or on the MilkyWay@home forums at milkyway.cs.rpi.edu. Improvements or additions are welcome, just send a pull request to the mwahpy github repository.

CONTENTS
========================================

A non-exhaustive list of contents of the package is given below:

 - easy importing of data from N-body output
 - easy manipulation of data after reading in
 - A variety of coordinate transformations for typical coordinate systems used in Galactic astronomy
 - easy visualization of the imported data through plotting functionality
 - a wide variety of useful scripts and routines for working with N-body simulations, especially those with dwarf galaxies
 - a tutorial .pdf document along with documentation for each function in the package

INSTALLATION
========================================

FOR USERS:

1. Open your terminal, and run

> python3 -m pip install mwahpy

2. Insert import statements for the subpackages that you want to use in your .py files:

> import mwahpy.{mwahpy subpackage}

> import mwahpy.{other mwahpy subpackage}

> ...

3. Do science

FOR DEVELOPERS:

1. Clone the mwahpy github repository

2. Make the desired changes in the source code

3. Navigate to the directory where you cloned the repo, and then run

> python3 setup.py develop --user

(note, you will probably need to uninstall any previous versions of mwahpy you had on your machine before running this)

4. To test your changes, insert import statements for the subpackages that you want to use in your .py files as you normally would:

> import mwahpy.{mwahpy subpackage}

> import mwahpy.{other mwahpy subpackage}

> ...

5. Once you are done making changes to the source code, put in a pull request to master

6. Navigate to the directory where you cloned the repo, and then run

> python3 setup.py develop --uninstall

> pip3 install mwahpy

Your changes will not be available in the main mwahpy build until a new release comes out.

TODO
========================================

MAJOR:
 - Expand plot capabilities
 - Finish refactoring coords.py
 - Finish unit testing of coordinate transformations
 - add animate() for the Nbody struct for nice animations
 - update documentation so it is current (probably last thing I'll do during summer 2023)

MINOR:
- Let subset_circ() and subset_rect() handle None as bounds
- Implement better linear algebra to reduce the computation time of coords.get_rvpm()
- Play around with turning off mwahpy_glob.verbose flag for some things to quiet unnecessary output
- Add levels of verbosity, and make this changeable by running a command

ISSUES
========================================

- current pypi repo dist doesn't automatically install pandas on install. This is easily fixed by installing pandas yourself if it is not already installed. It has been fixed in the current github version of the code. 
- output_handler.make_nbody_input() has to set all particles types to dark matter. This is because MilkyWay@home N-Body can only read .in files that only contain dark matter (#ignore = 1) files. This is more of a bug in the N-Body client than mwahpy, but doesn't change the physics at all. 
