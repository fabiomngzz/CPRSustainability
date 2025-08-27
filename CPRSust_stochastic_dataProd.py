import sys
sys.path.append('/Users/fabiomenegazzo/Documents/Università/codes')
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import itertools
import scipy.integrate as scint
import copy
plt.rcParams['font.size'] = 20
plt.rcParams['pcolor.shading'] = 'auto'
from helpers import *
from Gillespie import *
from CPRsust_rates import *
from extinctionTimes import *
from CPRSust_detEqs import *

reactsCPRsust_homogeneous_detRes = [
    {
        'description': 'Change of strategy: cooperator to defector',
        'probFunc' : rateMinus_detRes,
        'probFuncVars' : ['R','varVec','N','nodeStates[2]','nodeStates[3]'],
        'oldState' : ['nodeStates[2]'],
        'newState' : ['nodeStates[3]']
    },
    {
        'description': 'Change of strategy: defector to cooperator',
        'probFunc' : ratePlus_detRes,
        'probFuncVars' : ['R','varVec','N','nodeStates[2]','nodeStates[3]'],
        'oldState' : ['nodeStates[3]'],
        'newState' : ['nodeStates[2]']
    }
]

reactsCPRsust_homogeneous_stocRes = [
    {
        'description': 'Offspring of resource',
        'probFunc' : resBirthRate,
        'probFuncVars' : ['varVec','b','K','nodeStates[1]'],
        'oldState' : ['nodeStates[0]'],
        'newState' : ['nodeStates[1]']
    },
    {
        'description': 'Change of strategy: cooperator to defector',
        'probFunc' : rateMinus,
        'probFuncVars' : ['varVec','K','nodeStates[1]','N','nodeStates[2]','nodeStates[3]'],
        'oldState' : ['nodeStates[2]'],
        'newState' : ['nodeStates[3]']
    },
    {
        'description' : 'Resource uptake by cooperator',
        'probFunc' : uptakeRate,
        'probFuncVars' : ['varVec','N','extractionRates[0]','nodeStates[1]','nodeStates[2]'],
        'oldState' : ['nodeStates[1]'],
        'newState' : ['nodeStates[0]']
    },
    {
        'description' : 'Resource uptake by defector',
        'probFunc' : uptakeRate,
        'probFuncVars' : ['varVec','N','extractionRates[-1]','nodeStates[1]','nodeStates[3]'],
        'oldState' : ['nodeStates[1]'],
        'newState' : ['nodeStates[0]']
    },
    {
        'description': 'Change of strategy: defector to cooperator',
        'probFunc' : ratePlus,
        'probFuncVars' : ['varVec','K','nodeStates[1]','N','nodeStates[2]','nodeStates[3]'],
        'oldState' : ['nodeStates[3]'],
        'newState' : ['nodeStates[2]']
    }
]

# Tolerance for the evaluation of the extinction times
tolerance = 1e-3
# Number of agents
N = 200
# Harvesting rates and corresponding network node states (used within the code)
extractionRates_main = [0.7,np.arange(1.1,2+tolerance,(2-1.1)/2)]
# Each node represents either a consumer (cooperator or defector) or a slot of resource (full or empty)
nodeStates = [0,1,2,3]
stateLabels = ['hole','resource','cooperator','defector']
# Carrying capacity of resource in terms of number of quanta of resource
K = 5*N
# Resource's birth rate
birthRate_main = np.arange(1.,2.+tolerance,0.5)

# Settings for numerical simulations
# Initial conditions
x0 = 0.5
R0 = 0.5

# Length of the simulation
tMax = 100

# Number of repetitions of the simulation
NReps = 4

paramPairs = list(itertools.product(birthRate_main,extractionRates_main[1]))

# Settings for output
outputPath = 'output' 
if not os.path.isdir(outputPath):
    raise FileNotFoundError(f'Folder for the outputs not found at relative path: {outputPath}. Create it before running the program.')
outputDirMF = outputPath + '/MF/'
os.makedirs(outputDirMF, exist_ok=True)
outputDirDetRes = outputPath + '/detRes/'
os.makedirs(outputDirDetRes, exist_ok=True)
outputDirStocRes = outputPath + '/stocRes/'
os.makedirs(outputDirStocRes, exist_ok=True)

for pair in paramPairs:
    b = pair[0]
    extractionRates = [extractionRates_main[0],pair[1]]

    paramsDict = {
    'N' : N,
    'b' : b,
    'ehatC' : extractionRates[0],
    'ehatD' : extractionRates[1],
    'xi' : x0,
    'Ri' : R0
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
        'nodeStates' : nodeStates
    }

    # Taking from the context the parameter values used by solve_ivp
    paramsString = ['b','extractionRates']
    params = evalContextVar(paramsString,context)

    zSeries = scint.solve_ivp(HES,[0,tMax],[R0,x0],method='RK45',args=(params))

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

    fName = 'outMF_' + '_'.join(f"{key}{value:.2f}" for key, value in paramsDict.items()) + '.json'
    outputPathMF = outputDirMF + fName
    with open(outputPathMF, 'w') as f:
        json.dump(outputObj, f, indent = 2)

    #########
    # MIXED #
    #########

    zSeries = np.ones(N,dtype=int)
    zSeries[0:int(N*x0)] = setVec(zSeries[0:int(N*x0)],nodeStates[2])
    zSeries[int(N*x0):N] = setVec(zSeries[int(N*x0):N],nodeStates[3])

    seriesObj = []

    for kRep in range(NReps):
        context['R'] = R0
        context['varVec'] = zSeries

        kStep = 1
        tSim_temp = [0]
        vecSim_temp = [evalContextVar(['varVec'],context)[0]]
        RSim_temp = [evalContextVar(['R'],context)[0]]

        while tSim_temp[-1] < tMax:
            absState, objNew = GillespieStep(context,reactsCPRsust_homogeneous_detRes)
            if absState:
                break

            tProcess = objNew['t']
            tSim_temp.append(tSim_temp[-1] + tProcess)

            vecSim_temp.append(objNew['vec'])

            # Update the resource deterministically
            RNew = RNew_Gillespie(context,tProcess)
            RSim_temp.append(RNew)
            context['R'] = RNew
            # print('\tResource',RNew)

            # Increase counter
            kStep+=1
        
        seriesObj.append({
            'time' : tSim_temp,
            'cooperators' : [speciesFrac(z,nodeStates[2]) for z in vecSim_temp],
            'resource' : RSim_temp,
            'absorbing' : absState
            })
        
    outputObj = {
        'parameters' : paramsDict,
        'series' : seriesObj
    }
    
    fName = 'outDetRes_' + '_'.join(f"{key}{value:.2f}" for key, value in paramsDict.items()) + '.json'
    outputPathDetRes = outputDirDetRes + fName
    with open(outputPathDetRes, 'w') as f:
        json.dump(outputObj, f, indent = 2)

    ##############
    # STOCHASTIC #
    ############## 

    zSeries = np.ones(N+K,dtype=int)
    # Vector of individuals - assignment of initial conditions
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
            absState, objNew = GillespieStep(context,reactsCPRsust_homogeneous_stocRes)
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

    fName = 'outStocRes_' + '_'.join(f"{key}{value:.2f}" for key, value in paramsDict.items()) + '.json'
    outputPathStocRes = outputDirStocRes + fName
    with open(outputPathStocRes, 'w') as f:
        json.dump(outputObj, f, indent = 2)