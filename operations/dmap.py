from . import *
import numpy
import warnings

def dmap(data,funcs):
    if isinstance(funcs,dict):
        for k, v in funcs.items():
            data[k] = dmap(v,funcs[k])
    else:
        for i,(col,f) in enumerate(zip(data,funcs)):
            if isinstance(f,(int,float,complex)):
                data[i]*=f
            elif callable(f):
                try: data[i] = f(col)
                except TypeError:
                    warnings.warn('dmap: funcs[%i] could not be applied, retry elementwise'%i)
                    data[i] = numpy.array(list(map(f,col)))

    return data

