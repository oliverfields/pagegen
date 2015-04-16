from setuptools import setup

files=['skel/*', 'pagegen.conf', 'changelog']

setup(name = 'pagegen',
	version='2.1.0',
	description='Static site generator',
	author='Oliver Fields',
	author_email='pagegen@phnd.netr',
	url='http://pagegen.phnd.net',
	license='GPLv3',
	packages=['pg'],
	package_data={'pg' : files },
	scripts=['pagegen'],
	long_description="""Python static site generator with reStructuredText markup.""",
	install_requires=['lxml','docutils']
)
