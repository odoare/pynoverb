#%%
import numpy as np
from numba import njit,prange

from .load_hrtf_mit_kemar import L, ELEVATIONS, AZIMUTHSTEPS, lhrtf, rhrtf

@njit()
def azim(xp,x,rnd=5):
    """Azimuthal angle calculation

    Args:
        xp (float): Source poition ()
        x (float): Receiver position
        rth (float) : Receiver angle
        rnd (float) : Round around rnd

    Returns:
        int: Angle
    """
    return int(
            np.round(
                (np.arctan2(xp[1]-x[1],-xp[0]+x[0])*180/np.pi-90
                    )/rnd
                )*rnd)

@njit()
def azim_ind(xp,x,rnd=5):
    """
    Azimuthal angle index calculation
    Considering that the azimuthal HRTFs are given each rnd degrees,
    starting from zero, returns the index of the nearest HRTF

    Args:
        xp (float): Source poition
        x (float): Receiver position
        rnd (float) : Round around rnd

    Returns:
        int: Angle index
    """
    return int(
            np.round(
                (np.arctan2(xp[1]-x[1],-xp[0]+x[0])*180/np.pi-90
                    )/rnd
                ))-1

@njit()
def elev(xp,x,rnd=5):
    """Elevation angle calculation

    Args:
        xp (float): Source poition
        x (float): Receiver position
        rnd (float) : Round around rnd

    Returns:
        int: Angle
    """
    r = np.sqrt((xp[0]-x[0])**2+(xp[1]-x[1])**2)
    return int(
            np.round(
                (np.arctan2(xp[2]-x[2],r)*180/np.pi
                    )/rnd
                )*rnd)

@njit()
def elev_ind(xp,x):
    """Elevation angle index calculation

    Args:
        xp (float): Source poition
        x (float): Receiver position

    Returns:
        int: Angle
    """
    r = np.sqrt((xp[0]-x[0])**2+(xp[1]-x[1])**2)
    alpha = np.arctan2(xp[2]-x[2],r)*180/np.pi
    ind = np.argmin(np.abs(ELEVATIONS-alpha))
    return ind

def get_n_from_r(r):
    """Number of reflections for 100dB attenuation

    Args:
        r (float): Reflection coefficient

    Returns:
        float: Number of reflections
    """
    return np.log10(1e-5)/np.log10(r)

#%%
@njit(parallel=True)
def rev1(n=10,
         fs=44100,
         l=np.array((4)),
         s=np.array((1)),
         x=np.array((2)),
         r=1.):
    dur = (n+1)*l/340
    print(dur)
    long = int(np.ceil(dur*fs))
    print(long)
    out = np.zeros(long)
    xp = np.zeros(1)
    for i0 in prange(-n,n+1):
        xp = 2*np.ceil(i0/2)*l+(-1)**(i0)*s
        # print(xp[1])
        dist = abs(xp-x)
        # print(dist)
        time = dist/340
        # print(time)
        indice = int(np.round(time*fs))
        damp = r**abs(i0)
        out[indice] += (-1)**(i0)*damp
        print(str(i0)+'/'+str(2*n))
    return out

@njit(parallel=True)
def rev2(n=100,
         fs=44100,
         l=np.array((4,3)),
         s=np.array((1,2)),
         x=np.array((2,1)),
         r=0.9):
    """ 2D reverberator

    Args:
        n (int, optional): Number of rebounds. Defaults to 50.
        fs (int, optional): Sampling frequency. Defaults to 44100.
        l (numpy.array, optional): Room dimensions in meters. Defaults to np.array((4,3)).
        s (numpy.array, optional): Source position in meters. Defaults to np.array((1,2)).
        x (numpy.array, optional): Receiver position in meters. Defaults to np.array((2,1)).
        r (numpy.array, optional): Wall reflexion coef. Defaults to 0.9

    Returns:
        numpy.array: Acoustic impulse response from source to receiver
    """
    dur = np.sqrt(np.sum(((n+1)*l)**2))/340
    print(dur)
    long = int(np.ceil(dur*fs))
    print(long)
    out = np.zeros(long)
    xp = np.zeros(2)
    for i0 in prange(-n,n+1):
        xp[0] = 2*np.ceil(i0/2)*l[0]+(-1)**(i0)*s[0]
        for i1 in prange(-n,n+1):
            xp[1] = 2*np.ceil(i1/2)*l[1]+(-1)**(i1)*s[1]
            # print(xp[1])
            dist = np.sqrt((xp[0]-x[0])**2+(xp[1]-x[1])**2)
            # print(dist)
            time = dist/340
            # print(time)
            indice = int(np.round(time*fs))
            damp = r**(abs(i0)+abs(i1))
            out[indice] += (-1)**(i0+i1)*damp/dist**(3/4)
        print(str(i0)+'/'+str(2*n))
    return out

