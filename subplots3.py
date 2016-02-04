import numpy
from matplotlib import pyplot, ticker

# tick locator creation helper
def ticloc(k,max=None):
    if max and max[k]: return ticker.MaxNLocator(max[k])
    else: return ticker.AutoLocator()

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
    try: width = [ right-left for left,right in xbreaks ]
    except TypeError: width = [ 1 ]
    try: height = [ top-bottom for bottom,top in ybreaks ]
    except TypeError: height = [ 1 ]

    gridspec = pyplot.GridSpec(nrows=len(ybreaks), ncols=len(xbreaks), width_ratios=width, height_ratios=height)
    def subplot(loc, **opts): return fig.add_subplot(gridspec.new_subplotspec(loc,1,1),**opts)
    
    for i,x in enumerate(xbreaks):
        for j,y in enumerate(ybreaks):
            ax = subplot((j,i),**plotopts)
            axs[j,i] = ax
            
            if x: ax.set_xlim(x)  # may have None-case
            if y: ax.set_ylim(y)  # dito
            
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            
            for side in ('top','bottom','left','right'):
                ax.spines[side].set_visible(False)
                            
            if twin == 'x': twinax = ax.twinx()
            if twin == 'y': twinax = ax.twiny()
            elif twin: ValueError('%s is not an axis specifier'%twin)
            
            if twin:
                twinax.get_xaxis().set_visible(False)
                twinax.get_yaxis().set_visible(False)
                for side in ('top','bottom','left','right'):
                    twinax.spines[side].set_visible(False)
                if x: twinax.set_xlim(x)  # may have None-case
                if y: twinax.set_ylim(y)  # dito
                twinaxs[j,i] = twinax
                twinax.xaxis.set_major_locator(ticloc(i,maxXTicks))
                twinax.yaxis.set_major_locator(ticloc(j,maxYTicks))
                
            ax.xaxis.set_major_locator(ticloc(i,maxXTicks))
            ax.yaxis.set_major_locator(ticloc(j,maxYTicks))
            
        # axs[0,i].get_shared_y_axes().join(*twinaxs[:,i])
        # restore deco on top, bottom plot
        axs[0,i].spines['top'].set_visible(True)
        axs[-1,i].spines['bottom'].set_visible(True)
        axs[-1,i].get_xaxis().set_visible(True)
        if twin == 'y': 
            twinaxs[0,i].get_xaxis().set_visible(True)
            # twinaxs[0,i].get_shared_y_axes().join(*twinaxs[:,i])
            # this seems not to be necessary due to plotting everything everywhere
            # commenting this out will however produce correct decorations
        axs[0,i].get_xaxis().set_visible(True)
        
    for j,y in enumerate(ybreaks):        
        # axs[j,-1].get_shared_x_axes().join(*twinaxs[j,:])
        axs[j,0].spines['left'].set_visible(True)
        axs[j,-1].spines['right'].set_visible(True)
        axs[j,0].get_yaxis().set_visible(True)
        axs[j,-1].get_yaxis().set_visible(True)
        if twin == 'x': 
            twinaxs[j,-1].get_yaxis().set_visible(True)
            #twinaxs[j,-1].get_shared_x_axes().join(*twinaxs[j,:])
        
    
    if twin: return axs, twinaxs
    else: return axs
