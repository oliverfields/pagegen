from pagegen.utility_no_deps import report_error, report_notice, get_site_conf_path, exec_script, urlify, remove_prefix
from os.path import expanduser, basename, join, isfile, isdir, dirname, exists, abspath
from sys import exit, argv
from os import getcwd, listdir, chdir, X_OK, access, get_terminal_size, makedirs, getenv, walk, environ
from pagegen.constants import SITECONF, HOME, CONFROOT, TARGETDIR, HOOKDIR, CONTENTDIR, ASSETDIR, THEMEDIR, SHORTCODECUSTOM, DIRDEFAULTFILE, PAGEGENVERSION
from subprocess import run, PIPE


def usage(exit_after=True):
    print('Usage: pgn [-i|--init] [-g|--generate <environment>] [-p|--page <page path>] [-s|--serve <environment>] [-v|--version] [-h|--help] <item>')

    if exit_after:
        exit(0)


def guess_site_conf_and_dir_paths(site_conf_path):
    if not site_conf_path:
        site_conf_path=get_site_conf_path()

    if not site_conf_path:
        report_error(1, "Not in pagegen directory tree, unable to find a valid site.conf")

    return (site_conf_path, site_conf_path[:-len('/'+basename(site_conf_path))])


def build_site(site_conf_path, environment, exclude_hooks=[], force_base_url=None, serve_mode=False, single_page_path=False):
    from pagegen.site import site

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
        if single_page_path:
            s.prepare_single_page(single_page_path)
        else:
            s.prepare_all_pages()

        chdir(s.site_dir)
        s.set_excerpts()
        s.generate_pages_html(s.pages)
        s.build_backlinks_index()
        s.apply_templates(s.pages)
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

    return s


def file_mode(item, site_conf_path):
    '''
    Create and open file for editing
    '''

    site_conf_file, site_dir=guess_site_conf_and_dir_paths(site_conf_path)
    selected_file = False
    content_dir = site_dir + '/' + CONTENTDIR

    # If item False and fzy or fzf exist then allow user to select a file to edit
    if item == False:

        # Get files and directories
        items = []
        for current_path, dirs, files in walk(content_dir):
            for f in files:
                items.append(join(current_path, f))

        paths = ''

        for i in items:
            # Skip assets
            if '/assets/' in i or i.endswith('/assets'):
                continue

            # Skip root
            if i == content_dir + '/':
                continue

            # Skip directories
            if isdir(i):
                continue

            # Strip content_dir
            paths += i[len(content_dir + '/'):] + '\n'

        paths = paths.rstrip()

        # Select file using fzy
        try:
            columns, lines = get_terminal_size()
            lines = lines - 1
            result = run(['fzy', '--lines=' + str(lines)], stdout=PIPE, input=paths.encode('utf-8'))
            selected_file = content_dir + '/' + result.stdout.decode('utf-8').rstrip()
        except FileNotFoundError:
            # Select file using fzf
            try:
                result = run(['fzf'], stdout=PIPE, input=paths.encode('utf-8'))
                selected_file = content_dir + '/' + result.stdout.decode('utf-8').rstrip()
            except FileNotFoundError:
                pass

        if result.returncode != 0:
            exit(0)

    # If item is not False then create it
    else:
        full_path = content_dir + '/' + item
        if not exists(full_path):
            # If new path is a directory, create dir and add index file
            if full_path.endswith('/'):
                makedirs(full_path.rstrip('/'), exist_ok=True)
                selected_file = full_path + DIRDEFAULTFILE
            # If path is file, create any dirs if needed
            else:
                if '/' in item:
                    makedirs(dirname(full_path), exist_ok=True)
                selected_file = full_path
        # File exists
        else:
            selected_file = full_path

    # Open file for editing
    if selected_file:
        if getenv('EDITOR'):
            editor = getenv('EDITOR')
        else:
            editor = 'vim'

        run([editor, selected_file])

    exit(0)


