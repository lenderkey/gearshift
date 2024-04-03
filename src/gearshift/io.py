import builtins
import os
import random

class Gearshift:
    def __init__(self, filename, mode="r", encoding=None, context=None, **ad):
        from .context import GearshiftContext

        if filename.endswith(".gear"):
            filename = filename[:-5]

        self.filename = filename
        self.filename_gear = filename + ".gear"

        self.mode = mode
        self.encoding = encoding
        self.fio = None
        self.context = context or GearshiftContext.instance()
        self.key_hash = None

        self.filename_tmp = None

        self._data = None
        self._position = None

    def __enter__(self):
        match self.mode:
            case 'w' | 'wb':
                dir, base = os.path.split(self.filename_gear)
                base = f".{base}.{random.randint(0, 999999):06d}"
                self.filename_tmp = os.path.join(dir, base)
                self.fio = builtins.open(self.filename_tmp, "wb")

                return self
            
            case 'r' | 'rb':
                try:
                    self.fio = builtins.open(self.filename_gear, "rb")
                except FileNotFoundError:
                    self.filename_gear = None
                    self.fio = builtins.open(self.filename, self.mode)

                return self
            
            case _:
                raise ValueError(f"Unsupported mode: {self.mode}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fio:
            self.fio.close()

        if self.filename_tmp and 'w' in self.mode:
            if exc_type:
                os.remove(self.filename_tmp)
            else:
                os.rename(self.filename_tmp, self.filename_gear)

                try: os.remove(self.filename)
                except IOError: pass

            self.filename_tmp = None

    def write(self, data):
        assert 'w' in self.mode

        if self.mode == "w":
            data = data.encode(self.encoding or "utf-8")
        
        self.context.aes_encrypt_to_stream(data, fout=self.fio, key_hash=self.key_hash)

    def read(self, /, size=None):
        if not self.filename_gear:
            return self.fio.read(size)
        
        if self._data is None:
            self._position = 0
            self._data = self.context.aes_decrypt_to_bytes(fin=self.fio)

            if self.mode == "r":
                self._data = self._data.decode(self.encoding or "utf-8")

        if size is None:
            self._position = len(self._data)
            return self._data

        chunk = self._data[self._position:self._position+size]
        self._position += size
        self._position = min(self._position, len(self._data))

        return chunk
    
    def flush(self):
        pass

def open(filename, mode="r", *av, **ad):
    return Gearshift(filename=filename, mode=mode, *av, **ad)

def strip(filename:str) -> str:
    if filename.endswith(".gear"):
        return filename[:-5]

    return filename

def exits(filename:str) -> bool:
    if filename.endswith(".gear"):
        return os.path.exists(filename)
    elif os.path.exists(filename):
        return True
    elif os.path.exists(filename + ".gear"):
        return True
    else:
        return False
