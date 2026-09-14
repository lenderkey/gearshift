import builtins
import io as stdlib_io
import logging as logger
import os
import random
from dataclasses import dataclass


@dataclass
class EnsureResult:
    crypt_name: str
    decrypt_name: str
    created: bool
    cleanup: bool | None = None


class Gearshift:
    def __init__(self, filename: str, mode="r", encoding: str = None, context=None, remove_on_write: bool = True, **ad):
        from .context import GearshiftContext

        if filename.endswith(".gear"):
            filename = filename[:-5]

        self.filename = filename
        self.filename_gear = filename + ".gear"

        self.mode = mode
        self.encoding = encoding
        self.fio = None
        self.context = context or GearshiftContext.instance()
        self.key_hash = None
        self.remove_on_write = remove_on_write

        self.filename_tmp = None

        self._data = None
        self._position = None
        self._write_buffer = None

    def __enter__(self):
        match self.mode:
            case 'w' | 'wb':
                dir, base = os.path.split(self.filename_gear)
                base = f".{base}.{random.randint(0, 999999):06d}"
                self.filename_tmp = os.path.join(dir, base)
                self.fio = builtins.open(self.filename_tmp, "wb")
                self._write_buffer = bytearray()

                return self

            case 'r' | 'rb':
                try:
                    self.fio = builtins.open(self.filename_gear, "rb")
                except FileNotFoundError:
                    self.filename_gear = None
                    self.fio = builtins.open(self.filename, self.mode)

                return self

            case _:
                raise ValueError(f"Unsupported mode: {self.mode}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.filename_tmp and 'w' in self.mode and not exc_type:
            try:
                self.context.aes_encrypt_to_stream(
                    bytes(self._write_buffer),
                    fout=self.fio,
                    key_hash=self.key_hash,
                )
            except BaseException:
                self.fio.close()
                os.remove(self.filename_tmp)
                self.filename_tmp = None
                raise

        if self.fio:
            self.fio.close()

        if self.filename_tmp and 'w' in self.mode:
            if exc_type:
                os.remove(self.filename_tmp)
            else:
                os.rename(self.filename_tmp, self.filename_gear)

                if self.remove_on_write:
                    try:
                        os.remove(self.filename)
                    except IOError:
                        pass

            self.filename_tmp = None

    def write(self, data):
        if "w" not in self.mode:
            raise stdlib_io.UnsupportedOperation("not writable")

        if self.mode == "w":
            data = data.encode(self.encoding or "utf-8")

        self._write_buffer.extend(data)

    def read(self, /, size=None):
        if "r" not in self.mode:
            raise stdlib_io.UnsupportedOperation("not readable")

        if not self.filename_gear:
            return self.fio.read(size)

        if self._data is None:
            self._position = 0
            self._data = self.context.aes_decrypt_to_bytes(fin=self.fio)

            if self.mode == "r":
                self._data = self._data.decode(self.encoding or "utf-8")

        if size is None or size < 0:
            chunk = self._data[self._position :]
            self._position = len(self._data)
            return chunk

        chunk = self._data[self._position : self._position + size]
        self._position += size
        self._position = min(self._position, len(self._data))

        return chunk

    def flush(self):
        pass


def open(filename, mode="r", *av, **ad):
    return Gearshift(filename=filename, mode=mode, *av, **ad)


def strip(filename: str) -> str:
    if filename.endswith(".gear"):
        return filename[:-5]

    return filename


def exists(filename: str) -> bool:
    if filename.endswith(".gear"):
        return os.path.exists(filename)
    elif os.path.exists(filename):
        return True
    elif os.path.exists(filename + ".gear"):
        return True
    else:
        return False


def is_encrypted(filename: str) -> bool:
    return os.path.exists(strip(filename) + ".gear")


def is_unencrypted(filename: str) -> bool:
    stripname = strip(filename)
    return os.path.exists(stripname) and not os.path.exists(stripname + ".gear")


def remove(filename: str) -> None:
    stripname = strip(filename)
    was_removed = False

    if os.path.exists(stripname):
        os.remove(stripname)
        was_removed = True

    if os.path.exists(stripname + ".gear"):
        os.remove(stripname + ".gear")
        was_removed = True

    if not was_removed:
        raise FileNotFoundError(f"No such file: {filename}")


def ensure_crypt(
    filename: str,
    lazy: bool = True,  ## if True, will not overwrite existing files
    required: bool = True,  ## if True, will raise FileNotFoundError if file does not exist
    cleanup: bool = False,  ## if True, will remove the decrypted file after encryption
) -> EnsureResult:
    operation = "ensure_crypt"
    decrypt_name = filename
    if decrypt_name.endswith(".gear"):
        decrypt_name = decrypt_name[:-5]

    crypt_name = decrypt_name + ".gear"
    created = False
    crypt_ready = False
    cleanup_completed = False

    if os.path.exists(crypt_name) and lazy:
        crypt_ready = True
    elif not os.path.exists(decrypt_name):
        if required:
            raise FileNotFoundError(f"{operation}: No such file: {decrypt_name}")
    else:
        with builtins.open(decrypt_name, "rb") as fin:
            data = fin.read()
        with Gearshift(crypt_name, mode="wb", remove_on_write=False) as fout:
            fout.write(data)

        created = True
        crypt_ready = True
        logger.info(f"{operation}: created {crypt_name}")

    if cleanup and crypt_ready:
        if not os.path.exists(decrypt_name):
            cleanup_completed = True
        else:
            try:
                os.remove(decrypt_name)
                cleanup_completed = True
                logger.info(f"{operation}: removed {decrypt_name}")
            except OSError:
                logger.warning(f"{operation}: failed to remove {decrypt_name}")

    return EnsureResult(
        crypt_name=crypt_name,
        decrypt_name=decrypt_name,
        created=created,
        cleanup=cleanup_completed,
    )


def ensure_decrypt(
    filename: str,
    lazy: bool = True,  ## if True, will not overwrite existing files
    required: bool = True,  ## if True, will raise FileNotFoundError if file does not exist
) -> EnsureResult:
    operation = "ensure_decrypt"
    decrypt_name = filename
    if decrypt_name.endswith(".gear"):
        decrypt_name = decrypt_name[:-5]

    crypt_name = decrypt_name + ".gear"
    created = False

    if lazy and os.path.exists(decrypt_name):
        logger.info(f"{operation}: {decrypt_name} already exists - skipping decryption")
    elif not os.path.exists(crypt_name):
        if required:
            raise FileNotFoundError(f"{operation}: No such file: {crypt_name}")
    else:
        with Gearshift(crypt_name, mode="rb") as fin, builtins.open(decrypt_name, "wb") as fout:
            fout.write(fin.read())

        created = True
        logger.info(f"{operation}: created {decrypt_name}")

    return EnsureResult(
        crypt_name=crypt_name,
        decrypt_name=decrypt_name,
        created=created,
    )
