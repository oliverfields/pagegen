#------------------------------------------------------------
# Pagegen - static site generator
# Copyright (C) 2015  Oliver Fields, pagegen@phnd.net
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------

from pagegen.utility import report_error, report_notice, get_site_conf_path, PAGEGENCONF, SITECONF, HOME, CONFROOT, TARGETDIR, DEPLOYSCRIPTDIR, HOOKDIR, CONTENTDIR, exec_script
from pagegen.site import site
from os.path import expanduser, basename, join, isfile
from os import getcwd, listdir, sep, chdir
from sys import exit, argv
from distutils.dir_util import copy_tree
from getopt import getopt, GetoptError
import pkg_resources


def usage(exit_after=True):
	print('Usage: %s [-i|--init] [-g|--generate] [-e|--environment <environment>] [-c|--config <site config file>] [-v|--version]' % (basename(argv[0])))

	if exit_after:
		exit(0)


def gen_mode(site_conf_path, environment):

	if not site_conf_path:
		site_conf_path=get_site_conf_path()

	if not site_conf_path:
		report_error(1, "Not in pagegen directory tree, unable to find a valid site.conf")
	site_dir=site_conf_path[:-len(sep+basename(site_conf_path))]

	try:
		s=site(site_dir, site_conf_path, environment)
	except Exception as e:
		report_error(1, "Unable to load site: %s" % e)

	# Set environment variable for hooks
	envs={
		'PAGEGEN_SITE_DIR': site_dir,
		'PAGEGEN_HOOK_DIR': join(site_dir, HOOKDIR),
		'PAGEGEN_DEPLOY_SCRIPT_DIR': join(site_dir, DEPLOYSCRIPTDIR),
		'PAGEGEN_SOURCE_DIR': join(site_dir, CONTENTDIR),
		'PAGEGEN_TARGET_DIR': join(site_dir, TARGETDIR, s.environment),
		'PAGEGEN_ENVIRONMENT': s.environment,
		'PAGEGEN_BASE_URL': s.base_url,
	}

	# Run pre hook
	envs['PAGEGEN_HOOK']='pre_generate'
	hook = join(site_dir,HOOKDIR,'pre_generate')
	if isfile(hook):
		exec_script(hook, envs)

	try:
		s.prepare()
		chdir(s.site_dir)
		s.generate_pages(s.pages)
	except Exception as e:
		report_error(1, "Unable to generate site: %s" % e)

	if s.exclude_sitemap != True:
		try:
			s.generate_sitemap(s.pages)
		except Exception as e:
			report_error(1, "Unable to generate /sitemap.xml: %s" % e)

	if s.include_rss != False:
		try:
			s.generate_rss()
		except Exception as e:
			report_error(1, "Unable to generate /feed.rss: %s" % e)

	try:
		s.move_to_target()
	except Exception as e:
		report_error(1, "Unable to copy to target directory '%s': %s" % (s.target_dir, e))

	# Run post hook
	envs['PAGEGEN_HOOK']='post_generate'
	hook = join(site_dir,HOOKDIR,'post_generate')
	if isfile(hook):
		exec_script(hook, envs)

	# If deploy mode set, then try to run the script of same name
	if s.deploy_script != None:

		# Environment settings for deploy script
		envs={
			'PAGEGEN_SITE_DIR': site_dir,
			'PAGEGEN_SOURCE_DIR': join(site_dir, CONTENTDIR),
			'PAGEGEN_GENERATED_DIR': join(site_dir, TARGETDIR, s.environment),
		}

		for (key, value) in  s.raw_config.items(s.environment):
			envs['PAGEGEN_' + key.upper()] = value

		exec_script(join(site_dir,DEPLOYSCRIPTDIR,s.deploy_script), envs)


	# Run post deploy
	envs['PAGEGEN_HOOK']='post_deploy'
	hook = join(site_dir,HOOKDIR,'post_deploy')
	if isfile(hook):
		exec_script(hook, envs)


def init_mode():
	''' Copy skeleton directory to current directory for basic setup '''

	skel_dir = pkg_resources.resource_filename('pagegen', 'skel/')
	root_dir=getcwd()

	if listdir(root_dir):
		report_error(1,"Cannot init non empty directory '%s'" % root_dir)

	try:
		copy_tree(skel_dir, root_dir)
	except Exception as e:
		report_error(1, "Unable to copy '%s' to '%s': %s" % (skel_dir, root_dir, e))


def main():

	environment=None

	try:
		opts, args=getopt(argv[1:],"igvc:e:", ["init", "generate", "version", "config=", "environment="])
	except GetoptError as e:
		usage(exit_after=False)
		report_error(1, "Invalid arguments: %s" % e)

	mode=False
	site_config=False

	for opt, arg in opts:
		if opt in ('-i', '--init'): 
			mode="init"
		elif opt in ('-g', '--generate'):
			mode='gen'
		elif opt in ('-v', '--version'):
			print("pagegen %s" % pkg_resources.get_distribution("pagegen").version)
			exit(0)
		elif opt in ('-c', '--config'):
			site_config=arg.lstrip('=')
			# Add current dir absolute path if supplied releative path argument
			if not site_config.startswith(sep):
				site_config=join(getcwd(), site_config)
		elif opt in ('-e', '--environment'):
			environment=arg.lstrip('=')

	if mode == 'gen':
		gen_mode(site_config, environment)
	elif mode == 'init':
		init_mode()
	else:
		usage(exit_after=True)


if __name__ == '__main__':
	main()
