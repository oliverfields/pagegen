import argparse
from sys import exit
from utils import log_error, find_site_dir
from traceback import print_exception


def generate_site():
    print('hi')


if __name__ == "__main__":

    try:
        p = argparse.ArgumentParser()

        p.add_argument('-g', '--generate', action='store_true', help='Generate site')
        a = p.parse_args()

        if a.generate:
            content_dir = find_site_dir()
            print(content_dir)
            generate_site()

    except Exception as e:
        log_error('Unknown failure')
        print_exception(type(e), e, e.__traceback__)
        exit(1)
