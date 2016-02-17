#!/usr/bin/python3
'''commandline interface for the package: specify recipe and optionally which target to work on'''

#import inputfilter, helpers, operations
import sys,os.path,re
import yaml
sys.path.insert(0,os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from plotter import yamlplot

# load recipe
try: recipes = yaml.load(open(sys.argv[1]))
except (FileNotFoundError,IndexError):
    print(help(yamlplot))
    sys.exit(1)

# first item in list is defaults if it has no target
#if set(('target','y','y1','y2','yx','y1x','y1x1','y2x','y2x1','y2x2')).intersection(recipes[0]):
if set(('target')).intersection(recipes[0]):
    firstRecipe = 0
else:
    firstRecipe = 1

targets = sys.argv[2:]
if targets:
    for recipe in recipes[firstRecipe:]:
        t = recipe['target']
        if isinstance(t,list):
            t=t[0]
        if t not in targets:
            recipes.remove(recipe)

yamlplot(recipes)
