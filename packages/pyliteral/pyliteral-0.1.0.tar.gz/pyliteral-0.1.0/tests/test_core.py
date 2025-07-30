from pyliteral import hello

def test_hello():
    assert hello("PyPI") == "Hello, PyPI!"
    assert hello() == "Hello, world!"
