from rest_encrypt import crypto


def test_encrypt_roundtrip():
    key = crypto.generate_key()
    secret = b"hello"
    enc = crypto.encrypt(key, secret)
    assert enc.startswith(crypto.HEADER)
    dec = crypto.decrypt(key, enc)
    assert dec == secret


def test_bad_header():
    key = crypto.generate_key()
    bogus = b"BAD" + crypto.encrypt(key, b"x")[len(crypto.HEADER) :]
    try:
        crypto.decrypt(key, bogus)
    except ValueError as e:
        assert "header" in str(e)
    else:
        assert False, "expected ValueError"
