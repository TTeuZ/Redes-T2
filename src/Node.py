import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import Constants
from Package import Package
import select
import socket

class Node:
    def __init__(self, machine, port, neighbor, neighbor_port, token):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.machines = []

        self.hostname = machine if machine in Constants.LOCAL_NAMES else socket.gethostname()
        self.ip = "127.0.0.1" if machine in Constants.LOCAL_NAMES else socket.gethostbyname(self.hostname)
        self.port = port

        self.neighbor, self.neighbor_port = neighbor, neighbor_port
        self.neighbor_ip = self.ip if neighbor in Constants.LOCAL_NAMES else socket.gethostbyname(neighbor)
        
        self.token = bool(token)
        self.socket.bind((self.ip, self.port))


    def send_package(self, package):
        while True:
            ready = select.select([], [self.socket], [], Constants.TIMEOUT)[1]
            if ready:
                self.socket.sendto(package.get_message().encode(), (self.neighbor_ip, self.neighbor_port))
                return


    def recv_package(self):
        while True:
            ready = select.select([self.socket], [], [], Constants.TIMEOUT)[0]
            if ready:
                data, _ = self.socket.recvfrom(Constants.BUFFER_SIZE)
                return Package(data.decode())


    def establish_connection(self):
        print("Estabelencendo conexao...")

        if self.token:
            connection_package = Package(src=self.ip, dst=None, token=False, type=Constants.CONNECTION, data="-1")
            self.send_package(connection_package)
            
            response = self.recv_package()
            splited_data = response.data.split("-")

            if response.type == Constants.CONNECTION and int(splited_data[-1]) == Constants.NUM_PLAYERS:
                self.machines = splited_data[0].split("/")[1:]

                self._send_full_connection_list(self.machines)
                response = self.recv_package()

                if response.type == Constants.LIST:
                    print("Conexao estabelecia - O jogo pode comecar!\n")
                else:
                    print(f"Falha na conexao. Atualizacao da lista de jogadores mal sucedida.")
            else:
                print(f"Falha na conexao. Apenas {int(splited_data[-1])} conectadas")
                
        else:
            response = self.recv_package()
            if response.type == Constants.CONNECTION:
                splited_data = response.data.split("-")
                data = splited_data[0] + f"/{self.hostname}-" + f"{int(splited_data[-1]) + 1}"

                connection_package = Package(src=self.ip, dst=None, token=False, type=Constants.CONNECTION, data=data)
                self.send_package(connection_package)

            response = self.recv_package()
            if response.type == Constants.LIST:
                self.machines = response.data.split("/")
                
                self._send_full_connection_list(self.machines)
                print("Conexao estabelecia - O jogo pode comecar!\n")

    # ------------------------------------------------------ Internal --------------------------------------------------------------------

    def _send_full_connection_list(self, machines):
        data = "/".join([machine for machine in machines if machine != self.neighbor])
        data += f"/{self.hostname}"

        list_package = Package(src=self.ip, dst=None, token=False, type=Constants.LIST, data=data)
        self.send_package(list_package)