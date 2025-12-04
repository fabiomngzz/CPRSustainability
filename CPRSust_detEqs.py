import numpy as np
import sys
sys.path.append('/Users/fabiomenegazzo/Documents/Università/codes')
from helpers import evalContextVar, getSubvec

def eqResourceLogistic_extensiveForm(R, x, b, eExt, N):
    return b*(R*(1-R)) - R*N*(x*eExt[0] + (1-x)*eExt[1])

def eqResourceLogistic_intensiveForm(R, x, b, ehat, K=1):
    return b*(R*(1-R/K) - R*(x*ehat[0] + (1-x)*ehat[1]))

def eqCommunity(R,x,w=1):
    return -w*R*x*(1-x)

def eqCommunity_knowledgeFeedback(R,x,b,e,N,K):
    return 1-R/(1-N*e/b)-x

# define the HES to be used with numpy.solve_ivp
def HES(t,z,b,extractionRates,N):
    R = z[0]
    x = z[1]
    return [eqResourceLogistic_extensiveForm(R, x, b, extractionRates,N),eqCommunity(R, x)]

def HES_knowledgeFeedback(t,z,b,extractionRates,N,K):
    R = z[0]
    x = z[1]
    return  [eqResourceLogistic_extensiveForm(R, x, b, extractionRates,N),eqCommunity_knowledgeFeedback(R,x,b,extractionRates[0],N,K)]


def RNew_Gillespie(context,Dt):
    N = evalContextVar(['N'],context)[0]
    b = evalContextVar(['b'],context)[0]
    R = evalContextVar(['R'],context)[0]
    z = evalContextVar(['varVec'],context)[0]
    x = len(getSubvec(z,evalContextVar(['nodeStates'],context)[0][2]))/len(z)
    extractionRates = evalContextVar(['extractionRates'],context)[0]
    harvestTerm = (x*extractionRates[0] + (1-x)*extractionRates[1])*N*R/b
    KEff = 1 - harvestTerm
    bEff = b * KEff
    A = (KEff-R)/R
    return KEff/(1 + A*np.exp(-bEff*Dt))