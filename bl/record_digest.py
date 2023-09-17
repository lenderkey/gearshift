from Context import Context
from structures import FileRecord
import helpers

def record_digest(record:FileRecord) -> bytes:
    """
    Return the data for a record. Don't think about the naming too much.
    """
    with open(record.linkpath, "rb") as fin:
        if not record.key_hash:
            return fin.read()

        header = fin.read(4)
        assert header == b"AES0"

        key_hash_len = int(fin.read(1)[0])
        key_hash = fin.read(key_hash_len).decode("ASCII")
        aes_iv_len = int(fin.read(1)[0])
        aes_iv = fin.read(aes_iv_len)
        aes_tag_len = int(fin.read(1)[0])
        aes_tag = fin.read(aes_tag_len)
        data = fin.read()
        key = Context.instance.server_key(key_hash)     
        data = helpers.aes_decrypt(key, iv=aes_iv, tag=aes_tag, ciphertext=data)

        if record.key_hash != key_hash:
            record = record.clone()
            record.key_hash = key_hash

        return data


