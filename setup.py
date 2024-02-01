from setuptools import setup
import os

setup(name = 'pagegen',
	version='3.11.1',
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
	packages=['pagegen'],
	package_dir={'':'src'},
	include_package_data=True,
	long_description="""Python static site generator with reStructuredText or Markdown markup and Mako templates.""",
	install_requires=[
		'lxml==4.6.3',
		'htmlmin==0.1.12',
		'rcssmin==1.1.2',
		'jsmin==3.0.1',
		'mako==1.3.0',
		'markdown==3.3.4',
		'pillow==8.2.0',
		'beautifulsoup4==4.12.2',
	],
	extra_require=[
		'docutils==0.16',
		'python-docutils-graphviz==1.0.3',
	],
	entry_points={
		'console_scripts': ['pgn=pagegen.pagegen:main'],
	}
)
