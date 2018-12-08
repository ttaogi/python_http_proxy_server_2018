#original url : https://null-byte.wonderhowto.com/how-to/sploit-make-proxy-server-python-0161232/
#maybe original code is for python2.
#I modified a little code for python3.
#+ https://fossjon.wordpress.com/2016/05/16/basic-https-tls-proxy-server-in-python/

import socket, sys
from threading import *
import re
import ssl
import subprocess
import socketserver

listening_port = 11000
max_conn = 1000
buffer_size = 8192
timeout = 20



def start():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(":::start - initialize socket.")
    except Exception as e:
        print(":::start - initialize error.")
        print(e)
        sys.exit(1)

    try:
        sa = socket.getaddrinfo("127.0.0.1", listening_port, socket.AF_INET, socket.SOCK_STREAM)[0]
        print(sa)
        print("sa[4] type", type(sa[4]), sa[4])
        print("sa[4][0] type", type(sa[4][0]), sa[4][0])
        s.bind(sa[4])
        print(":::start - bind socket.")
    except Exception as e:
        print(":::start - bind error.")
        print(e)
        sys.exit(1)

    try:
        s.listen(max_conn)
        print(":::start - listen.")
    except Exception as e:
        print(":::start - listen error.")
        print(e)
        sys.exit(1)

    while 1:
        try:
            try:
                conn, addr = s.accept()
            except Exception as e:
                if conn:
                    conn.close()
                print(e)
                continue
            
            try:
                data = conn.recv(buffer_size)
            except Exception as e:
                if conn:
                    conn.close()
                print(e)
                continue
            
            if not data:
                if conn:
                    conn.close()
                continue

            try:
                new_thread = Thread(target=conn_string, args=(conn, data, addr), daemon=True)
                new_thread.start()
            except Exception as e:
                if conn:
                    conn.close()
                print(e)
                continue
        except Exception as e:
            if s:
                s.close()
            print(":::start - terminate proxy server.")
            sys.exit(1)

    print(":::start - exit.")
    s.close()

def conn_string(conn, data, addr):
    str_data = ''
    first_line = ''
    url = ''
    http_pos = -1
    temp = ''
    port_pos = -1
    webserver_pos = -1
    webserver = ''
    port = 80

    if not data:
        print(":::conn_string - error-0")
        conn.close()
        return

    try:
        str_data = data.decode('utf-8')
        first_line = str_data.split('\n')[0]
        url = first_line.split(' ')[1]
        http_pos = url.find("://")
    except Exception as e:
        print(":::conn_string - error-1")
        print(e)
        return

    try:
        if(http_pos == -1):
                temp = url
        else:
            temp = url[(http_pos+3):]

        port_pos = temp.find(":")
        webserver_pos = temp.find("/")
        if(webserver_pos == -1):
            webserver_pos = len(temp)

        webserver = ""
        port = -1
    except Exception as e:
        print(":::conn_string - error-2")
        print(e)
        return

    try:
        if(port_pos == -1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos+1):])[:webserver_pos - port_pos-1])
            webserver = temp[:port_pos]
    except Exception as e:
        print(":::conn_string - error-3")
        print(e)
        return

    if(port == 443):
        try:
            proxy_server_HTTPS(webserver, port, conn, data, addr)
        except Exception as e:
            print(":::conn_string error-4")
            print(e)
            pass
    else:
        try:
            proxy_server(webserver, port, conn, data, addr)
        except Exception as e:
            print(":::conn_string error-5")
            print(e)
            pass

def proxy_server(webserver, port, conn, data, addr):
    print(":::proxy_server")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((webserver, port))
        s.send(data)

        while 1:
            reply = s.recv(buffer_size)
            if(len(reply) > 0):
                conn.send(reply)
            else:
                break

        s.close()
        conn.close()
    except Exception as e:
        print(":::proxy_server - error")
        print(e)
        if s:
            s.close()
        if conn:
            conn.close()
        sys.exit(1)
        
def proxy_server_HTTPS(webserver, port, conn, data, addr):
    addresses_flag = False
    print(":::proxy_server_HTTPS")
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        context.check_hostname = False

        web2addr = ""
        looks = subprocess.check_output(["nslookup", webserver])
        looks = looks.decode('euc-kr').split("\n")
        
        for look in looks:
            match = re.match("^address:[ ]+([^ ]+).*$", look.strip(), re.I)
            if(match):
                web2addr = match.group(1)

        for look in looks:
            if(addresses_flag):
                match = re.match(".*$", look.strip(), re.I)
                if(match):
                    web2addr = match.group(0)
                    break
            match = re.match("^addresses:[ ]+([^ ]+).*$", look.strip(), re.I)
            if(match):
                addresses_flag = True

        s = context.wrap_socket(socket.socket(socket.AF_INET))
        s.settimeout(timeout)
        s.connect((web2addr, port))

        s.send(data)
        print("msg\n", data.decode('utf-8'), "\n")

        resp = ""
        while 1:
            reply = s.recv(buffer_size)
            print("reply : ", reply, "\n")
            if(len(reply) > 0):
                conn.send(reply)
            else:
                break

        s.close()
        conn.close()
    except Exception as e:
        print(":::proxy_server_HTTPS -error")
        print(e)
        if s:
            s.close()
        if conn:
            conn.close()
        sys.exit(1)



try:
    listening_port = int(input(":::Enter listening port number : "))
except KeyboardInterrupt:
    print(":::User requested an interrupt.")
    sys.exit()

start()



