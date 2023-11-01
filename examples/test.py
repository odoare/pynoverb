import sys
sys.path.insert(0, "..")

from pynoverb import rev3_binau
import matplotlib.pyplot as plt
import numpy as np
#%matplotlib tk

l = np.array([3,3,3])
s = np.array([2,2,2])
x = np.array([1,1,1])
d = 0.9

l,r = rev3_binau(n=50,fs=44100,l=l,s=s,x=x,d=d)

plt.plot(l)
plt.plot(r)
plt.show()
