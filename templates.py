from sys import argv
from os import listdir
from pprint import pprint
dirname = argv[1]
'''
from mako.template import Template
from mako.lookup import TemplateLookup

mylookup = TemplateLookup(
    directories=['/home/oliver/Documents/pgn4/mysite/themes/ebbandflow/templates'],
    module_directory='/home/oliver/Documents/pgn4/template_cache_dir',
    collection_size=500 # Caching
)
t = mylookup.get_template('pages.mako')
t.render()
breakpoint()
'''

from mako import util, lexer
#from mako.parsetree import InheritTag, BlockTag, IncludeTag

# Thanks! https://groups.google.com/g/mako-discuss/c/rNj6Vxc984k/m/dVM08xaUAmoJ

for filename in listdir(dirname):

    t = dirname + '/' + filename

    text = util.read_file(t)
    lex = lexer.Lexer(text=text, filename=t)
    lex.parse()

    deps = []
    for n in lex.template.nodes:
        if getattr(n, 'keyword', None) == 'inherit': #if isinstance(n, InheritTag):
            deps.append(n.attributes['file'])
        elif getattr(n, 'keyword', None) == 'block': #elif isinstance(n, BlockTag):
            for nn in n.nodes:
                if getattr(nn, 'keyword', None) == 'include': #if isinstance(nn, IncludeTag):
                    deps.append(nn.attributes['file'])
    print(filename + ' -> ' + str(deps))
#breakpoint()

