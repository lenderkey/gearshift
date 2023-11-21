# gearshift

Encryption at Rest Tools

## Technical Details
### File Format

* First 4 bytes: b"GEAR"
* N "Blocks"

Each block is:

* 1 byte: length (N) of data
* 1 byte: type
* N bytes: data

All upper case "types" must be understood by Readers.
Lower case "types" are optional and can be ignored if not understood.

Blocks are ended by:

* 1 byte: type (0x00)
* 1 byte: length (0x00)

The types are:

* 'I': AES IV
* 'T': AES Tag
* 'H': Key Hash (in ASCII)
* 'Z': Data is Compressed by ZLIB

### Vault Setup
### Local FS Setup

To instance(), have a `~/.gearshift/gearshift.yaml` that looks like this

```
security:
  key_file: "~/.gearshift/keys/keys.key"
  key_hash: "Zdl_YEUEGi32D241xVUdxsZG25lEFUauNkTSRXgd-mU"
```

Note that if you're using this method, probably best
to have the actual data you're encrypting on a different
file system on a different machine (e.g. NFS).

Otherwise, Vault is the preferred way to do things.

## Commands
### Encrypting and Decrypting files

You can use the `gearshift` command to encrypt and decrypt files.
You can find it in `./scripts`

Encrypt to stdin to stdout:

```
scripts/gearshift encrypt < file.txt > file.txt.gear
```

Encrypt a file to a file:

```
scripts/gearshift encrypt file.txt --output file.txt.gear
```

Decrypt to stdin to stdout:

```
scripts/gearshift decrypt < file.txt.gear > file.txt
```

Decrypt a file to a file:

```
scripts/gearshift decrypt file.txt.gear --output file.txt
```

### Vault Commands

Coming Soon

### Local FS Commands

And use the following commands to make the keys. You
will have to copy the `key_hash` into `~/.gearshift/gearshift.yaml`

```
gearshift key-create --output ~/.gearshift/keys/keys.key
```
