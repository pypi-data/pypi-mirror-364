# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 10:52:29 2025
Modified: July 21, 2025

@author: mfren
"""


import thermo as th
import matplotlib.pyplot as plt

st1 = th.state('water', p=( 1,'bar'), x=0, name="A")
st2 = th.state('water', p=(20,'bar'), s=st1.s,name="B")
st3 = th.state('water', p=(20,'bar'), x=1,name="C")
st4 = th.state('water', p=( 1,'bar'), s=st3.s, name="D")
pr = th.process([(st1,st2),(st2,st3),(st3,st4),(st4,st1)])
pr.plot("pv")


plt.figure
sub = 'air'
st5 = th.state(sub, p=(1,'bar'), t=300, name="1")
st6 = th.state(sub, p=(2,'Mpa'), s=st5.s, name="2")
st7 = th.state(sub, p=(2,'Mpa'), t=1600, name="3")
st8 = th.state(sub, p=(1,'bar'), s=st7.s)
st8.name = "4"
pr = th.process([st5, st6, st7, st8, st5])
pr.plot("ts")