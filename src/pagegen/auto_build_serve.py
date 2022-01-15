import hashlib
import glob
import os
import time
from pagegen.utility import load_config, get_environment_config, exec_script, SEARCHMODESITEUPDATEDFILE, write_file
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


def auto_build_serve(site_conf_path, environment, watch_elements, serve_dir, exclude_hooks, build_function, serve_base_url, serve_port):

	try:
		http_server_process = subprocess.Popen(["python3", "-m", "http.server", serve_port, "-d", serve_dir], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
		global http_server_pid
		http_server_pid = http_server_process.pid
		atexit.register(kill_http_server)

		print('[' + get_time_stamp() + '] Serving from: ' + serve_dir)
		print('[' + get_time_stamp() + '] Serving to: ' + serve_base_url + ':' + serve_port)

		print('[' + get_time_stamp() + '] Watching changes to: ')
		for we in watch_elements:
			print('           ' + we)

		while True:
			names_and_modified_times = '' # Create string of file and directories with timestamps, create hash of this and compare to previous hash to detect changes

			for we in watch_elements:

				if os.path.isdir(we):
					we += '/**/*'

				#for item in glob.iglob(root_dir + '**/*', recursive=True):
				for item in glob.iglob(we, recursive=True):
					names_and_modified_times += (item + ' ' + str(os.path.getmtime(item)) + '\n')

			this_hash = hashlib.md5(names_and_modified_times.encode('utf-8')).hexdigest()

			if 'last_hash' not in locals():
				last_hash = this_hash

			if last_hash != this_hash:
				print('[' + get_time_stamp() + '] Building..')
				build_function(site_conf_path, environment, exclude_hooks, serve_base_url + ':' + serve_port, serve_mode=True)

				# Update timestamp to signal to live reaload js poll script to reload
				write_file(serve_dir + '/' + SEARCHMODESITEUPDATEDFILE, this_hash)
				print('[' + get_time_stamp() + '] Serving..')
			else:
				write_status('[' + get_time_stamp() + '] Watching.. (Ctrl+C to quit)')

			last_hash = this_hash

			time.sleep(2)

	except KeyboardInterrupt:
		pass

