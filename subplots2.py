import numpy
from matplotlib import pyplot, ticker, figure

def subplots2(fig,xbreaks,ybreaks,xaxpos='bottom',yaxpos='left',xtticks=True,ytticks=True,
              maxXTicks=None, maxYTicks=None,axset=None, **plotopts):
    '''creates subaxs similar to matplotlib.pyplot.subplots with shared axes
    no inner spines, ticks, useful for broken axes

    fig is pyplot figure object,
    grid is a GridSpec,
    [xy]axpos specifies the side on which labels and ticks are shown
    [xy]ttiks specifies wether [xy]axpos opposing side will get ticks
    plotopts is passed to subplot2grid calls
    '''

    axs = numpy.ndarray((len(ybreaks),len(xbreaks)),dtype=object)
    xlabel = plotopts.pop('xlabel',None)
    ylabel = plotopts.pop('ylabel',None)
    def subplot(loc, **opts):
        if not axset:
            return fig.add_subplot(gridspec.new_subplotspec(loc,1,1),**opts)
        else:
            return fig.add_axes(axset[loc].get_position,**opts)

    # gridspec: alignment of the subplots
    try: width = [ right-left for left,right in xbreaks ]
    except TypeError: width = [ 1 ]
    try: height = [ top-bottom for bottom,top in ybreaks ]
    except TypeError: height = [ 1 ]

    gridspec = pyplot.GridSpec(nrows=len(ybreaks), ncols=len(xbreaks), width_ratios=width, height_ratios=height)

    # first plot. Others will share its y axes
    ax = subplot((0,0), xlabel=xlabel, ylabel=ylabel, **plotopts)

    # creating remaining axs. Matplotlib uses columns as least significant, i.e. european reading convention
    for i,x in enumerate(xbreaks):
        axs[0,i] = subplot((0,i), sharey=axs[0,0], **plotopts)
        for j,y in enumerate(ybreaks):
            ax = subplot((j,i), sharex=axs[0,i], **plotopts)
            if x: ax.set_xlim(x)  # may have None-case
            if y: ax.set_ylim(y)  # dito
            ax.tick_params(which='both',
                bottom=False,top=False,left=False,right=False)
            for side in ('top','bottom','left','right'):
                ax.spines[side].set_visible(False)

            def ticloc(k,max=None):
                if max and max[k]: return ticker.MaxNLocator(max[k])
                else: return ticker.AutoLocator()

            ax.xaxis.set_major_locator(ticloc(i,maxXTicks)) #,prune='both'))
            ax.yaxis.set_major_locator(ticloc(j,maxYTicks)) #,prune='both'))
            axs[j,i] = ax

        axs[0,i].spines['top'].set_visible(True)
        axs[-1,i].spines['bottom'].set_visible(True)

        if xaxpos == 'bottom':
            axs[-1,i].tick_params(which='both',bottom=True)
            if xtticks:
                axs[0,i].tick_params(which='both',top=True,labeltop=False)

        elif xaxpos == 'top':
            axs[0,i].spines['top'].set_visible(True)
            axs[0,i].tick_params(which='both',top=True)
            if xtticks:
                axs[-1,i].tick_params(which='both',bottom=True,labelbottom=False)
        else:
            raise ValueError('That direction (%s) is invalid'%xaxpos)

    for j in range(len(ybreaks)):
        axs[j,0].spines['left'].set_visible(True)
        axs[j,-1].spines['right'].set_visible(True)

        if yaxpos == 'left':
            axs[j,0].tick_params(which='both',left=True)
            if ytticks:
                axs[j,-1].tick_params(which='both',right=True,labelright=False, labelleft=False)

        elif yaxpos == 'right':
            axs[j,-1].tick_params(which='both',right=True,labelleft=False, labelright=True)
            if xtticks:
                axs[j,0].tick_params(which='both',left=True,labelleft=False)

        else:
            raise ValueError('That direction (%s) is invalid'%yaxpos)


    return axs