@njit(parallel=False)
def rev2_binau(n=100,
         fs=44100,
         l=np.array((4,3)),
         s=np.array((1,2)),
         x=np.array((2,1)),
         r=0.9):
    """
    2D reverberator, stereo, binaural version
    For each echo grain incoming to the receiver,
    an HRTF is applied based on the azimutal angle between
    head and beam direction.

    Args:
        n (int, optional): Number of rebounds. Defaults to 50.
        fs (int, optional): Sampling frequency. Defaults to 44100.
        l (numpy.array, optional): Room dimensions in meters. Defaults to np.array((4,3)).
        s (numpy.array, optional): Source position in meters. Defaults to np.array((1,2)).
        x (numpy.array, optional): Receiver position in meters. Defaults to np.array((2,1)).
        r (numpy.array, optional): Wall reflexion coef. Defaults to 0.9

    Returns:
        tuple: Acoustic impulse response from source to receiver in the form
        of a tuple of numpy arrays.
    """
    dur = np.sqrt(np.sum(((n+1)*l)**2))/340
    print(dur)
    long = int(np.ceil(dur*fs))
    print(long)
    outl = np.zeros(long+L)
    outr = np.zeros(long+L)
    xp = np.zeros(2)
    for i0 in prange(-n,n+1):
        xp[0] = 2*np.ceil(i0/2)*l[0]+(-1)**(i0)*s[0]
        for i1 in prange(-n,n+1):
            xp[1] = 2*np.ceil(i1/2)*l[1]+(-1)**(i1)*s[1]
            # print(xp[1])
            dist = np.sqrt((xp[0]-x[0])**2+(xp[1]-x[1])**2)
            # print(dist)
            time = dist/340
            # print(time)
            indice = int(np.round(time*fs))
            damp = r**(abs(i0)+abs(i1))
            outl[indice:indice+L] += lhrtf[azim_ind(xp,x),:]*(-1)**(i0+i1)*damp/dist**(3/4)
            outr[indice:indice+L] += rhrtf[azim_ind(xp,x),:]*(-1)**(i0+i1)*damp/dist**(3/4)
        print(str(i0)+'/'+str(2*n))
    return outl,outr

