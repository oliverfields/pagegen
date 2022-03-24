from setuptools import setup
import os

setup(name = 'pagegen',
	version='3.7.0',
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
		'lxml',
		'docutils',
		'htmlmin',
		'rcssmin',
		'jsmin',
		'mako',
		'markdown',
		'libsass',
		'python-docutils-graphviz',
		'pillow',
	],
	entry_points={
		'console_scripts': ['pagegen=pagegen.pagegen:main'],
	}
)
