#!/usr/local/bin/python

import sys
import graphviz as gv
import functools
from pprint import pprint
import random
import math

#### functions and classes ####

def apply_styles(graph, styles):
  graph.graph_attr.update(
    ('graph' in styles and styles['graph']) or {}
  )
  graph.node_attr.update(
    ('nodes' in styles and styles['nodes']) or {}
  )
  graph.edge_attr.update(
    ('edges' in styles and styles['edges']) or {}
  )
  return graph

def add_nodes(graph, nodes):
  global courses
  for n in nodes:
    if isinstance(n, tuple):
      graph.node(courses[n[0]].name+' '+str(courses[n[0]].credits), **n[1])
    else:
      if courses[n].completed:
        graph.attr('node', fillcolor='#cecdc9', color='#cecdc9')
      else:
        graph.attr('node', fillcolor='white', color='white')
      graph.node(courses[n].name,'<<font color="#6e6d6a"><sub>'+str(courses[n].credits)+'</sub></font>   '+courses[n].name+'>')
  return graph

def add_edges(graph, edges):
  for e in edges:
    if isinstance(e[0], tuple):
      graph.edge(*e[0], **e[1])
    else:
      graph.edge(*e)
  return graph

class course:
  """Defines a course"""

  def __init__(self, name, credits, term, completed=False):
    self.name = name
    self.credits = credits
    self.term = term
    self.completed = completed
    self.prereqs = []
    self.coreqs = []
    self.coprereqs = []
    self.styles = {}

  def add_prereq(self, prereq):
    self.prereqs.append(prereq)
    return self

  def add_coreq(self, coreq):
    self.coreqs.append(coreq)
    return self

  def add_coprereq(self, coprereq):
    self.coprereqs.append(coprereq)
    return self

  def add_style(self, style_key, style_value):
    self.styles.update({style_key: style_value})
    return self

  def set_completed(self, coprereq=True):
    self.completed = coprereq
    return self

def new_course(name,credits,term,completed=False):
  global courses
  try: courses
  except NameError: courses = {}
  courses.update({name: course(name,credits,term,completed)})
  return courses[name]

#### colors ####

kelly_colors_hex = [
  0xFFB300, # Vivid Yellow
  0x803E75, # Strong Purple
  0xFF6800, # Vivid Orange
  0xA6BDD7, # Very Light Blue
  0xC10020, # Vivid Red
  0xCEA262, # Grayish Yellow
  0x817066, # Medium Gray

  # The following don't work well for people with defective color vision
  0x007D34, # Vivid Green
  0xF6768E, # Strong Purplish Pink
  0x00538A, # Strong Blue
  0xFF7A5C, # Strong Yellowish Pink
  0x53377A, # Strong Violet
  0xFF8E00, # Vivid Orange Yellow
  0xB32851, # Strong Purplish Red
  0xF4C800, # Vivid Greenish Yellow
  0x7F180D, # Strong Reddish Brown
  0x93AA00, # Vivid Yellowish Green
  0x593315, # Deep Yellowish Brown
  0xF13A13, # Vivid Reddish Orange
  0x232C16, # Dark Olive Green
  ]

#### build the graph ####

graph = functools.partial(gv.Graph, format='svg')
digraph = functools.partial(gv.Digraph, format='svg')

exec(open(sys.argv[1]).read())

nodes_by_term = [[],[],[],[],[],[],[],[]] # initialize
terms_by_name = ['1F','1S','2F','2S','3F','3S','4F','4S']
for course_key in courses.keys():
  course_term_index = terms_by_name.index(courses[course_key].term)
  nodes_by_term[course_term_index].append(courses[course_key].name)

