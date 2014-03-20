
from webob import Request
from friendsecure.lookup_server import make_app
from simplejson import dumps


def test_post_invalid():
    app = make_app()
    req = Request.blank('http://localhost/12345678', method="POST")
    r = req.get_response(app)
    assert r.status_code == 400


def test_post_invalid_signature():
    app = make_app()
    req = Request.blank('http://localhost/12345678', method="POST")
    data = dict(key="123", message="456", signature="102938")
    req.body = dumps(data)
    r = req.get_response(app)
    assert r.status_code == 400


def test_post_mismatching_fingerprint(key):
    app = make_app()
    req = Request.blank('http://localhost/12345678', method="POST")
    message = '456'
    data = key.sign_message(message)
    req.body = dumps(data)
    r = req.get_response(app)
    assert r.status_code == 400


def test_post_and_get(key):
    app = make_app()
    url = 'http://localhost/%s' % key.fingerprint
    req = Request.blank(url, method="POST")
    message = '456'
    data = key.sign_message(message)
    req.body = dumps(data)
    r = req.get_response(app)
    assert r.status_code == 200

    req = Request.blank(url, method="GET")
    r = req.get_response(app)
    assert r.status_code == 200
    assert not r.json["error"]
    assert r.json["result"] == data
