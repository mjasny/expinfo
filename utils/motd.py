import os

from utils import bcolors
from utils.helper import DBHelper, get_jobs
from config import *


def get_fmt_exp(id, user, start, end, cmd, msg, exclusive, pid, numa='?'):
    line = ''

    if exclusive:
        line += '\n{}*** EXCLUSIVE ACCESS ***{}\n'.format(
            bcolors.FAIL, bcolors.ENDC)

    line += '{}{:<15}{} {}Start:{} {}'.format(
        bcolors.WARNING, user, bcolors.ENDC, bcolors.OKBLUE, bcolors.ENDC, start)
    line += ' {}NUMA:{} {} {}PID:{} {}'.format(
        bcolors.OKBLUE, bcolors.ENDC, numa, bcolors.OKBLUE, bcolors.ENDC, pid)
    line += '\n{}Message:{} {}'.format(bcolors.OKBLUE, bcolors.ENDC, msg)

    if exclusive:
        line += '\n{}*** EXCLUSIVE ACCESS ***{}'.format(
            bcolors.FAIL, bcolors.ENDC)

    return line


def print_motd():
    print('{}Experiment Job Manager: {} --help{}'.format(bcolors.OKGREEN,
          EXE_NAME, bcolors.ENDC))
    print()
    print('{}Please register all processes you start!{}'.format(
        bcolors.WARNING, bcolors.ENDC))
    print()

    jobs = get_jobs()
    if not jobs:
        return

    print('{}{}Currently the following experiments are running:{}'.format(
        bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))

    for id, exp in jobs.items():
        print(get_fmt_exp(id=id, **exp), end='\n\n')
