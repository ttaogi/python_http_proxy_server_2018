#original url : https://null-byte.wonderhowto.com/how-to/sploit-make-proxy-server-python-0161232/
#maybe original code is for python2.
#I modified a little code for python3.

import socket, sys
#from thread import *
from threading import *

listening_port = 4000
max_conn = 5
buffer_size = 4096

##########
##########
##########

def start():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(":::initialize socket.")
    except Exception as e:
        print(":::initialize error.")
        print(e)
        sys.exit(1)

    try:
        sa = socket.getaddrinfo("127.0.0.1", 4000, socket.AF_INET, socket.SOCK_STREAM)[0]
        print(sa)
        #s.bind(('', listening_port))
        #s.bind((socket.gethostname, listening_port))
        s.bind(sa[4])
        print(":::bind socket.")
    except Exception as e:
        print(":::bind error.")
        print(e)
        sys.exit(1)

    try:
        s.listen(max_conn)
        print(":::start server.")
    except Exception as e:
        print(":::listen error.")
        print(":::listening port num : %d."%(listening_port))
        print(e)
        sys.exit(1)

    while 1:
        try:
            conn, addr = s.accept()
            data = conn.recv(buffer_size)
            #start_new_thread(conn_string, (conn, data, addr))
            new_thread = Thread(target=conn_string, args=(conn, data, addr))
            new_thread.start()
        except KeyboardInterrupt as e:
            s.close()
            print(":::Terminate proxy server.")
            sys.exit(1)

    s.close()

def conn_string(conn, data, addr):
    print(":::call conn_string")
    webserver = ''
    port = 80

    try:
        str_data = data.decode('utf-8')
        first_line = str_data.split('\n')[0]
        print("first line:")
        print(first_line)
        url = first_line.split(' ')[1]
        print("url:")
        print(url)
        http_pos = url.find("://")

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

        if(port_pos == -1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos+1):])[:webserver_pos - port_pos-1])
            webserver = temp[:port_pos]
        print("port:")
        print(port)
        print("webserver:")
        print(webserver)
    except Exception as e:
        print(":::conn_string error-1")
        print(e)
        return

    try:
        proxy_server(webserver, port, conn, data, addr)
    except Exception as e:
        print(":::conn_string error-2")
        print(e)
        pass

def proxy_server(webserver, port, conn, data, addr):
    print(":::call proxy_server")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("&&&&")
        s.connect((webserver, port))
        print("****")
        print("data type:")
        print(type(data))
        print("data:")
        print(data)
        s.send(data)

        print("%%%%")
        while 1:
            reply = s.recv(buffer_size)

            print(":::proxy_sever reply:")
            print(reply)

            if(len(reply) > 0):
                conn.send(reply)
                dar = float(len(reply))
                dar = float(dar/1024)
                dar = "%.3s"%(str(dar))
                dar = "%s KB"%(dar)
                print(":::Request done : %s = %s."%(str(addr[0]), str(dar)))
            else:
                break

        print(":::proxy_server end")
        s.close()
        conn.close()
    except Exception as e:
        print(":::proxy_server error")
        print(e)
        s.close()
        conn.close()
        sys.exit(1)
        
##########
##########
##########

try:
    listening_port = int(input(":::Enter listening port number : "))
except KeyboardInterrupt:
    print(":::User requested an interrupt.")
    sys.exit()

start()


