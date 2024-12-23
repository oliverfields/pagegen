from pagegen.utility import get_first_words, load_config, load_file, relative_path, render_template, write_file, generate_menu, rst_to_html, markdown_to_html
from pagegen.utility_no_deps import exec_script, is_default_file, report_error, report_notice, report_warning, remove_suffix, remove_prefix
from pagegen.constants import ASSETDIR, CONFROOT, CONTENTDIR, DATEFORMAT, DIRDEFAULTFILE, DIRECTORIESTEMPLATE, HOOKDIR, NEWLINE, RSSFEEDFILE, SEARCHINDEXFILE, SERVEMODEJSFILE, SITECONF, SITEMAPFILE, SITEMAPTXTFILE, STOPWORDSFILE, TAGSTEMPLATE, TAGTEMPLATE, TARGETDIR, TEMPLATEDIR, THEMEDIR, AUTHORTEMPLATE, AUTHORSTEMPLATE, AUTHORSCONF, DEFAULTMARKUP
from pagegen.utility_no_deps import urlify
from configparser import ConfigParser, NoOptionError
from os.path import isdir, join, isfile, exists, islink, split
from pathlib import Path
from os import listdir, sep, makedirs, remove, unlink, X_OK, access
from shutil import rmtree, copytree
from pagegen.page import page
from pagegen.virtualpage import virtualpage
from re import sub, search
from datetime import date
from datetime import datetime
from operator import itemgetter
from pagegen.searchindex import searchindex
from glob import glob
import pkg_resources
from pagegen.shortcodes import shortcodes


