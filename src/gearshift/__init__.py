from .Gearshift import Gearshift
from .io import open

if __name__ == '__main__':
    with open("README.md", "w") as fout:
        fout.write("Hello world!")

    ## gearshift.open("README.md", "w")