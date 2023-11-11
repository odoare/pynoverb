# Test the parallel version of 
#%%
import sys
sys.path.insert(0, "..")

from pynoverb import rev3_binau_hfdamp, rev3_binau_hfdamp_par, writewav24
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
#%matplotlib tk
import time
import os

ncores = os.cpu_count()

l = np.array([4,3.5,3])
s = np.array([2,2,2])
x = np.array([2,1,1])
r = 0.95
d = 0.5
n = 50
nc=np.array(range(0,ncores))
print(nc)
t = np.zeros(ncores)

impl = {}
impr = {}

# Compute 1 time to compile numba function
impl[0],impr[0] = rev3_binau_hfdamp(n=10,fs=44100,l=l,s=s,x=x,r=r,d=d)
impl[0],impr[0] = rev3_binau_hfdamp_par(n=10,fs=44100,l=l,s=s,x=x,r=r,d=d,nc=nc[1])

start_time = time.time()
impl[0],impr[0] = rev3_binau_hfdamp(n=n,fs=44100,l=l,s=s,x=x,r=r,d=d)
t[0] = time.time() - start_time
for ic in range(1,ncores):
    print(str(ic)+'/'+str(nc[ic]))
    start_time = time.time()
    impl[ic],impr[ic] = rev3_binau_hfdamp_par(n=n,fs=44100,l=l,s=s,x=x,r=r,d=d,nc=nc[ic])
    t[ic] = time.time() - start_time

# fichier1 = 'parallel=False.wav'
# fichier2 = 'parallel=True.wav'

# #writewav24(fichier1,44100,np.array([impl1,impr1]).T)
# writewav24(fichier2,44100,np.array([impl2,impr2]).T)
# #print('Calculation time no parallel: '+str(t1))
for ic,nn in enumerate(nc):
    print('number of cores: '+str(nn))
    print('Calculation time parallel: '+str(t[ic]))
    plt.plot(impl[ic],label=str(ic)+' cores: '+'{0:.2f}'.format(t[ic]) )
plt.legend()
plt.title('Total number of cores: '+str(ncores)+'    Number of iterations: '+str(n))
plt.show()
plt.savefig("check_time_n="+str(n)+".svg")

# # %%
