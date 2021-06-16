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
    parser.add_argument('--prompt', default=False,
                        action='store_true', help='print small info for terminal prompt')
    parser.add_argument(
        '-t', '--time', help='expected runtime [hours:minutes]')

    parser.add_argument('-ex', '--exclusive', default=False, action='store_true',
                        help='request exclusive experiment access (shared by default)')
    parser.add_argument('-p', '--pin', default=False,
                        action='store_true', help='pin executeable to specified numa nodes (does invoke numactl)')

    required_group = parser.add_argument_group('required arguments')
    required_group.add_argument('-m', '--message',
                                help='descriptive message for the job')
    required_group.add_argument(
        '-n', '--numa', help='Pin to numa node (does *not* invoke numactl)')

    parser.add_argument(
        'cmd', nargs='*', help='run command as experiment job. pro-tip: write -- before your command.')

    args = parser.parse_args()

    if args.prompt:
        print_prompt()
        sys.exit(0)

    if not args.cmd:
        from utils import print_motd
        print_motd()
        sys.exit(0)

    if not args.message:
        parser.print_help()
        print('error: the following arguments are required: -m/--message')
        sys.exit(1)

    if not args.numa:
        parser.print_help()
        print('error: the following arguments are required: -n/--numa')
        sys.exit(1)

    return args


def get_jobs():
    try:
        return DBHelper.get()
    except:
        print('{}Cannot aquire lock, please run: rm -r {}/{}'.format(bcolors.WARNING,
              os.path.dirname(DB_FILE), bcolors.ENDC))
        sys.exit(0)


def kill_pg(pid):
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except ProcessLookupError:
        pass


def print_prompt():
    from utils import bcolors
    jobs = get_jobs()
    if not jobs:
        return

    for _, exp in jobs.items():
        if exp['exclusive']:
            print('{}{}*** EXCLUSIVE ACCESS by {}{}{}{}{} ***{}'.format(bcolors.BOLD,
                  bcolors.FAIL, bcolors.ENDC, bcolors.OKBLUE, exp['user'], bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
            return

    n = len(jobs)
    plural = 's' if n > 1 else ''
    info = ', '.join(set(x['user'] for x in jobs.values()))
    print('{}{} job{} running from {}{}{}!{}'.format(bcolors.WARNING, n,
          plural, bcolors.OKBLUE, info, bcolors.WARNING, bcolors.ENDC))


def exit(my_id):
    job = DBHelper.rm(my_id)
    if 'pid' in job:
        kill_pg(job['pid'])
    sys.exit(0)
