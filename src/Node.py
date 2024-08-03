import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from Constants import BUFFER_SIZE, CONNECTION, TIMEOUT
from Package import Package
import select
import socket

class Node:
    def __init__(self, port, neighbor, neighbor_port, token):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.neighbor_ip = self.ip if neighbor == "local" else socket.gethostbyname(neighbor)
        self.neighbor, self.neighbor_port = neighbor, neighbor_port

        self.hotsname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hotsname)
        self.port = port

        self.token = bool(token)
        self.socket.bind((self.ip, self.port))


    def send_package(self, package):
        while True:
            ready = select.select([], [self.socket], [], TIMEOUT)[1]
            if ready:
                self.socket.sendto(package.get_message().encode(), (self.neighbor_ip, self.neighbor_port))
                return


    def recv_package(self):
        while True:
            ready = select.select([self.socket], [], [], TIMEOUT)[0]
            if ready:
                data, _ = self.socket.recvfrom(BUFFER_SIZE)
                return Package(data.decode())
    

    def establish_connection(self):
        print("Establishing connection...")
        if self.token:
            connection_package = Package(src=self.ip, dst=None, token=False, type=CONNECTION, data="-1")
            self.send_package(connection_package)
            
            package = self.recv_package()
            print(package.data)
        else:
            package = self.recv_package()

            if package.type == CONNECTION:
                splited_data = package.data.split("-")
                count = splited_data[-1] + 1
                data = splited_data[0] + f"({self.hostname}, {self.ip})" + f"-{count}"

                connection_package = Package(src=self.ip, dst=None, token=False, type=CONNECTION, data=data)
                self.send_package(connection_package)

