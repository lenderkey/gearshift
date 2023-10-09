import builtins
import os
import random

class AES0File:
    def __init__(self, filename, mode="r", encoding=None, context=None, **ad):
        from .Gearshift import Gearshift

        self.filename = filename
        self.filename_aes0 = filename + ".aes0"  
        self.mode = mode
        self.encoding = encoding
        self.fio = None
        self.context = context or Gearshift.instance()
        self.key_hash = None

        self.filename_tmp = None

    def __enter__(self):
        match self.mode:
            case 'w' | 'wb':
                dir, base = os.path.split(self.filename_aes0)
                base = f".{base}.{random.randint(0, 999999):06d}"
                self.filename_tmp = os.path.join(dir, base)
                self.fio = builtins.open(self.filename_tmp, "wb")
                self.filename = self.filename_aes0

                return self
            
            case 'r' | 'rb':
                try:
                    self.fio = builtins.open(self.filename_aes0, "rb")
                    self.filename = self.filename_aes0
                except FileNotFoundError:
                    self.fio = builtins.open(self.filename, self.mode)

                return self
            
            case _:
                raise ValueError(f"Unsupported mode: {self.mode}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fio:
            self.fio.close()

        if self.filename_tmp:
            if exc_type:
                os.remove(self.filename_tmp)
            else:
                os.rename(self.filename_tmp, self.filename_aes0)

            self.filename_tmp = None

    def write(self, data):
        assert 'w' in self.mode

        if self.mode == "w":
            data = data.encode(self.encoding or "utf-8")
        
        self.context.aes_encrypt_to_stream(data, fout=self.fio, key_hash=self.key_hash)

    def read(self):
        if not self.filename.endswith('.aes0'):
            return self.fio.read()
        
        data = self.context.aes_decrypt_to_bytes(fin=self.fio)

        if self.mode == "r":
            data = data.decode(self.encoding or "utf-8")

        return data

def open(filename, mode="r", *av, **ad):
    return AES0File(filename=filename, mode=mode, *av, **ad)

