from hks_pylib.hksenum import HKSEnum

from hkserror import HTypeError
from hks_pylib.errors.http import HTTPTypeError


class HTTPType(HKSEnum):
    RESPONSE = "Response"
    REQUEST = "Request"


class HTTPREQUEST(HKSEnum):
    HTTP_METHOD = "http_method"
    REQUEST_TARGET = "request_target"
    PROTOCOL_VERSION = "protocol_version"


class HTTPRESPONSE(HKSEnum):
    PROTOCOL_VERSION = "protocol_version"
    STATUS_CODE = "status_code"
    STATUS_TEXT = "status_text"


class HTTPPacket(object):
    def __init__(self) -> None:
        self.__type = None
        self.__start_line = {}
        self.__header = {}
        self.__body = ""

    def type(self, type: HTTPType = None):
        if type == None:
            return self.__type

        if not isinstance(type, HTTPType):
            raise HTypeError("type", type, HTTPType, None)

        if type is HTTPType.RESPONSE:
            self.__type = HTTPRESPONSE
        else:
            self.__type = HTTPREQUEST
    
        self.__start_line = {}

    def __setitem__(self, index: HKSEnum, value: str):
        if self.__type is None:
            raise HTTPTypeError("HTTPType must be set before configuring.")

        if not isinstance(value, str):
            raise HTypeError("value", value, str)

        if not isinstance(index, self.__type):
            raise HTypeError("index", index, self.__type)

        self.__start_line[index] = value

    def header(self):
        return self.__header

    def reset_header(self):
        self.__header = {}

    def update_header(self, key: str, value: str):
        if not isinstance(key, str):
            raise HTypeError("key", key, str)
        
        if not isinstance(value, str):
            raise HTypeError("value", value, str)

        self.__header.update({key: value})

    def start_line(self):
        return self.__start_line

    def body(self, body: str = None):
        if body is None:
            return self.__body

        if not isinstance(body, str):
            raise HTypeError("body", body, str, None)

        self.__body = body

    def update_body(self, body: str):
        if not isinstance(body, str):
            raise HTypeError("body", body, str)

        self.__body += body

    def to_byte(self):
        start_line = " ".join([self.__start_line[key] for key in self.__type])

        packet = start_line + "\r\n"

        for key, value in self.__header.items():
            packet += "{}: {}".format(key, value)
            packet += "\r\n"

        packet += "\r\n"
        packet += self.__body
        return packet.encode()

    def __str__(self):
        return "{}\n{}\n{}".format(self.__start_line, self.__header, self.__body)


class HTTPParser(object):
    @staticmethod
    def parse(packet: bytes):
        if not isinstance(packet, (bytes, bytearray)):
            raise HTypeError("packet", packet, bytes, bytearray)

        http_packet = HTTPPacket()

        header, body = packet.split(b"\r\n\r\n")
        header = header.split(b"\r\n")

        tmp_start_line = header[0].split(b" ")
        if b"HTTP/" in tmp_start_line[0]:  # If protocol version is in first element of start line
            http_packet.type(HTTPType.RESPONSE)
            http_packet[HTTPRESPONSE.PROTOCOL_VERSION] = tmp_start_line[0].decode()
            http_packet[HTTPRESPONSE.STATUS_CODE] = tmp_start_line[1].decode()
            http_packet[HTTPRESPONSE.STATUS_TEXT] = tmp_start_line[2].decode()
        else:
            http_packet.type(HTTPType.REQUEST)
            http_packet[HTTPREQUEST.HTTP_METHOD] = tmp_start_line[0].decode()
            http_packet[HTTPREQUEST.REQUEST_TARGET] = tmp_start_line[1].decode()
            http_packet[HTTPREQUEST.PROTOCOL_VERSION] = tmp_start_line[2].decode()

        for field in header[1:]:
            key, value = field.split(b": ")
            http_packet.update_header(key.decode(), value.decode())

        http_packet.body(body.decode())

        return http_packet
