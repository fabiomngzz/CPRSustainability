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

def normalisedResourceLevel_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate):
    return countSpecies(vec,resourceState)/(carryingCapacity*(1-NAgents*extractionRateCoop/intrinsicResourceBirthRate(birthrate)))

def consumersEncounterFraction(vec,N,coopState,defState):
    NCoops = countSpecies(vec,coopState)
    NDefs = countSpecies(vec,defState)
    return NCoops*NDefs/N

def pMinus(vec,carryingCapacity,resourceState):
    return 0.5*(1+countSpecies(vec,resourceState)/carryingCapacity)

def rateMinus(vec,carryingCapacity,resourceState,N,coopState,defState):
    return pMinus(vec,carryingCapacity,resourceState)*consumersEncounterFraction(vec,N,coopState,defState)

def pMinus_knowledgeFeedback_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate):
    return normalisedResourceLevel_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate)

def rateMinus_knowledgeFeedback_stocRes(vec,coopState,resourceState,birthrate,carryingCapacity,NAgents,extractionRateCoop):
    NCoops = countSpecies(vec,coopState)
    return NCoops*pMinus_knowledgeFeedback_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate)

def rateMinus_kFpP_stocRes(vec,coopState,defState,resourceState,birthrate,carryingCapacity,NAgents,extractionRateCoop):
    NCoops = countSpecies(vec,coopState)
    NDefs = countSpecies(vec,defState)
    return NCoops*NDefs*pMinus_knowledgeFeedback_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate)/NAgents

def pMinus_detRes(resourceLevel):
    return 0.5*(1+resourceLevel)

def rateMinus_detRes(resourceLevel,vec,N,coopState,defState):
    return pMinus_detRes(resourceLevel)*consumersEncounterFraction(vec,N,coopState,defState)

def pPlus(vec,carryingCapacity,resourceState):
    return 0.5*(1-countSpecies(vec,resourceState)/carryingCapacity)

def ratePlus(vec,carryingCapacity,resourceState,N,coopState,defState):
    return pPlus(vec,carryingCapacity,resourceState)*consumersEncounterFraction(vec,N,coopState,defState)

def pPlus_knowledgeFeedback_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate):
    return 1 - normalisedResourceLevel_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate)

def ratePlus_knowledgeFeedback_stocRes(vec,defState,resourceState,birthrate,carryingCapacity,NAgents,extractionRateCoop):
    NDefs = countSpecies(vec,defState)
    return NDefs*pPlus_knowledgeFeedback_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate)

def ratePlus_kFpP_stocRes(vec,coopState,defState,resourceState,birthrate,carryingCapacity,NAgents,extractionRateCoop):
    NCoops = countSpecies(vec,coopState)
    NDefs = countSpecies(vec,defState)
    return NCoops*NDefs*pPlus_knowledgeFeedback_stocRes(vec,carryingCapacity,NAgents,resourceState,extractionRateCoop,birthrate)/NAgents

def pPlus_detRes(resourceLevel):
    return 0.5*(1-resourceLevel)

def ratePlus_detRes(resourceLevel,vec,N,coopState,defState):
    return pPlus_detRes(resourceLevel)*consumersEncounterFraction(vec,N,coopState,defState)

def intrinsicUptakeRate(vec,extractionRate,agentState):
    NAgents = countSpecies(vec,agentState)
    return extractionRate*NAgents

def uptakeRate(vec,extractionRate,resourceState,agentState):
    NRes = countSpecies(vec,resourceState)
    return NRes*intrinsicUptakeRate(vec,extractionRate,agentState)

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
        'probFuncVars' : ['varVec','extractionRates[0]','nodeStates[1]','nodeStates[2]'],
        'oldState' : ['nodeStates[1]'],
        'newState' : ['nodeStates[0]']
    },
    {
        'description' : 'Resource uptake by defector',
        'probFunc' : uptakeRate,
        'probFuncVars' : ['varVec','extractionRates[-1]','nodeStates[1]','nodeStates[3]'],
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

reactsCPRsust_homogeneous_knowledgeFeedback_stocRes = [
    {
        'description': 'Offspring of resource',
        'probFunc' : resBirthRate,
        'probFuncVars' : ['varVec','b','K','nodeStates[1]'],
        'oldState' : ['nodeStates[0]'],
        'newState' : ['nodeStates[1]']
    },
    {
        'description': 'Change of strategy: cooperator to defector',
        'probFunc' : rateMinus_knowledgeFeedback_stocRes,
        'probFuncVars' : ['varVec','nodeStates[2]','nodeStates[1]','b','K','N','extractionRates[0]'],
        'oldState' : ['nodeStates[2]'],
        'newState' : ['nodeStates[3]']
    },
    {
        'description' : 'Resource uptake by cooperator',
        'probFunc' : uptakeRate,
        'probFuncVars' : ['varVec','extractionRates[0]','nodeStates[1]','nodeStates[2]'],
        'oldState' : ['nodeStates[1]'],
        'newState' : ['nodeStates[0]']
    },
    {
        'description' : 'Resource uptake by defector',
        'probFunc' : uptakeRate,
        'probFuncVars' : ['varVec','extractionRates[-1]','nodeStates[1]','nodeStates[3]'],
        'oldState' : ['nodeStates[1]'],
        'newState' : ['nodeStates[0]']
    },
    {
        'description': 'Change of strategy: defector to cooperator',
        'probFunc' : ratePlus_knowledgeFeedback_stocRes,
        'probFuncVars' : ['varVec','nodeStates[3]','nodeStates[1]','b','K','N','extractionRates[0]'],
        'oldState' : ['nodeStates[3]'],
        'newState' : ['nodeStates[2]']
    }
]

reactsCPRsust_homgeneous_kFpP_stocRes = [
    {
        'description': 'Offspring of resource',
        'probFunc' : resBirthRate,
        'probFuncVars' : ['varVec','b','K','nodeStates[1]'],
        'oldState' : ['nodeStates[0]'],
        'newState' : ['nodeStates[1]']
    },
    {
        'description': 'Change of strategy: cooperator to defector',
        'probFunc' : rateMinus_kFpP_stocRes,
        'probFuncVars' : ['varVec','nodeStates[2]','nodeStates[3]','nodeStates[1]','b','K','N','extractionRates[0]'],
        'oldState' : ['nodeStates[2]'],
        'newState' : ['nodeStates[3]']
    },
    {
        'description' : 'Resource uptake by cooperator',
        'probFunc' : uptakeRate,
        'probFuncVars' : ['varVec','extractionRates[0]','nodeStates[1]','nodeStates[2]'],
        'oldState' : ['nodeStates[1]'],
        'newState' : ['nodeStates[0]']
    },
    {
        'description' : 'Resource uptake by defector',
        'probFunc' : uptakeRate,
        'probFuncVars' : ['varVec','extractionRates[-1]','nodeStates[1]','nodeStates[3]'],
        'oldState' : ['nodeStates[1]'],
        'newState' : ['nodeStates[0]']
    },
    {
        'description': 'Change of strategy: defector to cooperator',
        'probFunc' : ratePlus_kFpP_stocRes,
        'probFuncVars' : ['varVec','nodeStates[2]','nodeStates[3]','nodeStates[1]','b','K','N','extractionRates[0]'],
        'oldState' : ['nodeStates[3]'],
        'newState' : ['nodeStates[2]']
    }
]