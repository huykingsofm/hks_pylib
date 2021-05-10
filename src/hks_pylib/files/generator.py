import io as IO
from typing import Union

from hkserror import HTypeError
from hks_pylib.errors.files import FilesError


ReadableIO = Union[str, IO.BufferedIOBase, bytes, bytearray]


class BytesGenerator(object):
    def __init__(self, io: ReadableIO):
        self._io = io

        self._stream = None

        if isinstance(io, str):
            self._stream = open(io, "rb")
            self._beigin_position = self._stream.tell()

        if isinstance(io, (bytes, bytearray)):
            self._stream = io.copy()
            self._index = 0
            if isinstance(io, bytes):
                self._stream = bytearray(self._stream)

        if isinstance(io, IO.BufferedIOBase):
            self._stream = io
            self._beigin_position = self._stream.tell()

        if self._stream is None:
            raise HTypeError("io", io, ReadableIO)

    def head(self):
        return b""

    def tail(self):
        return b""

    def read(self, buffer_size: int = 1024):
        if isinstance(self._stream, IO.BufferedIOBase):
            return self._stream.read(buffer_size)

        elif isinstance(self._stream, bytearray):
            value = self._stream[self._index : buffer_size]
            self._index += buffer_size
            return value

        else:
            raise FilesError("Invalid stream type. "
            "Expected an bytearray or "
            "IOBase, but got {}.".format(type(self._stream)))

    def close(self):
        if isinstance(self._stream, IO.BufferedIOBase):
            self._stream.close()
            del self._stream

        elif isinstance(self._stream, bytearray):
            del self._stream
            self._index = 0

        else:
            raise FilesError("Invalid stream type. "
            "Expected an bytearray or "
            "IOBase, but got {}.".format(type(self._stream)))

    def iter(self, buffer_size: int = 1024):
        while True:
            data = self.read(buffer_size)

            if not data:
                break

            yield data

    def reset(self):
        if isinstance(self._stream, IO.BufferedIOBase):
            self._stream.seek(self._beigin_position)

        elif isinstance(self._stream, bytearray):
            self._index = 0

        else:
            raise FilesError("Invalid stream type. "
            "Expected an bytearray or "
            "IOBase, but got {}.".format(type(self._stream)))


class BMPImageGenerator(BytesGenerator):
    def __init__(self, path):
        with open(path, "rb") as stream:
            header = stream.read(14)
            if header[0:2] != b"BM":
                raise Exception("This is not BMP file")
            start_of_img = int.from_bytes(header[-4:], "little")

        stream = open(path, "rb")

        self._header = stream.read(start_of_img)

        super().__init__(stream)

    def head(self):
        return self._header
