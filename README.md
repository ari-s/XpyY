XpyY
===

Create lineplots with rather declarative "recipes".

[matplotlib](http://matplotlib.org/) is the one python library for plotting, and it's capable of producing the plots the author wants. However for common situations it necessitates much boilerplate code and some common plots are hard to produce [1]. It also encourages intermixing of data analysis and plotting code, and, to some extent, data parsing code - often you need plots for one paper or similar, so no need for maintaineability right? And later you want to change one thing on your plots...

XpyY is pronounced as  ```X⋅Y```: "X py Y"

[1] Want a broken axis? Just follow [this example](http://matplotlib.org/examples/pylab_examples/broken_axis.html), right? Want twin axis too? Well, broken axis of one plot is produced with multiple subplots, so you can't twin your single subplot. What now? Well, the code is in subplots2.py


Recipes
---
```
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
```

Example recipe
---

```
---
- figsize: [170,70]
  srcprefix: /tmp/data/
  targetprefix: /tmp/plots/

- src: data.lvm
  target: [plot.pdf, r, t, r]
  y:
    - smoothen:
        derive: [0,3]
      args:
        M: 150
    - label: rate
  y2:
    - [0,4]
    - color: r
      label: temperature
  y2label: Temperature
  maxXTicks: [ 0, 4 ]
  xbreaks: [[0,24000],[81000,98000]]
  legendopts: {loc: upper left}
```

