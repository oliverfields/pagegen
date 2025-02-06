from pagegen.Common import Common
from os import linesep
from re import search
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)


class Page(Common):
    '''
    Generate page

    Key concepts:
    Page consists of optional headers (key: value) if first line is not header then it is considered content
    '''

    def __init__(self):
        self.headers = {}


    def load(self, target_path, site, source_path=False, raw_string=False):
        '''
        Create page from source file or raw string
        '''

        self.target_path = target_path

        self.relative_url = self.target_path[len(site.build_dir):].rstrip('/')
        self.absolute_url = f'{site.base_url.rstrip("/")}{self.relative_url}'

        if raw_string:
            self.raw = raw_string
        elif source_path:
            self.source_path = source_path
            self.raw = self.read_file(self.source_path)
        else:
            logger.error(f'Must load page with either a string or source path: {self.relative_url}')
            raise

        self.parse()


    def load_page_string(self, target_path, raw_string, site):
        '''
        Create page from passed raw string
        '''

        self.target_path = target_path

        self.set_urls(site)

        self.raw = raw_string


    def write(self):
        try:
            self.write_file(self.target_path, self.out)
        except AttributeError:
            self.write_file(self.target_path, self.body)


    def __str__(self):
        try:
            return f'<page: {self.relative_url}: {self.source_path}>'
        except AttributeError:
            return f'<page: {self.relative_url}: <string>>'


    def __repr__(self):
        r = '{\n'

        for attribute in sorted(self.__dict__):
            value = self.__dict__[attribute]
            if isinstance(value, str) or isinstance(value, bool) or isinstance(value, int):
                r += "\t'" + attribute + "': " + str(value) + ",\n"
            elif isinstance(value, list):
                if len(value) > 0:
                    r += "\t'" + attribute + "': [\n"
                    for i in value:
                        r += "\t\t" + str(i) + ",\n"
                    r = r.rstrip(",\n")
                    r += "\n\t]\n"
                else:
                    r += "\t'" + attribute + "': []\n"
            elif isinstance(value, dict):
                if len(value.keys()):
                    r += "\t'" + attribute + "': {\n"
                    for k, v in value.items():
                        r += "\t\t'" + k + "': " + str(v) + ",\n"
                    r = r.rstrip("\n,")
                    r += "\n\t},\n"
                else:
                    r += "\t'" + attribute + "': {}\n"

        r = r.rstrip("\n,")
        r += "\n}"

        return r


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


    def set_header(self, line):
        try:
            result = search('([^:]*):(.*)', line)
            header = result.group(1).lower().strip()
            value = result.group(2).strip()
            value_lower = value.lower()

            if value_lower == 'yes' or value_lower == 'true' or value_lower == '1':
                value = True

            if value_lower == 'no' or value_lower == 'false' or value_lower == '0':
                value = False

            self.headers[header] = value

            return True
        except AttributeError:
            return False
        except Exception as e:
            print(type(e))
            raise


    def parse(self):
        '''
        Parse source and save headers and body attributes
        Format:
            <header>: <value>    <- Optional
                                <-Blanke line, if headers
            <content>

        First line must either be header or content
        '''

        self.headers = {}
        self.body = ''

        in_headers = None
        for line in self.raw.split(linesep):
            # As long as we can set header values do so, after that add raw content to body property

            if in_headers == None or in_headers:
                in_headers = self.set_header(line)

            if not in_headers:
                self.body += line + linesep

        # Strip empty first or last new lines
        self.body = self.body.lstrip(linesep)
        self.body = self.body.rstrip(linesep)

        # Set output to body, typically plugins will process the out before it is saved
        self.out = self.body

