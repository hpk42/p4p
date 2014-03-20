from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from os.path import exists


rng = Random.new().read


def fingerprint(key):
    """ Return cryptographic fingerprint (hash) for the given key. """
    public_key = key.publickey().exportKey('DER')
    return SHA256.new(public_key).hexdigest()


def sign_message(message, key):
    digest = SHA256.new(message).digest()
    signature = key.sign(digest, rng)
    public_key = key.publickey().exportKey('DER')
    return dict(message=message, public_key=public_key, signature=signature)


def verify_message(message, public_key, signature):
    try:
        key = RSA.importKey(public_key)
    except ValueError:
        return False
    else:
        digest = SHA256.new(message).digest()
        return bool(key.verify(digest, signature))


def get_my_key(filename='key.pem', size=2048):
    if exists(filename):
        key = RSA.importKey(open(filename, 'rb').read())
    else:
        key = RSA.generate(size, rng)
        open(filename, 'wb').write(key.exportKey('PEM'))
    return key
