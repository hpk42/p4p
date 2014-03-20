
from webob import Request
from friend_lookup_server import make_app
from simplejson import dumps, loads

def test_post_invalid():
    app = make_app()
    req = Request.blank('http://localhost/12345678', method="POST")
    data = {"hello": 42}
    r = req.get_response(app)
    assert r.status_code == 400

def test_post_and_get():
    app = make_app()
    req = Request.blank('http://localhost/12345678', method="POST")
    data = dict(key="123", message="456", signature="102938")
    req.body = dumps(data)
    r = req.get_response(app)
    assert r.status_code == 200

    req = Request.blank("http://localhost/12345678", method="GET")
    r = req.get_response(app)
    assert r.status_code == 200
    assert not r.json["error"]
    assert r.json["result"] == data
