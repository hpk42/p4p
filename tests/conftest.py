from pytest import fixture
from Crypto.PublicKey import RSA


keydata = """-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----"""


@fixture(scope='session')
def key():
    from friendsecure.crypto import Key
    return Key(RSA.importKey(keydata))
