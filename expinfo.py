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
    
    with JobDB(DB_FILE) as f:
        d = f.load()
        if not d:
            return
        
        print('{}{}Currently the following experiments are running:{}'.format(bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
        
        for uuid, exp in d.items():
            print(FMT_STR.format(**exp))
    
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
    
    
    print('Starting cmd={}'.format(cmd), file=sys.stderr)
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        pass
        
    
    with JobDB(DB_FILE) as f:
        d = f.load() or {}
        if my_id in d:
            del d[my_id]
        f.store(d)
        
    
    
if __name__ == '__main__':
    main()


''''
#!/bin/bash

int_trap() {
        echo 1>&2
        echo "cleaning up..." 1>&2
}
trap int_trap INT


pid_file="/tmp/run_exp/cmds.list"
owner="${SUDO_USER:-$USER}"


read -p "Input approximate runtime of experiment [01:00]: " runtime 1>&2
runtime=${runtime:-1:00}

if ! [[ "$runtime" =~ ^[0-9]+\:[0-9]{2}$ ]]; then
        echo "\"${runtime}\" has the wrong format" 1>&2
        exit 1
fi

pid_line="username=${owner} runtime=${runtime}h start=$(date '+%T %F') cmd=${@}"
echo "Add to MOTD: ${pid_line}" 1>&2

if [[ ! -e "${pid_file}" ]]; then
        mkdir -p $(dirname "${pid_file}")
        touch "${pid_file}"
        chmod -R 777 $(dirname "${pid_file}")
fi

echo "${pid_line}" >> "${pid_file}" 
echo "Command is now running..." 1>&2
echo 1>&2

#set -x
"$@"
#set +x

sed -i "/^${pid_line}/d" "${pid_file}"

#echo "Del from MOTD: ${pid_line}" 1>&2




#!/bin/bash


pid_file="/tmp/run_exp/cmds.list"

echo "Run experiments using: run_exp <command>"
if [ ! -s "${pid_file}" ]; then
        echo 
        exit 0
fi

echo -e "\e[1;31mCurrently the following experiments are running:\e[0m"
echo 
cat "${pid_file}" 
echo
'''
