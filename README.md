# gearshift

Encryption at Rest Tools

## File Format

* First 4 bytes: b"AES0"
* Next 1 byte: Key Hash length
* Next N bytes: Key Hash (in ASCII)
* Next 1 byte: AES IV length
* Next N bytes: AES IV
* Next 1 byte: AES tag length
* Next N bytes: AES tag
* Remainder: AES encrypted data

