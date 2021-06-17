# expinfo

A small tool for managing experiments of multiple users on a research servers


## Installation

* `git clone https://github.com/mjasny/expinfo`
* `ln -s $(pwd)/expinfo/expinfo.py /usr/local/bin/run_exp`
* `ln -s $(pwd)/expinfo/expinfo.py /etc/update-motd.d/99-expinfo`
* `echo "export PROMPT_COMMAND='run_exp --prompt'" >> /etc/profile`

## Usage

```
usage: expinfo.py [-h] [--prompt] [-t TIME] [-ex] [-p] [-m MESSAGE] [-n NUMA] [cmd ...]

positional arguments:
  cmd                   run command as experiment job. pro-tip: write -- before your command.

optional arguments:
  -h, --help            show this help message and exit
  --prompt              print small info for terminal prompt
  -t TIME, --time TIME  expected runtime [hours:minutes]
  -ex, --exclusive      request exclusive experiment access (shared by default)
  -p, --pin             pin executeable to specified numa nodes (does invoke numactl)

required arguments:
  -m MESSAGE, --message MESSAGE
                        descriptive message for the job
  -n NUMA, --numa NUMA  Pin to numa node (does *not* invoke numactl)
```