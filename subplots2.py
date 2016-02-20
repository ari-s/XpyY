#!/usr/bin/python3
# Copyright (c) 2016, Arian Sanusi
# License: Artistic License 2.0 (see ./Artistic-2.0)

import numpy,pdb
from matplotlib import pyplot, ticker

# tick locator creation helper
def ticloc(k,max=None):
    if max and max[k]: return ticker.MaxNLocator(max[k])
    else: return ticker.AutoLocator()

def breakSign(ax, d=.015):
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)

def subplots2(fig,xbreaks,ybreaks,twin=None,maxXTicks=None,maxYTicks=None,**plotopts):
    '''creates subaxs similar to matplotlib.pyplot.subplots with shared axes
    no inner spines, ticks, useful for broken axes

    fig is pyplot figure object,
    twin is one of None, 'x' or 'y' specifying the other axis for which you want a dual axis for.
    [xy]axpos specifies the side on which labels and ticks are shown
    [xy]ttiks specifies wether [xy]axpos opposing side will get ticks
    plotopts is passed to subplot2grid calls
    '''
    # for the sharing of axes, see https://stackoverflow.com/questions/12919230
    axs = numpy.ndarray((len(ybreaks),len(xbreaks)),dtype=object)
    if twin: twinaxs = numpy.empty_like(axs)

    # for ratios of subplots
    try: width = numpy.array([ right-left for left,right in xbreaks ],dtype=float)
    except TypeError: width = [ 1 ]
    else: width/=sum(width)
    try: height = numpy.array([ top-bottom for bottom,top in ybreaks ],dtype=float)
    except TypeError: height = [ 1 ]
    else: width/=sum(width)

    xlim,ylim,twinxlim,twinylim = ( plotopts.pop(i,None) for i in
                                    ( 'xlim','ylim','twinxlim','twinylim' ) )

    gridspec = pyplot.GridSpec(
        nrows=len(ybreaks), ncols=len(xbreaks), width_ratios=width, height_ratios=height,
        wspace=0.015*len(xbreaks), hspace=0.015*len(ybreaks)) # wspace is _w_ertical, hspace horizontal.

    def subplot(loc, **opts): return fig.add_subplot(gridspec.new_subplotspec(loc,1,1),**opts)

    # dummy background plot for the axes' labels
    bgax = fig.add_subplot(111)
    for side in ('top','bottom','left','right'):
        bgax.spines[side].set_visible(False)

    for i,x in enumerate(xbreaks):
        for j,y in enumerate(ybreaks):
            ax = subplot((j,i),**plotopts)
            axs[j,i] = ax

            if x: ax.set_xlim(x)            # may have None-case
            elif xlim: ax.set_xlim(xlim)    # if x axis unbroken, may have xlim set
            if y: ax.set_ylim(y)            # dito
            elif ylim: ax.set_ylim(ylim)

            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)

            for side in ('top','bottom','left','right'):
                ax.spines[side].set_visible(False)

            if twin == 'x': twinax = ax.twinx()
            if twin == 'y': twinax = ax.twiny()
            elif twin: ValueError('%s is not an axis specifier'%twin)

            # removing twin deco
            if twin:
                twinax.get_xaxis().set_visible(False)
                twinax.get_yaxis().set_visible(False)
                for side in ('top','bottom','left','right'):
                    twinax.spines[side].set_visible(False)
                if x: twinax.set_xlim(x)                    # may have None-case
                elif twinxlim: twinax.set_xlim(twinxlim)    # can have lim on non-broken axes
                if y: twinax.set_ylim(y)                    # dito
                elif twinylim: twinax.set_ylim(twinylim)
                twinaxs[j,i] = twinax

                # change ticklabels
                twinax.xaxis.set_major_locator(ticloc(i,maxXTicks))
                twinax.yaxis.set_major_locator(ticloc(j,maxYTicks))

            ax.xaxis.set_major_locator(ticloc(i,maxXTicks))
            ax.yaxis.set_major_locator(ticloc(j,maxYTicks))

        # restore deco on top, bottom plots
        axs[0,i].spines['top'].set_visible(True)
        axs[-1,i].spines['bottom'].set_visible(True)
        axs[-1,i].get_xaxis().set_visible(True)
        if twin == 'y':
            twinaxs[0,i].get_xaxis().set_visible(True)
            twinaxs[0,i].get_shared_y_axes().join(*twinaxs[:,i])
            bgtwin = bgax.twiny()
            if twinxlim: bgtwin.set_xlim(twinxlim)
        # now the break significant:
        c=.006
        d=c/width[i]
        c=.03
        bkwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
        if i>0:
            axs[0,i].plot((-d, +d), (-c, +c), **bkwargs)
            axs[0,i].plot((-d, +d), (1 - c, 1 + c), **bkwargs)
        if i+1<len(xbreaks):
            axs[-1,i].plot((1 - d, 1 + d), (1 - c, 1 + c), **bkwargs)
            axs[-1,i].plot((1 - d, 1 + d), (-c, +c), **bkwargs)

    # restore deco on left, right plots
    for j,y in enumerate(ybreaks):
        axs[j,0].spines['left'].set_visible(True)
        axs[j,-1].spines['right'].set_visible(True)
        axs[j,0].get_yaxis().set_visible(True)
        if twin == 'x':
            twinaxs[j,-1].get_yaxis().set_visible(True)
            twinaxs[j,-1].get_shared_x_axes().join(*twinaxs[j,:])
            bgtwin = bgax.twinx()
            if twinylim: bgtwin.set_ylim(twinylim)
                # now the break significant:

        d=.015
        bkwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
        if j>0:
            axs[j,0].plot((-d, +d), (-d, +d), **bkwargs)
            axs[j,-1].plot((1 - d, 1 + d), (-d, +d), **bkwargs)
        if j+1<len(ybreaks):
            axs[j,0].plot((-d, +d), (1 - d, 1 + d), **bkwargs)
            axs[j,-1].plot((1 - d, 1 + d), (1 - d, 1 + d), **bkwargs)

    if twin:
        for side in ('top','bottom','left','right'):
            bgtwin.spines[side].set_visible(False)
    # return signature deliberately different, make sure callee does what he intended
    if twin: return axs, bgax, twinaxs, bgtwin
    else: return axs, bgax
