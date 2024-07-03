from pagegen.virtualpage import virtualpage
from os import sep, access, X_OK, environ
from os.path import splitext, join
from re import sub, search
from pagegen.utility import load_file, relative_path
from pagegen.utility_no_deps import is_default_file, report_warning, report_error, setup_environment_variables, urlify
from pagegen.constants import DIRDEFAULTFILE, CONTENTDIR, NEWLINE, HEADERPROFILEDIR, TARGETDIR, AUTHORSCONF
from subprocess import check_output
from bs4 import BeautifulSoup


class page(virtualpage):
    """ Bread and butter of pagegen """

    def __init__(self):
        virtualpage.__init__(self)

    def load(self, path, site_dir, parent=False, base_url='', url_include_index=True, default_extension='', environment='', absolute_urls=False, default_markup='md', authors=None, strip_extensions=None):

        self.source_path=path
        self.site_dir=site_dir
        self.parent=parent
        self.base_url=base_url
        self.url_include_index=url_include_index
        self.default_extension=default_extension
        self.markup = default_markup
        self.environment = environment

        # If file is executable then the contents from it's stdout, else just read the file
        if access(self.source_path, X_OK):
            page_environment={
                'PAGEGEN_SITE_DIR': self.site_dir,
                'PAGEGEN_SOURCE_DIR': self.source_path,
                'PAGEGEN_TARGET_DIR': self.site_dir + '/' + TARGETDIR + '/' + self.environment + '/FIXME', # TODO: This needs to be fixed
                'PAGEGEN_ENVIRONMENT': self.environment,
                'PAGEGEN_BASE_URL': self.base_url,
                'PAGEGEN_DEFAULT_EXTENSION': self.default_extension
            }

            setup_environment_variables(page_environment)

            try:
                content = check_output(self.source_path, text=True)

            except Exception as e:
                report_error(1,"File '%s' execution failed: %s" % (self.source_path, e))
        else:
            content = load_file(self.source_path)

        self.load_page_content(self.source_path, content, self.site_dir, self.default_extension, absolute_urls, authors, strip_extensions)


    def new_toc_id(self, title):
        ''' Creates a new unique toc id from title '''

        new_id = urlify(title)

        if new_id not in self.toc_ids:
            self.toc_ids.append(new_id)
            return new_id
        else:
            # If id already existed, keep adding _x until it is unique
            tmp_new_id = new_id
            counter = 0
            while tmp_new_id in self.toc_ids:
                counter += 1
                tmp_new_id = new_id + '_' + str(counter)

            self.toc_ids.append(tmp_new_id)
            return tmp_new_id


    def add_toc(self):
        ''' Add toc and anchor links to titles in page content '''

        soup = BeautifulSoup(self.html, 'html.parser')
        self.toc_ids = [] # Use to ensuer unique ids
        self.toc = [] # For use in templates

        h_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

        for tag in soup.find_all(h_tags):

            new_id = self.new_toc_id(tag.string)

            new_a = soup.new_tag('a')
            new_a['id'] = new_id 

            self.toc.append({
                'title': tag.string,
                'level': int(tag.name[-1]),
                'id': new_id
            })

            tag.insert_before(new_a)

        self.html = str(soup)


    def number_headings(self):
        ''' Add mumbering to h2-5 tags, 1, 1.1, 1.2 etc '''

        soup = BeautifulSoup(self.html, 'html.parser')

        h_tags = ['h1', 'h2', 'h3', 'h4', 'h5']
        h_c = { # Counters, h1 and h6 are not numbered
            'h2': 0,
            'h3': 0,
            'h4': 0,
            'h5': 0,
        }

        for tag in soup.find_all(h_tags):

            if tag.name == 'h1':

                h_c['h2'] = 0
                h_c['h3'] = 0
                h_c['h4'] = 0
                h_c['h5'] = 0

            if tag.name == 'h2':
                h_c['h2'] += 1

                tag.string = str(h_c['h2']) + ' ' + tag.text

                h_c['h3'] = 0
                h_c['h4'] = 0
                h_c['h5'] = 0

            if tag.name == 'h3':
                h_c['h3'] += 1

                tag.string = str(h_c['h2']) + '.' + str(h_c['h3']) + ' ' + tag.text

                h_c['h4'] = 0
                h_c['h5'] = 0

            if tag.name == 'h4':
                h_c['h4'] += 1

                tag.string = str(h_c['h2']) + '.' + str(h_c['h3']) + '.' + str(h_c['h4']) + ' ' + tag.text

                h_c['h5'] = 0

            if tag.name == 'h5':
                h_c['h5'] += 1

                tag.string = str(h_c['h2']) + '.' + str(h_c['h3']) + '.' + str(h_c['h4']) + '.' + str(h_c['h5']) + ' ' + tag.text

        self.html = str(soup)


    def set_header(self, line):
        ''' Try to set header value, return false if fail '''

        if ':' in line:
            potential_header = line.partition(':')
            potential_name=potential_header[0].lower().strip()
            potential_value=potential_header[2]

            if potential_name == 'tags':
                tags=potential_value.split(',')
                for t in tags:
                    self.headers['tags'].append(t.strip())
                return self.headers['tags']

            elif potential_name in self.headers:
                self.headers[potential_name]=potential_value.strip()
                return self.headers[potential_name]

            else:
                self.custom_headers[potential_name] = potential_value.strip()
                return self.custom_headers[potential_name]

        else:
            return False


    def is_header(self, line):
        if ':' in line:
            potential_header=line.partition(':')
            potential_name=potential_header[0].lower().strip()
            potential_value=potential_header[2]

            if isinstance(potential_name, str) and isinstance(potential_value, str):
                return True
            else:
                report_warning("Unknown header in '%s': %s" % (self.source_path, line))
                return False
        else:
            return False


    def load_page_content(self, path, content, site_dir, default_extension, absolute_urls, authors, strip_extensions):
        '''
        Parse source and save headers and content attributes
        Format:
            <header>: <value>    <- Optional
                                <-Blanke line, if headers
            <content>

        First line must either be header or content
        '''

        in_header=None
        for line in content.split(NEWLINE):
            # If file starts with lines that match possible headers, then grab values, after first blank line rest is content.

            if in_header is None and search(r'^[a-zA-Z]+', line) is None:
                in_header=False

            if in_header is None and self.is_header(line):
                self.raw_headers.append(line)
                in_header=True
                continue

            if line == '' and in_header:
                in_header=False
                continue

            # If blank line definitely not in header
            if line == '':
                in_header=False

            # First line was a header
            if in_header:
                # Set header
                if self.is_header(line):
                    self.raw_headers.append(line)
                    continue
                # If blank line next lines are content
                else:
                    in_header=False
                    continue
            else:
                self.content+=line+NEWLINE

        # Load headers from page
        for header in self.raw_headers:
            self.set_header(header)

        # Strip last new line
        self.content=self.content.rstrip(NEWLINE)

        # Split off extension
        path_part, file_extension=splitext(path)

        if self.headers['title'] != None:
            self.title=self.headers['title']
        else:
            self.title = self.set_title_from_path(path)

        if self.headers['menu title'] != None:
            self.menu_title=self.headers['menu title']
        else:
            self.menu_title=self.title

        if self.headers['markup'] != None:
            self.markup = self.headers['markup']

        if self.headers['authors'] != None:
            self.load_page_authors(self.headers['authors'], authors)

        if file_extension:
            self.extension = file_extension
            self.set_paths(path, site_dir, absolute_urls, self.environment, self.base_url, strip_extensions)
        else:
            if self.headers['preserve file name'] == False:
                self.extension = default_extension

            self.set_paths(path+self.extension, site_dir, absolute_urls, self.environment, self.base_url, strip_extensions)


    def load_page_authors(self, author_list, authors):
        ''' Add authors to page '''

        if authors != None:
            # If CSV then split, else if just one assign
            if ',' in author_list:
                author_list = author_list.split(',')
            else:
                author_list = [ author_list ]

            # Tidy any whitespace
            for a in author_list:
                a = a.strip()

                # Make reference to site.authors (authors argument) if match
                if a in authors.keys():
                    self.authors.append(authors[a])

                    if not 'pages' in authors[a].keys():
                        authors[a]['pages'] = []

                    authors[a]['pages'].append(self)
                else:
                    report_error(1, 'Author "' + a + '" defined in ' + self.source_path + ' not defined in ' + AUTHORSCONF)


