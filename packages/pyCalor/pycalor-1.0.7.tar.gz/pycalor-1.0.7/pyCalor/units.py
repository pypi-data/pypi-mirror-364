"""
Created on Thu Dec 19 13:42:51 2024
Last modified: Dec 28, 2024

@author: mfrenklach
"""
import json

univR = 8.314472    # kJ/kmol_K
base = {'T':'K','P':'kPa','v':'m3/kg','u':'kJ/kg','h':'kJ/kg',
    's':'kJ/kg K','x':'fraction'}
ONEatm = 101.325;  # in kPa

showBase = lambda : print(json.dumps(base, indent=4))

def convertToBase(prop,val,units,molW=None):
    # value(baseUnits) = value(givenUnits) /|- factor
    factor = conversionFactor(prop,units,molW)
    if prop.lower() == 't':
        return val - factor
    else:
        return val / factor

def convertFromBase(prop,val,units,molW=None):
    # value(givenUnits) = value(baseUnits) *|+ factor
    factor = conversionFactor(prop,units,molW)
    if prop.lower() == 't':
        return val + factor
    else:
        return val * factor

def conversionFactor(prop,unitsGiven,molW):
    # value(baseUnits) *|+ f = value(givenUnits)
    match prop.lower():
        case 'p':
            match unitsGiven.lower():
                case "mpa":  f = 0.001
                case "bar":  f = 0.01
                case "atm":  f = 0.00986923
                case "kpa":  f = 1
                case "":     f = 1
                case "base": f = 1
                case "pa":   f = 1000
                case _:
                    raise ValueError("there is no units '" + unitsGiven + 
                                     "' for property " + prop)
        case 't':
            match unitsGiven.lower():
                case "c":    f = -273.16
                case "k":    f = 0
                case "":     f = 0
                case "base": f = 0
                case _:
                    raise ValueError("there is no units '" + unitsGiven + 
                                     "' for property " + prop)
        case 'v':
            match unitsGiven.lower():
                case "cm3/kg":   f = 1e+6
                case "cm3/g":    f = 1e+3
                case "l/kg":     f = 1e+3
                case "liter/kg": f = 1e+3
                case "m3/kg":    f = 1
                case "l/g":      f = 1
                case "":         f = 1
                case "base":     f = 1
                case _:
                    raise ValueError("there is no units '" + unitsGiven + 
                                     "' for property " + prop)
        case 'u'|'h':
            match unitsGiven.lower():
                case "kj/kg":    f = 1
                case "kj/g":     f = 1e-3
                case "j/kg":     f = 1e+3
                case "j/g":      f = 1
                case "":         f = 1
                case "base":     f = 1
                case "kj/kmol":  f = molW
                case "kj/mol":   f = molW/1000
                case "j/kmol":   f = molW*1000
                case "j/mol":    f = molW
                case _:
                    raise ValueError("there is no units '" + unitsGiven + 
                                     "' for property " + prop)
        case 's'|'cv'|'cp':
            match unitsGiven.lower():
                case "kj/kg k":   f = 1
                case "kj/g k":    f = 1e-3
                case "j/kg k":    f = 1e+3
                case "j/g k":     f = 1
                case "":          f = 1
                case "base":      f = 1
                case "kj/kmol k": f = molW
                case "kj/mol k":  f = molW/1000
                case "j/kmol k":  f = molW*1000
                case "j/mol k":   f = molW
                case _:
                    raise ValueError("there is no units '" + unitsGiven + 
                                     "' for property " + prop)
        case 'x':      # quality
            match unitsGiven.lower():
                case "":     f = 1
                case "base": f = 1
                case "%":    f = 100
                case _:
                    raise ValueError("there is no units '" + unitsGiven + 
                                     "' for property " + prop)
        case _:
            raise ValueError('prop exception: ', prop)
    return f