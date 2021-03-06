#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sep 2018
    
@author: BH @ BNU
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

#Units
#import astropy.units as u
#from astropy.units import deg

#file name
unlensed_spectra_filename = './lcdm_scalCls.dat'

##-------parameter setting-----------##

#number of pixel
n_sides = 512
#field degree (have to be a squared field)
field_deg = 100
#number of ell bins
nbins = n_sides
#comoving distance
chi = 14000.0 #in the unit of [Mpc]


##------------------##

#reading the spectrum data
unlensed_spectra = np.loadtxt(unlensed_spectra_filename)
#print(unlensed_spectra.shape[0])
ell = np.zeros(unlensed_spectra.shape[0])
TT_unlensed = np.zeros(unlensed_spectra.shape[0])
ell[0:len(ell)] = unlensed_spectra[:,0]
TT_unlensed[0:len(ell)] = unlensed_spectra[:,1]/unlensed_spectra[:,0]/(unlensed_spectra[:,0]+1)*2.0*np.pi
np.savetxt('try1.dat', np.c_[ell,TT_unlensed], fmt='%1.4e')

#pixelization setup

l_min = 360.0/field_deg #ell minimum ell=2pi/theta
l_max = n_sides * l_min
#sample y-axis n_sides frequencies in the range of (-l_amx/2, l_max/2)
ly = np.fft.fftfreq(n_sides)*l_max #* l_max
#sample x-axis only need half of the frequency domain (due to numpy.fft convention)
#the input of real ifft, is a (N,N/2+1) with N=n_sides, complex matrix
#since it is the real discrete fourier transform, we only need to sample the zero- and positive- frequencies by rfftfreq. Hence, actually, we only sample (0,l_max/2)
lx = np.fft.rfftfreq(n_sides)*l_max

#print(lx.shape)
#print(ly.shape)

#Compute the multipole moment of each FFT pixel
#l is N*(N/2+1) complex matrix, with N=n_sides
#each component in the l matrix is the module of wave vectors
l = np.sqrt(lx[np.newaxis,:]**2 + ly[:,np.newaxis]**2)
#print(l.shape)

#Perform the interpolation, the interpolation range may outof bound of sampling points
power_interp = interpolate.interp1d(ell,TT_unlensed,bounds_error=False,kind='linear',fill_value=0.0)
Pl = power_interp(l)

#test suite: generate the same random variable set every time
np.random.seed(1)

#Generate real and imaginary parts
#bh: not sure about the scaling factor: l_min/(2.0*np.pi)
real_part = np.sqrt(0.5*Pl) * np.random.normal(loc=0.0,scale=1.0,size=l.shape)
imaginary_part = np.sqrt(0.5*Pl) * np.random.normal(loc=0.0,scale=1.0,size=l.shape)
#print(real_part.shape)

llist = l.flatten()
#print(llist)
norm, bins = np.histogram(llist, bins=nbins)
#norm[ np.where(norm != 0.0) ] = 1./norm[ np.where(norm != 0.0) ]
norm = 1./(norm + 0.00001)
#print(norm)
#print(bins)
#cltt, bins = np.histogram(llist, bins=nbins, weights=(np.sqrt(real_part**2+imaginary_part**2)).flatten())
cltt, bins = np.histogram(llist, bins=nbins, weights=(real_part**2+imaginary_part**2).flatten())
cltt *= norm
#print(cltt)
#print(bins)
np.savetxt('cl.dat', np.c_[bins[1:],cltt])
quit()

#Get map in real space and return
#bh: not sure about the scaling factor: l.shape[0]**2
ft_map = (real_part + imaginary_part*1.0j)
#print(ft_map.shape)

#ft_map is a (N,N/2+1) complex matrix, noise_map is a (N,N) matrix
noise_map = np.fft.irfft2(ft_map)

np.savetxt('map_data.dat', noise_map)

'''
#testing visualization
map_data_path = './map_data.dat'
map_data = np.loadtxt(map_data_path)
plt.imshow(map_data)
'''

plt.imshow(noise_map,cmap='bwr',vmin=-1e-4,vmax=1e-4)
#plt.imshow(noise_map)
#plt.show()

plt.axis('off')
plt.colorbar()
plt.savefig('map.png')

exit()
