from os import listdir
from os.path import join
from mako import util, lexer
import logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)
#from mako.parsetree import InheritTag, BlockTag, IncludeTag

# Thanks! https://groups.google.com/g/mako-discuss/c/rNj6Vxc984k/m/dVM08xaUAmoJ

class TemplateDeps():
    '''
    Load mako templates and return list of dependencies for each one
    '''

    def __init__(self, template_dir):
        '''
        Parse each template and work out its dependencies
        '''
        self.deps = {}

        for t in listdir(template_dir):
            t_path = join(template_dir, t)

            self.deps[t_path] = []

            text = util.read_file(t_path)
            lex = lexer.Lexer(text=text, filename=t_path)
            lex.parse()

            for n in lex.template.nodes:
                if getattr(n, 'keyword', None) == 'inherit': #if isinstance(n, InheritTag):
                    self.deps[t_path].append(join(template_dir, n.attributes['file']))
                elif getattr(n, 'keyword', None) == 'block': #elif isinstance(n, BlockTag):
                    for nn in n.nodes:
                        if getattr(nn, 'keyword', None) == 'include': #if isinstance(nn, IncludeTag):
                            self.deps[t_path].append(join(template_dir, nn.attributes['file']))

