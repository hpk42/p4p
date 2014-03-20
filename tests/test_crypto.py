from Crypto.PublicKey import RSA
from friendsecure import crypto


key = RSA.importKey("""-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCrKjAdC1PQ/JiR43TK4wd8Xq56vpXTB7LNU28lXeenOxiCMhLw
2c5NKX0zynOqAzt3fn74u1j6iJq5oLKaqxcdXGShGit4fkvNkKJyymNnTemFEfIB
hrCCUPrMRXk3n/OBax7bdM2mZL2LKgh1p5nllr5IXIAjZ+BFT4iqFsvKsQIDAQAB
AoGAeGM46gTAlBpF+T6BM/5QkpJJqD2KRZ6BjVcksqSEvaOcDl7H4a1gI/eNfzLi
/W4+kkJfbfTflX8lTHCRjqXNoAj/yQ7/aDlvJQIlx0PpRNQblPMX+PT3MaxezZ2S
j7iDwcW19anD3eUyl0BuTHGQwYI6ADJbMLzzaFnj3JIgBZECQQC3UCYcvCJqTrbm
Ke7d3MiRYavlLlI+kNAnD/c8+FapWgAulD/ZS411slV3lb5mS5+K5iJxp47YfG17
S3WgSXHVAkEA7wjiRjP812JTSfsrphnzikLroydw2jbc1eoLKdu21947GeYNxCoL
a8/D96DKWYIEeSfqC8WkOfj557tHKwOHbQJAabMIVtdQTNYYdjzFpB4zdEjKUjrU
Z4kezPdSy1AywDHKGxGWg1giODRdPbgVcmy2kOPEBp7kKgYNJuPK7mKLBQJBAKeV
Z+ZmLl7m3ZPhl1GFojwN/NxPG4yxqBQFWTxIgSFI+dCHfKFKBOXaLP8gaJ1mTTKP
7EPClgfa6YIwx419lOUCQQC3Phca8TFMCmf1izAq61iNlMBhuA6k4yZ+JXR3RYNb
iZKNrWEbc3I6xUWqpRul+mBeUjOwkc+9LLnqecgubO/3
-----END RSA PRIVATE KEY-----""")


def test_fingerprint():
    assert crypto.Key(key).fingerprint == '657cd81a6b106b4c1f3e82af2ce9c1a50d61d3fea9bb5d44d6c6796362b257aa'


def test_sign_message():
    data = crypto.sign_message('hello world', key)
    assert data['message'] == 'hello world'
    assert data['public_key'] == key.publickey().exportKey('DER')
    assert 'signature' in data


def test_verify_message():
    data = crypto.sign_message('hello world', key)
    assert crypto.verify_message(**data)


def test_verify_tampered_message():
    data = crypto.sign_message('hello world', key)
    data['message'] += '!'
    assert not crypto.verify_message(**data)


def test_verify_tampered_signature():
    data = crypto.sign_message('hello world', key)
    # signature is a tuple of longs and/or strings
    signature = list(data['signature'])
    signature[0] += 1
    data['signature'] = tuple(signature)
    assert not crypto.verify_message(**data)


def test_verify_bad_public_key():
    data = crypto.sign_message('hello world', key)
    data['public_key'] += '!'
    assert not crypto.verify_message(**data)
