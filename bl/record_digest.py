from Context import Context
from structures import FileRecord
import helpers

def record_digest(record:FileRecord) -> bytes:
    """
    Return the data for a record. Don't think about the naming too much.
    """
    with open(record.linkpath, "rb") as fin:
        aes_iv_len = int(fin.read(1)[0])
        aes_iv = fin.read(aes_iv_len)
        aes_tag_len = int(fin.read(1)[0])
        aes_tag = fin.read(aes_tag_len)
        data = fin.read()
        key = Context.instance.server_key(record.key_hash)     
        data = helpers.aes_decrypt(key, iv=aes_iv, tag=aes_tag, ciphertext=data)

        return data


