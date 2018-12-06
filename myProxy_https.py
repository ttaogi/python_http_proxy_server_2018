
import re
import socket
import ssl
import subprocess
import socketserver

resolv = {}
PORT_NUM = 11000

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global resolv
        isHttp = False
        
        #heads = self.request.recv(10024).strip().split("\n")
        heads = self.request.recv(10024).decode('utf-8').strip().split("\n")
        
        page = ""; host = ""
        for head in heads:
            #print("head", head)
            match = re.match("^get ([^ ]+).*$", head.strip(), re.I)
            if (match):
                #print("match get", match)
                page = match.group(1)
            else:
                match = re.match("^connect ([^ ]+).*$", head.strip(), re.I)
                if(match):
                    #print("match connect", match)
                    print("type : ", type(match))
                    page = match.group(1)
            match = re.match("^host: ([^ ]+).*$", head.strip(), re.I)
            if (match):
                #print("match host", match)
                host = match.group(1)


        if ((not page) or (not host)):
            print("err", heads)
            print(":1:", page, "::", host)
        else:
            print("msg", heads)
            print(":2:", page, "::", host)
            print(":host-4:", host[:len(host)-4])
            addr = ""
            if (host in resolv.keys()):
                addr = resolv[host]
            else:
                print("check looks\n\n")
                looks = subprocess.check_output(["nslookup", host[:len(host)-4]])#.split("\n")
                print("looks 1", looks)
                looks = looks.decode('utf-8').split("\n")
                print("looks 2", looks)
                for look in looks:
                    match = re.match("^address:[ ]+([^ ]+).*$", look.strip(), re.I)
                    if (match):
                        addr = match.group(1)
                print("addf : ", addr)
                resolv[host] = addr
            
            print(page,host,addr)
            
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.verify_mode = ssl.CERT_NONE
            context.check_hostname = False
            print("check point 1")
            conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=addr)
            print("check point 2")
            conn.connect((addr, 443))
            print("check point 3")
            conn.sendall(("GET "+page+" HTTP/1.1\r\n"+"Host: "+host+"\r\n"+"Connection: close\r\n"+"\r\n").encode('utf-8'))
            print("check point 4")
            resp = "";
            while (1):
                temp = (conn.recv(10024)).decode('utf-8')
                print(":", len(temp))
                print(temp)
                if (not temp):
                    break
                resp += temp
            print("check point 5")
            print(resp)
            self.request.sendall(resp.encode('utf-8'))

if (__name__ == "__main__"):
    (HOST, PORT) = ("127.0.0.1", PORT_NUM)
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
