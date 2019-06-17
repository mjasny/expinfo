import os

from utils import bcolors
from utils.helper import DBHelper
from config import *


def print_motd():
    print('{}Experiment Job Manager: {} --help{}'.format(bcolors.OKGREEN, EXE_NAME, bcolors.ENDC))
    print()
    
    try:
        jobs = DBHelper.get()
        if not jobs:
            return
        
        print('{}{}Currently the following experiments are running:{}'.format(bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
        
        for uuid, exp in jobs.items():
            print(FMT_STR.format(**exp))
    except:
        print('{}Cannot aquire lock, please run: rm -r {}/{}'.format(bcolors.WARNING, os.path.dirname(DB_FILE), bcolors.ENDC))
    
    print()
