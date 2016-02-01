
import pyparsing,re
from packagedefaults import packagedefaults
from plot import inputfilter,operations

def execDraw(src, instructions,p,**plotopts):
    '''executes drawing instruction as described in __main__.__doc__'''
    pass

def plot(recipe,fig,defaults,xlen=1,ylen=1,xpos=1,ypos=1):
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

    # extracting drawing instructions
    plotRe = re.compile(r'(y[12]?)(x[12]?)?')
    y1x1,y2x1,y1x2,y2x2 = [],[],[],[]
    pop=[] #: need to delete drawing instructions from recipe
    for k in recipe.keys():
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

    # extract recipe keys that are not plot args
    xbreak = popset('xbreak')
    ybreak = popset('ybreak')
    src = popset('src')
    plotpos= popset('plotpos',((xlen*ylen),xpos,ypos))
    subplotopts = popset('subplotopts',{})
    target = recipe.pop('target') # no default for target

    # parse target, if not shorthand notation extract labels
    if isinstance(target,list):
        labels = target[2:]
        target,caption = target[:2]
    else:
        labels = list(map(popset,('xlabel','ylabel'),('x1label','y1label')))
        labels.extend(map(popset,('x2label', 'y2label')))

    if not isinstance(src,list):
        src = [ src ]

    srcprefix = popset('srcprefix')
    src = [ inputfilter.__call__( srcprefix+i ) for i in src ]

    # y1x1 plots
    p11 = fig.add_subplot(*plotpos,**subplotopts)
    execDraw(src, y1x1,p11,**recipe)
    if labels[0]: p11.set_xlabel(labels[0])
    if labels[1]: p11.set_ylabel(labels[1])

    if y2x1:
        p21 = p11.twiny()
        execDraw( y2x1, p21, **recipe )
        if labels[3]: p21.set_ylabel(labels[3])

    if y1x2:
        p12 = p11.twinx()
        execDraw( y1x2, p12, **recipe )
        if labels[2]: p12.set_xlabel(labels[2])

    if y2x2:
        raise NotImplementedError('Could not figure out how to handle reasonably in pyplot')

    return fig
