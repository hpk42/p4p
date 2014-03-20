
import sys
import argparse
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
        '-H', '--host', default='127.0.0.1', type=str,
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
        self._pubkeyid_to_addresses = {}

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            meth = getattr(self, req.method, None)
            if meth is None:
                raise exc.HTTPMethodNotAllowed(
                    "method %r not allowed" % req.method)
                    #allowed='POST')
            resp = meth(req)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        return resp(environ, start_response)

    def POST(self, req):
        # XXX verify signature
        json = loads(req.body)
        pubkeyid = req.path.split("/")[-1]
        self._pubkeyid_to_addresses[pubkeyid] = json
        return Response(status=200)

    def GET(self, req):
        # XXX also transport back signature
        pubkeyid = req.path.split("/")[-1]
        addresses = self._pubkeyid_to_addresses[pubkeyid]
        resp = Response(
            content_type='application/json',
            body=dumps(dict(result=addresses, error=None)))
        return resp

if __name__ == '__main__':
    main()
