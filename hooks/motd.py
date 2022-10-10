import os
import config
from utils import bcolors


class Motd:
    def __init__(self, db):
        self.db = db
        self.filename = os.path.join(config.LOCATION, config.MOTD_FILENAME)

    def update(self, msg=None):
        if msg is not None and msg['method'] not in ['insert', 'update', 'delete', 'delete_many']:
            return

        f = open(self.filename, 'w')

        f.write('{}Experiment Job Manager: {} --help{}\n'.format(bcolors.OKGREEN,
                                                                 config.EXE_NAME, bcolors.ENDC))
        f.write('\n')
        f.write('{}Please register all processes you start!{}\n'.format(
            bcolors.WARNING, bcolors.ENDC))
        f.write('\n')

        entries = self.db.read()
        if not entries:
            return

        f.write('{}{}Currently the following experiments are running:{}\n'.format(
            bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
        for _id, exp in entries.items():
            f.write(self.get_fmt_exp(_id=_id, **exp))
            f.write('\n\n')

    def get_fmt_exp(self, _id, user, start, end, cmd, msg, exclusive, pid, numa='?'):
        line = ''

        if exclusive:
            line += '\n{}*** EXCLUSIVE ACCESS ***{}\n'.format(
                bcolors.FAIL, bcolors.ENDC)

        line += '{}{:<15}{} {}Start:{} {}'.format(
            bcolors.WARNING, user, bcolors.ENDC, bcolors.OKBLUE, bcolors.ENDC, start)
        line += ' {}NUMA:{} {} {}PID:{} {}'.format(
            bcolors.OKBLUE, bcolors.ENDC, numa, bcolors.OKBLUE, bcolors.ENDC, pid)
        if end is not None:
            line += '\n{}   User estimated End:{} {}'.format(bcolors.OKBLUE, bcolors.ENDC, end)
        line += '\n{}Message:{} {}'.format(bcolors.OKBLUE, bcolors.ENDC, msg)
        line += '\n{}Exec:{} {}'.format(bcolors.OKBLUE, bcolors.ENDC, cmd)

        if exclusive:
            line += '\n{}*** EXCLUSIVE ACCESS ***{}'.format(
                bcolors.FAIL, bcolors.ENDC)

        return line

