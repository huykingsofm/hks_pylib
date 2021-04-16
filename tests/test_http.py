import pytest
import hks_pylib.http as http


@pytest.fixture
def packet():
    return write_http()


def test_read_http(packet):
    reader = http.HTTPParser()
    reader.parse(packet)


def write_http():
    a = http.HTTPGenerator()
    a.type = http.HTTPType.RESPONSE
    a.set_start_line(protocol_version="HTTP/1.1", status_code="200", status_text="OK")
    a.add_header("Agent", "LeuLeu")
    return a.generate()
