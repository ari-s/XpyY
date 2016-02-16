from .derive import derive
from .smoothen import smoothen
from .strptime import strptime,strptime2
from .dmap import dmap
from .unsparse import unsparse
import numpy
operations = {
    'derive': derive,
    'smoothen': smoothen,
    'strptime': strptime,
    'strptime2': strptime2,
    'numpy': numpy,
    'dmap':dmap,
    'unsparse':unsparse }