@njit()
def rev3_binau_noel(n=50,
         fs=44100,
         l=np.array((4,3,3.5)),
         s=np.array((1,2,3)),
         x=np.array((2,1,0.7)),
         r=0.9):
    """
    3D reverberator, stereo, binaural version
    For each echo grain incoming to the receiver,
    an HRTF is applied base on the azimutal angles
    between head and beam direction.
    This version ignores elevation angle. Use rev3_binau
    instead if elevation angle matters.

    Args:
        n (int, optional): Number of rebounds. Defaults to 50.
        fs (int, optional): Sampling frequency. Defaults to 44100.
        l (numpy.array, optional): Room dimensions in meters. Defaults to np.array((4,3)).
        s (numpy.array, optional): Source position in meters. Defaults to np.array((1,2)).
        x (numpy.array, optional): Receiver position in meters. Defaults to np.array((2,1)).
        r (numpy.array, optional): Wall reflexion coef. Defaults to 0.9

    Returns:
        tuple: Acoustic impulse response from source to receiver in the form
        of a tuple of numpy arrays.
    """
    dur = np.sqrt(np.sum(((n+1)*l)**2))/340
    print(dur)
    long = int(np.ceil(dur*fs))
    print(long)
    outl = np.zeros(long+L)
    outr = np.zeros(long+L)
    xp = np.zeros(3)
    for i0 in prange(-n,n+1):
        xp[0] = 2*np.ceil(i0/2)*l[0]+(-1)**(i0)*s[0]
        for i1 in prange(-n,n+1):
            xp[1] = 2*np.ceil(i1/2)*l[1]+(-1)**(i1)*s[1]
            for i2 in prange(-n,n+1):
                xp[2] = 2*np.ceil(i2/2)*l[2]+(-1)**(i2)*s[2]
                dist = np.sqrt((xp[0]-x[0])**2+(xp[1]-x[1])**2+(xp[2]-x[2])**2)
                # Starting index for rebound sound (time of arrival is dist/340)
                indice = int(np.round(dist/340*fs))
                damp = r**(abs(i0)+abs(i1)+abs(i2))
                outl[indice:indice+L] += lhrtf[4,azim_ind(xp[0:2],x[0:2]),:]*(-1)**(i0+i1+i2)*damp/dist
                outr[indice:indice+L] += rhrtf[4,azim_ind(xp[0:2],x[0:2]),:]*(-1)**(i0+i1+i2)*damp/dist
        print(str(i0)+'/'+str(2*n))
    return outl,outr

@njit()
def rev3_binau(n=100,
         fs=44100,
         l=np.array((4,3,3.5)),
         s=np.array((1,2,3)),
         x=np.array((2,1,0.7)),
         r=0.9):
    """
    3D reverberator, stereo, binaural version
    For each echo grain incoming to the receiver,
    an HRTF is applied base on the azimutal and elevation angles
    between head and beam direction.

    Args:
        n (int, optional): Number of rebounds. Defaults to 100.
        fs (int, optional): Sampling frequency. Defaults to 44100.
        l (numpy.array, optional): Room dimensions in meters. Defaults to np.array((4,3,3.5)).
        s (numpy.array, optional): Source position in meters. Defaults to np.array((1,2,3)).
        x (numpy.array, optional): Receiver position in meters. Defaults to np.array((2,1,0.7)).
        r (numpy.array, optional): Wall reflexion coef. Defaults to 0.9

    Returns:
        tuple: Acoustic impulse response from source to receiver in the form
        of a tuple of numpy arrays.
    """
    dur = np.sqrt(np.sum(((n+1)*l)**2))/340
    print(dur)
    long = int(np.ceil(dur*fs))
    print(long)
    outl = np.zeros(long+L)
    outr = np.zeros(long+L)
    xp = np.zeros(3)
    for i0 in prange(-n,n+1):
        xp[0] = 2*np.ceil(i0/2)*l[0]+(-1)**(i0)*s[0]
        for i1 in prange(-n,n+1):
            xp[1] = 2*np.ceil(i1/2)*l[1]+(-1)**(i1)*s[1]
            for i2 in prange(-n,n+1):
                xp[2] = 2*np.ceil(i2/2)*l[2]+(-1)**(i2)*s[2]
                dist = np.sqrt((xp[0]-x[0])**2+(xp[1]-x[1])**2+(xp[2]-x[2])**2)
                # Starting index for rebound sound (time of arrival is dist/340)
                indice = int(np.round(dist/340*fs))
                damp = r**(abs(i0)+abs(i1)+abs(i2))
                alpha_i = elev_ind(xp,x)
                outl[indice:indice+L] += lhrtf[alpha_i,azim_ind(xp[0:2],x[0:2],rnd=AZIMUTHSTEPS[alpha_i]),:]*(-1)**(i0+i1+i2)*damp/dist
                outr[indice:indice+L] += rhrtf[alpha_i,azim_ind(xp[0:2],x[0:2],rnd=AZIMUTHSTEPS[alpha_i]),:]*(-1)**(i0+i1+i2)*damp/dist
        print(str(i0)+'/'+str(2*n))
    return outl,outr

