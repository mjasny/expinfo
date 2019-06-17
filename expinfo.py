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
import uuid
import re
import copy
import signal

from utils import JobDB, bcolors
from utils.helper import *
from config import *
   


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
    
    DBHelper.set(
        my_id, 
        user=get_user(),
        start=start_time.strftime('%Y-%m-%d %H:%M:%S'),
        end=end_time.strftime('%Y-%m-%d %H:%M:%S'),
        cmd=cmd
    )
        
    
    clean_shutdown = lambda sig, frame: exit(my_id)
    signal.signal(signal.SIGALRM, clean_shutdown)
    signal.signal(signal.SIGHUP, clean_shutdown)
    signal.signal(signal.SIGINT, clean_shutdown)
    signal.signal(signal.SIGTERM, clean_shutdown)
    
    print('Starting cmd={}'.format(cmd), file=sys.stderr)        
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, 
                             shell=True, preexec_fn=os.setsid) 
        
        DBHelper.set(my_id, pid=p.pid)

        p.wait()
    finally:
        exit(my_id)
        
    
    
if __name__ == '__main__':
    main()
