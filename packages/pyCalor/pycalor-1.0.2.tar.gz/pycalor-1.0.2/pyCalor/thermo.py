"""
Created on Wed Dec 18, 2024
Modified   Jan  5, 2025: added plot function
Modified  June 19, 2025: added option to plot
Modified  July 14, 2025: added isoProp
Modified  July 21, 2025: added edge property "span"

@author: mfrenklach

"""

# import units
from . import units
# import plots
from . import plots
from . import utils
import CoolProp
import igraph as ig
import numpy as np

info = lambda : print(state.__doc__)

# propIndDict = {"P":"iP","T":"iT","D":"iDmass","V":"",
#            "U":"iUmass","H":"iHmass","S":"iSmass","X":"iQ","Q":"iQ"}
# propInd = lambda ind: getattr(CoolProp,propIndDict[ind])

class state:
    """stateObject = state(fluidName, property1=value1, property2, value2, name="A")
    
    fluidName = 'water, 'r134a', 'air', ''nitrogen', etc.
    proporty1 and property2 are two independent intensive properties
    value1 and value2 are propery values (in base units; see >>> th.state.units)
    
    Examples:
        >>> import thermo as th
        >>> th.state.units
        >>> st1 = th.state('water', p=(1,'bar'), v=0.1, name="1")
        >>> st1.plot("Pv")
        >>> st2 = th.state('R134a', x=1, t=300, name="B")
        >>> st2.plot("Ts",isoProp="v")    
        >>> st3 = th.state('air', p=(1,'Mpa'), t=(10,'c'))
        >>> st3.name = "2a"
    """
    fluidSet = {}        # container of fluid factories
    # phases = {0: "liquid", 1: "supercritical", 2: "supercritical_gas",
    #           3: "supercritical_liquid", 5: "gas", 6: "twophase"}
    phases = {0:"liquid", 1:"liquid", 2:"gas", 3:"liquid", 5:"gas", 6:"twophase"}
    units = units.base
    propList = ("p","t","v","u","h","s")
    
    def __init__(self,fluidName, **props):
        self.fluidName = fluidName
        if fluidName not in self.fluidSet:
            self.fluidSet[fluidName] = CoolProp.AbstractState("HEOS", fluidName)
        fluid = self.fluidSet[fluidName]
        self.name = ""
        argIn = ();
        for prop, val in props.items():
            if prop == "name":
                self.name = val
                continue
            if isinstance(val,(list,tuple)) and len(val)==2:
                valIn = units.convertToBase(prop,val[0],val[1],self.molW)
            else:
                valIn = val;
            propUp = prop.upper()
            match propUp:
                case 'P':
                    propIn = "iP"
                    valIn *= 1000;
                case 'T':
                    propIn = "iT"
                case 'V':
                    propIn = "iDmass"
                    valIn = 1/valIn
                case 'U'|'H'|'S':
                    propIn = "i" + propUp + "mass"
                    valIn *= 1000
                case 'X':
                    propIn = "iQ"
                case _:
                    raise ValueError("unmatched property " + prop)
            argIn += (getattr(CoolProp,propIn), valIn)
        propPair = CoolProp.CoolProp.generate_update_pair(*argIn)
        fluid.update(*propPair)
        self.T = fluid.T()
        self.p = fluid.p() * 0.001
        self.v = 1/fluid.rhomass()
        self.u = fluid.umass() * 0.001  # J to kJ
        self.h = fluid.hmass() * 0.001
        self.s = fluid.smass() * 0.001
        self.x = fluid.Q()
        self.cp = fluid.cpmass() * 0.001
        self.cv = fluid.cvmass() * 0.001
        self.phase = fluid.phase()
    
    def __str__(self):
        s = f"""
        {self.fluidName}: {self.phases[self.phase]+"   "+self.name}
        molar mass: {round(self.molW,3)}  (kg/kmol)
        R: {round(8.314/self.molW,3)}  (kJ/kg K)
        T: {round(self.T,2)}  (K)
        p: {round(self.p,2)}  (kPa)
        v: {round(self.v,4)}  (m3/kg)
        u: {round(self.u,1)}  (kJ/kg)
        h: {round(self.h,1)}  (kJ/kg)
        s: {round(self.s,4)}  (kJ/kg K)"""
        if self.x > -1.0:
            s += f"""\n        x: {round(self.x,3)}"""
        # s += f"""
        # cp: {round(self.cp,3)}  (kJ/kg K)
        # cv: {round(self.cv,3)}  (kJ/kg K)"""
        return s
    
    def plot(self, opt, isoProp=''):
        plots.plotState(self,opt,isoProp)
        
    @property
    def molW(self):
        return 1000 * self.fluidSet[self.fluidName].molar_mass()
    @property
    def R(self):
        return 8.314/self.molW
    @property
    def P(self):
        return self.p
    @property
    def t(self):
        return self.T
    @property
    def prop_array(self):
        return np.array([self.p,self.t,self.v,self.u,self.h,self.s])
    
