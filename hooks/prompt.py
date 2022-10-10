from utils import bcolors
import os
import config


class Prompt:
    def __init__(self, db):
        self.db = db
        self.filename = os.path.join(config.LOCATION, config.PROMPT_FILENAME)

    def update(self, msg=None):
        if msg is not None and msg['method'] not in ['insert', 'update', 'delete', 'delete_many']:
            return

        f = open(self.filename, 'w')

        entries = self.db.read()
        if not entries:
            return

        # 🔴 🟡 🟢 \033[0;31m ● job 1\033[0m\n
        for entry in entries.values():
            if entry['exclusive']:
                f.write(
                    f'{bcolors.BOLD}{bcolors.FAIL}*** EXCLUSIVE ACCESS by{bcolors.ENDC} {bcolors.OKBLUE}{entry["user"]}{bcolors.ENDC} {bcolors.BOLD}{bcolors.FAIL}***{bcolors.ENDC}')
                f.write('\\n')
                return

        n = len(entries)
        plural = 's' if n > 1 else ''
        info = ', '.join(set(x['user'] for x in entries.values()))
        f.write(
            f'{bcolors.WARNING}{n} job{plural} running from {bcolors.OKBLUE}{info}{bcolors.WARNING}!{bcolors.ENDC}')
        f.write('\\n')


