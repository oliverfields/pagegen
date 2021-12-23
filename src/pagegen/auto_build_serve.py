import hashlib
import glob
import os
import time
import time
from http.server import HTTPServer, CGIHTTPRequestHandler
import threading
from pagegen.utility import load_config, get_environment_config, exec_script


def start_server(path, port=8000):
    '''Start a simple webserver serving path on port'''
    os.chdir(path)
    httpd = HTTPServer(('', port), CGIHTTPRequestHandler)
    httpd.serve_forever()


def write_status(msg):
	print(msg, end='\r')


def get_time_stamp():
	t = time.localtime()
	return time.strftime("%H:%M:%S", t)


def auto_build_serve(site_conf_path, site_content_dir, site_target_dir):
	try:
		site_config=load_config([site_conf_path], add_dummy_section=False)
	except Exception as e:
		raise Exception("Unable to load site config '" + site_conf_path + "': " + str(e))

	environment = get_environment_config(site_config)

	site_target_dir = site_target_dir + '/' + environment

	try:
		port = 8000
		http_daemon = threading.Thread(name='daemon_server',
			target=start_server,
			args=(site_content_dir, port))

		http_daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.

		print('[' + get_time_stamp() + '] Serving from: ' + site_target_dir)
		print('[' + get_time_stamp() + '] Serving to: http://localhost:' + str(port))

		http_daemon.start()

		print('[' + get_time_stamp() + '] Watching changes to: ' + site_content_dir)

		while True:
			root_dir = site_content_dir
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
				script = ['pagegen', '--generate', '--environment', environment]
				exec_script(script)
				print('[' + get_time_stamp() + '] Serving..')
			else:
				write_status('[' + get_time_stamp() + '] Watching.. (Ctrl+C to quit)')

			last_hash = this_hash

			time.sleep(2)

	except KeyboardInterrupt:
		pass

