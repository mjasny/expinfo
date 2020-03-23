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
    jobs = get_jobs()

    for _, j in jobs.items():
        if j['exclusive']:
            from utils import print_motd
            print_motd()

            print('{}{}An exclusive job is running, please wait until it has finished.{}'.format(bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
            sys.exit(1)

    if args.exclusive and len(jobs) > 0:
        from utils import print_motd
        print_motd()

        print('{}{}Cannot start job exclusively, please wait until all other jobs finished.{}'.format(bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
        sys.exit(1)
    
    
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
        cmd=cmd,
        msg=args.message,
        exclusive=args.exclusive,
        pid=0
    )
    
    clean_shutdown = lambda sig, frame: exit(my_id)
    signal.signal(signal.SIGALRM, clean_shutdown)
    signal.signal(signal.SIGHUP, clean_shutdown)
    signal.signal(signal.SIGINT, clean_shutdown)
    signal.signal(signal.SIGTERM, clean_shutdown)
    
    print('Starting cmd={}'.format(cmd), file=sys.stderr)     
    
    try:
        p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid) 
        
        DBHelper.set(my_id, pid=p.pid)

        p.wait()
    finally:
        exit(my_id)
        
    
    
if __name__ == '__main__':
    main()
