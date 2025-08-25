import sys
sys.path.append('/Users/fabiomenegazzo/Documents/Università/codes')
from helpers import countSpecies

def intrinsicResourceBirthRate(birthrate):
    return birthrate

def resEncounterFactor(vec,carryingCapacity,resourceState):
    NRes = countSpecies(vec,resourceState)
    return NRes*(1-NRes/carryingCapacity)

def resBirthRate(vec,birthrate,carryingCapacity,resourceState):
    return intrinsicResourceBirthRate(birthrate)*resEncounterFactor(vec,carryingCapacity,resourceState)

def consumersEncounterFraction(vec,N,coopState,defState):
    NCoops = countSpecies(vec,coopState)
    NDefs = countSpecies(vec,defState)
    return NCoops*NDefs/N

def pMinus(vec,carryingCapacity,resourceState):
    return 0.5*(1+countSpecies(vec,resourceState)/carryingCapacity)

def pMinus_detRes(resourceLevel):
    return 0.5*(1+resourceLevel)

def rateMinus_detRes(resourceLevel,vec,N,coopState,defState):
    return pMinus_detRes(resourceLevel)*consumersEncounterFraction(vec,N,coopState,defState)

def pPlus(vec,carryingCapacity,resourceState):
    return 0.5*(1-countSpecies(vec,resourceState)/carryingCapacity)

def pPlus_detRes(resourceLevel):
    return 0.5*(1-resourceLevel)

def ratePlus_detRes(resourceLevel,vec,N,coopState,defState):
    return pPlus_detRes(resourceLevel)*consumersEncounterFraction(vec,N,coopState,defState)

def intrinsicUptakeRate(vec,NTotAgents,extractionRate,agentState):
    agentsFrac = countSpecies(vec,agentState)/NTotAgents
    return extractionRate*agentsFrac

def uptakeRate(vec,NTotAgents,extractionRate,resourceState,agentState):
    NRes = countSpecies(vec,resourceState)
    return NRes*intrinsicUptakeRate(vec,NTotAgents,extractionRate,agentState)

def ratePlus(vec,carryingCapacity,resourceState,N,coopState,defState):
    return pPlus(vec,carryingCapacity,resourceState)*consumersEncounterFraction(vec,N,coopState,defState)

def rateMinus(vec,carryingCapacity,resourceState,N,coopState,defState):
    return pMinus(vec,carryingCapacity,resourceState)*consumersEncounterFraction(vec,N,coopState,defState)