"""
Created on Sun Jan  5, 2025
Modified: July 21, 2025

@author: mfrenklach

"""

import CoolProp
import CoolProp.CoolProp as CP
from CoolProp.Plots.SimpleCycles import StateContainer
from CoolProp.Plots import PropertyPlot
from matplotlib import pyplot as plt
# import thermo as th
from . import utils
import math
import numpy as np
import igraph as ig
import warnings
warnings.filterwarnings("ignore")

labDict = {"P":r'$P$ [kPa]', "T":r"$T$ [K]", "D":r'$\rho =1/v$ [kg/m$^3$]',
           "V":r'$v$ [m$^3$/kg]',"H":r'$h$ [kJ/kg]',"U":r'$u$ [kJ/kg]',"S": r'$s$ [kJ/kg K]'}
multDict= {"P":0.001,"T":1,"D":1,"V":1,"H":0.001,"U":0.001,"S":0.001}
propList= ['p','t','v','s','h','u']

def plotState(st, opt, isoProp=''):
    """ opt: 'Ts', 'Pv, 'Ph', 'PD''  """
    flName = st.fluidName
    fluid = st.fluid
    # if not (flName.lower()=="water" or flName.startswith("R" or "r")
    #         or flName.lower()=="ammonia"):
    if fluid.T_crtical() < 200:
        print("there is no need to plot a single state for a gas")
        return
    sc = StateContainer()
    
    optUP = opt.upper()
    match optUP:
        case 'TS':
            xlab = r'$s$ [kJ/kg K]'
            ylab = r"$T$ [K]"
            yfactor = 1
            isoProp0 = "P"
        case 'PH':
            xlab = r'$h$ [kJ/kg]'
            ylab = r'$P$ [kPa]'
            yfactor = 0.001
            isoProp0 = "T"
        case 'PD':
            xlab = r'$\rho =1/v$ [kg/m$^3$]'
            ylab = r'$P$ [kPa]'
            yfactor = 0.001
            isoProp0 = "T"
        case 'PV':
            xlab = r'$v$ [m$^3$/kg]'
            ylab = r'$P$ [kPa]'
            yfactor = 0.001
            isoProp0 = "T"
        case _:
            raise ValueError("option " + opt + " is not available")
            
    isoUP = isoProp.upper()
    if not isoProp:
        isoUP = isoProp0
        isoProp = isoProp0
    elif isoUP == "X":
        if st.x <= 0 or st.x >= 1:
            isoUP = ""
        else:
            isoUP = "Q"
    elif isoUP in optUP or isoUP in ["D","H","U"]:
        isoUP = ""
        
    sc[0,"T"] = st.T
    sc[0,"P"] = st.p
    sc[0,"D"] = 1/st.v
    sc[0,"U"] = st.u
    sc[0,"H"] = st.h
    sc[0,"S"] = st.s
    sc[0,"Q"] = st.x
            
    if optUP == "PV":
        pd_plot = PropertyPlot(flName, 'PD', unit_system="KSI", tp_limits='ORC')
        axesLim = pd_plot.get_axis_limits()
        pd_plot.calc_isolines(CoolProp.iQ, iso_range=[0,1], num=2)
        satL = pd_plot.isolines[CoolProp.iQ]
        i0, i1 = satL
        # plot sat lines
        # pd_plot.calc_isolines(CoolProp.iT, num=7)
        # isoL = pd_plot.isolines[CoolProp.iT]
        if isoUP:
            isoPropId = utils.propInd(isoUP)
            pd_plot.calc_isolines(isoPropId,[sc[0,isoUP]], num=1, rounding=False)
            isoL = pd_plot.isolines[isoPropId]
        pd_plot.figure.clear()
        plt.loglog(1/i0.x,yfactor*i0.y,1/i1.x,yfactor*i1.y)
        plt.xlim = [1/axesLim[1],1/ axesLim[0]]
        plt.title('Graph for ' + flName)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        if isoUP:
            j0 = isoL[-1]
            plt.loglog(1/j0.x,yfactor*j0.y,'g',lw=0.25)
            isoVal = sc[0,isoUP]
            nRnd = 4 - math.ceil(math.log10(isoVal))
            if nRnd < 1:
                legVal = round(isoVal)
            else:
                legVal = round(isoVal,nRnd)
            plt.legend([isoProp + "=" + str(legVal)])
        # plot the state point
        plt.loglog(st.v,st.p,'or')
        plt.show()
        return plt.gcf
    else:
        st_plot = PropertyPlot(flName, opt, unit_system="KSI", tp_limits='ORC')
        st_plot.calc_isolines(CoolProp.iQ, iso_range=[0,1], num=2)
        st_plot.title('Graph for ' + flName)
        st_plot.xlabel(xlab)
        st_plot.ylabel(ylab)
        if isoUP:
            if isoUP=="V":
                isoVal = 1/sc[0,"D"]
                st_plot.calc_isolines(CoolProp.iDmass,[sc[0,"D"]], num=1, rounding=False)
                st_plot.draw()
            else:
                isoPropId = utils.propInd(isoUP)
                isoVal = sc[0,isoUP]
                st_plot.calc_isolines(isoPropId,[sc[0,isoUP]], num=1, rounding=False)
                st_plot.draw()
            nRnd = 4 - math.ceil(math.log10(isoVal))
            if nRnd < 1:
                legVal = round(isoVal)
            else:
                legVal = round(isoVal,nRnd)
            hL = st_plot.axis.lines
            st_plot.axis.legend([hL[3]],[isoProp + "=" + str(legVal)])
        # plot the state point
        st_plot.axis.plot(sc[0,optUP[1]] ,sc[0,optUP[0]],'or')
        st_plot.show()

        
