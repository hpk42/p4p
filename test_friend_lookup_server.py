
from webob import Request
from friend_lookup_server import make_app
from simplejson import dumps, loads

def test_post_and_get():
    req = Request.blank('http://localhost/12345678', method="POST")
    app = make_app()
    data = {"hello": 42}
    req.body = dumps(data)
    r = req.get_response(app)
    assert r.status_code == 200
    req = Request.blank("http://localhost/12345678", method="GET")
    r = req.get_response(app)
    assert r.status_code == 200
    assert not r.json["error"]
    assert r.json["result"] == data
