# styles.py

FONT = 'Helvetica'
NODE_COLOR = '#5e5d87'

styles = {
    'graph': {
        'fontsize': '16',
        'fontname': FONT,
        'bgcolor': 'white',
        'rankdir': 'LR',
    },
    'nodes': {
        'fontname': FONT,
        'shape': 'rectangle',
        'fontcolor': NODE_COLOR,
        'color': 'white',
        'style': 'filled',
        'fillcolor': 'white',
    },
    'edges': {
        'style': 'dashed',
        'color': 'black',
        'fontname': FONT,
        'fontsize': '12',
        'fontcolor': 'black',
        'penwidth': '3',
        'arrowsize': '1',
        'arrowhead': 'normal',
    }
}