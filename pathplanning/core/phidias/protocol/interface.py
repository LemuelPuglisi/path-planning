import json
import threading
import requests

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from io import BytesIO

""" Code extracted from RoboticSystem repository.
"""

class PhidiasHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    consumer = None
    port = 0

    def do_GET(self):
        self.send_response(500)
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        payload = json.loads(body.decode())
        response = process_incoming_request(
            PhidiasHTTPServer_RequestHandler.consumer, 
            self.client_address[0], 
            payload
        )
        body = json.dumps(response)
        response = BytesIO()
        response.write(body.encode())
        self.wfile.write(response.getvalue())

    def log_message(self, format, *args):
        pass


def send_belief_http(agent_name, destination, belief, terms, source):
    parsed_url = urlparse("//" + destination)
    if parsed_url.hostname is None:
        raise Exception()
    port = parsed_url.port
    if port is None: port = 6565
    payload = { 'from' : source,
                'net-port': PhidiasHTTPServer_RequestHandler.port,
                'to': agent_name,
                'data' : ['belief', [ belief, terms ] ] }

    json_payload = json.dumps(payload)
    new_url = "http://" + parsed_url.hostname + ":" + str(port)
    r = requests.post(new_url, data=json_payload)
    reply = json.loads(r.text)
    if reply['result'] != "ok":
        print("Messaging Error: ", reply)


def server_thread_http(consumer, port):
    server_address = ('', port)
    PhidiasHTTPServer_RequestHandler.port = port
    PhidiasHTTPServer_RequestHandler.consumer = consumer
    httpd = HTTPServer(server_address, PhidiasHTTPServer_RequestHandler)
    print("")
    print("\tPHIDIAS Messaging Server is running at port ", port)
    print("")
    print("")
    #print(httpd.socket)
    httpd.serve_forever()
    server_thread()


def server_thread(self):
    incoming_buffer = b''
    while True:
        new_data = self.sock.recv(64)
        if len(new_data) == 0:
            raise RuntimeError('Lost connection to gateway')
        incoming_buffer += new_data

        while True:
            nl_pos = incoming_buffer.find(b"\n")
            if nl_pos < 0:
                break  # no full message yet, keep on waiting

            response_payload = json.loads(incoming_buffer[:nl_pos])
            incoming_buffer = incoming_buffer[nl_pos + 1:]

            # Process the message
            with self.lock:
                if 'result' in response_payload:  # response to our past request
                    self.sent_requests_queue.pop(0).set_result(response_payload)
                else:  # incoming request
                    from_address = response_payload.pop('from-address')
                    response = process_incoming_request(self.engines, self._globals, from_address, response_payload)

                    json_response = json.dumps(response).encode('ascii') + b'\n'
                    self.sock.sendall(json_response)


def start_message_server_http(consumer, port = 6566):
    t = threading.Thread(target = server_thread_http, args = (consumer, port, ))
    t.daemon = True
    t.start()
    return t



def process_incoming_request(consumer, from_address, payload):
    response = { 'result' : 'err',
                'reason' : 'Malformed HTTP payload',
                'data'   : payload }
    if 'from' in payload.keys():
        if 'net-port' in payload.keys():
            if 'to' in payload.keys():
                if 'data' in payload.keys():
                    # format is valid
                    _from = payload['from']
                    _to = payload['to']
                    _data = payload['data']
                    _net_port = payload['net-port']
                    if _net_port == 0:
                        _from = _from + "@<unknown>"
                    else:
                        _from = _from + "@" + from_address + ":" + repr(_net_port)
                    if _to == 'robot':
                        if _data[0] == 'belief':
                            [ Name, Terms ] = _data[1]
                            consumer.on_belief(_from, Name, Terms)
                            response = { 'result' : 'ok' }
                        else:
                            response = { 'result' : 'err',
                                        'reason' : 'Invalid verb',
                                        'data'   : _data }
                    else:
                        response = { 'result' : 'err',
                                    'reason' : 'Destination agent not found',
                                    'data'   : _to }
    return response


class Messaging:

    @classmethod
    def parse_destination(cls, agent_name):
        at_pos = agent_name.find("@")
        if at_pos < 0:
            return (None, None)
        else:
            agent_local_name = agent_name[:at_pos]
            site_name = agent_name[at_pos + 1:]
            return (agent_local_name, site_name)

    @classmethod
    def send_belief(cls, destination, belief, terms, source):
        (agent_name, destination) = Messaging.parse_destination(destination)
        send_belief_http(agent_name, destination, belief, terms, source)

