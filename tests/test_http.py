import pytest
import hks_pylib.http as http

@pytest.fixture
def url():
    return "www.google.com"

def test_read_http(url):
    http_request = http.HTTPWriter()
    http_request.set_http_request("GET", url, "HTTP/1.1")
    reader = http.HTTPReader()
    a = reader.read(http_request.generate())

def test_write_http():
    a = http.HTTPWriter()
    a.type = "RESPONSE"
    a.set_start_line(protocol_version="HTTP/1.1", status_code="200", status_text="OK")
    a.add_header("Agent", "LeuLeu")
    a.generate()