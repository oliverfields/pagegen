from configparser import ConfigParser
import codecs
from os import environ
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Config():
    '''
    Load config from environment variables first else from config file
    '''

    def __init__(self, conf_file):
        ds = 'site' # Default section

        c = ConfigParser(default_section=ds)

        c[ds] = {
            'theme': 'basic'
        }

        # Open the file with the correct encoding
        with codecs.open(conf_file, 'r', encoding='utf-8') as f:
            c.read_file(f)

        # Overwrite any settings from environment variables
        for section in c:
            for name, value in c[ds].items():
                env_name = f'PGN_{section}_{name}'.upper()
                if env_name in environ.keys():
                    c[section][name] = environ[env_name]

        self.configparser = c
        logger.debug('Config loaded from: ' + conf_file)
