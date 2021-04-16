from hks_pylib.hksenum import HKSEnum
from hks_pylib.errors import InvalidHTTPKeyFieldError, InvalidParameterError, UnknownHTTPTypeError


class HTTPType(HKSEnum):
    RESPONSE = "Response"
    REQUEST = "Request"
    NONE = None


class HTTPParser(object):
    def __init__(self):
        self.__type = HTTPType.NONE
        self.__start_line = {}
        self.__header = {}
        self.__body = None

    def parse(self, packet: bytes):
        if not isinstance(packet, (bytes, bytearray)):
            raise InvalidParameterError("Parameter packet must be a bytes or bytearray object.")

        header, self.__body = packet.split(b"\r\n\r\n")
        header = header.split(b"\r\n")

        tmp_start_line = header[0].split(b" ")
        if b"HTTP/" in tmp_start_line[0]:  # If protocol version is in first element of start line
            self.__type = HTTPType.RESPONSE
            self.__start_line["protocol_version"] = tmp_start_line[0].decode()
            self.__start_line["status_code"] = tmp_start_line[1].decode()
            self.__start_line["status_text"] = tmp_start_line[2].decode()
        else:
            self.__type = HTTPType.REQUEST
            self.__start_line["http_method"] = tmp_start_line[0].decode()
            self.__start_line["request_target"] = tmp_start_line[1].decode()
            self.__start_line["protocol_version"] = tmp_start_line[2].decode()

        for field in header[1:]:
            key, value = field.split(b": ")
            self.__header.update({key.decode(): value.decode()})

        return self.__type

    @property
    def type(self):
        return self.__type

    @property
    def header(self):
        return self.__header

    @property
    def start_line(self):
        return self.__start_line

    @property
    def body(self):
        return self.__body


class HTTPGenerator(object):
    def __init__(self):
        self.__type = HTTPType.NONE
        self.__start_line = {}

        self.__header = {}
        self.__body = b""

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value: str):
        if value not in (HTTPType.RESPONSE, HTTPType.REQUEST):
            raise InvalidParameterError("Type is only the HTTPType.RESPONSE or HTTPType.REQUEST.")

        self.__type = value

    def set_http_request(self, http_method, request_target, protocol_version):
        self.type = HTTPType.REQUEST
        self.set_start_line(
            http_method=http_method,
            request_target=request_target,
            protocol_version=protocol_version
        )

    def set_http_response(self, protocol_version, status_code, status_text):
        self.type = HTTPType.RESPONSE
        self.set_start_line(
            protocol_version=protocol_version,
            status_code=status_code,
            status_text=status_text
        )

    def set_start_line(self, **kwargs):
        if self.__type is HTTPType.NONE:
            raise UnknownHTTPTypeError("Please set the http type before calling set_start_line().")

        if self.__type is HTTPType.REQUEST:
            http_method = kwargs.pop("http_method", None)
            request_target = kwargs.pop("request_target", None)
            protocol_version = kwargs.pop("protocol_version", None)
            
            if http_method is None or not isinstance(http_method, str):
                raise InvalidParameterError("Parameter http_method must passed as be a str.")

            if request_target is None or not isinstance(request_target, str):
                raise InvalidParameterError("Parameter request_target must passed as be a str.")

            if protocol_version is None or not isinstance(protocol_version, str):
                raise InvalidParameterError("Parameter protocol_version must be passed as a str.")

            if kwargs:
                raise InvalidParameterError("Unknown parameters {}.".format(kwargs.keys()))

            self.__start_line.update({
                "http_method": http_method,
                "request_target": request_target,
                "protocol_version": protocol_version
            })

        elif self.__type is HTTPType.RESPONSE:
            protocol_version = kwargs.pop("protocol_version", None)
            status_code = kwargs.pop("status_code", None)
            status_text = kwargs.pop("status_text", None)
            
            if protocol_version is None or not isinstance(protocol_version, str):
                raise InvalidParameterError("Parameter protocol_version must be passed as a str.")

            if status_code is None or not isinstance(status_code, str):
                raise InvalidParameterError("Parameter status_code must passed as be a str.")

            if status_text is None or not isinstance(status_text, str):
                raise InvalidParameterError("Parameter status_text must passed as be a str.")

            if kwargs:
                raise InvalidParameterError("Unknown parameters {}.".format(kwargs.keys()))

            self.__start_line.update({
                "protocol_version": protocol_version,
                "status_code": status_code,
                "status_text": status_text
            })

        else:
            raise UnknownHTTPTypeError("Unknown type ({}).".format(self.__type.name))

    def add_header(self, key: str, value: str):
        if not isinstance(key, str):
            raise InvalidParameterError("Parameter key must be a str.")

        if not isinstance(value, str):
            raise InvalidParameterError("Parameter value must be a str.")

        self.__header.update({key: value})

    def del_header(self, key):
        if key not in self.__header.keys():
            raise InvalidHTTPKeyFieldError("Key {} doesn't exist.".format(key))

        return self.__header.pop(key, None)

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, value: bytes):
        if not isinstance(value, bytes):
            raise InvalidParameterError("Parameter value must be a bytes object.")

        self.__body = value

    def generate(self):
        packet = ""
        packet += " ".join(self.__start_line.values()) + "\r\n"
        for field in self.__header.items():
            packet += field[0] + ": " + field[1]
            packet += "\r\n"
        packet += "\r\n"
        packet = packet.encode()
        packet += self.__body
        return packet
