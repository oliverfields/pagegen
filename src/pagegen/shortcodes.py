from pagegen.utility import SHORTCODECUSTOM, report_warning
from os.path import isfile
import importlib.util
from inspect import getmembers, isfunction
import pagegen.shortcodes_built_in
import re


class shortcodes:

	def __init__(self, site):

		self.site = site
		self.shortcodes = {}

		self.sc_built_in = pagegen.shortcodes_built_in
		sc_custom_file = self.site.site_dir + '/' + SHORTCODECUSTOM + '.py'

		self.load_shortcodes(SHORTCODECUSTOM, sc_custom_file, self.sc_built_in)

		self.sc_regexp = re.compile(r'<sc>(.*?)</sc>')


	def load_shortcodes(self, module_name, file_path, built_in_shortcodes):
		''' Load built in shortcodes and then custom shortcodes if shortcodes.py exists '''

		# Load built in shortcodes
		built_in_functions = getmembers(built_in_shortcodes, isfunction)

		for built_in_name, built_in_function in built_in_functions:
			self.shortcodes[built_in_name] = built_in_function

		if isfile(file_path):
			try:
				spec = importlib.util.spec_from_file_location(module_name, file_path)
				m = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(m)
			except Exception as e:
				raise Exception('Unable to load ' + SHORTCODECUSTOM + '.py: ' + str(e))

			# Check no naming conflicts
			custom_functions = getmembers(m, isfunction)

			for custom_name, custom_function in custom_functions:
				if custom_name in self.shortcodes.keys():
					report_warning(SHORTCODECUSTOM + '.py contains function ' + custom_name + ' that is also a built in shortcode, not loading the custom one')
				else:
					self.shortcodes[custom_name] = custom_function


	def __repr__(self):

		shortcodes = ''

		for n, f in sorted(self.shortcodes.items()):
			args = ''
			is_first_arg = True
			for a in f.__code__.co_varnames:
				if is_first_arg:
					args += a
					is_first_arg = False
				else:
					args += ', ' + a
			shortcodes += '<sc>' + n + '(' + args + ')</sc>\n'

		return shortcodes.rstrip('\n')


	def run(self, page):
		''' Replace return value for any shortcode tags (<sc>...</sc>) fund in content '''

		self.page = page # Use this just to make references from sc tags same for page and site, ie. self.page or self.site in shortcall argument list

		for function in re.findall(self.sc_regexp, page.content):

			# Get function name, everything until first ( is the name
			sc_tmp = function.split('(', 1)

			shortcode_name = sc_tmp[0]

			# Shortcodes may be just "name" or "name()" or "name(arguments)", need get arguments for shortcode function..
			if len(sc_tmp) == 1: # only "name", always add site as argument
				shortcode_arguments = '()'
			else:
				shortcode_arguments = '(' + sc_tmp[1] # Need to add back the ( split char

			# Try to run shortcode
			if shortcode_name in self.shortcodes.keys():
				sc_function_call = 'self.shortcodes["' + shortcode_name + '"]' + shortcode_arguments
				try:
					shortcode_result = eval(sc_function_call)
				except Exception as e:
					raise Exception('Unable to run shortcode ' + shortcode_name + shortcode_arguments + ': ' + sc_function_call + ': ' + str(e))

			else:
				raise Exception('Shortcode "' + shortcode_name + '" is not defined')

			shortcode_string = '<sc>' + function + '</sc>'
			page.content = page.content.replace(shortcode_string, shortcode_result)