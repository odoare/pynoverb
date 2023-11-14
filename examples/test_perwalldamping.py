#%%
import sys
sys.path.insert(0, "..")

from pynoverb import rev3_binau_hfdamp_perwalldamp_par, get_n_from_r
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
%matplotlib tk

l = np.array([4,3.5,3])
s = np.array([0.5,2,2])
x = np.array([2,1,1])
r = np.array([0.9, 0.9, 0.9, 0.8, 0.9, 0.8])
d = 0.5
n = int(get_n_from_r(max(r)))
l,r = rev3_binau_hfdamp_perwalldamp_par(n=n,fs=44100,l=l,s=s,x=x,r=r,d=d)

wavfile.write("ir_pwalsamp.wav",44100,np.array([l,r]).T)

plt.plot(l)
plt.show()

# %%