def serve_mode(site_conf_path, environment, single_page_path=False, default_extension=False):
    site_conf_path, site_dir=guess_site_conf_and_dir_paths(site_conf_path)
    serve_dir = site_dir + '/' + TARGETDIR + '/' + environment
    exclude_hooks=['deploy','post_deploy']
    serve_base_url='http://localhost'
    serve_port = '8000'


    # Build site and serve
    site = build_site(site_conf_path, environment, exclude_hooks, serve_base_url + ':' + serve_port, serve_mode=True, single_page_path=single_page_path)

    default_serve_url = False

    if single_page_path:
        default_serve_url = remove_prefix(single_page_path, site_dir + '/' + CONTENTDIR + '/')
        # urlify needs to strip /digits_ so add / and then strip it
        default_serve_url = urlify('/' + default_serve_url)[1:]
        default_serve_url += site.default_extension

    watch_elements = [
        CONTENTDIR,
        HOOKDIR,
        ASSETDIR,
        SITECONF,
        THEMEDIR,
        SHORTCODECUSTOM + '.py',
    ]

    watch_elements_full_path = [site_dir + '/' + we for we in watch_elements]

    from pagegen.auto_build_serve import auto_build_serve

    auto_build_serve(site_conf_path, environment, watch_elements_full_path, serve_dir, exclude_hooks, build_site, serve_base_url, serve_port, default_url=default_serve_url, single_page_path=single_page_path)


def gen_mode(site_conf_path, environment):
    build_site(site_conf_path, environment, exclude_hooks=[], force_base_url=None, serve_mode=False)


def init_mode():
    ''' Copy skeleton directory to current directory for basic setup '''

    from distutils.dir_util import copy_tree

    skel_dir = dirname(abspath(__file__)) + '/skel'
    root_dir=getcwd()

    if listdir(root_dir):
        report_error(1,"Cannot init non empty directory '%s'" % root_dir)

    try:
        copy_tree(skel_dir, root_dir)
    except Exception as e:
        report_error(1, "Unable to copy '%s' to '%s': %s" % (skel_dir, root_dir, e))


def main():
    site_config=False

    # Do file mode first, for perfomance
    if len(argv) < 3:
        if len(argv) == 1:
            file_mode(False, site_config)
        elif not argv[1].startswith('-'):
            file_mode(argv[1], site_config)

    environment=None

    # Lazy load what we can
    from getopt import getopt, GetoptError

    try:
        opts, args=getopt(argv[1:],"ig:vs:hp:", ["init", "generate=", "version", "page=", "serve=", "help"])
    except GetoptError as e:
        usage(exit_after=False)
        report_error(1, "Invalid arguments: %s" % e)

    mode=False
    page_path=False
    for opt, arg in opts:
        if opt in ('-i', '--init'): 
            mode="init"
        elif opt in ('-g', '--generate'):
            environment=arg.lstrip('=')
            mode='gen'
        elif opt in ('-v', '--version'):
            print("pagegen %s" % PAGEGENVERSION)
            exit(0)
        elif opt in ('-p', '--page'):
            page_path=arg.lstrip('=')
            mode='page'
        elif opt in ('-s', '--serve'):
            environment=arg.lstrip('=')
            mode='serve'
        elif opt in ('-h', '--help'):
            usage(exit_after=True)

    if mode == 'gen':
        gen_mode(site_config, environment)
    elif mode == 'init':
        init_mode()
    elif page_path:
        if environment == None:
            report_error(1, 'Argument -p|--page requires that -s|--serve <env> is also set')
            usage(exit_after=True)
        if not page_path.startswith('/'):
            page_path = getcwd() + '/' + page_path
        serve_mode(site_config, environment, single_page_path=page_path)
    elif mode == 'serve':
        serve_mode(site_config, environment)
    else:
        usage(exit_after=True)

if __name__ == '__main__':
    main()
