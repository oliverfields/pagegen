from os.path import isfile, join
import importlib.util
from inspect import getmembers, isfunction
import shortcodes_built_in
import re
from inspect import signature
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)


class UndefinedShortcodeError(Exception):
    '''
    Exception raised when a shortcode is found but no definition exists
    '''


class Plugin:

    def hook_pre_build(self, objects):

        self.cache = {} # For shortcodes use
        self.shortcodes = {}

        self.sc_built_in = shortcodes_built_in
        self.sc_custom_file = join(objects['site'].site_dir, 'shortcodes.py')

        self.sc_regexp = re.compile(r'<sc>(.*?)</sc>')

        self.load_shortcodes(self.sc_custom_file, self.sc_built_in)



    def __getitem__(self, shortcode):
        ''' Return shortcode function '''
        return self.shortcodes[shortcode]


    def load_shortcodes(self, custom_shortcodes, built_in_shortcodes):
        '''
        Load built in shortcodes and then custom shortcodes if shortcodes.py exists
        '''

        # Load built in shortcodes
        built_in_functions = getmembers(built_in_shortcodes, isfunction)

        for built_in_name, built_in_function in built_in_functions:
            if built_in_name.startswith('built_in_'):
                sc_name = built_in_name[9:]
                self.shortcodes[sc_name] = built_in_function


        if isfile(custom_shortcodes):
            spec = importlib.util.spec_from_file_location('custom_shortcodes', custom_shortcodes)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)

            # Add custom shortcodes, will overwrite built-in ones
            custom_functions = getmembers(m, isfunction)
            for custom_name, custom_function in custom_functions:
                self.shortcodes[custom_name] = custom_function


    def __repr__(self):

        shortcodes = ''

        for n, f in sorted(self.shortcodes.items()):
            s = signature(f)
            shortcodes += n + str(s) + '\n'

        return shortcodes.rstrip('\n')


    def hook_page_render(self, objects):
        '''
        Replace return value for any shortcode tags (<sc>...</sc>) fund in content
        '''

        for function in re.findall(self.sc_regexp, objects['page'].body):

            # Get function name, everything until first ( is the name
            sc_tmp = function.split('(', 1)

            shortcode_name = sc_tmp[0]

            p = objects['page']

            # Shortcodes may be just "name" or "name()" or "name(arguments)", need get arguments for shortcode function..
            if sc_tmp[1] == ')': # only "name", always add site as argument
                shortcode_arguments = '(objects["site"], p)'
            else:
                shortcode_arguments = '(objects["site"], p, ' + sc_tmp[1] # Need to add back the ( split char

            # Try to run shortcode
            try:
                sc_function_call = 'self.shortcodes["' + shortcode_name + '"]' + shortcode_arguments
                shortcode_result = eval(sc_function_call)
            except KeyError:
                raise KeyError(f'{p}: Undefined shortcode: {shortcode_name}')
            #raise Exception('Unable to run shortcode ' + shortcode_name + shortcode_arguments + ': ' + sc_function_call + ': ' + str(e))

            if not isinstance(shortcode_result, str):
                raise Exception('Shortcode ' + shortcode_name + ' did not return a string, it returned a ' + str(type(shortcode_result)))


            shortcode_string = '<sc>' + function + '</sc>'

            p.out = p.out.replace(shortcode_string, shortcode_result)

