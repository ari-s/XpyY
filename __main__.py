#import inputfilter, helpers, operations
import sys,os.path,re
sys.path.insert(0,os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
import yaml
import matplotlib.pyplot as plt
from plotter import plot

__doc__ = '''
plot src[] to dest using recipes

usage: plot recipefile [*targets]

runs the recipes for targets. If no targets are given all recipes are run.
If one recipe target exists and is newer than both src and recipe, it is skipped

recipe: YAML document with a list with (in this order):
- at most one dict without src, target and plots providing defaults
- at least on dict with src, target keys

src[]:        provides an array which is to be plotted possibly after some calculations on their data.
              array: 2D numpy array where entries along the first axis is assumed to represent one data vector
target:       plot filename
target: *l    shorthand for { target=l[1], caption, x1label=l[2],[[x2label]],y1label,[y2label]}
format:       target format, if not given deduced from dest by pyplot.savefig().
targetprefix: prepended to all plots       - a simple string. Breaks recipe portability bc / vs \
srcprefix:    prepended to all src files
srcformat:    which inputfilter is used to get an array from src. defaults to the file extension

figurekwargs:
xbreaks:      skip data between break tuples:
ybreaks:      ex [[0,10],[20,100]]
legendopts:   kwargs for the legend
maxXTicks:    how many X ticks to place er break segment. Has to be overriden sometimes. 0=auto
maxYTicks:    ditto for Y

y[12]?(x[12])? designator where to plot to.
    x1 bottom axis, x2 top axis dual to x1
    y1 left axis, y2 right axis dual to y1

y[12]?(x[12])? : instructions
    instructions is list
      first item: data to plot. may be an operation(dict) or data(list)
      every other item: plotkwargs

    data specifies which columns of the src to take

    operation is a function from operations, src specifies which column
    an operation dict may have a second entry args with operationkwargs

figurekwargs are passed to figure() call, same for legendopts, plotkwargs, operationkwargs
'''

# load recipe
try: recipes = yaml.load(open(sys.argv[1]))
except (FileNotFoundError,IndexError):
    print(__doc__)
    sys.exit(1)

# get default
if not set(('src','target','y','y1','y2','yx','y1x','y1x1','y2x','y2x1','y2x2')).intersection(recipes[0]):
    defaults = recipes.pop(0)
    fontsize = defaults.pop('fontsize',None)
    if fontsize:
        plt.rcParams['font.size'] = fontsize
else:
    defaults = {}

# regard targets
targets = sys.argv[2:]
if targets:
    for i,candidate in enumerate(recipes):
        candidate = candidate['target']
        if isinstance(candidate,list): #shorthand notation
            candidate = candidate[0]
        if candidate not in targets:
            recipes.pop(i)

for y in recipes:
    if isinstance(y, dict):
        try: figsize = y.pop('figsize')
        except KeyError:
            try: figsize = defaults['figsize']
            except KeyError: fig = plt.figure()
            else: fig = plt.figure(figsize=[d/25.4 for d in figsize])
        else: fig = plt.figure(figsize=[d/25.4 for d in figsize])
        plot(y,fig, defaults,targets=targets)

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
                    plot(i,fig,xlen,ylen,xpos,ypos,targets=targets)
            else:
                plot(x,fig,defaults,1,ylen,1,ypos,targets=targets)

    else:
        raise ValueError('first depth item in yaml must be list or dict')


