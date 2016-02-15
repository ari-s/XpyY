from .derive import derive
from .smoothen import smoothen
from .strptime import strptime
from .dmap import dmap
from .unsparse import unsparse
import numpy
operations = {
    'derive': derive,
    'smoothen': smoothen,
    'strptime': strptime,
    'numpy': numpy,
    'dmap':dmap,
    'unsparse':unsparse }
