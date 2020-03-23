import os

from utils import bcolors
from utils.helper import DBHelper, get_jobs
from config import *


def get_fmt_exp(id, user, start, end, cmd, msg, exclusive, pid):
    lines = []
    
    lines.append('{}{:<15}{}'.format(bcolors.WARNING, user, bcolors.ENDC) + '{} until {}'.format(start, end))

    if exclusive:
        lines.append('{}*** EXCLUSIVE ACCESS ***{}'.format(bcolors.FAIL, bcolors.ENDC))
    
    lines.append('{}PID:{} {}'.format(bcolors.OKBLUE, bcolors.ENDC, pid) + ' '*4 + '{}Message:{} {}'.format(bcolors.OKBLUE, bcolors.ENDC, msg))

    return '\n'.join(lines)


def print_motd():
    print('{}Experiment Job Manager: {} --help{}'.format(bcolors.OKGREEN, EXE_NAME, bcolors.ENDC))
    print()
    
    jobs = get_jobs()
    if not jobs:
        return
    
    print('{}{}Currently the following experiments are running:{}'.format(bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
    
    for id, exp in jobs.items():
        print(get_fmt_exp(id=id, **exp), end='\n\n')