def plotProcess(pr, opt):
    optUP = opt.upper()
    plt.figure();
    xsc = "linear"; ysc = "linear"
    if optUP[0] in ("P","V","D"):
        plt.yscale('log'); ysc = "log"
    if optUP[1] in ("P","V","D"):
        plt.xscale('log'); xsc = "log"
    g = pr.StateNet
    if not opt:
        h = plt.figure().gca()
        ig.plot(g,target=h)
        return
    st = pr.StateList
    flName = st[0].fluidName
    fluid  = st[0].fluidSet[flName]
    # if (flName.lower()=="water" or flName.startswith("R" or "r")
    #         or flName.lower()=="ammonia"):      # draw sat lines
    if fluid.T_critical() > 200:
        T_critical = fluid.T_critical()
        T_triple = fluid.Ttriple()
        TT = np.linspace(T_triple + 0.1, T_critical, 100)
        xyLiq = getSatLine(fluid,0,TT,optUP)
        xyVap = getSatLine(fluid,1,TT,optUP)
        plt.plot(xyLiq[0],xyLiq[1],'b',xyVap[0],xyVap[1],'g')
        if optUP[0] in ("P","V","D"): plt.yscale('log')
        if optUP[1] in ("P","V","D"): plt.xscale('log')
            
    py,px = opt.lower()
    edges = g.es
    # nodes = g.vs
    ax = plt.gca()
    for eg in edges:
        xp,yp = getLine(fluid,st,eg,optUP)
        h = plt.plot(xp[1:],yp[1:],'r',lw=2)
        if len(xp) == 2:
            if xsc == "log":
                x1,x2 = np.geomspace(xp[0],xp[1],4)[1:3]
            else:
                x1,x2 = np.linspace(xp[0],xp[1],4)[1:3]
            if ysc == "log":
                y1,y2 = np.geomspace(yp[0],yp[1],4)[1:3]
            else:
                y1,y2 = np.linspace(yp[0],yp[1],4)[1:3]
            xy1 = [x1,y1]
            xy2 = [x2,y2]
        else:
            if abs(xp[1]-xp[-2])/np.mean(xp) >= abs(yp[1]-yp[-2])/np.mean(yp):
                if xsc == "log":
                    logx = np.log10(xp)
                    x2m = 10**np.mean([logx[0],logx[-1]])
                else:
                    x2m = np.mean([xp[0],xp[-1]])
                j = np.argmin(abs(xp-x2m))
            else:
                if ysc == "log":
                    logy = np.log10(yp)
                    y2m = 10**np.mean([logy[0],logy[-1]])
                else:
                    y2m = np.mean([yp[0],yp[-1]])
                j = np.argmin(abs(yp-y2m))
            xy1 = (xp[j],yp[j])
            xy2 = (xp[j+1],yp[j+1])
        plt.annotate("", xytext=xy1, xy=xy2,
                    arrowprops=dict(arrowstyle="->",
                                    facecolor='red',
                                    edgecolor='red',
                                    mutation_scale=20,
                                    lw=2))
    xp = [getattr(sti,px) for sti in st]
    yp = [getattr(sti,py) for sti in st]
    plt.scatter(xp,yp,color='red',marker='o',s=50, zorder=2)
    stLabels = [s.name for s in st]
    for i, txt in enumerate(stLabels):
        ax.annotate(
            txt,
            (xp[i], yp[i]),
            xytext=(xp[i] + 0.0, yp[i] + 1.0), # Slightly offset text
            transform=ax.transData,
            fontsize=18,
            fontweight="bold",
            color="darkviolet"
        )
    
    plt.title('fluid: ' + flName)
    plt.xlabel(labDict[optUP[1]])
    plt.ylabel(labDict[optUP[0]])
    plt.show()


