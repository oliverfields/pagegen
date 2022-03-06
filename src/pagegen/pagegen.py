from pagegen.utility import report_error, report_notice, get_site_conf_path, SITECONF, HOME, CONFROOT, TARGETDIR, HOOKDIR, CONTENTDIR, exec_script, ASSETDIR, THEMEDIR, SHORTCODECUSTOM
from pagegen.site import site
from os.path import expanduser, basename, join, isfile
from os import getcwd, listdir, sep, chdir, X_OK, access
from sys import exit, argv
from distutils.dir_util import copy_tree
from getopt import getopt, GetoptError
import pkg_resources
from pagegen.auto_build_serve import auto_build_serve


def usage(exit_after=True):
	print('Usage: %s [-i|--init] [-g|--generate <environment>] [-s|--serve <environment>] [-v|--version] [-h|--help]' % (basename(argv[0])))

	if exit_after:
		exit(0)


def guess_site_conf_and_dir_paths(site_conf_path):
	if not site_conf_path:
		site_conf_path=get_site_conf_path()

	if not site_conf_path:
		report_error(1, "Not in pagegen directory tree, unable to find a valid site.conf")

	return (site_conf_path, site_conf_path[:-len(sep+basename(site_conf_path))])


def build_site(site_conf_path, environment, exclude_hooks=[], force_base_url=None, serve_mode=False):
	site_conf_path, site_dir=guess_site_conf_and_dir_paths(site_conf_path)

	try:
		s=site(site_dir, site_conf_path, environment, serve_mode)
	except Exception as e:
		report_error(1, "Unable to load site: %s" % e)

	# Force base_url, needed to make --serve work correctly
	if force_base_url != None:
		s.base_url = force_base_url

	# Set environment variable for hooks
	envs={
		'PAGEGEN_SITE_DIR': site_dir,
		'PAGEGEN_HOOK_DIR': join(site_dir, HOOKDIR),
		'PAGEGEN_SOURCE_DIR': join(site_dir, CONTENTDIR),
		'PAGEGEN_TARGET_DIR': join(site_dir, TARGETDIR, s.environment),
		'PAGEGEN_ENVIRONMENT': s.environment
	}

	# Put all config settings for current environment into hook env
	for (key, value) in  s.raw_config.items(s.environment):
		envs['PAGEGEN_' + key.upper()] = value

	# Run pre hook
	if not 'pre_generate' in exclude_hooks:
		envs['PAGEGEN_HOOK']='pre_generate'
		hook = join(site_dir,HOOKDIR,'pre_generate')
		if isfile(hook) and access(hook, X_OK):
			exec_script(hook, envs)

	try:
		s.prepare()
		chdir(s.site_dir)
		s.set_excerpts()
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

	s.move_to_target()

	# Run post hook
	if not 'post_generate' in exclude_hooks:
		envs['PAGEGEN_HOOK']='post_generate'
		hook = join(site_dir,HOOKDIR,'post_generate')
		if isfile(hook) and access(hook, X_OK):
			exec_script(hook, envs)

	# Run deploy hook
	if not 'deploy' in exclude_hooks:
		envs['PAGEGEN_HOOK']='deploy'
		hook = join(site_dir,HOOKDIR,'deploy')
		if isfile(hook) and access(hook, X_OK):
			exec_script(hook, envs)

	# Run post deploy
	if not 'post_deploy' in exclude_hooks:
		envs['PAGEGEN_HOOK']='post_deploy'
		hook = join(site_dir,HOOKDIR,'post_deploy')
		if isfile(hook) and access(hook, X_OK):
			exec_script(hook, envs)


def serve_mode(site_conf_path, environment):
	site_conf_path, site_dir=guess_site_conf_and_dir_paths(site_conf_path)
	serve_dir = site_dir + '/' + TARGETDIR + '/' + environment
	exclude_hooks=['deploy','post_deploy']
	serve_base_url='http://localhost'
	serve_port = '8000'

	# Build site and serve
	build_site(site_conf_path, environment, exclude_hooks, serve_base_url + ':' + serve_port, serve_mode=True)

	watch_elements = [
		CONTENTDIR,
		HOOKDIR,
		ASSETDIR,
		SITECONF,
		THEMEDIR,
		SHORTCODECUSTOM + '.py',
	]

	watch_elements_full_path = [site_dir + '/' + we for we in watch_elements]

	auto_build_serve(site_conf_path, environment, watch_elements_full_path, serve_dir, exclude_hooks, build_site, serve_base_url, serve_port)


def gen_mode(site_conf_path, environment):
	build_site(site_conf_path, environment, exclude_hooks=[], force_base_url=None, serve_mode=False)


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
		opts, args=getopt(argv[1:],"ig:vs:h", ["init", "generate", "version", "serve=", "help"])
	except GetoptError as e:
		usage(exit_after=False)
		report_error(1, "Invalid arguments: %s" % e)

	mode=False
	site_config=False

	for opt, arg in opts:
		if opt in ('-i', '--init'): 
			mode="init"
		elif opt in ('-g', '--generate'):
			environment=arg.lstrip('=')
			mode='gen'
		elif opt in ('-v', '--version'):
			print("pagegen %s" % pkg_resources.get_distribution("pagegen").version)
			exit(0)
		elif opt in ('-s', '--serve'):
			environment=arg.lstrip('=')
			mode='serve'
		elif opt in ('-h', '--help'):
			usage(exit_after=True)

	if mode == 'gen':
		gen_mode(site_config, environment)
	elif mode == 'init':
		init_mode()
	elif mode == 'serve':
		serve_mode(site_config, environment)
	else:
		usage(exit_after=True)


if __name__ == '__main__':
	main()
