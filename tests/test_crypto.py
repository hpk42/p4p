from friendsecure import crypto


def test_fingerprint(key):
    assert key.fingerprint == '657cd81a6b106b4c1f3e82af2ce9c1a50d61d3fea9bb5d44d6c6796362b257aa'


def test_sign_message(key):
    data = key.sign_message('hello world')
    assert data['message'] == 'hello world'
    assert data['key'] == key.key.publickey().exportKey('DER').encode('base64')
    assert 'signature' in data


def test_verify_message(key):
    data = key.sign_message('hello world')
    assert crypto.verify_message(**data)


def test_verify_tampered_message(key):
    data = key.sign_message('hello world')
    data['message'] += '!'
    assert not crypto.verify_message(**data)


def test_verify_tampered_signature(key):
    data = key.sign_message('hello world')
    # signature is a tuple of longs and/or strings
    signature = list(data['signature'])
    signature[0] += 1
    data['signature'] = tuple(signature)
    assert not crypto.verify_message(**data)


def test_verify_bad_public_key(key):
    data = key.sign_message('hello world')
    data['key'] += 'abba'
    assert not crypto.verify_message(**data)