@njit(parallel=True)
def rev3(n=100,
         fs=44100,
         l=np.array((4,3,3.5)),
         s=np.array((1,2,3)),
         x=np.array((2,1,0.7)),
         r=1.):
    """
    3D reverberator, mono version.

    Args:
        n (int, optional): Number of rebounds. Defaults to 100.
        fs (int, optional): Sampling frequency. Defaults to 44100.
        l (numpy.array, optional): Room dimensions in meters. Defaults to np.array((4,3,3.5)).
        s (numpy.array, optional): Source position in meters. Defaults to np.array((1,2,3)).
        x (numpy.array, optional): Receiver position in meters. Defaults to np.array((2,1,0.7)).
        r (numpy.array, optional): Wall reflexion coef. Defaults to 0.9

    Returns:
        numpy array: Acoustic impulse response from source to receiver.
    """
    dur = np.sqrt(np.sum(((n+1)*l)**2))/340
    print(dur)
    long = int(np.ceil(dur*fs))
    print(long)
    out = np.zeros(long)
    xp = np.zeros(3)
    for i0 in prange(-n,n+1):
        xp[0] = 2*np.ceil(i0/2)*l[0]+(-1)**(i0)*s[0]
        for i1 in prange(-n,n+1):
            xp[1] = 2*np.ceil(i1/2)*l[1]+(-1)**(i1)*s[1]
            for i2 in prange(-n,n+1):
                xp[2] = 2*np.ceil(i2/2)*l[2]+(-1)**(i2)*s[2]
                # print(xp[1])
                dist = np.sqrt((xp[0]-x[0])**2+(xp[1]-x[1])**2+(xp[2]-x[2])**2)
                # print(dist)
                time = dist/340
                # print(time)
                indice = int(np.round(time*fs))
                damp = r**(abs(i0)+abs(i1)+abs(i2))
                if damp>1:
                    print(damp)
                out[indice] += (-1)**(i0+i1+i2)*damp/dist
        print(str(i0)+'/'+str(2*n))
    return out

@njit(parallel=True,nopython=True)
def rev4(n=50,
         fs=44100,
         l=np.array((4,3,3.5,3.8)),
         s=np.array((1,2,3,2.5)),
         x=np.array((2,1,0.7,3)),
         r=0.9):
    """
    4D, experimental reverberator, mono version.

    Args:
        n (int, optional): Number of rebounds. Defaults to 50.
        fs (int, optional): Sampling frequency. Defaults to 44100.
        l (numpy.array, optional): Room dimensions in meters. Defaults to np.array((4,3,3.5,3.8)).
        s (numpy.array, optional): Source position in meters. Defaults to np.array((1,2,3,2.5)).
        x (numpy.array, optional): Receiver position in meters. Defaults np.array((2,1,0.7,3)).
        r (numpy.array, optional): Wall reflexion coef. Defaults to 0.9

    Returns:
        numpy array: Acoustic impulse response from source to receiver.
    """
    dur = np.sqrt(np.sum(((n+1)*l)**2))/340
    print(dur)
    long = int(np.ceil(dur*fs))
    print(long)
    out = np.zeros(long)
    xp = np.zeros(4)
    for i0 in prange(-n,n+1):
        xp[0] = 2*np.ceil(i0/2)*l[0]+(-1)**(i0)*s[0]
        for i1 in prange(-n,n+1):
            xp[1] = 2*np.ceil(i1/2)*l[1]+(-1)**(i1)*s[1]
            for i2 in prange(-n,n+1):
                xp[2] = 2*np.ceil(i2/2)*l[2]+(-1)**(i2)*s[2]
                for i3 in prange(-n,n+1):
                    xp[3] = 2*np.ceil(i3/2)*l[3]+(-1)**(i3)*s[3]
                    # print(xp[1])
                    dist = np.sqrt((xp[0]-x[0])**2+(xp[1]-x[1])**2+(xp[2]-x[2])**2+(xp[3]-x[3])**2)
                    # print(dist)
                    time = dist/340
                    # print(time)
                    indice = int(np.round(time*fs))
                    damp = r**(abs(i0)+abs(i1)+abs(i2)+abs(i3))
                    out[indice] += (-1)**(i0+i1+i2+i3)*damp/dist**(4/3)
        print(str(i0)+'/'+str(2*n))
    return out
