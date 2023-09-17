set -ex
[ ! -d ~/.gearshift ] && mkdir ~/.gearshift
cp -R dot-gearshift ~/.gearshift
cd ~/.gearshift
rm -f db/*.db
rm -rf corpii/*
mkdir corpii/client-2
mkdir corpii/server
