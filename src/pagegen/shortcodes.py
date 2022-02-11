from pagegen.utility import SHORTCODECUSTOM, report_warning
from os.path import isfile
import importlib.util
from inspect import getmembers, isfunction
import pagegen.shortcodes_built_in


class shortcodes:

	def __init__(self, dir_path):

		self.shortcodes = {}

		self.sc_built_in = pagegen.shortcodes_built_in
		sc_custom_file = dir_path + '/' + SHORTCODECUSTOM + '.py'

		self.load_shortcodes(SHORTCODECUSTOM, sc_custom_file, self.sc_built_in)


	def load_shortcodes(self, module_name, file_path, built_in_shortcodes):
		''' Load built in shortcodes and then custom shortcodes if shortcodes.py exists '''

		# Load built in shortcodes
		built_in_functions = getmembers(built_in_shortcodes, isfunction)

		for built_in_name, built_in_function in built_in_functions:
			self.shortcodes[built_in_name] = built_in_function

		if isfile(file_path):
			spec = importlib.util.spec_from_file_location(module_name, file_path)
			m = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(m)

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


	def run(self, content):
		''' Replace return value for any shortcode tags (<sc>...</sc>) fund in content '''

		return content
