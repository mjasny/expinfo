import time
import json
import fcntl
import errno
import os


class JobDB:
    def __init__(self, path, mode='a+', timeout=None):
        self._path = path
        self._mode = mode
        self._timeout = timeout
        self._fp = None
        
    def __enter__(self):
        start_ts = time.time()
        self._fp = open(self._path, self._mode)
        try:
            os.chmod(self._path, 0o777)
        except PermissionError:
            pass
        
        while True:
            try:
                fcntl.flock(self._fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                # lock aquired
                return self
            except (OSError, IOError) as e:
                if e.errno != errno.EAGAIN:
                    self._fp.close()
                    raise
                elif self._timeout and time.time() > (start_ts + self._timeout):
                    self._fp.close()
                    raise
            
            time.sleep(0.1)
    
    def __exit__(self, *args):
        fcntl.flock(self._fp.fileno(), fcntl.LOCK_UN)
        self._fp.close()
        
    
    def load(self):
        self._fp.seek(0)
        data = self._fp.read()
        try:
            j = json.loads(data)
        except json.decoder.JSONDecodeError:
            j = None
        return j
        
        
    def store(self, j):
        data = json.dumps(j, sort_keys=True, indent=4)
        self._fp.seek(0)
        self._fp.truncate()
        self._fp.write(data)
        self._fp.flush()    
