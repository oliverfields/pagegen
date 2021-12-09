import ftplib
from os import walk
from os.path import isdir, join, sep, split

class upload():

	def __init__(self):

		self.source_files = []
		self.source_directories = []


	def get_file_lists(self, source_dir):
		''' Get list of files and directories to upload '''

		try:
			# Get lists relative paths of files and directories
			for root, dirs, files in walk(source_dir):
				for name in files:
					file_name = join(root.replace(source_dir, ''), name)
					file_name = file_name.lstrip('/')
					self.source_files.append(file_name)
				for name in dirs:
					dir_name = join(root.replace(source_dir, ''), name)
					dir_name = dir_name.lstrip('/')
					self.source_directories.append(dir_name)

		except Exception as e:
			raise Exception('Unable to get contents list from FTP server')


	def ftp_upload(self, source_dir, config = {}):
		''' Upload site to ftp '''

		self.get_file_lists(source_dir)

		try:
			file_permissions = config['ftp_file_permissions']
		except:
			file_permissions = '644'

		try:
			directory_permissions = config['ftp_directory_permissions']
		except:
			directory_permissions = '755'

		try:
			ftp = ftplib.FTP(config['ftp_host'])
			ftp.login(config['ftp_username'], config['ftp_password'])
		except Exception as e:
			raise Exception('Unable to login to FTP server: %s' % e)

		# Delete target directory content
		self.ftp_rm_tree(ftp, config['ftp_target_directory'])

		# Create directory structure
		for d in self.source_directories:
			#print config['ftp_target_directory'] + '/' + d
			directory = config['ftp_target_directory'] + '/' + d

			try:
				ftp.mkd(directory)
				ftp.sendcmd('SITE CHMOD %s %s' % (directory_permissions, directory))
			except:
				raise Exception('Unable to create and/or set directory permissions')

		# Upload files
		# Need to know if file is binary or not for FTP upload
		for f in self.source_files:
			target_file = config['ftp_target_directory'] + '/' + f
			source_file = join(source_dir, f)
			try:
				ftp.storbinary("STOR " + target_file, open(source_file, "rb"), 1024)
				ftp.sendcmd('SITE CHMOD %s %s' % (file_permissions, target_file))
			except:
				raise Exception('Unable to upload and/or set file permissions')

		ftp.close()


	def ftp_rm_tree(self, ftp, path):
		''' Recursively delete a directory tree on a remote server '''

		# Thanks! -> https://gist.github.com/artlogic/2632647

		try:
			names = ftp.nlst(path)
		except ftplib.all_errors as e:
			# some FTP servers complain when you try and list non-existent paths
			raise Exception('Could not remove {0}: {1}'.format(path, e))
			return

		for name in names:
			if split(name)[1] in ('.', '..'): continue

			# On domeneshop paths seem to come full, whilst the other one returned just the name.. May need rewrite
			#file_or_dir = path + '/' + name
			file_or_dir = name

			try:
				ftp.cwd(file_or_dir)  # if we can cwd to it, it's a directory
				self.ftp_rm_tree(ftp, file_or_dir) # Go delete more

				try:
					ftp.rmd(file_or_dir)
				except ftplib.all_errors as e:
					raise Exception('Could not remove {0}: {1}'.format(path, e))
			except ftplib.all_errors:
				# A file, so just remove
				ftp.delete(file_or_dir)
