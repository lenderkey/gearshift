#
#   See ../README.md
#   This will setup ~/.gearshift
#   You need to have your own ~/Corpus with files to test
#
set -ex
[ ! -d ~/.gearshift ] && mkdir ~/.gearshift
cp -R dot-gearshift/* ~/.gearshift
cd ~/.gearshift
[ ! -d db ] && mkdir db
rm -f db/*.db
[ ! -d corpii ] && mkdir corpii
rm -rf corpii/*
mkdir corpii/client-2
mkdir corpii/client-3
mkdir corpii/server
