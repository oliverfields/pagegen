import hashlib
import glob
import os
import time
from pagegen.utility import load_config, get_environment_config, exec_script
import subprocess
import sys
import signal
import atexit

def write_status(msg):
	print(msg, end='\r')


def get_time_stamp():
	t = time.localtime()
	return time.strftime("%H:%M:%S", t)


def kill_http_server():
	if http_server_pid is None:
		pass
	else:
		os.kill(http_server_pid, signal.SIGTERM)


def auto_build_serve(site_conf_path, environment, watch_dir, serve_dir, exclude_hooks, build_function, serve_base_url, serve_port):

	try:
		http_server_process = subprocess.Popen(["python3", "-m", "http.server", serve_port, "-d", serve_dir], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
		global http_server_pid
		http_server_pid = http_server_process.pid
		atexit.register(kill_http_server)

		print('[' + get_time_stamp() + '] Serving from: ' + serve_dir)
		print('[' + get_time_stamp() + '] Serving to: ' + serve_base_url + ':' + serve_port)

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
				build_function(site_conf_path, environment, exclude_hooks, serve_base_url + ':' + serve_port )
				print('[' + get_time_stamp() + '] Serving..')
			else:
				write_status('[' + get_time_stamp() + '] Watching.. (Ctrl+C to quit)')

			last_hash = this_hash

			time.sleep(2)

	except KeyboardInterrupt:
		pass

