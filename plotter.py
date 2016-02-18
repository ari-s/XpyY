#!/usr/bin/python3
# Copyright (c) 2016, Arian Sanusi
# License: Artistic License 2.0 (see ./Artistic-2.0)

try:
    from .packagedefaults import packagedefaults as pdefaults
    from . import inputfilter
    from .operations import operations,instructEval
    from .subplots2 import subplots2
    from . import helpers

except SystemError:
    from packagedefaults import packagedefaults as pdefaults
    from XpyY import inputfilter
    from XpyY.operations import operations,instructEval
    from XpyY.subplots2 import subplots2
    from XpyY import helpers

import re, numbers, numpy, copy, sys
from matplotlib import pyplot,transforms,text
import pdb
import time

figs = []

def yamlplot(recipes):
    '''plot src[] to dest using recipes

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

    # get default
    #if not set(('src','target','y','y1','y2','yx','y1x','y1x1','y2x','y2x1','y2x2')).intersection(recipes[0]):
    if not set(('target')).intersection(recipes[0]):
        defaults = recipes.pop(0)
        # rcparams must be set before any matplotlib interaction...
        fontsize = defaults.pop('fontsize',None)
        if fontsize:
            pyplot.rcParams['font.size'] = fontsize
    else:
        defaults = {}

    for y in recipes:
        fig = pyplot.figure()
        figs.append(fig)
        if isinstance(y, dict):
            plot(y,fig, defaults)

        elif isinstance(y, list):

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

def plot(recipe,fig,defaults,xlen=1,ylen=1,xpos=1,ypos=1):
    '''plots on fig from one recipe (as python dictionary) as described in __main__.__doc__'''

    # preserve defaults over different runs
    packagedefaults = copy.deepcopy(pdefaults)
    defaults = copy.deepcopy(defaults)

    packagedefaults.update(defaults)
    packagedefaults.update(recipe)
    recipe = packagedefaults

    def popset(key, default=None, *altnames):
        '''returns key from either recipe, defaults or packagedefaults
        key is popped from dic with given default'''
        v = default

        if any( isinstance(i,dict) for i in (recipe.get(key,None), default) ):
            if default == None:
                v = {}
            v.update(recipe.pop(key,{}))
        else:
            v = recipe.pop(key,v)
        #if not v:
        #    raise KeyError('%s not found in any of packagedefaults,defaults,recipe'%key)
        return v

    target = recipe.pop('target') # no default for target
    # parse target, if not shorthand notation extract axlabels
    if isinstance(target,list):
        labels = target[2:]
        target,caption = target[:2]
    else:
        labels = list(map(popset,('xlabel','ylabel'),('x1label','y1label')))
    # need space as default second label b/c to differ subplot call from first axis
    # this will break for ylabel,xlabel = ' '
    labels.extend(map(popset,('x2label', 'y2label'), (' ',' ')))

    target = popset('targetprefix')+target

    # extract recipe keys that are not plot args
    figsize = popset('figsize')
    subplotopts = popset('opts',{})
    xbreaks = popset('xbreaks',[None]) # have to have something inside b/c later iterate over
    ybreaks = popset('ybreaks',[None])
    src = popset('src')
    srcprefix = popset('srcprefix')
    plotpos= popset('plotpos',((xlen*ylen),xpos,ypos))
    outformat = popset('format')
    legendopts = popset('legendopts',{})
    legendpos = popset('legendpos',(0,1))
    maxXTicks = popset('maxXTicks')
    maxYTicks = popset('maxYTicks')
    xlim = popset('xlim')
    twinxlim = popset('twinxlim')
    ylim = popset('ylim')
    twinylim = popset('twinylim')
    plotargs = popset('plotargs',{})
    twinplotargs = popset('twinplotargs',copy.deepcopy(plotargs))

    # extracting drawing instructions
    plotRe = re.compile(r'(y[12]?)(x[12]?)?')
    lines = []
    y1x1,y2x1,y1x2,y2x2 = [],[],[],[]
    linelabels = []
    pop=[] #: need to delete drawing instructions from recipe

    for k in recipe:
        try:
            y,x = plotRe.match(k).groups() # x may be None
        except AttributeError:
            pass
        else:
            pop.append(k)
            p = recipe[k]
            if '2' in y:
                if x and '2' in x: y2x2.append(p)
                else: y2x1.append(p)
            else:
                if x and '2' in x: y1x2.append(p)
                else: y1x1.append(p)
    for i in map(recipe.pop,pop): pass

    print('working on target %s'%target)
    if isinstance(src,dict):
        src = { k: inputfilter.__call__( srcprefix+v ) for k,v in src.items() }
    elif isinstance(src,str):
        src = inputfilter.__call__( srcprefix+src )

    dmap = popset('dmap')
    if dmap:

        if isinstance(src,numpy.ndarray):
            dmaplocals = instructEval.LetterColsFromArray(src)
            dmaplocals.update(src=src)
            src = numpy.array(eval(dmap,dmaplocals,operations))
        elif isinstance(src,dict):
            for k,v in dmap.items():
                src[k] = eval(v,{k:src[k]},operations)

    def subplot(recipes, *plots, **plotargs):
        '''plot the recipe on all *plots - this is like pyplot.plot, not subplots2'''
        lines = []
        linelabels = []
        for recipe in recipes:
            data = []
            for i,v in enumerate(recipe):
                ilabel = plotargs.get('label', None)
                if isinstance(v,dict):
                    ilabel = v.pop('label', ilabel)
                    plotargs.update(v)
                elif isinstance(v,str):
                    data.extend(instructEval.instructEval(src,v))
                    # FIXME: if this provides data for several plots, then linelabel must be repeated
                else:
                    raise ValueError('Could not parse %s'%v)

            if ilabel != None:
                linelabels.append(ilabel)

            for p in plots:
                # these may be several lines, must ensure if there are several
                # that labels is None or list of same length
                lines.append(p.plot(*data,**plotargs))

        # if len(linelabels)>0 and len(linelabels) != len(lines):
        #    raise ValueError("You provided Linelabels and not for every line one")
        return lines,linelabels

    # if we have breaks, come up with a new figure, no way to save the old one -
    # incompatible with more than one plot per figure
    subplots2args = dict(xbreaks=xbreaks, ybreaks=ybreaks, maxXTicks=maxXTicks, maxYTicks=maxYTicks)
    if xbreaks[0] or ybreaks[0]:

        if not ( y2x1 or y1x2 ):
            axs,bgax = subplots2(fig, **subplots2args)
            bgtwinlines = [] # so we can do legend call independend on the others existence

        elif y2x1:
            axs, bgax, twinaxs, bgtwin = subplots2(fig, twin='x', **subplots2args)
#            (bgtwinlines, *twinlines),(bgtwinlinelabels, *twinlinelabels) \
#                = subplot(y2x1, bgtwin, *twinaxs.flat, **twinplotargs)
            (bgtwinlines, *twinlines),bgtwinlinelabels = subplot(y2x1, bgtwin, *twinaxs.flat, **twinplotargs)
            # above for some reasons produces a list arround what we want, therefore:
            if labels[3]: bgtwin.set_ylabel(labels[3])

        elif y1x2:
            axs, bgax, twinaxs, bgtwin = subplots2(fig,twin='y', **subplots2args)
            (bgtwinlines, *twinlines), bgtwinlinelabels = subplot(y1x2, bgtwin, *twinaxs.flat, **twinplotargs)
            if labels[2]: bgtwin.set_xlabel(labels[2])

        #(bglines, *lines),(bglinelabels, *linelabels) = subplot(y1x1, bgax, *axs.flat, **plotargs)
        (bglines, *lines), bglinelabels = subplot(y1x1, bgax, *axs.flat, **plotargs)
        legend = fig.legend(bglines+bgtwinlines,bglinelabels+bgtwinlinelabels,**legendopts)
        legend.set_zorder(20)
        legend.set_bbox_to_anchor(legendpos,bgax.transAxes)

        for line in bglines + bgtwinlines:
            line.set_visible(False)

        # print the labels onto the bgax
        if labels[0] or labels[1]:
            if labels[0]: bgax.set_xlabel(labels[0])
            if labels[1]: bgax.set_ylabel(labels[1])
        for l in bgax.get_xticklabels() + bgax.get_yticklabels() + \
                  bgtwin.get_xticklabels() + bgtwin.get_yticklabels():
            l.set_alpha(0.0)

        for line,label in zip(bglines+bgtwinlines,bglinelabels+bgtwinlinelabels):
            print('made line with label %s'%label)
        linecount = len(bglines+bgtwinlines)
        labelcount = len(bglinelabels+bgtwinlinelabels)
        if linecount != labelcount:
            print("len(lines)=%i != len(labels)=%i"%(linecount,labelcount))

    else:
        # y1x1 plots
        p11 = fig.add_subplot(*plotpos,**subplotopts)
        line,linelabel = subplot(y1x1,p11,**plotargs)
        lines.extend(line[0])
        linelabels.extend(linelabel)
        if labels[0]: p11.set_xlabel(labels[0])
        if labels[1]: p11.set_ylabel(labels[1])
        if xlim: p11.set_xlim(xlim)
        if ylim: p11.set_ylim(ylim)

        if y2x1:
            p21 = p11.twinx()
            line,linelabel = subplot(y2x1,p21,**twinplotargs)
            lines.extend(line[0])
            linelabels.extend(linelabel)
            if twinylim: p21.set_ylim(twinylim)
            try: labels[3]
            except IndexError: pass
            else: p21.set_ylabel(labels[3])

        if y1x2:
            p12 = p11.twiny()
            line,linelabel = subplot(y1xx,p12,**twinplotargs)
            lines.extend(line[0])
            linelabels.extend(linelabel)
            if twinxlim: p12.set_xlim(twinxlim)
            try: labels[2]
            except IndexError: pass
            else: p12.set_xlabel(labels[2])

        if y2x2:
            raise NotImplementedError('Could not figure out how to handle reasonably in pyplot')
        p11.legend(lines,linelabels,**legendopts)

    if figsize:
        fig.set_size_inches(helpers.inchesmm(*figsize))
    fig.savefig(target,format=outformat,bbox_inches='tight')
    print('done\n')
    return fig
