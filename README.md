XpyY
===

Create lineplots with rather declarative "recipes".

[matplotlib](http://matplotlib.org/) is the one python library for plotting, and it's capable of producing the plots the author wants. However for common situations it necessitates much boilerplate code and some common plots are hard to produce [1]. It also encourages intermixing of data analysis and plotting code, and, to some extent, data parsing code - often you need plots for one paper or similar, so no need for maintaineability right? And later you want to change one thing on your plots...

This is prealpha, so missing documentation, here is an example recipe (YAML):
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

XpyY is pronounced as  ```X⋅Y```: "X py Y"

[1] Want a broken axis? Just follow [this example](http://matplotlib.org/examples/pylab_examples/broken_axis.html), right? Want twin axis too? Well, broken axis of one plot is produced with multiple subplots, so you can't twin your single subplot. What now? Well, the code is in subplots2.py
