#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        #reference http://stackoverflow.com/questions/9530950/parsing-hostname-and-port-from-string-or-url
        parsex = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*?(?P<path>[^?#]*)'
        match = re.search(parsex, url)
        self.host = match.group('host')
        self.port = int(match.group('port'))
        self.path = match.group('path')
        if not self.port:
            self.port = 80

    def connect(self, url):
        # create an INET, STREAMing socket
        self.get_host_port(url)
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((self.host, self.port))
        return soc

    def make_headers(self, method, path, data=None):
        header = "%s %s HTTP/1.1\r\n" %(method, path) \
                 +"Host: %s\r\n" %(self.host) \
                 +"Connection: Keep-Alive\r\n\n"
        #extra header lines for POST
        if data:
            content = urllib.urlencode(data)
            header += "Content-Length: %d\r\n" %(len(content)) \
                      +"\r\n" + content + "\r\n"
        return header

    def get_code(self, data):
        return int(data.split(' ')[1])

    def get_body(self, data):
        return data.split("\r\n",1)[1]
  

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""
        connection = self.connect(url)
        req = self.make_headers('GET', self.path)
        print(req, "\n\n\n")
        connection.sendall(req)

        response = self.recvall(connection)
        code = self.get_code(response)
        body = self.get_body(response)

        connection.close()
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        connection = self.connect(url)
        req = self.make_headers('POST', self.path)

        connection.sendall(req)
        response = self.recvall(connection)
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
