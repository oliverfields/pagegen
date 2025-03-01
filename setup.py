from setuptools import setup
import os

setup(name = 'pagegen',
    version='4.0.0',
    description='Static site generator',
    author='Oliver Fields',
    author_email='pagegen@phnd.net',
    url='http://pagegen.phnd.net',
    project_urls={
        "Issues": "https://github.com/oliverfields/pagegen/issues",
        "Repository": "https://github.com/oliverfields/pagegen",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    packages=[
        'pagegen',
        'pagegen.plugins.mako_templates',
        'pagegen.plugins.minify',
        'pagegen.plugins.pgn_markdown',
        'pagegen.plugins.rss',
        'pagegen.plugins.shortcodes',
        'pagegen.plugins.sitemap',
        'pagegen.plugins.site_search'
    ],
    package_dir={'':'src'},
    include_package_data=True,
    long_description="""Python static site generator""",
    install_requires=[
        'lxml==4.6.3',
        'htmlmin==0.1.12',
        'rcssmin==1.1.2',
        'jsmin==3.0.1',
        'mako==1.3.0',
        'markdown==3.3.5',
        'pillow==8.2.0',
    ],
    entry_points={
        'console_scripts': ['pgn=pagegen.pagegen:main'],
    }
)
