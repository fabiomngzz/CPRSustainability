import numpy as np
import sys
sys.path.append('/Users/fabiomenegazzo/Documents/Università/codes')
from helpers import evalContextVar, getSubvec


def eq_resource_logistic(R, x, b, ehat, K=1):
    return b*(R*(1-R/K) - R*(x*ehat[0] + (1-x)*ehat[1]))

def eq_strategy(R,x,w=1):
    return -w*R*x*(1-x)

# define the HES to be used with numpy.solve_ivp
def HES(t,z,b,extractionRates):
    R = z[0]
    x = z[1]
    return [eq_resource_logistic(R, x, b, extractionRates),eq_strategy(R, x)]


def RNew_Gillespie(context,Dt):
    b = evalContextVar(['b'],context)[0]
    R = evalContextVar(['R'],context)[0]
    z = evalContextVar(['varVec'],context)[0]
    x = len(getSubvec(z,evalContextVar(['nodeStates'],context)[0][1]))/len(z)
    extractionRates = evalContextVar(['extractionRates'],context)[0]
    harvestTerm = x*extractionRates[0] + (1-x)*extractionRates[1]
    KEff = 1 - harvestTerm
    bEff = b * KEff
    A = (KEff-R)/R
    return KEff/(1 + A*np.exp(-bEff*Dt))