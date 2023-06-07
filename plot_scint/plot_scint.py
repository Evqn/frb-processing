import numpy as np
from collections import deque
from itertools import islice
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import click
import glob
import os
import re
from multiprocessing import Pool

#################
##  SMOOTHING  ##
#################

def moving_average(dat, n=100):
    it = iter(dat)
    d = deque(islice(it, n-1))
    d.appendleft(0)
    s = np.sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield s / float(n)

def moving_average_full(dat, n=100):
    ma = np.array([ ii for ii in moving_average(dat, n) ])
    front_pad = (len(dat) - len(ma)) // 2
    back_pad  = len(dat) - front_pad - len(ma)
    ma = np.hstack( (np.hstack((np.zeros(front_pad), ma)),
                     np.zeros(back_pad)) )
    return ma

def rebin(x, nbins=1024, strip_pad=False):
    avgkern = int(len(x) / nbins)
    avgx = moving_average_full(x, n=avgkern)
    tt0 = np.linspace(0, 1, len(avgx))
    tt1 = np.linspace(0, 1, nbins)
    nx = np.interp(tt1, tt0, avgx)
    if strip_pad:
        if nx[0] == 0:
            nx = nx[1:]
        if nx[-1] == 0:
            nx = nx[:-1]
    return nx

def rebin_spec(freqs, spec, dsfac=1, strip_pad=True):
    N = len(freqs)
    nbins = int( N / dsfac )
    afreqs = rebin(freqs, nbins=nbins, strip_pad=strip_pad)
    aspec  = rebin(spec, nbins=nbins, strip_pad=strip_pad)
    return afreqs, aspec

def rebin2(x, avgkern=1):
    nbins = int(len(x) / avgkern)
    avgx = moving_average_full(x, n=avgkern)
    tt0 = np.linspace(0, 1, len(avgx))
    tt1 = np.linspace(0, 1, nbins)
    nx = np.interp(tt1, tt0, avgx)
    return nx



##########
## ACFS ##
##########

