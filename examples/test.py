#%%
import sys
sys.path.insert(0, "..")

from pynoverb import rev3_binau, rev3_binau_hfdamp, get_n_from_r
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
#%matplotlib tk

l = np.array([4,3.5,3])
s = np.array([2,2,2])
x = np.array([2,1,1])
r = 0.95
d = 0.5
n = int(get_n_from_r(r))
l1,r1 = rev3_binau(n=n,fs=44100,l=l,s=s,x=x,r=r)
l2,r2 = rev3_binau_hfdamp(n=n,fs=44100,l=l,s=s,x=x,r=r,d=d)

fichier1 = 'nohfdamp.wav'
fichier2 = 'hfdamp.wav'
wavfile.write(fichier1,44100,np.array([l1,r1]).T)
wavfile.write(fichier2,44100,np.array([l2,r2]).T)

plt.semilogy(abs(l1))
#plt.plot(r1)
plt.semilogy(abs(l2))
#plt.plot(r2)

plt.show()

# %%
