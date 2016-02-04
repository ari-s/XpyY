try:
    from .packagedefaults import packagedefaults
    from . import inputfilter
    from .operations import operations
    from .subplots2 import subplots2
    
except SystemError:
    from packagedefaults import packagedefaults
    from plot import inputfilter
    from plot.operations import operations
    from subplots2 import subplots2
import re, numbers, copy, numpy
from matplotlib import pyplot
import pdb

def execCompute(src, instructions):
    '''executes drawing instruction as described in __main__.__doc__'''
    if isinstance(instructions, list):

        if all( isinstance(i, int) for i in instructions ):
            return ( src[0][i] for i in instructions )

        elif all( isinstance(i, dict) for i in instructions ):
            return NotImplementedError('did not get here')

    elif isinstance(instructions, dict):
        kwargs = instructions.pop('args',{})
        operation,operands = list(instructions.items())[0] #there may only be one
        if isinstance(operands,dict):
            intermediate = execCompute(src,operands)
            return operations[operation](*intermediate, **kwargs)
        elif isinstance(operands, list):
            if all( isinstance(i, dict) for i in operands ):
                raise NotImplementedError('did not get here')
            args = [ src[0][i] for i in operands ]
            return operations[operation](*args, **kwargs)
        else:
            raise ValueError('Invalid instruction in recipe')

def plot(recipe,fig,defaults,xlen=1,ylen=1,xpos=1,ypos=1, targets=[]):
    '''plots on fig from one recipe (as python dictionary) as described in __main__.__doc__'''

    def popset(key, default=None, *altnames):
        '''returns key from either recipe, defaults or packagedefaults
        key is popped from dic with given default'''

        if default != None:
            v = default
        else:
            v = packagedefaults.get(key)
            v = defaults.get(key,v)

        v = recipe.pop(key,v)
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
        labels.extend(map(popset,('x2label', 'y2label')))

    if targets and target not in targets:
        return fig
    target = popset('targetprefix')+target

    # extract recipe keys that are not plot args
    subplotopts = popset('opts',{})
    xbreaks = popset('xbreaks',[None]) # have to have something inside b/c later iterate over
    ybreaks = popset('ybreaks',[None])
    src = popset('srcprefix')+popset('src')
    plotpos= popset('plotpos',((xlen*ylen),xpos,ypos))
    outformat = popset('format')
    legendopts = popset('legendopts',{})
    maxXTicks = popset('maxXTicks')
    maxYTicks = popset('maxYTicks')

    # extracting drawing instructions
    plotRe = re.compile(r'(y[12]?)(x[12]?)?')
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

    if not isinstance(src,list):
        src = [ src ]

    src = [ inputfilter.__call__( i ) for i in src ]

    def subplot(recipes, *plots):
        lines = []
        for recipe in recipes:
            opts = {}
            for i,v in enumerate(recipe):
                if isinstance(v,dict):
                    if all( isinstance(j,(numbers.Number, str)) for j in v.values()):
                        print(v)
                        if 'label' in v:
                            linelabels.append(v.pop('label'))
                        opts.update(v)
                        del(recipe[i])
            for part in recipe:
                data = execCompute(src,part)
                for p in plots:
                    lines.extend(p.plot(*data,**opts))
        return lines

    lines = []

    # if we have breaks, come up with a new figure, no way to save the old one -
    # incompatible with more than one plot per figure
    if xbreaks[0] or ybreaks[0]:
        
        axs = subplots2(fig, xbreaks, ybreaks, maxXTicks=maxXTicks, maxYTicks=maxYTicks)
        pdb.set_trace()

        # the actual draw call
        lines.extend(subplot(y1x1,*axs.flat))

        #if y2x1:
            #twinxs = numpy.array([ ax.twinx() for ax in axs.flat ])
            #twinxs.shape = axs.shape
            #lines.extend(subplot(y2x1,*twinxs.flat))
            #try: labels[3]
            #except IndexError: pass
            #else: twinxs[0,-1].set_ylabel(labels[3])

        #elif y1x2:
            #twinxs = numpy.array([ ax.twiny() for i in axs.flat ])
            #twinxs.shape = axs.shape
            #lines.extend(subplot(y1x2,*twinxs.flat))
            #try: labels[2]
            #except IndexError: pass
            #else: twinxs[-1,0].set_xlabel(labels[2])



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
    fig.tight_layout()
    fig.savefig(target,format=outformat)
    return fig
