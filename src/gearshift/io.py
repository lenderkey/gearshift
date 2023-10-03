import builtins

import builtins
import codecs

class ROT13File:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        if 'w' in self.mode:
            self.file = builtins.open(self.filename + ".rot13", self.mode)
            return self
        elif 'r' in self.mode:
            try:
                self.file = builtins.open(self.filename + ".rot13", self.mode)
            except FileNotFoundError:
                self.file = builtins.open(self.filename, self.mode)
            return self
        else:
            raise ValueError("Unsupported mode: {}".format(self.mode))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

    def write(self, data):
        if 'w' in self.mode:
            self.file.write(codecs.encode(data, 'rot_13'))

    def read(self):
        content = self.file.read()
        if self.filename.endswith('.rot13'):
            return codecs.decode(content, 'rot_13')
        return content

def open(filename, mode='r'):
    return ROT13File(filename, mode)

if __name__ == '__main__':
    # Testing
    # Writing to a file
    with open('example.txt', 'w') as fout:
        fout.write('Hello, World!')

    # Reading from a file
    with open('example.txt', 'r') as fin:
        print(fin.read())  # Urfry, Jbeyq!
