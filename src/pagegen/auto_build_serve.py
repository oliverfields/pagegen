import hashlib
import glob
import os
import time
import time
from pagegen.utility import load_config, get_environment_config, exec_script
import subprocess

def write_status(msg):
	print(msg, end='\r')


def get_time_stamp():
	t = time.localtime()
	return time.strftime("%H:%M:%S", t)


def auto_build_serve(site_conf_path, environment, watch_dir, serve_dir, exclude_hooks, build_function):

	try:
		port = "8000"
		with open(os.devnull, 'w') as t:
			subprocess.Popen(["python3", "-m", "http.server", port, "-d", serve_dir], stdout=t, stderr=t)

		print('[' + get_time_stamp() + '] Serving from: ' + serve_dir)
		print('[' + get_time_stamp() + '] Serving to: http://localhost:' + port)

		print('[' + get_time_stamp() + '] Watching changes to: ' + watch_dir)

		while True:

			root_dir = watch_dir + '/'
			directory_list = ''

			# root_dir needs a trailing slash (i.e. /root/dir/)
			for filename in glob.iglob(root_dir + '**/*', recursive=True):
				directory_list += (filename + ' ' + str(os.path.getmtime(filename)) + '\n')

			#print(directory_list)
			this_hash = hashlib.md5(directory_list.encode('utf-8')).hexdigest()

			if 'last_hash' not in locals():
				last_hash = this_hash

			if last_hash != this_hash:
				print('[' + get_time_stamp() + '] Building..')
				#script = ['pagegen', '--generate', environment]
				#exec_script(script)
				build_function(site_conf_path, environment, exclude_hooks)
				print('[' + get_time_stamp() + '] Serving..')
			else:
				write_status('[' + get_time_stamp() + '] Watching.. (Ctrl+C to quit)')

			last_hash = this_hash

			time.sleep(2)

	except KeyboardInterrupt:
		pass

