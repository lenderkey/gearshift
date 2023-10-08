import builtins

import builtins

class AES0File:
    def __init__(self, filename, mode="r", encoding=None, context=None, **ad):
        from .Gearshift import Gearshift

        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.fio = None
        self.context = context or Gearshift.instance()
        self.key_hash = None

    def __enter__(self):
        if 'w' in self.mode:
            self.fio = builtins.open(self.filename + ".aes0", "wb")
            self.filename = self.filename + ".aes0"
            return self
        elif 'r' in self.mode:
            try:
                self.fio = builtins.open(self.filename + ".aes0", "rb")
                self.filename = self.filename + ".aes0"
            except FileNotFoundError:
                self.fio = builtins.open(self.filename, self.mode)
            return self
        else:
            raise ValueError("Unsupported mode: {}".format(self.mode))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fio:
            self.fio.close()

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

