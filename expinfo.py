#!/usr/bin/env python3
# author: mjasny

import os
import sys
import time
import datetime as dt
import fcntl
import errno
import json
import subprocess
import argparse
import uuid
import re
import signal


class JobDB:
    def __init__(self, path, mode='a+', timeout=None):
        self._path = path
        self._mode = mode
        self._timeout = timeout
        self._fp = None
        
    def __enter__(self):
        start_ts = time.time()
        self._fp = open(self._path, self._mode)
        try:
            os.chmod(self._path, 0o777)
        except PermissionError:
            pass
        
        while True:
            try:
                fcntl.flock(self._fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                # lock aquired
                return self
            except (OSError, IOError) as e:
                if e.errno != errno.EAGAIN:
                    self._fp.close()
                    raise
                elif self._timeout and time.time() > (start_ts + self._timeout):
                    self._fp.close()
                    raise
            
            time.sleep(0.1)
    
    def __exit__(self, *args):
        fcntl.flock(self._fp.fileno(), fcntl.LOCK_UN)
        self._fp.close()
        
    
    def load(self):
        self._fp.seek(0)
        data = self._fp.read()
        try:
            j = json.loads(data)
        except json.decoder.JSONDecodeError:
            j = None
        return j
        
        
    def store(self, j):
        data = json.dumps(j, sort_keys=True, indent=4)
        self._fp.seek(0)
        self._fp.truncate()
        self._fp.write(data)
        self._fp.flush()    


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    

def get_user():
    if 'SUDO_USER' in os.environ:
        return os.environ['SUDO_USER']
    else:
        return os.environ['USER']

EXE_NAME = 'run_exp'
DB_FILE = '/tmp/expinfo/expinfo.json'
FMT_STR = bcolors.WARNING + '{user:<15}' + bcolors.ENDC + '{start} until {end}\n{cmd}'


def print_motd():
    print('{}Experiment Job Manager: {} --help{}'.format(bcolors.OKGREEN, EXE_NAME, bcolors.ENDC))
    print()
    
    try:
        with JobDB(DB_FILE, timeout=1) as f:
            d = f.load()
            if not d:
                return
        
            print('{}{}Currently the following experiments are running:{}'.format(bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
            
            for uuid, exp in d.items():
                print(FMT_STR.format(**exp))
    except:
        print('{}Cannot aquire lock, please run: rm -r {}/{}'.format(bcolors.WARNING, os.path.dirname(DB_FILE), bcolors.ENDC))
    
    print()


def get_args(print_help=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', help='expected runtime [hours:mm]')
    parser.add_argument('cmd', nargs='*', help='run command as experiment job')
    args = parser.parse_args()
    
    if not args.cmd:
        print_motd()
        sys.exit(0)
    
    return args


def cleanup(my_id, force=False):
    with JobDB(DB_FILE) as f:
        d = f.load() or {}
        if my_id in d:
            del d[my_id]
        f.store(d)
        
    if force:
        print('exited forcefully', file=sys.stderr)
        sys.exit(1)

    
def main():
    os.makedirs(os.path.dirname(DB_FILE), mode=0o777, exist_ok=True)
    args = get_args()
    
    hours, minutes = 1, 0
    if args.time:
        m = re.search(r'([0-9]+)\:([0-9]{2})', args.time)
        hours, minutes = map(int, m.groups())
 
    cmd = ' '.join(args.cmd)
    my_id = uuid.uuid4().hex
    start_time = dt.datetime.now()
    end_time = start_time + dt.timedelta(hours=hours, minutes=minutes)
    
    with JobDB(DB_FILE) as f:
        d = f.load() or {}
        d.update({
            my_id: {
                'user': get_user(),
                'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'cmd': cmd
            }
        })
        f.store(d)
    
    
    clean_shutdown = lambda sig, frame: cleanup(my_id, True)
    signal.signal(signal.SIGALRM, clean_shutdown)
    signal.signal(signal.SIGHUP, clean_shutdown)
    signal.signal(signal.SIGINT, clean_shutdown)
    signal.signal(signal.SIGTERM, clean_shutdown)
    
    print('Starting cmd={}'.format(cmd), file=sys.stderr)        
    try:
        subprocess.run(cmd, shell=True)
    finally:
        cleanup(my_id)
        
    
    
if __name__ == '__main__':
    main()
