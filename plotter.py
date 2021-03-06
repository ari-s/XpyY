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
        defaults.pop('anchors',None)
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

def linesModStyle(linestyle,lines):
    if linestyle == None: return lines
    else:
        newlines = []
        for line in lines:
            axn = line.axes
            x = line.get_xdata()[0]
            y = line.get_ydata()[0]
            newlines.extend( axn.plot((x,x),(y,y),color=line.get_color(),linestyle=linestyle) )
        return newlines

def plot(recipe,fig,defaults,xlen=1,ylen=1,xpos=1,ypos=1):
    '''plots on fig from one recipe (as python dictionary) as described in __main__.__doc__'''

    # preserve defaults over different runs
    packagedefaults = copy.deepcopy(pdefaults)
    defaults = copy.deepcopy(defaults)

    def update(d1,d2):
        for k,v in d2.items():
            if isinstance(v,dict) and k in d1 and isinstance(d1[k],dict):
                update(d1[k],d2[k])
            else:
                d1[k] = d2[k]

    update(packagedefaults,defaults)
    update(packagedefaults,recipe)
    recipe = packagedefaults

    def popset(key, default=None, *altnames):
        '''returns key from either recipe, defaults or packagedefaults
        key is popped from dic with given default'''
        v = default

        if any( isinstance(i,dict) for i in (recipe.get(key,None), default) ):
            if default == None:
                v = {}

            update(v,recipe.pop(key,{}))
        else:
            v = recipe.pop(key,v)
        #if not v:
        #    raise KeyError('%s not found in any of packagedefaults,defaults,recipe'%key)
        return v

    target = recipe.pop('target') # no default for target
    # parse target, if not shorthand notation extract axlabels
    if isinstance(target,list):
        axlabels = target[2:]
        target,caption = target[:2]
    else:
        axlabels = [ popset(i) for i in ('xlabel','ylabel', 'twinaxlabel') ]

    target = popset('targetprefix')+target

    # extract recipe keys that are not plot args
    figsize = popset('figsize')
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
    ylim = popset('ylim')
    twinxlim = popset('twinxlim')
    twinylim = popset('twinylim')
    plotargs = popset('plotargs',{})
    twinplotargs = popset('twinplotargs',copy.deepcopy(plotargs))
    legendlinestyle = popset('legendlinestyle')
    twinlegendlinestyle = popset('twinlegendlinestyle',legendlinestyle)

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

    dmap = popset('dmap')

    # done with parsing
    print("remaining", recipe)

    print('working on target %s'%target)
    if isinstance(src,dict):
        src = { k: inputfilter.__call__( srcprefix+v ) for k,v in src.items() }
    elif isinstance(src,str):
        src = inputfilter.__call__( srcprefix+src )

    if dmap:
        if isinstance(src,numpy.ndarray):
            dmaplocals = instructEval.LetterColsFromArray(src)
            dmaplocals.update(src=src)
            src = numpy.array(eval(dmap,dmaplocals,operations))
        elif isinstance(src,dict):
            for k,v in dmap.items():
                dmaplocals = instructEval.LetterColsFromArray(src[k])
                dmaplocals.update(src=src[k])
                src[k] = eval(v,dmaplocals,operations)
        else:
            raise TypeError()


    def subplot(recipes, *plots, **plotargs):
        '''plot the recipe on all *plots - this is like pyplot.plot, not subplots2'''
        lines = []
        linelabels = []
        for recipe in recipes:
            data = []
            ilines = []
            ilabel = plotargs.get('label', None)
            for i,v in enumerate(recipe):
                if isinstance(v,dict):
                    ilabel = v.pop('label', ilabel)
                    plotargs.update(v)
                elif isinstance(v,str):
                    data.extend(instructEval.instructEval(src,v))
                else:
                    raise ValueError('Could not parse %s'%v)

            for p in plots:
                # these may be several lines, must ensure if there are several
                # that labels is None or list of same length
                ilines.append(p.plot(*data,**plotargs))
            # ilines is now in ilines[plots][lineno] "shape", transpose
            lines.append(list(zip(*ilines)))
            if ilabel != None:
                linelabels.append([ilabel]*len(ilines[0]))

        # if len(linelabels)>0 and len(linelabels) != len(lines):
        #    raise ValueError("You provided Linelabels and not for every line one")
        return lines,linelabels

    # if we have breaks, come up with a new figure, no way to save the old one -
    # incompatible with more than one plot per figure
    subplots2args = dict(
        xbreaks=xbreaks, ybreaks=ybreaks,
        maxXTicks=maxXTicks, maxYTicks=maxYTicks,
        xlim=xlim, ylim=ylim,
        twinxlim=twinxlim, twinylim=twinylim)

    if xbreaks[0] or ybreaks[0]:

        def subplotbreaks(fig,*plots,**plotargs):
            '''wrapper around subplot that sorts out the lines and labels returned by subplot
               due to the numerus helper plots'''

            # lines will hold one list per recipe with one line per plot, need item 0 of those
            # labels will hold one list per recipe with ^linecount - need all of them

            lines, labels = subplot(fig, *plots, **plotargs)
            bglines = [ i[0] for recipe in lines for i in recipe ]
            lines = [ i[1] for recipe in lines for i in recipe ]
            labels = [ i for recipe in labels for i in recipe ]
            for line in bglines:
                # these are in background, with recipes[0] above discarded references to the actual ones
                line.set_visible(False)
            return lines, labels

        if not ( y2x1 or y1x2 ):
            axs,bgax = subplots2(fig, **subplots2args)
            twinlines = [] # so we can do legend call independend on the others existence

        elif y2x1:
            axs, bgax, twinaxs, bgtwin = subplots2(fig, twin='x', **subplots2args)
