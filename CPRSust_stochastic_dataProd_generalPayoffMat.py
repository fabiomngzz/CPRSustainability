import sys
sys.path.append('/Users/fabiomenegazzo/Documents/Università/codes')
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import itertools
import scipy.integrate as scint
plt.rcParams['font.size'] = 20
plt.rcParams['pcolor.shading'] = 'auto'
from helpers import *
from Gillespie import *
from CPRsust_rates import *
from extinctionTimes import *
from CPRSust_detEqs import *

epsilon = 1e-3
# Number of agents
N = 500
# Carrying capacity of resource in terms of number of quanta of resource
K = 4*N
# Resource's birth rate
b = 1.
# Speed of dynamics of change of strategies
nu = 0.29553
# Harvesting rates
extractionRatesReduced = [[0.5,0.5],[1.5,1.5]]
extractionRates = [[b*e/N for e in row] for row in extractionRatesReduced]
# Each node represents either a consumer (cooperator or defector) or a slot of resource (full or empty)
nodeStates = [0,1,2,3]
stateLabels = ['hole','resource','cooperator','defector']

# Settings for numerical simulations
# Initial conditions
x0 = 0.5
R0 = 0.5

# Length of the simulation
tMax = 100

runObj = {
    'MF' : True,
    'stocRes' : True
}

# Number of repetitions of the simulation
NReps = 100

# Settings for output
outputPath = 'output/kFpP_genPayoffMat' 
if not os.path.isdir(outputPath):
    raise FileNotFoundError(f'Folder for the outputs not found at relative path: {outputPath}. Create it before running the program.')
outputDirMF = outputPath + '/MF/'
os.makedirs(outputDirMF, exist_ok=True)
outputDirStocRes = outputPath + '/stocRes/'
os.makedirs(outputDirStocRes, exist_ok=True)

paramsDict = {
    'N' : N,
    'K' : K,
    'b' : b,
    'extractionRates' : extractionRates,
    'xi' : x0,
    'Ri' : R0,
    'nu' : nu
}

###############
#  MEAN FIELD #
###############

# Define the context object to be used with all integrators in the rest of the code
context = {
    'N' : N,
    'b' : b,
    'K' : K,
    'extractionRates' : extractionRates,
    'nodeStates' : nodeStates,
    'nu' : nu
}

# Taking from the context the parameter values used by solve_ivp
paramsString = ['b','extractionRates','N','K','nu']
params = evalContextVar(paramsString,context)

tEvalDet = np.linspace(0,tMax,1000)
zSeries = scint.solve_ivp(HES_kFpP_generalPayoffMat,[0,tMax],[R0,x0],method='RK45',t_eval=tEvalDet,args=(params))

# Unpack the resulting object
seriesObj = {
    'time' : zSeries.t.tolist(),
    'cooperators' : zSeries.y[1].tolist(),
    'resource' : zSeries.y[0].tolist()
    }

outputObj = {
    'parameters' : paramsDict,
    'series' : seriesObj
}

fName = 'outMF_' + '_'.join(
    f'{key}{value:.2g}' if isinstance(value, (int,float))
    else f'{key}{"_".join(f"{v:.5g}" for row in value for v in row)}'
    for key, value in paramsDict.items()
    ) + '.json'
outputPathMF = outputDirMF + fName
with open(outputPathMF, 'w') as f:
    json.dump(outputObj, f, indent = 2)

##############
# STOCHASTIC #
############## 

zSeries = np.ones(N+K,dtype=int)
# Vector of variables - assignment of initial conditions
zSeries[0:int(N*x0)] = setVec(zSeries[0:int(N*x0)],nodeStates[2])
zSeries[int(N*x0):N] = setVec(zSeries[int(N*x0):N],nodeStates[3])
zSeries[N:N+int(K*R0)] = setVec(zSeries[N:N+int(K*R0)],nodeStates[1])
zSeries[N+int(K*R0):] = setVec(zSeries[N+int(K*R0):],nodeStates[0])

seriesObj = []

for kRep in range(NReps):
    # Reset the vatiables of the context to their initial conditions
    context['R'] = R0
    context['varVec'] = zSeries

    kStep = 1
    tSim_temp = [0] 
    vecSim_temp = [evalContextVar(['varVec'],context)[0]]

    while tSim_temp[-1] < tMax:
        absState, objNew = GillespieStep(context,reactsCPRsust_homogeneous_kFpP_stocRes)
        if absState:
            break

        tProcess = objNew['t']
        tSim_temp.append(tSim_temp[-1] + tProcess)

        vecSim_temp.append(objNew['vec'])

        kStep+=1

    seriesObj.append({
        'time' : tSim_temp,
        'cooperators' : [countSpecies(z,nodeStates[2])/N for z in vecSim_temp],
        'resource' : [countSpecies(z,nodeStates[1])/K for z in vecSim_temp],
        'absorbing' : absState
    })

outputObj = {
    'parameters' : paramsDict,
    'series' : seriesObj
}

fName = 'outStocRes_' + '_'.join(
    f'{key}{value:.2g}' if isinstance(value, (int,float))
    else f'{key}{"_".join(f"{v:.5g}" for row in value for v in row)}'
    for key, value in paramsDict.items()
    ) + '.json'
outputPathStocRes = outputDirStocRes + fName
with open(outputPathStocRes, 'w') as f:
    json.dump(outputObj, f, indent = 2)