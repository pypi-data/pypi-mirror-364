import CoolProp

propIndDict = {"P":"iP","T":"iT","D":"iDmass","V":"",
            "U":"iUmass","H":"iHmass","S":"iSmass","X":"iQ","Q":"iQ"}
propInd = lambda ind: getattr(CoolProp,propIndDict[ind])