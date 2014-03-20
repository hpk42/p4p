"""
web storage for posting and getting data for a given pubkeyid.

The following requests are handled:

    POST /PUBKEYID (content-type=application-json)
        {"key": FULL_PUBLIC_KEY,  # must match pubkeyid,
         "message": json_blob,
         "signature": signature for data blob,
        }

    GET /PUBKEYID (reply will have content-type=application-json)
        same content as previously posted

A client will typically do the following to POST new information:

    data = # some data structure
    message = json.dumps(data)
    signature = sign_data(message, key)
    POST(URL + pubkeyid, data=json.dumps(
        {"key": full_pubkey,
         "message": message,
         "signature": signature
        }
    )

and it will do the following to GET and verify information:

    r = GET(URL + pubkeyid)
    json = r.json()
    message = json["message"]
    key = json["key"]
    verify_pubkeyid_belongs_to_pubkey(pubkeyid, key)
    verify_signature(message, signature, key)
    data = # the data structure posted above.

"""
import sys
import argparse
import logging
from simplejson import loads, dumps
from webob import Request, Response, exc

def main(args=None):
    from wsgiref import simple_server
    parser = argparse.ArgumentParser(
        usage="%prog [OPTIONS]")
    parser.add_argument(
        '-p', '--port', default='8080', type=int,
        help='Port to serve on (default 8080)')
    parser.add_argument(
        '-H', '--host', default='0.0.0.0', type=str,
        help='Host to serve on (default localhost; 0.0.0.0 to make public)')
    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args()
    app = make_app()
    server = simple_server.make_server(args.host, args.port, app)
    print ('Serving on http://%s:%s' % (args.host, args.port))
    server.serve_forever()

def make_app():
    return JsonRpcApp()


class JsonRpcApp(object):
    def __init__(self):
        self._pubkeyid2data = {}

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            meth = getattr(self, req.method, None)
            if meth is None:
                raise exc.HTTPMethodNotAllowed(
                    "method %r not allowed" % req.method)
                    #allowed='POST')
            pubkeyid = req.path.split("/")[-1]
            resp = meth(req, pubkeyid)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        return resp(environ, start_response)

    def POST(self, req, pubkeyid):
        # XXX verify signature
        json = loads(req.body)
        self.verify_signed_json_presence(pubkeyid, json)
        logging.warn("registering %s" %(json,))
        self._pubkeyid2data[pubkeyid] = json
        return Response(status=200)

    def GET(self, req, pubkeyid):
        # XXX also transport back signature
        data = self._pubkeyid2data[pubkeyid]
        resp = Response(
            content_type='application/json',
            body=dumps(dict(result=data, error=None)))
        return resp

    _JSON_KEYS = set(("key", "message", "signature"))

    def verify_signed_json_presence(self, pubkeyid, json):
        if not set(json.keys()) == self._JSON_KEYS:
            raise exc.HTTPBadRequest(
                "json must have these keys: %s" %(self._JSON_KEYS))
        pubkey = json["key"]
        message = json["message"]
        signature = json["signature"]
        #verify_data_integrity(pubkeyid, pubkey, data, signature)
        #verify that pubkeyid fits to pubkey and that signature is a valid
        #signature for data
