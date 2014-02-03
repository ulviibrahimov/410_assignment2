'''
    Copyright (C) Ulvi Ibrahimov, Abram Hindle Winter 2014 CMPUT 410 University of Alberta

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 '''

import sys
import socket
import re
from urlparse import urlparse
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return s
    
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
    
    def getPath(self,url):
        o=urlparse(url)
        return o.path
    
    def getPort(self,url):
        o=urlparse(url)
        return o.port 
    
    def getHost(self,url):
        o=urlparse(url)
        return o.netloc.split(':')[0]
    
    def getGetRequest (self,filePath, host):
        get="GET "+ filePath+ " HTTP/1.1\r\n"
        get=get+"Host: "+host+"\r\n"
        get=get+"Connection: close\r\n"
        get=get+"Accept: */*\r\n\r\n"   
        return get
    
    def getPostRequest (self, filePath,host, args):
        post= "POST "+ filePath+ " HTTP/1.1\r\n"
        post=post+"Host: 127.0.0.1\r\n"
        post=post+"Connection: close\r\n"
        post=post+"Accept: */*\r\n" 
        post= post + "Content-Type: application/x-www-form-urlencoded\r\n"
        if type(args) is dict:
            newArgs=urllib.urlencode(args)    
        else:
            newArgs=""
        post=post+"Content-length: "+str(len(newArgs)) 
        post=post+"\r\n\r\n"
        post=post+newArgs
        return post
        
    def getBody(self,data):
        l=data.split("\r\n\r\n")
        return l[1]
    
    def getCode(self, data):
        l=data.split(" ")
        return int (l[1])
    
    def GET(self, url, args=None):
        filePath=self.getPath(url)
        socketPort=self.getPort(url)
        if(socketPort==None):
            socketPort=80
        host=self.getHost(url)
        request= self.getGetRequest(filePath,host)
        getSocket=self.connect(host,socketPort)
        getSocket.send(request)
        responseData=self.recvall(getSocket)
        code=self.getCode(responseData) 
        if (code==404):
            body=''
        else:
            body=self.getBody(responseData)
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        filePath=self.getPath(url)
        socketPort=self.getPort(url)     
        host=self.getHost(url)
        request= self.getPostRequest(filePath,host,args)
        postSocket=self.connect(host,socketPort)
        postSocket.send(request)
        responseData=self.recvall(postSocket)
        postSocket.close()
        code=self.getCode(responseData) 
        if (code==404):
            body=''
        else:
            body=self.getBody(responseData)        
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
        print client.command( sys.argv[2], sys.argv[1] ).body
    else:
        print client.command(sys.argv[1], command)    