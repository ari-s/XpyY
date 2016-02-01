#import inputfilter, helpers, operations
#from recipesParser import recipesParser
import sys,os.path,re
sys.path.insert(0,os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from plot import ordered_yaml as yaml
import matplotlib.pyplot as plt
from plotter import plot

__doc__ = '''
plot src[] to dest using recipes

usage: plot recipefile [*targets]

runs the recipes for targets. If no targets are given all recipes are run.
If one recipe target exists and is newer than both src and recipe, it is skipped

recipe: YAML document with a list with (in this order):
- at most one dict without src, target and plots providing defaults
- lists nested zero to two deep with:
  - at least one dict with src[], target and plot spec
  if item at depth two is a list, the first item may be an (x,y) tuple of figsize/mm
  else figsize may be a dict key

src[]: providing >=1 arrays which are to be plotted possibly after having some
    arrays: 2D numpy arrays where entries along the first axis is assumed to represent one data vector
    single src (no iterable arround the 2D array) also permissable
srcformat:  which inputfilter is used to get an array from src. defaults to the file extension
target:     plot name
target: *l  shorthand for { target=l[1], caption, x1label=l[2],[[x2label]],y1label,[y2label]}
format:     target format, if not given deduced from dest by pyplot.savefig().
y[12]?(x[12])? designator where to plot to.
    x1 bottom axis, x2 top axis dual to x1
    y1 left axis, y2 right axis dual to y1

y[12]?(x[12])? = (operation)?\(src,...),*args,**kwargs
    operation is a function from operations, src specifies which column
    (from which src, must be explicit if more than one source)
    identity is implicit operation.

all other entries are passed to pyplot.figure()
'''

try: recipes = yaml.ordered_load(open(sys.argv[1]))
except (FileNotFoundError,IndexError):
    print(__doc__)
    sys.exit(1)

if not set(('src','target','y','y1','y2','yx','y1x','y1x1','y2x','y2x1','y2x2')).intersection(recipes[0]):
    defaults = recipes.pop(0)
else:
    defaults = {}

for y in recipes:
    if isinstance(y, dict):
        try: figsize = y.pop('figsize')
        except KeyError: fig = plt.figure()
        else: fig = plt.figure(figsize)
        plot(y,fig, defaults)

    elif isinstance(y, list):

        # deal with figsize as first list item
        try:
            xdim,ydim = map(helper.inchesmm,y[0])
        except (TypeError,ValueError):
            fig = plt.figure()
        else:
            fig = plt.figure(figsize=(xdim,ydim))
            y.pop(0)

        ylen = len(y)
        for ypos,x in enumerate(y):
            if isinstance(x,list):
                xlen = len(x)
                for xpos,i in enumerate(x):
                    plot(i,fig,xlen,ylen,xpos,ypos)
            else:
                plot(x,fig,defaults,1,ylen,1,ypos)

    else:
        raise ValueError('first depth item in yaml must be list or dict')


