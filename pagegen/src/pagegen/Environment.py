from configparser import ConfigParser
import codecs
from os import environ


class Environment():
    '''
    Load environment settings from environment variables first else from file
    '''

    def __init__(self, env_file):
        ds = 'site' # Default section

        c = ConfigParser(default_section=ds)

        c[ds] = {
            'theme': 'basic'
        }

        # Open the file with the correct encoding
        with codecs.open(env_file, 'r', encoding='utf-8') as f:
            c.readfp(f)

        # Overwrite any settings from environment variables
        for section in c:
            for name, value in c[ds].items():
                env_name = f'PGN_{section}_{name}'.upper()
                if env_name in environ.keys(): 
                    c[section][name] = environ[env_name]

        self.env = c
