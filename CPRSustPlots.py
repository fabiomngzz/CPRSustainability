import numpy as np
import copy
import matplotlib.pyplot as plt
import sys
sys.path.append('/Users/fabiomenegazzo/Documents/Università/codes')
from helpers import setVec

def rebuildContext(nodeStates,data,paramsLabel='parameters',seriesLabel='series'):
    paramsDict = data[paramsLabel]
    context = copy.copy(paramsDict)
    context['extractionRates'] = [context['eC'],context['eD']]
    context['nodeStates'] = nodeStates
    context['R'] = data[seriesLabel][0]['resource'][0]
    N = paramsDict['N']
    z = np.zeros(N,dtype=int)
    z[0:int(N*paramsDict['xi'])] = setVec(z[0:int(N*paramsDict['xi'])],nodeStates[2])
    z[int(N*paramsDict['xi']):N] = setVec(z[int(N*paramsDict['xi']):N],nodeStates[3])
    context['varVec'] = z
    context = paramsDict | context
    return context

def CPRSustStocSimPlot(plotsObj):
    figSim, axSim = plt.subplots(1,2,figsize=(16,8))
    for ax,plotObj in zip(axSim,plotsObj):
        ax.set_title(plotObj['name'])
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        ax.set_xlabel(plotObj['xlabel'])
        ax.set_ylabel(plotObj['ylabel'])
        ax.set_ylim(plotObj['yLims'])
        ax.plot(plotObj['xCommon'],plotObj['yMean'],color=plotObj['color'])
        for kRep in range(len(plotObj['x'])):
            ax.plot(plotObj['x'][kRep],plotObj['y'][kRep],plotObj['color'], alpha=0.1)
        ax.grid(which='both',linestyle=':',color='k',alpha=0.25)
    return figSim, axSim

def latexLabel(s):
    if s.startswith('ehat'):
        pedix = s[-1]
        return rf'$\hat{{e}}_{{{pedix}}}$'
    elif s == 'payoffThreshold':
        return r'$a_{min}$'
    else:
        return s

def CPRSustPhaseDiagram(xStat,RStat,tExt,paramLabels,paramsGrid,axPD=None,xStatLims=[0,1],RStatLims=[0,1],tExtLims=[0,None]):
    # Produce the grid of parameters for matplotlib
    p1_allVals = [d[paramLabels[0]] for d in paramsGrid]
    p2_allVals = [d[paramLabels[1]] for d in paramsGrid]
    p1_uniqueVals = np.unique(p1_allVals)
    p2_uniqueVals = np.unique(p2_allVals)
    p1Meshgrid, p2Meshgrid = np.meshgrid(p1_uniqueVals,p2_uniqueVals)

    # Initialize the lists for the values of the observables
    xStatGrid = np.full(p1Meshgrid.shape,np.nan)
    RStatGrid = copy.copy(xStatGrid)
    tExtGrid = copy.copy(xStatGrid)

    # Fill them
    for (p1, p2, xS, RS, tE) in zip(p1_allVals, p2_allVals, xStat, RStat, tExt):
        i = np.where(p1_uniqueVals == p1)[0][0]
        j = np.where(p2_uniqueVals == p2)[0][0]
        xStatGrid[j, i] = xS
        RStatGrid[j, i] = RS
        tExtGrid[j, i] = tE

    for i,l in enumerate(paramLabels):
        if l.startswith('e'):
            paramLabels[i] = 'N '+ paramLabels[i]
    paramLabels = [latexLabel(l) for l in paramLabels]

    # Plot
    if axPD is None:
        figPD, axPD = plt.subplots(1, 3, figsize=(20, 8))
    else:
        figPD = axPD[0].get_figure()

    PDxS = axPD[0].pcolormesh(p1Meshgrid,p2Meshgrid,xStatGrid,shading='auto',vmin=xStatLims[0],vmax=xStatLims[1])
    figPD.colorbar(PDxS, ax=axPD[0], label='x*')
    axPD[0].set_title('Fraction of cooperators')

    PDRS = axPD[1].pcolormesh(p1Meshgrid, p2Meshgrid, RStatGrid,vmin=RStatLims[0],vmax=RStatLims[1])
    figPD.colorbar(PDRS, ax=axPD[1], label='R*')
    axPD[1].set_title('Resource')

    PDtExt = axPD[2].pcolormesh(p1Meshgrid, p2Meshgrid, tExtGrid,vmin=tExtLims[0])
    figPD.colorbar(PDtExt, ax=axPD[2], label='$t_{ext}$')
    axPD[2].set_title('Time to TOC')

    for ax in axPD:
        ax.set_xlabel(paramLabels[0])
        ax.set_ylabel(paramLabels[1])
        ax.set_xticks(p1_uniqueVals)
        ax.set_yticks(p2_uniqueVals)
        ax.set_xticklabels([f'{val:.2f}' for val in p1_uniqueVals])
        ax.set_yticklabels([f'{val:.2f}' for val in p2_uniqueVals])
        ax.set_xlim([np.min(p1_uniqueVals),np.max(p1_uniqueVals)])
        ax.set_ylim([np.min(p2_uniqueVals),np.max(p2_uniqueVals)])
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        low  = min(xmin, ymin)
        high = max(xmax, ymax)
        ax.plot([low, high], [low, high],color='r',linestyle='--',linewidth=2)

    return figPD, axPD