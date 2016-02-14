from .derive import derive
from .smoothen import smoothen
from .strptime import strptime
import numpy
operations = {
    'derive': derive,
    'smoothen': smoothen,
    'strptime': strptime,
    'numpy': numpy }
