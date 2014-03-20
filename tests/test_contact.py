
import json
from friendsecure.contacts import Contacts

def test_basic(tmpdir):
    p = tmpdir.join("contact.json")
    with p.open("wb") as f:
        json.dump({'123': {'nick': 'andi'}}, f)
    contacts = Contacts(str(p))
    assert contacts.get_fingerprint("123") == "123"
    assert contacts.get_fingerprint("andi") == "123"
    assert contacts.get_fingerprint("lqkwje") is None
