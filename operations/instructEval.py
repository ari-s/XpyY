import numpy
import keyword
import warnings
from . import operations
import collections

def base26(num):
    '''returns str(num) in base26 with roman letters as numerals'''
    n = num // 26
    d = chr(num%26+ord('a'))
    rv = ''
    if n: r=base26(n)
    return rv+d

def LetterColsFromArray(a):
    '''returns a dict with base26()->col mapping'''
    adict = { base26(i): v for i,v in enumerate(a) }
    # issue warning for hidden columns
    for k in adict:
        if k in keyword.kwlist:
            warnings.warn('column %s hidden by python keyword, use data[i]'%i)
    return adict

def instructEval(data, instructions):
    '''evals instructions with all columns from data available by their chr, i.e. a=data[0],...
    beware: a takes the role of zero, so col 26_{10}->ba_{26} unlike to e.g. M$ excel and alike'''

    if isinstance(data,numpy.ndarray):
        datadict = LetterColsFromArray(data)
    elif isinstance(data,dict):
        datadict = data
        #for k,d in data.items():
            #idDict = LetterColsFromArray(d)
            #dataMapping = collections.namedtuple('dataMapping',idDict.keys())
            #datadict[k] = dataMapping(**idDict)
    else: raise TypeError( "Can't handle data type %s"%(type(data)) )

    return eval(instructions,operations,datadict)