def getSatLine(fluid,x,T,optUP):
    n = len(T)
    xy = np.zeros((n,2))
    for  i in range(n):
        fluid.update(CP.QT_INPUTS, x, T[i])
        for j in (0,1):
            axProp = optUP[j]
            if axProp == "V":
                xy[i,j] =  1/fluid.rhomass()
            elif axProp == "P":
                xy[i,j] = fluid.p()
            elif axProp in ("D","H","U","S"):
                xy[i,j] = getattr(fluid, axProp.lower()+"mass")()
            else:
                xy[i,j] = getattr(fluid,axProp)()
    x = xy[:,1] * multDict[optUP[1]]
    y = xy[:,0] * multDict[optUP[0]]
    return [x,y]


def getLine(fluid,st,eg,optUP):
    st1 = st[eg.source]
    st2 = st[eg.target]
    isoProp = eg["isoProp"]
    if not isoProp:
        py,px = optUP.lower()
        x = [getattr(st1,px), getattr(st2,px)]
        y = [getattr(st1,py), getattr(st2,py)]
        return x, y
    
    propSpan = eg["span"][0]
    def getVarProp(props):
        propi = [propList.index(i) for i in props]
        prop = props[np.argmax(propSpan[propi])]
        if prop == "v":
            propV = utils.propInd("D")
            varray = np.geomspace(1/st1.v,1/st2.v,200)
        elif prop == "t":
            propV = utils.propInd("T")
            varray = np.linspace(st1.t,st2.t,200)
        elif prop == "s":
            propV = utils.propInd("S")
            varray = np.linspace(st1.s,st2.s,200) *1000
        elif prop == "p":
            propV = utils.propInd("P")
            varray = np.geomspace(st1.p,st2.p,200) *1000
        elif prop == "h":
            propV = utils.propInd("H")
            varray = np.linspace(st1.h,st2.h,200) *1000
        return  propV, varray

    if "v" in isoProp:
        propIso = utils.propInd("D")
        valIso = 1/isoProp["v"]
        propVar, xx = getVarProp(["t","p"])
    elif "t" in isoProp:
        propIso = utils.propInd("T")
        valIso = isoProp["t"]
        # if twophase:
        propVar, xx = getVarProp(["v","s"])
        # else:
        #     propVar, xx = getVarProp(["v","s","p"])
    elif "p" in isoProp:
        propIso = utils.propInd("P")
        valIso = isoProp["p"] *1000
        # if twophase:
        propVar, xx = getVarProp(["v","s","h"])
        # else:
        #     propVar, xx = getVarProp(["v","s","t","h"])
    elif "s" in isoProp:
        propIso = utils.propInd("S")
        valIso = isoProp["s"] *1000
        propVar, xx = getVarProp(["t","p"])
    elif "h" in isoProp:
        propIso = utils.propInd("H")
        valIso = isoProp["h"] *1000
        ropVar, xx = getVarProp(["p"])
    n = len(xx)
    xy = np.zeros((n,2))
    for i in range(n):
        propPair = CP.generate_update_pair(propVar,xx[i],propIso,valIso)
        fluid.update(*propPair) 
        for j in (0,1):
            axProp = optUP[j]
            if axProp in ("V","D"):
                xy[i,j] =  1/fluid.rhomass()
            elif axProp == "P":
                xy[i,j] = fluid.p()
            elif axProp in ("H","U","S"):
                xy[i,j] = getattr(fluid, axProp.lower()+"mass")()
            else:
                xy[i,j] = getattr(fluid,axProp)()
    x = xy[:,1] * multDict[optUP[1]];
    y = xy[:,0] * multDict[optUP[0]];
    return x, y