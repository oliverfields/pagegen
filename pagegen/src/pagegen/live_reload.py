import hashlib
import glob
from os import remove, kill
from os.path import join, isdir, getmtime, dirname, abspath
import time
from constants import LIVE_RELOAD_HASH_FILE
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
    print('killing')
    http_server_process.kill()
    if http_server_pid is None:
        pass
    else:
        remove(hash_file)
        http_server_process.kill()
        #kill(http_server_pid, signal.SIGTERM)


def write_file(file, content):
    # 'a' -> Open file for appending, will create if not exist
    try:
        with open(file, 'a') as f:
            f.write(content)
    except Exception as e:
        raise (Exception('Unable to write file %s: %s' % (file, e)))

def live_reload(site, watch_elements, serve_base_url, serve_port):

    http_server_script = join(dirname(abspath(__file__)), 'http_server.py')
    print(http_server_script)

    try:
        global hash_file
        hash_file = join(site.build_dir, LIVE_RELOAD_HASH_FILE)
        global http_server_process
        http_server_process = subprocess.Popen(["python3", http_server_script, site.build_dir], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        global http_server_pid
        http_server_pid = http_server_process.pid
        atexit.register(kill_http_server)

        #print('[' + get_time_stamp() + '] Serving from: ' + site.build_dir)
        #print('[' + get_time_stamp() + '] Serving to: ' + serve_base_url + ':' + serve_port)

        print('[' + get_time_stamp() + '] Watching changes to: ')
        for we in watch_elements:
            print('           ' + we)

        # Write hash file so there is something to poll
        write_file(hash_file, '')

        while True:
            names_and_modified_times = '' # Create string of file and directories with timestamps, create hash of this and compare to previous hash to detect changes

            for we in watch_elements:

                if isdir(we):
                    we += '/**/*'

                #for item in glob.iglob(root_dir + '**/*', recursive=True):
                for item in glob.iglob(we, recursive=True):
                    names_and_modified_times += (item + ' ' + str(getmtime(item)) + '\n')

            this_hash = hashlib.md5(names_and_modified_times.encode('utf-8')).hexdigest()

            if 'last_hash' not in locals():
                last_hash = this_hash

            if last_hash != this_hash:
                print('[' + get_time_stamp() + '] Building..')
                site.build_site()

                # Update timestamp to signal to live reaload js poll script to reload
                write_file(hash_file, this_hash)
                print('[' + get_time_stamp() + '] Serving..')
            else:
                write_status('[' + get_time_stamp() + '] Watching.. (Ctrl+C to quit)')

            last_hash = this_hash

            time.sleep(2)

    except KeyboardInterrupt:
        pass