#            (bgtwinlines, *twinlines),(bgtwinlinelabels, *twinlinelabels) \
#                = subplot(y2x1, bgtwin, *twinaxs.flat, **twinplotargs)
            twinlines, twinlinelabels = subplotbreaks(y2x1, bgtwin, *twinaxs.flat, **twinplotargs)
            # above for some reasons produces a list arround what we want, therefore:
            if axlabels[2]: bgtwin.set_ylabel(axlabels[2])

        elif y1x2:
            axs, bgax, twinaxs, bgtwin = subplots2(fig,twin='y', **subplots2args)
            twinlines, twinlinelabels = subplotbreaks(y1x2, bgtwin, *twinaxs.flat, **twinplotargs)
            if axlabels[2]: bgtwin.set_xlabel(axabels[2])

        #(bglines, *lines),(bglinelabels, *linelabels) = subplot(y1x1, bgax, *axs.flat, **plotargs)
        lines, linelabels = subplotbreaks(y1x1, bgax, *axs.flat, **plotargs)
        lines = linesModStyle(legendlinestyle,lines)
        twinlines = linesModStyle(twinlegendlinestyle,twinlines)
        legend = fig.legend(lines+twinlines,linelabels+twinlinelabels,**legendopts)
        legend.set_zorder(20)
        legend.set_bbox_to_anchor(legendpos,bgax.transAxes)

        # print the labels onto the bgax
        if axlabels[0] or axlabels[1]:
            if axlabels[0]: bgax.set_xlabel(axlabels[0])
            if axlabels[1]: bgax.set_ylabel(axlabels[1])
        for l in bgax.get_xticklabels() + bgax.get_yticklabels() + \
                  bgtwin.get_xticklabels() + bgtwin.get_yticklabels():
            l.set_alpha(0.0)

        for line,label in zip(lines+twinlines,linelabels+twinlinelabels):
            print('made line with label %s'%label)
        linecount = len(lines+twinlines)
        labelcount = len(linelabels+twinlinelabels)
        if linecount != labelcount:
            print("len(lines)=%i != len(labels)=%i"%(linecount,labelcount))

    else:
        # y1x1 plots
        p11 = fig.add_subplot(*plotpos)
        line,linelabel = subplot(y1x1,p11,**plotargs)
        lines.extend( i[0] for recipe in line for i in recipe )
        linelabels.extend( i for recipe in linelabel for i in recipe )
        if axlabels[0]: p11.set_xlabel(axlabels[0])
        if axlabels[1]: p11.set_ylabel(axlabels[1])
        if xlim: p11.set_xlim(xlim)
        if ylim: p11.set_ylim(ylim)

        if y2x1:
            p21 = p11.twinx()
            line,linelabel = subplot(y2x1,p21,**twinplotargs)
            lines.extend( i[0] for recipe in line for i in recipe )
            linelabels.extend( i for recipe in linelabel for i in recipe )
            if xlim: p21.set_xlim(xlim) # apparently this needs to be set on both axes
            if twinylim: p21.set_ylim(twinylim)
            try: axlabels[3]
            except IndexError: pass
            else: p21.set_ylabel(axlabels[3])

        if y1x2:
            p12 = p11.twiny()
            line,linelabel = subplot(y1xx,p12,**twinplotargs)
            lines.extend( i[0] for recipe in line for i in recipe )
            linelabels.extend( i for recipe in linelabel for i in recipe )
            if ylim: p12.set_ylim(ylim)
            if twinxlim: p12.set_xlim(twinxlim)
            try: axlabels[2]
            except IndexError: pass
            else: p12.set_xlabel(axlabels[2])

        if y2x2:
            raise NotImplementedError('Could not figure out how to handle reasonably in pyplot')

        lines = linesModStyle(legendlinestyle,lines)
        p11.legend(lines,linelabels,**legendopts)
        if axlabels[0]: p11.set_xlabel(axlabels[0])
        if axlabels[1]: p11.set_ylabel(axlabels[1])

    if figsize:
        fig.set_size_inches(helpers.inchesmm(*figsize))
    fig.savefig(target,format=outformat,bbox_inches='tight')
    print('done\n')
    return fig
