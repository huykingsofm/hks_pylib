class HTTPReader(object):
    def __init__(self):
        self.__type = None
        self.__start_line = {}
        self.__header = {}
        self.__body = None

    def read(self, packet: bytes):
        assert isinstance(packet, (bytes, bytearray))

        header, self.__body = packet.split(b"\r\n\r\n")
        header = header.split(b"\r\n")

        tmp_start_line = header[0].split(b" ")
        if b"HTTP/" in tmp_start_line[0]:  # If protocol version is in first element of start line
            self.__type = "RESPONSE"
            self.__start_line["protocol_version"] = tmp_start_line[0].decode()
            self.__start_line["status_code"] = tmp_start_line[1].decode()
            self.__start_line["status_text"] = tmp_start_line[2].decode()
        else:
            self.__type = "REQUEST"
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


class HTTPWriter(object):
    def __init__(self):
        self.__type = None
        self.__start_line = {}

        self.__header = {}
        self.__body = b""

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value: str):
        assert value in ("REQUEST", "RESPONSE")
        self.__type = value

    def set_http_request(self, http_method, request_target, protocol_version):
        self.type = "REQUEST"
        self.set_start_line(
            http_method=http_method,
            request_target=request_target,
            protocol_version=protocol_version
        )

    def set_http_response(self, protocol_version, status_code, status_text):
        self.type = "RESPONSE"
        self.set_start_line(
            protocol_version=protocol_version,
            status_code=status_code,
            status_text=status_text
        )

    def set_start_line(self, **kwargs):
        if self.__type is None:
            raise Exception("type of http writer hasn't been set yet")

        if self.__type == "REQUEST":
            assert isinstance(kwargs["http_method"], str)
            assert isinstance(kwargs["request_target"], str)
            assert isinstance(kwargs["protocol_version"], str)
            self.__start_line.update({
                "http_method": kwargs["http_method"],
                "request_target": kwargs["request_target"],
                "protocol_version": kwargs["protocol_version"]
            })
        else:
            assert isinstance(kwargs["protocol_version"], str)
            assert isinstance(kwargs["status_code"], str)
            assert isinstance(kwargs["status_text"], str)
            self.__start_line.update({
                "protocol_version": kwargs["protocol_version"],
                "status_code": kwargs["status_code"],
                "status_text": kwargs["status_text"]
            })

    def add_header(self, key, value):
        assert isinstance(key, str)
        assert isinstance(value, str)
        self.__header.update({key: value})

    def del_header(self, key):
        return self.__header.pop(key, None)

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, value: bytes):
        assert isinstance(value, bytes)
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
