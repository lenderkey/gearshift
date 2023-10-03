# gearshift

Encryption at Rest Tools

## Technical Details
### File Format

* First 4 bytes: b"AES0"
* Next 1 byte: Key Hash length
* Next N bytes: Key Hash (in ASCII)
* Next 1 byte: AES IV length
* Next N bytes: AES IV
* Next 1 byte: AES tag length
* Next N bytes: AES tag
* Remainder: AES encrypted data

### Vault Setup
### Local FS Setup

To setup, have a `~/.gearshift/gearshift.yaml` that looks like this

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

Encrypt to stdin to stdout:

```
gearshift encrypt < file.txt > file.txt.aes
```

Encrypt a file to a file:

```
gearshift encrypt file.txt --output file.txt.aes
```

Decrypt to stdin to stdout:

```
gearshift decrypt < file.txt.aes > file.txt
```

Decrypt a file to a file:

```
gearshift decrypt file.txt.aes --output file.txt
```

### Vault Commands

Coming Soon

### Local FS Commands

And use the following commands to make the keys. You
will have to copy the `key_hash` into `~/.gearshift/gearshift.yaml`

```
gearshift key-create --output ~/.gearshift/keys/keys.key
```
