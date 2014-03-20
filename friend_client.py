
import sys
import argparse
import subprocess
import requests
import threading
import webob
import logging
from simplejson import loads, dumps
from webob import Request, Response, exc

class LookupService:
    def __init__(self, url):
        self.url = url

    def announce_presence(self, myid, url):
        print ("announcing myself as %s on %s to %s" % (myid, url, self.url))
        data = {"key": "123",
                "message": dumps({"url": url}),
                "signature": "123"}
        r = requests.post(self.url + "/" + myid,
                          data=dumps(data),
                          headers={"CONTENT-TYPE": "application/json"})
        assert r.status_code == 200

    def get_other_address(self, id):
        r = requests.get(self.url + "/" + id)
        assert r.status_code == 200
        result = r.json()["result"]
        addresses = loads(result["message"])
        return addresses["url"]

def main(args=None):
    from wsgiref import simple_server
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--lookup', default='http://teta.local:8080',
        help='lookup service url')
    parser.add_argument(
        '-p', '--port', default=8090, type=int,
        help='the port i am listening on for communication')
    parser.add_argument("myid", help="id to connect as")
    parser.add_argument("otherid", help="id to connect to", default=None, nargs="?")
    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args()
    my_hostname = subprocess.check_output("hostname").strip()
    if not my_hostname.endswith(".local"):
        my_hostname += ".local"
    my_url = "http://%s:%s"% (my_hostname, args.port)
    lookup = LookupService(args.lookup)
    uithread = InputThread(args.myid, lookup)
    uithread.setDaemon(True)
    if args.otherid is not None:
        uithread.add_id(args.otherid)
    uithread.start()
    app = ReceiveApp(uithread)
    server = simple_server.make_server(my_hostname, args.port, app)
    print ('Serving on http://%s:%s' % (my_hostname, args.port))
    lookup.announce_presence(args.myid, my_url)
    server.serve_forever()

class InputThread(threading.Thread):
    def __init__(self, myid, lookup):
        super(InputThread, self).__init__()
        self.myid = myid
        self.lookup = lookup
        self.id2address = {}

    def add_id(self, otherid):
        if otherid not in self.id2address:
            logging.info("looking up ip of %s" % otherid)
            address = self.lookup.get_other_address(otherid)
            if not address:
                logging.warn("could not get address for %s" % args.otherid)
            else:
                self.id2address[otherid] = address

    def run(self):
        while 1:
            line = raw_input() # self.myid + " -> ")
            if line:
                self.send_line(line)

    def send_line(self, line):
        if not self.id2address:
            logging.info("not connected to anybody")
            return

        for otherid,address in self.id2address.copy().items():
            data = {"myid": self.myid, "line": line}
            r = requests.post(address, dumps(data),
                              headers={"CONTENT-TYPE": "application/json"})
            if r.status_code != 200:
                logging.error("ERROR %r SENDING line TO %s, removing node" % (r.status_code, address))
                del self.id2address[otherid]


class ReceiveApp(object):
    def __init__(self, uithread):
        self.uithread = uithread

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
        myid = json["myid"]
        line = json["line"]
        self.uithread.add_id(myid)
        print "[%s] %s" %(myid, line)
        #self.verify_signed_json_presence(pubkeyid, json)
        return Response(status=200)
