import gearshift

import unittest

## Run me with:
## python -m unittest tests/*py


class TestIO(unittest.TestCase):

    def test_upper(self):
        with gearshift.io.open("xxx_hello.txt", "w") as fout:
            fout.write("Hello, world!\n")


if __name__ == '__main__':
    unittest.main()
