from Common import Common


class Page(Common):
    '''
    Generate page

    Key concepts:
    Page consists of optional headers (key: value) if first line is not header then it is considered content
    '''

    def __init__(self, source_path, settings={}):
        self.source_path = source_path
        self.settings = settings
        self.log_info(f'Generating page {source_path}')


    def write(self, target_path):
        self.target_path = target_path
        self.write_file(target_path, 'fantasthtml')

