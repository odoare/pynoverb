
# pynoverb/load_hrtf_mit_kemar.py
#
# -------------------------------------------------
# Imports HRTF
# -------------------------------------------------
#
# Part of pynoverb package
# (c) OD - 2023
# https://github.com/odoare/pynoverb


import numpy as np
import os
from .wavio import readwav

location = os.path.dirname(os.path.realpath(__file__))
datapath = location+'/hrtf/mit_kemar/'
# Load HRTFs
ELEVATIONS = np.array([-40,-30,-20,-10,0,10,20,30,40,50,60,70,80,90])
AZIMUTHSTEPS = np.array([6.43,6,5,5,5,5,5,6,6.43,8,10,15,30,360])
lmax = len(range(0,360,5))
#AZIMUTH = range(0,360,5)
#ELEVATION = 0
L = 128
NORM = 2**15
lhrtf = np.zeros((len(ELEVATIONS),lmax,L))
rhrtf = np.zeros((len(ELEVATIONS),lmax,L))
for ind1,el in enumerate(ELEVATIONS):
    #print(ind1)
    for ind2,az in enumerate(np.arange(0,360,AZIMUTHSTEPS[ind1])):
        chemin = datapath
        if az<=180:
            fich = chemin+'H'+str(el)+'e'+str(round(az)).zfill(3)+'a.wav'
            #print(fich)
            #fs,y = wavfile.read(fich)
            fs, sw, y = readwav(file=fich)
            # print(type(y))
            # print(y.max())
            lhrtf[ind1,ind2,:] = y[:,0]
            rhrtf[ind1,ind2,:] = y[:,1]
        else:
            try:
                fich = chemin+'H'+str(el)+'e'+str(int(np.round(360-az))).zfill(3)+'a.wav'
                #print(fich)
                # fs,y = wavfile.read(fich)
                fs, sw, y = readwav(file=fich)
                # print(type(y))
            except:
                fich = chemin+'H'+str(el)+'e'+str(int(np.round(360-az)+1)).zfill(3)+'a.wav'
                #print(fich)
                # fs,y = wavfile.read(fich)
                fs, sw, y = readwav(file=fich)
                # print(type(y))
            lhrtf[ind1,ind2,:] = y[:,1]
            rhrtf[ind1,ind2,:] = y[:,0]

lhrtf = lhrtf/NORM
rhrtf = rhrtf/NORM
