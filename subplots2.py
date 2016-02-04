import numpy
from matplotlib import pyplot

def subplots2(fig,grid,xaxpos='bottom',yaxpos='left',xtticks=True,ytticks=True,**plotopts):
    '''creates subaxs similar to matplotlib.pyplot.subplots with shared axes
    no inner spines, ticks, useful for broken axes

    fig is pyplot figure object,
    grid is a GridSpec,
    [xy]axpos specifies the side on which labels and ticks are shown
    [xy]ttiks specifies wether [xy]axpos opposing side will get ticks
    plotopts is passed to subplot2grid calls
    '''

    nrows = grid._nrows
    ncols = grid._ncols
    axs = numpy.ndarray((nrows,ncols),dtype=object)
    xlabel = plotopts.pop('xlabel',None)
    ylabel = plotopts.pop('ylabel',None)
    def subplot(loc, **opts): return pyplot.subplot(grid.new_subplotspec(loc,1,1),**opts)

    # first plot. Others will share its y axes
    ax = subplot((0,0), xlabel=xlabel, ylabel=ylabel, **plotopts)

    # creating remaining axs. Matplotlib uses columns as least significant, i.e. european reading convention
    for i in range(ncols):
        axs[0,i] = subplot((0,i), sharey=axs[0,0], **plotopts)
        for j in range(nrows):
            ax = subplot((j,i), sharex=axs[0,i], **plotopts)
            ax.tick_params(which='both',bottom=False,top=False,left=False,right=False)
            for side in ('top','bottom','left','right'):
                ax.spines[side].set_visible(False)
            axs[j,i] = ax

        if xaxpos == 'bottom':
            axs[-1,i].spines['bottom'].set_visible(True)
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

    for j in range(nrows):
        if yaxpos == 'left':
            axs[j,-1].spines['left'].set_visible(True)
            axs[j,-1].tick_params(which='both',left=True)
            if ytticks:
                axs[j,0].tick_params(which='both',right=True,labelright=False)

        elif yaxpos == 'right':
            axs[j,0].spines['right'].set_visible(True)
            axs[j,0].tick_params(which='both',top=True)
            if xtticks:
                axs[j,-1].tick_params(which='both',left=True,labelleft=False)
        else:
            raise ValueError('That direction (%s) is invalid'%yaxpos)


    return axs
