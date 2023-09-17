# gearshift

Encryption at Rest Server /
Efficient Immutable File Transfer


## File Format

* First 4 bytes: b"AES0"
* Next 1 byte: Key Hash length
* Next N bytes: Key Hash (in ASCII)
* Next 1 byte: AES IV length
* Next N bytes: AES IV
* Next 1 byte: AES tag length
* Next N bytes: AES tag
* Remainder: AES encrypted data

# Sample

This sets up a local encryption at rest server and two clients.
Client 1 is the origin of the files, and Client 2 is where they will end up.

(Note that this isn't a hard restriction - Client 1 and Client 2 
can equally control what is on the Server! This is just for the
purposes of this example)

You should create a folder called ~/lenderkey/Corpus and put files
to sync in it. If you want to use Client3, make a subfolder called
ENVS2060.


```
cd samples

## set up everything and bring everything back to ground state
sh Reset.sh

## in a new Terminal - run the Encryption at Rest Server
## files will be in ~/.gearshift/corpii/server and will be encrypted
sh Server.sh

## load files up to the server
## files are from ~/lenderkey/Corpus and are cleartext
sh Client1.sh

## download files from the server (into a new folder)
## files will be in ~/.gearshift/corpii/client-2 and will be cleartext
sh Client2.sh

## like Client2.sh, but only syncs a folder named ENVS2060
sh Client3.sh
```

At this point you can try things like adding and removing files from 
`~/lenderkey/Corpus` and running `Client1.sh` and `Client2.sh` and see 
the changes propagate.