edges = [] # initialize
edges_cluster = [] # initialize
color_lookup = {} # initialize
i_mod = 0
for course_key in courses.keys():
  for prereq in courses[course_key].prereqs:
    if prereq in color_lookup:
      edge_color = color_lookup[prereq]
    else:
      i_mod = (i_mod+1)%len(kelly_colors_hex)
      edge_color = str("#%06x" % kelly_colors_hex[i_mod])
      color_lookup[prereq] = edge_color
    if not courses[prereq].completed:
      edges.append(
        ((prereq,courses[course_key].name),{'style': 'solid','color': edge_color})
      )
  for coreq in courses[course_key].coreqs:
    if coreq in color_lookup:
      edge_color = color_lookup[coreq]
    else:
      i_mod = (i_mod+1)%len(kelly_colors_hex)
      edge_color = str("#%06x" % kelly_colors_hex[i_mod])
      color_lookup[coreq] = edge_color
    if not courses[coreq].completed:
      edges.append(
        ((coreq,courses[course_key].name),{'style': 'solid','color': edge_color,'dir': 'both'})
      )
  for coprereq in courses[course_key].coprereqs:
    if coprereq in color_lookup:
      edge_color = color_lookup[coprereq]
    else:
      i_mod = (i_mod+1)%len(kelly_colors_hex)
      edge_color = str("#%06x" % kelly_colors_hex[i_mod])
      color_lookup[coprereq] = edge_color
    if not courses[coprereq].completed:
      edges.append(
        ((coprereq,courses[course_key].name),{'style': 'dashed','color': edge_color})
      )

g = digraph(engine='dot')
g.attr(newrank='true',compound='true')
for i,term in enumerate(terms_by_name):
  term_credits = 0
  for c in nodes_by_term[i]:
    term_credits += courses[c].credits
  name_now = 'cluster_'+str(i)
  label_cluster = {'label': '<<B>term: '+str(terms_by_name[i])+'</B><BR/><FONT POINT-SIZE="10" COLOR="#6e6d6a">'+str(term_credits)+' cr</FONT>>'}
  h = add_nodes(digraph(name_now), nodes_by_term[i])
  h.graph_attr.update(rank='same',color='#cecdc9',style='filled',**label_cluster)
  g.subgraph(h)
  if i > 0:
    edges_cluster.append(
      (
        (nodes_by_term[i-1][0],nodes_by_term[i][0]),
        {'ltail': 'cluster_'+str(i-1),'lhead': name_now,'style': 'invis'}
      )
    )

g = add_edges(g, edges_cluster)
g = add_edges(g, edges)

font = 'Helvetica'
node_color = '#5e5d87'
styles = {
  'graph': {
    # 'label': 'Prerequisite structure',
    'fontsize': '16',
    'fontcolor': 'black',
    'fontname': font,
    'bgcolor': 'white',
    'rankdir': 'LR',
  },
  'nodes': {
    'fontname': font,
    'shape': 'rectangle',
    'fontcolor': node_color,
    'color': 'white',
    'style': 'filled',
    'fillcolor': 'white',
  },
  'edges': {
    'style': 'dashed',
    'color': 'black',
    'fontname': font,
    'fontsize': '12',
    'fontcolor': 'black',
    'penwidth': '3',
    'arrowsize': '1',
    'arrowhead': 'normal',
  }
}


g = apply_styles(g, styles)
g.render('img/'+sys.argv[1].split('.')[0])
g.view()

#### legend ####
# gl = digraph(engine='dot')
# gl.node('pr','pre-requisite')
# gl.node('cr','co-requisite')
# gl.node('pcr','pre- or co-requisite')
# gl.edge()

from graphviz import Source
temp = """
digraph {
  rankdir=LR
  node [shape=plaintext]
  fontname=Helvetica
  subgraph cluster_01 {
    label=Legend
    key [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">
      <tr><td align="right" port="i1">prerequisite  </td></tr>
      <tr><td align="right" port="i2">corequisite  </td></tr>
      <tr><td align="right" port="i3">con-prerequisite  </td></tr>
      </table>>, fontname=Helvetica]
    key2 [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">
      <tr><td port="i1">&nbsp;</td></tr>
      <tr><td port="i2">&nbsp;</td></tr>
      <tr><td port="i3">&nbsp;</td></tr>
      </table>>, fontname=Helvetica]
    key:i1:e -> key2:i1:w [penwidth=3]
    key:i2:e -> key2:i2:w [dir="both",penwidth=3]
    key:i3:e -> key2:i3:w [style=dashed,penwidth=3]
  }
}
"""
gl = Source(temp, filename="img/legend", format="svg")
gl.render('img/'+sys.argv[1].split('.')[0]+'_legend')
# gl.view()