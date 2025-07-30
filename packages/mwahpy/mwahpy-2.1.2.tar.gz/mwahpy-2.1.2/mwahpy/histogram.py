'''
Class implementation for .hist files 
Variable names follow the naming scheme used in the histogram files with the exception of a few
WARNING: This file is pretty dependent on how the .hist file is outputted so if the .hist file is of an older version, this code might not work in getting all
the correct header information especially if spacing is changed
'''

#===============================================================================
# IMPORTS
#===============================================================================


#===============================================================================
# Histogram Data Class
#===============================================================================

class histData():

    def __init__(self, generationDate=None, eulerAngles=None, lambdaRange=None, betaRange=None, lambdaBinSize=None, betaBinSize=None, nbody=None, evolveBackwardTime=None, 
                 evolveFowardTime=None, bestLikelihood=None, timestep=None, criterion=None, sunGCDist=None, theta=None, quadrupoleMoments=None, eps=None, barTimeError=None, 
                 barAngleError=None, spherical=None, primaryDisk=None, secondaryDisk=None, halo=None, n=None, massPerParticle=None, totalSimulated=None, lambdaBins=None, 
                 betaBins=None, hasPM=None, columnHeaders=None, useBin=None, lamb=None, beta=None, normalizedCounts=None, countError=None, betaDispersion=None, betaDispersionError=None, 
                 losVelocityDispersion=None, velocityDispersionError=None, losVelocity=None, losVelocityError=None, betaAverage=None, betaAverageError=None, distance=None, 
                 distanceError=None, pmra=None, pmraError=None, pmdec=None, pmdecError=None, orbitFitting=False):
        
        #Header portion of Histogram 
        self.generationDate = generationDate if generationDate is not None else ""
        self.eulerAngles = eulerAngles if eulerAngles is not None else []
        self.lambdaRange = lambdaRange if lambdaRange is not None else []
        self.betaRange = betaRange if betaRange is not None else []
        self.lambdaBinSize = lambdaBinSize if lambdaBinSize is not None else 0.0
        self.betaBinSize = betaBinSize if betaBinSize is not None else 0.0

        self.nbody = nbody if nbody is not None else 0
        self.evolveBackwardTime = evolveBackwardTime if evolveBackwardTime is not None else 0.0
        self.evolveFowardTime = evolveFowardTime if evolveFowardTime is not None else 0.0
        self.bestLikelihood = bestLikelihood if bestLikelihood is not None else 0.0
        self.timestep = timestep if timestep is not None else 0.0
        self.sunGCDist = sunGCDist if sunGCDist is not None else 0.0
        self.criterion = criterion if criterion is not None else ""
        self.theta = theta if theta is not None else 0.0
        self.quadrupoleMoments = quadrupoleMoments if quadrupoleMoments is not None else ""
        self.eps = eps if eps is not None else 0.0
        self.barTimeError = barTimeError if barTimeError is not None else 0.0
        self.barAngleError = barAngleError if barAngleError is not None else 0.0
        
        #Potential portion of Histogram
        self.spherical = spherical if spherical is not None else ""
        self.primaryDisk = primaryDisk if primaryDisk is not None else ""
        self.secondaryDisk = secondaryDisk if secondaryDisk is not None else ""
        self.halo = halo if halo is not None else ""

        #More histogram infomation
        self.n = n if n is not None else 0
        self.massPerParticle = massPerParticle if massPerParticle is not None else 0.0
        self.totalSimulated = totalSimulated if totalSimulated is not None else 0
        self.lambdaBins = lambdaBins if lambdaBins is not None else 0
        self.betaBins = betaBins if betaBins is not None else 0
        self.hasPM = hasPM if hasPM is not None else 0

        #Column Headers
        self.columnHeaders = columnHeaders if columnHeaders is not None else ""

        #Data Portion of Histogram
        self.useBin = useBin if useBin is not None else []
        self.lamb = lamb if lamb is not None else []
        self.beta = beta if beta is not None else []
        self.normalizedCounts = normalizedCounts if normalizedCounts is not None else []
        self.countError = countError if countError is not None else []
        self.betaDispersion = betaDispersion if betaDispersion is not None else []
        self.betaDispersionError = betaDispersionError if betaDispersionError is not None else []
        self.losVelocityDispersion = losVelocityDispersion if losVelocityDispersion is not None else []
        self.velocityDispersionError = velocityDispersionError if velocityDispersionError is not None else []
        self.losVelocity = losVelocity if losVelocity is not None else []
        self.losVelocityError = losVelocityError if losVelocityError is not None else []
        self.betaAverage = betaAverage if betaAverage is not None else []
        self.betaAverageError = betaAverageError if betaAverageError is not None else []
        self.distance = distance if distance is not None else []
        self.distanceError = distanceError if distanceError is not None else []
        self.pmra = pmra if pmra is not None else []
        self.pmraError = pmraError if pmraError is not None else []
        self.pmdec = pmdec if pmdec is not None else []
        self.pmdecError = pmdecError if pmdecError is not None else []

        #Marker for if orbit fitting is included in histogram
        self.orbitFitting = orbitFitting


        self.array_dict = {'generationDate':self.generationDate, 'eulerAngles':self.eulerAngles, 'lambdaRange':self.lambdaRange, 'betaRange':self.betaRange, \
                            'lambdaBinSize':self.lambdaBinSize, 'betaBinSize':self.betaBinSize, 'nbody':self.nbody, 'evolveBackwardTime':self.evolveBackwardTime, \
                            'evolveFowardTime':self.evolveFowardTime, 'bestLikelihood':self.bestLikelihood, 'timestep':self.timestep, 'sunGCDist':self.sunGCDist, \
                            'criterion':self.criterion, 'theta':self.theta, 'quadrupoleMoments':self.quadrupoleMoments, 'eps':self.eps, 'barTimeError':self.barTimeError, \
                            'barAngleError':self.barAngleError, 'spherical':self.spherical, \
                            'primaryDisk':self.primaryDisk, 'secondaryDisk':self.secondaryDisk, 'halo':self.halo, 'n':self.n, 'massPerParticle':self.massPerParticle,\
                            'columnHeaders':self.columnHeaders, 'totalSimulated':self.totalSimulated, 'lambdaBins':self.lambdaBins, 'betaBins':self.betaBins, 'hasPM':self.hasPM, \
                            'useBin':self.useBin, 'lamb':self.lamb, 'beta':self.beta, 'normalizedCounts':self.normalizedCounts, 'countError':self.countError,  \
                            'betaDispersion':self.betaDispersion, 'betaDispersionError':self.betaDispersionError, 'losVelocityDispersion':self.losVelocityDispersion, \
                            'velocityDispersionError':self.velocityDispersionError, 'losVelocity':self.losVelocity, 'losVelocityError':self.losVelocityError, \
                            'betaAverage':self.betaAverage, 'betaAverageError':self.betaAverageError, \
                            'distance':self.distance, 'distanceError':self.distanceError, 'pmra':self.pmra, 'pmraError':self.pmraError, 'pmdec':self.pmdec, 'pmdecError':self.pmdecError, \
                            'orbitFitting':self.orbitFitting}


