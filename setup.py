from setuptools import setup
import os

setup(name = 'pagegen',
	version='3.8.0',
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
		'lxml==4.9.1',
		'docutils==0.19',
		'htmlmin==0.1.12',
		'rcssmin==1.1.1',
		'jsmin==3.0.1',
		'mako==1.2.1',
		'markdown==3.3.6',
		'libsass==0.21.0',
		'python-docutils-graphviz==1.0.3',
		'pillow==9.2.0',
	],
	entry_points={
		'console_scripts': ['pagegen=pagegen.pagegen:main'],
	}
)