def calc_acf(x):
    a = np.correlate(x, x, mode='full')
    return a[len(a)//2:]

def calc_ccf(x, z):
    a = np.correlate(x, z, mode='full')
    N = len(z)
    lags = np.arange(-1 * N + 1, N, 1)
    return lags, a

def fft_conv(a, b):
    cc = np.fft.irfft( np.fft.rfft(a) * np.fft.rfft(b) )
    cc /= np.sum(b)
    return cc

def calc_norm_acf(x, y, normbin=-1):
    a = calc_acf(y)
    lags = np.abs(x - x[0])
    if normbin > -1:
        a = a / a[int(normbin)]
    return lags, a


##############
## SPEC ACF ##
##############

def spec_acf(freqs, spec, normbin=1):
    """
    calculate spectrum acf 
    """
    m = np.mean(spec)
    lags, acf = calc_norm_acf(freqs, spec-m, normbin=normbin)
    return lags, acf


def pulse_acf(tt, prof, normbin=1):
    """
    calculate pulse acf 
    """
    m = np.mean(prof)
    lags, acf = calc_norm_acf(tt, prof-m, normbin=normbin)
    return lags, acf


def simple_scint_bw(freqs, spec):
    """
    Calc scint bw as 1/e point of ACF
    """
    # Calc ACF and normalize so ACF(0) = 1
    lags, acf = spec_acf(freqs, spec, normbin=0)

    # Find first instance where ACF(x) <= 1/e
    xx = np.where( acf <= 1/np.e )[0][0]

    sbw = lags[xx] 

    return lags, acf, sbw


def simple_pulse_acf(tt, prof):
    """
    Calc char width as 1/e point of ACF
    """
    # Calc ACF and normalize so ACF(0) = 1
    lags, acf = pulse_acf(tt, prof, normbin=1)

    # Find first instance where ACF(x) <= 1/e
    xx = np.where( acf <= 1/np.e )[0][0]

    w = lags[xx] 

    return lags, acf, w


def scint_plot(freqs, spec, out_file):
    """
    Make a plot of the spectrum + ACF
    """
    fig = plt.figure()
    
    ax_s = fig.add_subplot(211)
    ax_a = fig.add_subplot(212)

    lags, acf, sbw = simple_scint_bw(freqs, spec)

    fs = 12

    # Spec plot
    ax_s.plot(freqs, spec)  
    smax = np.max(spec)
    fmid = np.mean(freqs)
    ax_s.errorbar(fmid, 0.9 * smax, xerr=sbw/2., 
                  marker='', capsize=3, capthick=1.5, 
                  color='r')



    ax_s.set_xlim(np.min(freqs), np.max(freqs))
    ax_s.set_xlabel("Frequency (MHz)", fontsize=fs)
    ax_s.set_ylabel("Flux Density (arb)", fontsize=fs)
    

    # ACF
    ax_a.plot(lags, acf, marker='o')
    ax_a.set_xlim(0, lags[-1])
    ax_a.axvline(x=sbw, ls='--', c='k')
    ax_a.set_xlabel("Frequency Lag (MHz)", fontsize=fs)
    ax_a.set_ylabel("ACF", fontsize=fs)

    sbw_str = r"$\Delta \nu_{\rm s} = %.1f\, {\rm MHz}$" %sbw
    ax_a.text(0.9, 0.8, sbw_str, ha='right', va='top', 
              transform=ax_a.transAxes, fontsize=16)
    plt.savefig(out_file)

    return sbw
     

def pulse_plot(tt, prof):
    """
    Make a plot of the pulse + ACF
    """
    fig = plt.figure()
    
    ax_s = fig.add_subplot(211)
    ax_a = fig.add_subplot(212)

    lags, acf, w = simple_pulse_acf(tt, prof)

    fs = 12

    # Pulse plot
    ax_s.plot(tt, prof)  
    smax = np.max(prof)
    tplt = tt[ int( 0.25 * len(tt)) ]
    ax_s.errorbar(tplt, 0.9 * smax, xerr=w/2., 
                  marker='', capsize=3, capthick=1.5, 
                  color='r')



    ax_s.set_xlim(tt[0], tt[-1])
    ax_s.set_xlabel("Time (ms)", fontsize=fs)
    ax_s.set_ylabel("Flux Density (arb)", fontsize=fs)
    

    # ACF
    ax_a.plot(lags, acf)
    ax_a.set_xlim(0, lags[-1])
    ax_a.axvline(x=w, ls='--', c='k')
    ax_a.set_xlabel("Time Lag (ms)", fontsize=fs)
    ax_a.set_ylabel("ACF", fontsize=fs)

    sbw_str = "Width = %.1f ms" %w
    ax_a.text(0.9, 0.8, sbw_str, ha='right', va='top', 
              transform=ax_a.transAxes, fontsize=16)

    plt.show()

    return w
     
    
def process_file(args):
    file, freq_band, bw, png_dir = args
    dat = np.load(file)
    print(dat.shape)
    spec = np.mean(dat, axis=0)

    # find number of channels
    match = re.search("n(\d+)", file)
    nchan = int(match.group(1)) 

    if freq_band == "x":
        fhi = 8336.0
    else:  # it's s
        fhi = 2250.0

    freqs = fhi - np.arange(nchan) * bw / nchan

    # extract basename
    basename = os.path.basename(file)
    basename = os.path.splitext(basename)[0]


    _ = scint_plot(freqs, spec, '%s/%s_scint.png' % (png_dir, basename))

@click.command()
@click.option("--out_dir", type=str,
             help="Out directory", required=True)
@click.option("--npy_dir", type=str,
              help='Dir of *npy file', required=True)
@click.option("--png_dir", type=str, 
              help="Dir of *png file", required=True)
@click.option("--npy_base", type=str, 
              help="basename of *npy files", required=True)
@click.option("--freq_band", type=str, 
              help="frequency band", required=True)
@click.option("--bw", type=float, default=128.0, 
              help="bandwidth", required=False)
def run(out_dir, npy_dir, png_dir, npy_base, freq_band, bw=128.0):
    npy_files = glob.glob('%s%s/%s*npy' % (out_dir, npy_dir, npy_base))
    # Create a pool of workers
    print(npy_files)
    with Pool() as p:
        p.map(process_file, [(file, freq_band, bw, '%s/%s' % (out_dir, png_dir)) for file in npy_files])

debug = 0

if __name__ == "__main__":
    if not debug: 
        run()
