
from json import dump, load

class Contacts:
    def __init__(self, contactfile):
        with open(contactfile, "rb") as f:
            self._contacts = load(f)

    def get_fingerprint(self, nick_or_fingerprint):
        for fingerprint, val in self._contacts.items():
            if fingerprint == nick_or_fingerprint:
                return bytes(fingerprint)
            elif val["nick"] == nick_or_fingerprint:
                return bytes(fingerprint)
