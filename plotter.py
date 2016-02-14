#!/usr/bin/python3
# Copyright (c) 2016, Arian Sanusi
# License: Artistic License 2.0 (see ./Artistic-2.0)

try:
    from .packagedefaults import packagedefaults
    from . import inputfilter
    from .operations import operations,instructEval
    from .subplots2 import subplots2

except SystemError:
    from packagedefaults import packagedefaults
    from XpyY import inputfilter
    from XpyY.operations import operations,instructEval
    from XpyY.subplots2 import subplots2
import re, numbers, numpy
from matplotlib import pyplot,transforms,text
import pdb
import time

def plot(recipe,fig,defaults,xlen=1,ylen=1,xpos=1,ypos=1, targets=[]):
    '''plots on fig from one recipe (as python dictionary) as described in __main__.__doc__'''

    def popset(key, default=None, *altnames):
        '''returns key from either recipe, defaults or packagedefaults
        key is popped from dic with given default'''

        def get(dic,key,default):
            if  isinstance(dic.get(key),dict) and isinstance(default,dict):
                default.update(dic.get(key))
                return default
            else:
                return dic.get(key,default)

        default = get(packagedefaults,key,default)
        v = get(defaults,key,default)
        v = get(recipe,key,v)

        # make sure it's gone
        recipe.pop(key,None)

        if v == default and altnames:
            v = popset(altnames[0],default,altnames[1:])
            # altnames[1:] works because slicing with indices outside iterable returns empty iterable
        return v

    target = recipe.pop('target') # no default for target
    # parse target, if not shorthand notation extract labels
    if isinstance(target,list):
        labels = target[2:]
        target,caption = target[:2]
    else:
        labels = list(map(popset,('xlabel','ylabel'),('x1label','y1label')))
    # need space as default second label b/c to differ subplot call from first axis
    # this will break for ylabel,xlabel = ' '
    labels.extend(map(popset,('x2label', 'y2label'), (' ',' ')))

    if targets and target not in targets:
        return fig
    target = popset('targetprefix')+target

    # extract recipe keys that are not plot args
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

    if isinstance(src,dict):
        src = { k: inputfilter.__call__( srcprefix+v ) for k,v in src.items() }
    elif isinstance(src,str):
        src = inputfilter.__call__( srcprefix+src )

    def subplot(recipes, *plots):
        lines = []
        for recipe in recipes:
            opts = {}
            data = []
            for i,v in enumerate(recipe):
                if isinstance(v,dict):
                    try: linelabels.append(v.pop('label'))
                    except KeyError: pass
                    opts.update(v)
                elif isinstance(v,str):
                    data.extend(instructEval.instructEval(src,v))
                else:
                    raise ValueError('Could not parse %s'%v)

            for p in plots:
                lines.append(p.plot(*data,**opts))

        return lines

    # if we have breaks, come up with a new figure, no way to save the old one -
    # incompatible with more than one plot per figure
    subplots2args = dict(xbreaks=xbreaks, ybreaks=ybreaks, maxXTicks=maxXTicks, maxYTicks=maxYTicks)
    if xbreaks[0] or ybreaks[0]:

        if not ( y2x1 or y1x2 ):
            axs,bgax = subplots2(fig, **subplots2args)
            bgtwinlines = [] # so we can do legend call independend on the others existence

        elif y2x1:
            axs, bgax, twinaxs, bgtwin = subplots2(fig, twin='x', **subplots2args)
            bgtwinlines, *twinlines = subplot(y2x1, bgtwin, *twinaxs.flat)
            # above for some reasons produces a list arround what we want, therefore:
            if labels[3]: bgtwin.set_ylabel(labels[3])

        elif y1x2:
            axs, bgax, twinaxs, bgtwin = subplots2(fig,twin='y', **subplots2args)
            (bgtwinlines, *twinlines) = subplot(y1x2, bgtwin, *twinaxs.flat)
            if labels[2]: bgtwin.set_xlabel(labels[2])

        bglines, *lines = subplot(y1x1, bgax, *axs.flat)
        legend = fig.legend(bglines+bgtwinlines,linelabels,**legendopts)
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

    else:
        # y1x1 plots
        p11 = fig.add_subplot(*plotpos,**subplotopts)
        lines.extend(subplot(y1x1,p11))
        if labels[0]: p11.set_xlabel(labels[0])
        if labels[1]: p11.set_ylabel(labels[1])

        if y2x1:
            p21 = p11.twinx()
            lines.extend(subplot(y2x1,p21))
            try: labels[3]
            except IndexError: pass
            else: p21.set_ylabel(labels[3])

        if y1x2:
            p12 = p11.twiny()
            lines.extend(subplot(y1x2,p12))
            try: labels[2]
            except IndexError: pass
            else: p12.set_xlabel(labels[2])

        if y2x2:
            raise NotImplementedError('Could not figure out how to handle reasonably in pyplot')
        p11.legend(lines,linelabels,**legendopts)

    fig.savefig(target,format=outformat,bbox_inches='tight')
    return fig
