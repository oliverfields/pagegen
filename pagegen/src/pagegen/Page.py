from Common import Common


class Page(Common):
    '''
    Generate page

    Key concepts:
    Page consists of optional headers (key: value) if first line is not header then it is considered content
    '''

    def __init__(self, source_path, target_path, settings={}):
        self.source_path = source_path
        self.target_path = target_path
        self.settings = settings
        self.headers = {}

        self.log_info(f'Generating page {source_path}')

        if source_path == '/home/oliver/Documents/pgn4/mysite/content/index':
            self.headers['template'] = 'home_page'
        else:
            self.headers['template'] = 'pages'


    def write(self):
        self.write_file(self.target_path, 'fantasthtml')

