import numpy
import keyword
import warnings

def base26(num):
    '''returns str(num) in base26 with roman letters as numerals'''
    n = num // 26
    d = chr(num%26+ord('a'))
    rv = ''
    if n: r=base26(n)
    return rv+d

def LetterColsFromArray(a):
    '''returns a dict with base26()->col mapping'''
    return { base26(i): v for i,v in enumerate(a) }

def instructEval(data, instructions):
    '''evals instructions with all columns from data available by their chr, i.e. a=data[0],...
    beware: a takes the role of zero, so col 26_{10}->ba_{26} contrary to e.g. M$ excel'''
    datadict = LetterColsFromArray(data)

    # issue warning for hidden columns
    for i in datadict:
        if i in keyword.kwlist:
            warnings.warn('column %s hidden by python keyword, use data[i]'%i)

    return eval(instructions,None,LetterColsFromArray(data))