class process:
    """pr = process([(state1,state2),(state2,state3),...])
    
    Examples:
        >>> import thermo as th
        >>> st1 = th.state('water', p=( 1,'bar'), x=0, name="A")
        >>> st2 = th.state('water', p=(20,'bar'), s=st1.s, name="B")
        >>> pr = process([st1,st2])
        >>> pr.plot("pv")
        >>> st3 = th.state('water', p=(20,'bar'), x=1,name="C")
        >>> st4 = th.state('water', p=( 1,'bar'), s=st3.s, name="D")
        >>> pr2 = th.process([(st1,st2),(st2,st3),(st3,st4),(st4,st1)])
        >>> pr2.plot("Ts")
    """
    def __init__(self, stateList, **props):
        if isinstance(stateList[0],(list,tuple)):
            # stEg = stateList[0]
            stList = []
            edges = []
            for eg in stateList:
                for st in eg:
                    if st not in stList:
                        stList.extend([st])
            n = len(stList)
            for eg in stateList:
                edges.append((stList.index(eg[0]),stList.index(eg[1])))
        else:
            stList  = stateList
            edges = []
            if stList[0] == stList[-1]:
                del stList[-1]
                n = len(stList)
                for i in range(n-1):
                    edges.append((i,i+1))
                    edges.append((n-1,0))
            else:
                n = len(stList)
                for i in range(n-1):
                    edges.append((i,i+1))
        self.StateList = stList
        g = ig.Graph(n,edges,directed=True)
        self.StateNet = g
        self.isoProps()
        
    def __str__(self):
        st = self.StateList
        g = self.StateNet
        names = [s.name for s in st[:]]
        s = ""
        for ei in g.es:
            props = ei["isoProp"]
            for prop, val in props.items():
                match prop.lower():
                    case 'p'|'t'|'u'|'h':
                        props[prop] = round(float(val), 1)
                    case 's'|'v'|'x':
                        props[prop] = round(float(val), 3)
            nami = [names[i] for i in ei.tuple]
            s += "process "+nami[0]+"-->"+nami[1]+"  isoProps:  "+str(props) + "\n"
        return s

    def isoProps(self):
        st = self.StateList
        g = self.StateNet
        for eg in g.es:
            yy = np.array([st[i].prop_array for i in eg.tuple])
            ave = np.mean(yy,axis=0)
            dd = np.abs(np.diff(yy,axis=0)) / ave
            pp = [(st[0].propList[i],ave[i]) for i in np.where(dd<0.001)[1].tolist()]
            eg["isoProp"] = dict(pp)
            eg["span"] = dd
            
    def isoProp(self,st1,st2):
        stList = self.StateList
        i1 = stList.index(st1); i2 = stList.index(st2)
        g = self.StateNet
        if g.are_connected(i1,i2):
            ieg = g.get_eid(i1,i2)
        else:
            return {}
        props = g.es[ieg]["isoProp"]
        for prop, val in props.items():
            match prop.lower():
                case 'p'|'t'|'u'|'h':
                    props[prop] = round(float(val), 1)
                case 's'|'v'|'x':
                    props[prop] = round(float(val), 3)
        return props
        
    def plot(self, opt='', isoProp=''):
        plots.plotProcess(self, opt)