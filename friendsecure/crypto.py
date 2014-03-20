from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from os.path import exists


rng = Random.new().read


class Key(object):

    def __init__(self, key):
        self.key = key

    @property
    def fingerprint(self):
        """ Return cryptographic fingerprint (hash) for the given key. """
        public_key = self.key.publickey().exportKey('DER')
        return SHA256.new(public_key).hexdigest()

    @property
    def public_key_base64(self):
        return self.key.publickey().exportKey('DER').encode('base64')

    def sign(self, message):
        digest = SHA256.new(message).digest()
        return list(self.key.sign(digest, rng))

    def sign_message(self, message):
        return dict(
            key=self.public_key_base64,
            message=message,
            signature=self.sign(message))


def verify_message(message, key, signature, fingerprint=None):
    try:
        key = RSA.importKey(key.strip().decode('base64'))
    except Exception:
        return False
    else:
        if fingerprint is not None and fingerprint != Key(key).fingerprint:
            return False
        digest = SHA256.new(message).digest()
        return bool(key.verify(digest, signature))


def get_my_key(filename='key.pem', size=2048):
    if exists(filename):
        key = RSA.importKey(open(filename, 'rb').read())
    else:
        key = RSA.generate(size, rng)
        open(filename, 'wb').write(key.exportKey('PEM'))
    return Key(key)