class site:
    """ Master object """

    def __init__(self, site_dir, config_file, environment, serve_mode):
        self.pages = []
        self.site_dir = ''
        self.base_url = ''
        self.theme = ''
        self.theme_template_dir = ''
        self.theme_asset_dir = ''
        self.sitemap = ''
        self.sitemaptxt = ''
        self.link_sequence = []
        self.rss_sequence = []
        self.rss = ''
        self.tags = {}
        self.search_index = searchindex(join(site_dir, STOPWORDSFILE))
        self.search_xpaths = []
        self.environment = environment
        self.serve_mode = serve_mode
        self.page_preview_path = False
        self.default_markup = DEFAULTMARKUP
        self.default_templates = {}
        self.page_list = []
        self.image_classes = {}
        self.authors = None
        self.strip_extensions = None
        self.cache = {} # Convinience attibure for general purpose storing of data

        if isdir(site_dir):
            self.site_dir = site_dir
            self.asset_dir = site_dir + '/' + CONTENTDIR + '/' + ASSETDIR
            self.content_dir = site_dir + '/' + CONTENTDIR
        else:
            raise Exception("Site dir '%s' is not a directory" % site_dir)

        self.shortcodes = shortcodes(self)

        if self.serve_mode:
            self.serve_mode_js_script = load_file(pkg_resources.resource_filename('pagegen', SERVEMODEJSFILE))

        try:
            config=load_config(config_file, add_dummy_section=False)
            self.raw_config=config
        except Exception as e:
            raise Exception("Unable to load site config '%s': %s" % e)

        # Ensure supplied environment exists as a section in the config
        if self.environment not in config.keys():
            report_error(1,'Environment "' + self.environment + '" not found as section in site.conf')

        # Set target dir based on environment
        self.target_dir=join(site_dir, TARGETDIR, self.environment)

        try:
            self.base_url=config.get(self.environment,'base_url')
        except:
            raise Exception('%s must contain base_url setting' % SITECONF)

        try:
            self.theme = config.get(self.environment,'theme')
            self.theme_template_dir = site_dir + '/' + THEMEDIR + '/' + self.theme + '/' + TEMPLATEDIR
            self.theme_asset_dir = site_dir + '/' + THEMEDIR + '/' + self.theme + '/' + ASSETDIR
            self.authors_conf = site_dir + '/' + AUTHORSCONF
        except:
            raise Exception('%s must contain theme setting' % SITECONF)

        # Set default template settings
        default_templates = {
            'directories': DIRECTORIESTEMPLATE,
            'tags': TAGSTEMPLATE,
            'tag': TAGTEMPLATE,
            'authors': AUTHORSTEMPLATE,
            'author': AUTHORTEMPLATE
        }

        for name, template in default_templates.items():
            if isfile(self.theme_template_dir + '/' + template):
                self.default_templates[name] = template
            else:
                self.default_templates[name] = False

        try:
            self.exclude_sitemap=self.ensure_bool('exclude_sitemap', config.get(self.environment,'exclude_sitemap'))
        except:
            self.exclude_sitemap=False

        try:
            self.tag_dir = config.get(self.environment,'tag_url')
        except:
            self.tag_dir = 'tag'

        try:
            self.tag_title = config.get(self.environment,'tag_title')
        except:
            self.tag_title = 'Tags'

        try:
            self.authors_title = config.get(self.environment,'authors_title')
        except:
            self.authors_title = 'Authors'

        try:
            self.authors_dir = config.get(self.environment,'author_dir')
        except:
            self.authors_dir = 'author'

        try:
            strip_extensions = config.get(self.environment,'strip_extensions')
            self.strip_extensions = strip_extensions.split(',')
        except:
            self.strip_extensions = None

        try:
            self.index_backlinks = self.ensure_bool('index_backlinks', config.get(self.environment, 'index_backlinks'))
        except:
            self.index_backlinks = False

        if isfile(self.authors_conf):
            try:
                authors_config = load_config(self.authors_conf, add_dummy_section=False)
                self.authors = {}
                for s in authors_config.sections():
                    self.authors[s] = {
                        'id': s
                    }
                    for setting, value in authors_config.items(s):
                        self.authors[s][setting] = value
            except Exception as e:
                pass

        try:
            self.include_rss=self.ensure_bool('include_rss', config.get(self.environment,'include_rss'))
        except:
            self.include_rss=False

        if self.include_rss:
            try:
                self.rss_title=config.get(self.environment,'rss_title')
            except:
                self.rss_title=''

            try:
                self.rss_description=config.get(self.environment,'rss_description')
            except:
                self.rss_description=''

        try:
            self.max_rss_items=int(config.get(self.environment,'max_rss_items'))
        except:
            self.max_rss_items=15

        try:
            self.absolute_urls = self.ensure_bool('absolute_urls', config.get(self.environment,'absolute_urls'))
        except:
            self.absolute_urls = True

        try:
            self.minify_html=self.ensure_bool('minify_html', config.get(self.environment,'minify_html'))
        except:
            self.minify_html=False

        try:
            self.minify_css=self.ensure_bool('minify_css', config.get(self.environment,'minify_css'))
        except:
            self.minify_css=False

        try:
            self.minify_javascript=self.ensure_bool('minify_javascript', config.get(self.environment,'minify_javascript'))
        except:
            self.minify_javascript=False

        try:
            title_length_range=config.get(self.environment,'title_length_range').split('-')
            min=int(title_length_range[0])
            max=int(title_length_range[1])

            if min < max:
                self.title_warn_min=min
                self.title_warn_max=max
        except:
            self.title_warn_min=0
            self.title_warn_max=0

        try:
            description_length_range=config.get(self.environment,'description_length_range').split('-')
            min=int(description_length_range[0])
            max=int(description_length_range[1])

            if min < max:
                self.description_warn_min=min
                self.description_warn_max=max
        except:
            self.description_warn_min=0
            self.description_warn_max=0

        try:
            self.default_extension=config.get(self.environment,'default_extension')
        except:
            self.default_extension=''

        try:
            self.url_include_index=self.ensure_bool('url_include', config.get(self.environment,'url_include_index'))
        except:
            self.url_include_index=True

        try:
            self.default_markup=config.get(self.environment,'default_markup')
        except:
            self.default_markup=DEFAULTMARKUP

        try:
            self.include_search=self.ensure_bool('include_search', config.get(self.environment,'include_search'))
        except:
            self.include_search=False

        try:
            xpaths=config.get(self.environment,'search_xpaths').split(',')
            for xpath in xpaths:
                self.search_index.index_xpaths.append(xpath)
        except:
            self.search_index.index_xpaths.append('/html/body')

        try:
            self.load_image_classes(config.get(self.environment, 'image_classes'))
        except NoOptionError:
            pass # Option was not defined
        except Exception as e:
            report_error(1, 'Unable to parse image_classes setting: ' + str(e))


    def load_image_classes(self, classes):
        ''' Parse setting string, format <name> <size WidthxHeight>[, <nameN> <WxH>]'''

        classes = sub(r'\s+', ' ', classes) # Replace whitespaces with single space
        classes = classes.split(',')

        for c in classes:
            c = c.strip()

            # Check it looks reasonable
            if not search(r'^\w*\ [0-9]*x[0-9]*$', c):
                report_error(1,'Unable to parse image_class: ' + c)

            c_s = c.split(' ')
            dims = c_s[1].split('x')

            c_name = c_s[0].strip()
            self.image_classes[c_name] = {
                'name': c_name,
                'width': int(dims[0].strip()),
                'height': int(dims[1].strip()),
            }


    def ensure_bool(self, setting_name, data):
        if data == "True":
            return True
        elif data == "False":
            return False

        report_error(1,'Setting "' + setting_name + '" must be either "True" or "False", value "' + data + '" is unrecognized')


    def prepare_single_page(self, path):
        ''' Prepare single page and its parents for site generation '''

        if path.startswith(self.site_dir + '/'):
            path = remove_prefix(path, self.site_dir + '/')

        full_path = self.site_dir
        old_parent = False

        for path_part in path.split('/'):
            full_path += '/' + path_part
            if isdir(full_path):
                full_path += '/' + DIRDEFAULTFILE

                p = virtualpage()

                p.site_dir = self.site_dir
                v_path = full_path + self.default_extension
                p.parent = old_parent
                p.title = p.set_title_from_path(v_path)
                p.menu_title = p.title
                p.set_paths(v_path, self.site_dir, self.absolute_urls, self.environment, self.base_url, self.strip_extensions)


                if self.default_templates['directories']:
                    p.headers['template'] = self.default_templates['directories']
                full_path = remove_suffix(full_path, '/' + DIRDEFAULTFILE)
            else:
                p = page()
                p.load(
                    full_path,
                    self.site_dir,
                    parent=old_parent,
                    base_url=self.base_url,
                    default_extension=self.default_extension,
                    environment=self.environment,
                    absolute_urls=self.absolute_urls,
                    default_markup=self.default_markup,
                    authors=self.authors,
                    strip_extensions = self.strip_extensions
                )

            self.pages.append(p)
            self.page_list.append(p)

            old_parent=p


    def prepare_all_pages(self):
        ''' Prepare site for generation '''

        content_path=join(self.site_dir, CONTENTDIR)

        # Try to load home page, ok if not there
        try:
            # Get home page, append it as first item
            home_page_path = self.get_dir_default_file(content_path)
            home_page = self.get_directory_page(home_page_path, False)

            if self.publish_page(home_page):
                self.pages.append(home_page)
                self.page_list.append(home_page)
            else:
                report_error(1, "Home page not publishable because publish date not reached yet '%s': %s" % (home_page.headers['publish'], relative_path(home_page.source_path)))
        except Exception as e:
            raise Exception("Unable to find home page '%s': %s" % (DIRDEFAULTFILE, e))

        # Load pages
        try:
            self.load_pages(content_path, self.pages, home_page, self.default_extension)
        except Exception as e:
            raise Exception('Unable to load content: %s' % e)

        self.set_tag_items(self.base_url, self.pages)

        if self.tags:
            self.load_tag_pages(home_page)

        if self.authors:
            self.load_author_pages(home_page)

        self.check_pages(self.pages)

        self.set_link_sequence(self.pages)
        self.set_next_previous_links()


    def generate_page_indexes(self, pages):
        ''' Index all pages with header Search index exclude: True '''
        for p in pages:
            if p.headers['search index exclude'] == False:
                if p.headers['description'] != None:
                    description=p.headers['description']
                else:
                    description=''

                self.search_index.index_file(p.target_path, p.url_path, p.title, get_first_words(description, 150))
            if p.children:
                self.generate_page_indexes(p.children)


    def generate_search_index(self):
        ''' For all indexable files get their terms and create json index file for site search use (requires javascript '''
        self.generate_page_indexes(self.pages)
        write_file(join(self.target_dir, SEARCHINDEXFILE), self.search_index.build_json_index())


    def load_author_pages(self, parent_page):
        ''' If authors.conf then create an overview page, and a page for each author '''

        # Overview page
        o = virtualpage()

        title = self.tag_title
        d = self.tag_dir
        item_list = self.tags

        if self.default_templates['authors']:
            o.headers['template'] = self.default_templates['authors']

        o.headers['menu exclude'] = True
        o.headers['link chain exclude'] = True
        o.parent = parent_page
        o.title = self.authors_title
        o.menu_title = self.authors_title

        v_path = self.site_dir + '/' + CONTENTDIR + '/' + self.authors_dir + '/' + DIRDEFAULTFILE + self.default_extension
        o.set_paths(v_path, self.site_dir, self.absolute_urls, self.environment, self.base_url, self.strip_extensions)
        self.page_list.append(o)

        # Create page (l) for each author
        for a, a_settings in self.authors.items():
            if a != 'root':

                l = virtualpage()
                l.headers['sitemap exclude'] = True
                l.headers['menu exclude'] = True
                l.headers['link chain exclude'] = True
                l.headers['author'] = a
                l.title = a_settings['name']
                l.menu_title = l.title
                v_path = self.site_dir + '/' + CONTENTDIR + '/' + self.authors_dir + '/' + a + self.default_extension
                l.set_paths(v_path, self.site_dir, self.absolute_urls, self.environment, self.base_url, self.strip_extensions)
                l.parent = o

                self.page_list.append(l)

                # Add url to authors, overwrites setting from conf file
                self.authors[a]['author_page'] = l.url_path

                if self.default_templates['author']:
                    l.headers['template'] = self.default_templates['author']

                o.children.append(l)

        # Create author overview content
        for p in o.children:
            o.content += '* [%s](%s)%s' % (p.menu_title, p.url_path, NEWLINE)

        self.pages.append(o)


    def load_tag_pages(self, parent_page):
        ''' For each tag, create page objects and replace their content with list of tagged pages. and index page, which is list of tags '''

        # Create top level overview page (o)
        o = virtualpage()

        title = self.tag_title
        d = self.tag_dir

        if self.default_templates['tags']:
            o.headers['template'] = self.default_templates['tags']

        o.headers['sitemap exclude'] = True
        o.headers['menu exclude'] = True
        o.headers['link chain exclude'] = True
        o.parent = parent_page
        o.title = title
        o.menu_title = title
        v_path = self.site_dir + '/' + CONTENTDIR + '/' + d + '/' + DIRDEFAULTFILE + self.default_extension
        o.set_paths(v_path, self.site_dir, self.absolute_urls, self.environment, self.base_url, self.strip_extensions)
        self.page_list.append(o)


        # Create each list page (l) for tags
        for tag_name, tags  in self.tags.items():
            l = virtualpage()
            l.headers['sitemap exclude'] = True
            l.headers['menu exclude'] = True
            l.headers['link chain exclude'] = True
            l.title = tag_name
            l.menu_title = tag_name
            v_path = self.site_dir + '/' + CONTENTDIR + '/' + d + '/' + tag_name + self.default_extension
            l.set_paths(v_path, self.site_dir, self.absolute_urls, self.environment, self.base_url, self.strip_extensions)
            l.parent = o
            self.page_list.append(l)

            if self.default_templates['tag']:
                l.headers['template'] = self.default_templates['tag']
            l.tag_pages = tags['pages']

            l.headers['tag page count'] = len(tags['pages'])

            for page in tags['pages']:
                l.content += '* %s [%s](%s)%s' % (page.headers['publish'], page.menu_title, page.url_path, NEWLINE)

            o.children.append(l)

        # Create tag overview content now so get right urls etc
        for p in o.children:
            o.content += '* `%s <%s>`_%s' % (p.menu_title, p.url_path, NEWLINE)

        self.pages.append(o)


    def set_tag_items(self, url_prefix, pages):
        ''' Get all tags that are defined in page headers '''

        for p in pages:

            # Tags
            if 'tags' in p.headers.keys():
                for t in p.headers['tags']:
                    # If not existing, create new list
                    if not t in self.tags.keys():
                        self.tags[t] = {
                            'name': t,
                            'url': url_prefix + '/' + self.tag_dir + '/' + urlify(t) + self.default_extension,
                            'pages': [],
                            'page_count': 0
                        }

                    self.tags[t]['pages'].append(p)
                    self.tags[t]['page_count'] += 1

            if p.children or p.url_path == '/':
                self.set_tag_items(url_prefix, p.children)


    def set_next_previous_links(self):
        ''' Add previous and next links to pages according to thier link sequence '''

        previous_page = False

        for i, p in enumerate(self.link_sequence):

            try:
                next_page = self.link_sequence[i+1]
            except:
                next_page = False

            p.previous_page = previous_page
            p.next_page = next_page

            previous_page = p


    def set_link_sequence(self, pages):
        ''' Add all pages to link sequence (for use with previous/next links) '''
        for p in pages:
            if p.headers['link chain exclude'] == False:
                self.link_sequence.append(p)

            if p.children:
                self.set_link_sequence(p.children)


    def get_directory_page(self, path, parent):
        ''' Return page object set according to configuration settings '''

        if self.url_include_index != True:
            url_include_index=False
        else:
            url_include_index=True

        p=page()

        p.load(
            path,
            self.site_dir,
            parent=parent,
            base_url=self.base_url,
            url_include_index=url_include_index,
            default_extension=self.default_extension,
            environment=self.environment,
            absolute_urls=self.absolute_urls,
            default_markup=self.default_markup,
            authors=self.authors,
            strip_extensions = self.strip_extensions
        )

        return p


    def generate_pages_html(self, pages):
        ''' Recursively iterate over and generate html for pages '''

        for p in pages:
            # Set environment variable for hooks
            p.environment={
                'PAGEGEN_SITE_DIR': self.site_dir,
                'PAGEGEN_SOURCE_DIR': self.site_dir + '/' + CONTENTDIR,
                'PAGEGEN_TARGET_DIR': self.target_dir,
                'PAGEGEN_HOOK_DIR': self.site_dir + '/' + HOOKDIR,
                'PAGEGEN_BASE_URL': self.base_url,
                'PAGEGEN_PAGE_TITLE': p.title,
                'PAGEGEN_PAGE_URL': p.url_path,
                'PAGEGEN_PAGE_SOURCE_PATH': p.source_path,
                'PAGEGEN_PAGE_TARGET_PATH': p.target_path,
                'PAGEGEN_ENVIRONMENT': self.environment,
                'PAGEGEN_HOOK': 'pre_generate_page'
            }

            for header_name, header_value in p.headers.items():
                header_value = str(header_value)
                env_name = 'PAGEGEN_PAGE_HEADER_' + header_name.upper().replace(' ', '_')
                p.environment[env_name] = header_value

            # Custom headers are always string values
            for custom_header_name, custom_header_value in p.custom_headers.items():
                env_name = 'PAGEGEN_PAGE_CUSTOM_HEADER_' + custom_header_name.upper().replace(' ', '_')
                p.environment[env_name] = custom_header_value

            # Run hook
            hook = join(self.site_dir,HOOKDIR,'pre_generate_page')
            if isfile(hook) and access(hook, X_OK):
                exec_script(hook, p.environment)

            if p.headers['generate html'] == True:

                if p.headers['disable shortcodes'] == False:
                    # Run any shortcodes in content
                    try:
                        self.shortcodes.run(self, p)
                    except Exception as e:
                        report_error(1, 'Failed to run shortcodes: ' + p.source_path + ': ' + str(e))

                # If defined use rst, else default to markdown
                if p.markup == 'rst':
                    try:
                        p.html = rst_to_html(p.content)
                    except:
                        raise(Exception(p.source_path + ': Content reStructruedText conversion failed'))
                else:
                    try:
                        p.html = markdown_to_html(p.content)
                    except RuntimeError as e:
                        report_error(1, p.source_path + ': ' + str(e))
                    except Exception as e:
                        raise(Exception(p.source_path + ': Content Markdown conversion failed: ' + str(e)))

                # Needs to happen to html content, i.e. after markup conversion
                if p.headers['number headings']:
                    p.number_headings()

                # Needs to happen to after a possible numbering, to ensure titles are correct
                if p.headers['toc']:
                    p.add_toc()

                self.generate_crumb_trail(p, p)
            else:
                if p.headers['disable shortcodes'] == False:
                    # Run any shortcodes in HTML content
                    try:
                        self.shortcodes.run(self, p)
                    except Exception as e:
                        report_error(1, 'Failed to run shortcodes: ' + p.source_path + ': ' + str(e))

                p.html = p.content 

            # If argument --serve(serve_mode) then add javascript script to each page that reloads page if site is regenerated
            if self.serve_mode:
                p.html += '<script>' + self.serve_mode_js_script + '</script>'

            if p.children:
                self.generate_pages_html(p.children)


    def apply_templates(self, pages):
        '''
        Recursively iterate over pages and apply Mako templates
        '''

        for p in pages:
            if p.headers['generate html'] == True:

                # Setup context for Mako template
                context = {
                    'page': p,
                    'site': self,
                    'year': date.today().strftime('%Y'),
                    'month': date.today().strftime('%m'),
                    'day': date.today().strftime('%d'),
                }

                p.html = render_template(self.theme_template_dir, p, context)

            if p.children:
                self.apply_templates(p.children)


    def check_pages(self, pages):
        ''' Check all files are uniquely named (because of xxx_ prefix potentially can have conflicts) '''
        page_urls={}
        page_target_paths={}

        for p in pages:

            # Check title length if range set
            if self.title_warn_min > 0 and self.title_warn_max > 0:
                if self.title_warn_min > len(p.title):
                    report_warning("Title too short '%s' (%s), minimum length %s characters: '%s'" % (p.title, len(p.title), self.title_warn_min, relative_path(p.source_path)))
                elif self.title_warn_max < len(p.title):
                    report_warning("Title too long '%s' (%s), maximum length %s characters: '%s'" % (p.title, len(p.title), self.title_warn_max, relative_path(p.source_path)))

            # Check description length if range set
            if self.description_warn_min > 0 and self.description_warn_max > 0:
                if  p.headers['description'] is None:
                    report_warning("Missing description '%s'" % relative_path(p.source_path))
                elif self.description_warn_min > len(p.headers['description']):
                    report_warning("Description too short '%s' (%s), minimum lenght %s characters: '%s'" % (p.headers['description'], len(p.headers['description']), self.description_warn_min, relative_path(p.source_path)))
                elif self.description_warn_max < len(p.headers['description']):
                    report_warning("Description too long '%s' (%s), maximum lenght %s characters: '%s'" % (p.headers['description'], len(p.headers['description']), self.description_warn_max, relative_path(p.source_path)))

            if p.target_path in page_target_paths:
                if page_target_paths[p.target_path] == '':
                    report_error(1,"Target path '%s' for page '%s' is already used by another virtual page, perhaps tags are used with different capitalization" % (relative_path(p.target_path), p))
                else:
                    report_error(1,"Target path '%s' for page '%s' is already set for '%s'" % (relative_path(p.target_path), p, relative_path(page_target_paths[p.target_path])))
            # TODO Better checking than ends with
            elif ((p.target_path.endswith(SITEMAPFILE) or p.target_path.endswith(SITEMAPTXTFILE)) and self.exclude_sitemap == False) or p.target_path==join(self.site_dir, ASSETDIR):
                report_error(1,"Page '%s' illegal name, cannot be either '%s' or '%s'" % (relative_path(p.source_path), SITEMAPFILE, SITEMAPTXTFILE))
            elif p.target_path.endswith(RSSFEEDFILE) and self.include_rss:
                report_error(1,"Page '%s' illegal name '%s'" % (relative_path(p.source_path), RSSFEEDFILE))
            elif p.target_path.endswith(SEARCHINDEXFILE) and self.include_search:
                report_error(1,"Page '%s' illegal name '%s'" % (relative_path(p.source_path), SEARCHINDEXFILE))

            else:
                page_target_paths[p.target_path] = p.source_path

            if p.url_path in page_urls:
                report_error(1,"URL '%s' for page '%s' already set for '%s'" % (p.url_path, p.source_path, page_urls[p.url_path]))
            else:
                page_urls[p.url_path]=p.source_path

            if p.children:
                self.check_pages(p.children)


    def get_dir_default_file(self, path):
        ''' Return default file starting with DIRDEFAUTFILE '''
        for f in listdir(path):
            if f.startswith(DIRDEFAULTFILE):
                return join(path, f)
        return False


    def load_pages(self, dir_path, siblings, parent, default_extension):
        ''' Recursively load pages from content directory '''
        file_list = sorted(listdir(dir_path))

        for f in file_list:
            f_path=join(dir_path, f)

            # Just skip content/assets file
            if f_path == self.asset_dir:
                continue

            # If dir then load default index page, if none found then create virtual page
            if isdir(f_path):

                dir_page=self.get_dir_default_file(f_path)

                # Index file exists on disk
                if dir_page:

                    p = self.get_directory_page(dir_page, parent)

                # No index file defined, create virutal one
                else:
                    p = virtualpage()
                    p.site_dir = self.site_dir
                    v_path = f_path + '/' + DIRDEFAULTFILE + self.default_extension
                    p.parent = parent
                    p.title = p.set_title_from_path(v_path)
                    p.menu_title = p.title
                    p.set_paths(v_path, self.site_dir, self.absolute_urls, self.environment, self.base_url, self.strip_extensions)

                    if self.default_templates['directories']:
                        p.headers['template'] = self.default_templates['directories']

                if self.publish_page(p):
                    siblings.append(p)
                    self.page_list.append(p)

                    try:
                        self.load_pages(f_path, p.children, p, self.default_extension)
                    except Exception as e:
                        raise Exception('Unable to load pages for %s: %s' % (f, e))

            elif is_default_file(f):
                pass
            elif isfile(f_path):
                p = page()
                p.load(
                    f_path,
                    self.site_dir,
                    parent=parent,
                    base_url=self.base_url,
                    default_extension=self.default_extension,
                    environment=self.environment,
                    absolute_urls=self.absolute_urls,
                    default_markup=self.default_markup,
                    authors=self.authors,
                    strip_extensions = self.strip_extensions
                )

                if self.publish_page(p):
                    siblings.append(p)
                    self.page_list.append(p)

            else:
                raise Exception("Unknown object '%s'" % f_path)


    def publish_page(self, page):
        ''' If page publish header date is today or in past return true. Pagegen dates are always strings, so need to convert '''

        try:
            if page.headers['publish'].lower() == 'false':
                publish = False
            else:
                page_publish_date = datetime.strptime(page.headers['publish'], DATEFORMAT)
                publish = page_publish_date < datetime.now()
        except Exception as e:
            report_error(1, "Unable to parse date '%s': %s: %s" % (page.headers['publish'], relative_path(page.source_path), e))

        if not publish:
            report_notice("Not publishing '%s' (or any child pages), header Publish is '%s': %s" % (page.title, page.headers['publish'], relative_path(page.source_path)))

        return publish


    def move_to_target(self):
        ''' Create generated site in target dir '''

        # Delete target dir if exists
        if exists(self.target_dir):
            try:
                for f in listdir(self.target_dir):
                    item=join(self.target_dir, f)
                    if islink(item):
                        unlink(item)
                    elif isdir(item):
                        rmtree(item)
                    else:
                        remove(item)

            except Exception as e:
                raise Exception(e)
        else:
            try:
                makedirs(self.target_dir)
            except Exception as e:
                raise Exception(e)

        # Write pages to disk
        self.save_pages(self.pages)

        # Copy assets
        target_assets_dir = self.target_dir + '/' + ASSETDIR
        if exists(target_assets_dir):
            report_error(1, target_assets_dir + ' already exists, aborting')
        if exists(self.asset_dir):
                copytree(self.asset_dir, target_assets_dir)

        # Copy theme assets
        target_theme_asset_dir = target_assets_dir + '/theme'
        if exists(target_theme_asset_dir):
            report_error(1, target_theme_asset_dir + ' already exists, aborting')
        else:
            copytree(self.theme_asset_dir, target_theme_asset_dir)

        # Create sitemap
        if self.exclude_sitemap == False:
            write_file(self.target_dir + '/' + SITEMAPFILE, self.sitemap)
            write_file(self.target_dir + '/' + SITEMAPTXTFILE, self.sitemaptxt)

        # Create rss feed
        if self.include_rss:
            write_file(join(self.target_dir, RSSFEEDFILE), self.rss)

        if self.include_search:
            self.generate_search_index()

        if self.minify_javascript:
            self.minify_javascript_in_directory(target_assets_dir)

        if self.minify_css:
            self.minify_css_in_directory(target_assets_dir)


    def minify_javascript_in_directory(self, directory):
        from jsmin import jsmin
        files = self.find_files_by_extension(directory, 'js')
        for file_name in files:
            with open(file_name, 'r+') as f:
                text = jsmin(f.read())
                f.seek(0)
                f.write(text)
                f.truncate()


    def minify_css_in_directory(self, directory):
        from rcssmin import cssmin
        files = self.find_files_by_extension(directory, 'css')
        for file_name in files:
            with open(file_name, 'r+') as f:
                text = cssmin(f.read())
                f.seek(0)
                f.write(text)
                f.truncate()


    def find_files_by_extension(self, directory, extension):
        pathname = directory + "/**/*." + extension
        files = glob(pathname, recursive=True)
        return files


    def save_pages(self, pages):
        ''' Create files and directories in target dir '''

        for p in pages:

            if self.minify_html and p.headers['exclude html minify'] == False:
                from htmlmin import minify
                p.html = minify(p.html)

            if p.parent and is_default_file(p.target_path):
                dir_path=p.target_path.rpartition(sep)[0]
                makedirs(dir_path)
                write_file(p.target_path, p.html)
                if p.children:
                    self.save_pages(p.children)
            else:
                write_file(p.target_path, p.html)

            p.environment['PAGEGEN_HOOK']='post_generate_page'

            hook = join(self.site_dir,HOOKDIR,'post_generate_page')
            if isfile(hook) and access(hook, X_OK):
                exec_script(hook, p.environment)


    def generate_crumb_trail(self, crumb_trail_page, page):
        # page.parent.parent checks for home page, don't want that in trail
        if page.parent:
            crumb_trail_page.crumb_trail.insert(0, page.parent)
            self.generate_crumb_trail(crumb_trail_page, page.parent)
        # Add current page
        if page==crumb_trail_page:
            crumb_trail_page.crumb_trail.append(page)


    def sitemap_url(self, page):
        url='<url><loc>%s</loc>' % (page.absolute_url.rstrip('/'))

        # Add lastmod if set
        if page.headers['sitemap lastmod']:
            try:
                date=datetime.strptime(page.headers['sitemap lastmod'], '%Y-%m-%d')
                url+='<lastmod>%s</lastmod>' % date.strftime('%Y-%m-%d')
            except:
                report_warning("Page header sitemap lastmod '%s' does not seem to be valid date: %s" % (page.headers['sitemap lastmod'], relative_path(page.source_path)))


        # Add change freq if set
        if page.headers['sitemap changefreq'] != None:
            valid_changefreq='always hourly daily weekly monthly yearly never'
            if page.headers['sitemap changefreq'] in valid_changefreq:
                url+='<changefreq>%s</changefreq>' % page.headers['sitemap changefreq']
            else:
                report_warning("Page header sitemap changefreq '%s' does not seem to be valid (%s): %s" % (page.headers['sitemap changefreq'], valid_changefreq, relative_path(page.source_path)))

        # Add priority
        if page.headers['sitemap priority'] != None:
            if search(r'^0.[0-9]*$', page.headers['sitemap priority']) or search(r'^1.0*$', page.headers['sitemap priority']):
                url+='<priority>%s</priority>' % page.headers['sitemap priority']
            else:
                report_warning("Page header sitemap priority '%s' does not seem to be valid, must be valur between 0.0 and 1.0 : %s" % (page.headers['sitemap priority'], relative_path(page.source_path)))

        url+='</url>'

        return url

    def generate_sitemap_urls(self, pages):

        ''' Create sitmap.txt '''
        for p in pages:
            if p.headers['sitemap exclude'] == False:
                if p.children or p.url_path == '/':
                    self.sitemap += self.sitemap_url(p)

                    self.sitemaptxt += p.absolute_url.rstrip('/') + '\n'

                    self.generate_sitemap_urls(p.children)
                else:
                    self.sitemap += self.sitemap_url(p)
                    self.sitemaptxt += p.absolute_url + '\n'

            else:
                self.generate_sitemap_urls(p.children)


    def generate_sitemap(self, pages):

        self.sitemap='<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">'

        self.generate_sitemap_urls(pages)

        self.sitemap += '</urlset>'


    def generate_rss(self):
        ''' Create rss feed '''

        self.create_rss_sequence(self.pages)

        # Sort rss pages by header publish value
        self.rss_sequence=sorted(self.rss_sequence, key=lambda k: k.headers['publish'], reverse=True) 

        self.rss='<?xml version="1.0" encoding="UTF-8" ?>'+NEWLINE
        self.rss+='<rss version="2.0">'+NEWLINE
        self.rss+='<channel>'+NEWLINE
        self.rss+='<title>'+self.rss_title+'</title>'+NEWLINE
        self.rss+='<link>'+self.base_url+'/'+RSSFEEDFILE+'</link>'+NEWLINE
        self.rss+='<description>'+self.rss_description+'</description>'+NEWLINE
        self.rss+='<generator>Pagegen - pagegen.phnd.net</generator>'+NEWLINE

        count=1
        for p in self.rss_sequence:

            try:
                page_publish_date=datetime.strptime(p.headers['publish'], DATEFORMAT)
            except Exception as e:
                report_error(1, "Unable to parse date '%s': %s: %s" % (p.headers['publish'], relative_path(p.source_path), e))

            self.rss+='<item>'+NEWLINE
            self.rss+='<title>'+p.title+'</title>'+NEWLINE
            self.rss+='<link>'+self.base_url+p.url_path+'</link>'+NEWLINE
            self.rss+='<pubDate>'+page_publish_date.strftime('%a, %d %b %Y')+' 00:00:00 +0000</pubDate>'+NEWLINE
            if p.headers['description'] != None:
                self.rss+='<description>'+p.headers['description']+'</description>'+NEWLINE
            self.rss+='</item>'+NEWLINE

            count+=1

            if count > self.max_rss_items:
                break

        self.rss+='</channel>'+NEWLINE
        self.rss+='</rss>'+NEWLINE


    def create_rss_sequence(self, pages):
        ''' Get all pages with header rss include True '''
        for p in pages:
            if p.headers['rss include']:
                self.rss_sequence.append(p)
                if p.children or p.url_path == '/':
                    self.create_rss_sequence(p.children)


    def __repr__(self):
        r = '{\n'

        for attribute in sorted(self.__dict__):
            value = self.__dict__[attribute]

            if attribute == 'rss':
                r += "\t'rss': <rss xml>,\n"

            elif attribute == 'sitemap':
                r += "\t'sitemap': <sitemap xml>,\n"

            elif attribute == 'sitemaptxt':
                r += "\t'sitemaptxt': <sitemap txt>,\n"

            elif isinstance(value, str) or isinstance(value, bool) or isinstance(value, int):
                r += "\t'" + attribute + "': " + str(value) + ",\n"
            elif isinstance(value, list):
                if len(value) > 0:
                    r += "\t'" + attribute + "': [\n"
                    for i in value:
                        r += "\t\t" + str(i) + ",\n"
                    r = r.rstrip(",\n")
                    r += "\n\t],\n"
                else:
                    r += "\t'" + attribute + "': [],\n"
            elif isinstance(value, dict):
                if len(value.keys()):
                    r += "\t'" + attribute + "': {\n"
                    for k, v in value.items():
                        r += "\t\t'" + k + "': " + str(v) + ",\n"
                    r = r.rstrip("\n,")
                    r += "\n\t},\n"
                else:
                    r += "\t'" + attribute + "': {},\n"

        r = r.rstrip("\n,")
        r += "\n}"

        return r


    def build_backlinks_index(self):
        '''
        Creates site.backlinks wich is a reverse lookup dict to find any URL's
        that link to a given URL
        Only links on the site are indexed, not external links
        '''

        if self.index_backlinks:
            self.backlinks = {}
            tag_url = '/' + self.tag_dir + '/'

            for p in self.page_list:
                # Skip links from tags
                if p.url_path.startswith(tag_url):
                    continue

                p.get_links()

                if len(p.links) > 0:
                    for l in p.links:
                        # Strip base url if set
                        if l['url'].startswith(self.base_url):
                            l['url'].lstrip(self.base_url)

                        # Only index local links, that are not tags
                        if not '://' in l['url']:
                            backlink = {
                                'page_title': p.title,
                                'context': l['title'], # Source context
                                'url': p.url_path # Source url
                            }

                            try:
                                self.backlinks[l['url']].append(backlink)
                            except:
                                self.backlinks[l['url']] = []
                                self.backlinks[l['url']].append(backlink)


    def set_excerpts(self):
        for p in self.page_list:
            p.set_excerpt()

            if p.excerpt:
                if p.markup == 'rst':
                    try:
                        p.excerpt = rst_to_html(p.excerpt)
                    except:
                        raise(Exception(p.source_path + ': Excerpt reStructruedText conversion failed'))
                else:
                    try:
                        p.excerpt = markdown_to_html(p.excerpt)
                    except RuntimeError as e:
                        report_error(1, p.source_path + ': ' + str(e))
                    except Exception as e:
                        raise(Exception(p.source_path + ': Excerpt Markdown conversion failed'))
