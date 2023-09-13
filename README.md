# gearshift

Encryption at Rest Server /
Efficient Immutable File Transfer


## File Format

* First 4 bytes: b"AES0"
* Next byte: AES IV length
* Next N buyes: AES IV
* Next 4 bytes: AES tag length
* Next N bytes: AES tag
* Remainder: AES encrypted data
