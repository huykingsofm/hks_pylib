import pytest
import hks_pylib.http as http


@pytest.fixture
def packet():
    return write_http()


def test_read_http(packet):
    packet = http.HTTPParser.parse(packet)
    print(packet)
    print(packet.to_byte())


def write_http():
    a = http.HTTPPacket()
    a.type(http.HTTPType.RESPONSE)
    a[http.HTTPRESPONSE.PROTOCOL_VERSION] =  "HTTP/1.1"
    a[http.HTTPRESPONSE.STATUS_CODE] = "200"
    a[http.HTTPRESPONSE.STATUS_TEXT] = "OK"
    a.update_header("Agent", "LeuLeu")
    a.body("huy thong minh nhat ne")
    return a.to_byte()
