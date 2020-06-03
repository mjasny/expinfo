# expinfo
  A small tool for managing experiments of multiple users on a research servers


## Installation

* `git clone https://github.com/mjasny/expinfo`
* `ln -s $(pwd)/expinfo/expinfo.py /usr/local/bin/run_exp`
* `ln -s $(pwd)/expinfo/expinfo.py /etc/update-motd.d/99-expinfo`
* `echo "export PROMPT_COMMAND='run_exp --prompt'" >> /etc/profile`

## Usage

```
usage: expinfo.py [-h] [-t TIME] [-m MESSAGE] [-ex] [cmd [cmd ...]]

positional arguments:
  cmd                   run command as experiment job

optional arguments:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  expected runtime [hours:minutes]
  -m MESSAGE, --message MESSAGE
                        descriptive message to display
  -ex, --exclusive      request exclusive experiment access (shared by default)
```