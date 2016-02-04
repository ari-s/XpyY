from scipy.signal import fftconvolve, gaussian
import numpy

def smoothen(x,y,M):
    '''returns v s.t. v[i] = array[i]*contribution + smoothen(array[:-i],contribution)*contribution'''
    window = gaussian(M=M,std=M/5)
    window /= window.sum()
    return (x,numpy.convolve(y,window,mode='same'))
