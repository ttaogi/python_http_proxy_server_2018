#http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/

import socket
import select
import time
import sys

buffer_size = 4096
delay = 0.0001
forward_to = ("smtp.zaz.ufsk.br", 25)

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
        except Exception as e:
            print(e)
            return False

class ProxyServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break
                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            print(clientaddr)
            print(" has connected")
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print("Can`t establich connection with remote server.")
            print("Closing connection with client side.")
            print(clientaddr)
            clientsock.close()

    def on_close(self):
        print(self.s.getpeername())
        print(" has disconnected.")

        self.inpout_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]

        self.channel[out].close()
        self.channel[self.s].close()

        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        print(data)
        self.channel[self.s].send(data)

if __name__ == "__main__":
    server = ProxyServer('', 4000)
    try:
        server.main_loop()
    except KeyboardInterrupt as ki:
        print("input ctrl + c")
        sys.exit(1)
