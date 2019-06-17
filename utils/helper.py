import os
import sys
import argparse
import signal
import copy

from utils import JobDB
from config import *

class DBHelper:
    @staticmethod
    def get(uuid=None):
        with JobDB(DB_FILE, timeout=1) as f:
            d = f.load() or {}
            return d if uuid is None else d.get(uuid, {})
        
    @staticmethod
    def rm(uuid):
        with JobDB(DB_FILE, timeout=1) as f:
            d = f.load() or {}
            if uuid not in d:
                return {}
            
            job = copy.deepcopy(d[uuid])
            del d[uuid]
            f.store(d)
            return job
        
    @staticmethod
    def set(uuid, **kwargs):
        with JobDB(DB_FILE, timeout=1) as f:
            d = f.load() or {}
            
            if uuid not in d:
                d[uuid] = {}
            d[uuid].update(kwargs)
            
            f.store(d)


def get_user():
    if 'SUDO_USER' in os.environ:
        return os.environ['SUDO_USER']
    else:
        return os.environ['USER']
    
    
def get_args(print_help=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', help='expected runtime [hours:mm]')
    parser.add_argument('cmd', nargs='*', help='run command as experiment job')
    args = parser.parse_args()
    
    if not args.cmd:
        from utils import print_motd
        print_motd()
        sys.exit(0)
    
    return args


def kill_pg(pid):
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except ProcessLookupError:
        pass

    

def exit(my_id):
    job = DBHelper.rm(my_id)
    if 'pid' in job:
        kill_pg(job['pid'])
    sys.exit(0)
