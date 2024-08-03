import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from Constants import BUFFER_SIZE, CONNECTION, LIST, TIMEOUT, NUM_PLAYERS
from Package import Package
import select
import socket

KEYS = ['name', 'ip', 'port']

class Node:
    def __init__(self, port, neighbor, neighbor_port, token):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.machines = []

        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.port = port

        self.neighbor_ip = self.ip if neighbor == "local" else socket.gethostbyname(neighbor)
        self.neighbor, self.neighbor_port = neighbor, neighbor_port

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
        print("Estabelencendo conexao...")

        if self.token:
            connection_package = Package(src=self.ip, dst=None, token=False, type=CONNECTION, data="-1")
            self.send_package(connection_package)
            
            package = self.recv_package()
            splited_data = package.data.split("-")

            if package.type == CONNECTION and int(splited_data[-1]) == NUM_PLAYERS:
                machines = splited_data[0].split("/")[1:]
                self._get_machines_dict(machines)

                self._send_full_connection_list(machines)
                package = self.recv_package()

                if package.type == LIST:
                    print("Conexao estabelecia - O jogo pode comecar!")
                else:
                    print(f"Falha na conexao. Atualizacao da lista de jogadores mal sucedida.")
            else:
                print(f"Falha na conexao. Apenas {int(splited_data[-1])} conectadas")
                
        else:
            package = self.recv_package()
            if package.type == CONNECTION:
                splited_data = package.data.split("-")
                count = int(splited_data[-1]) + 1
                data = splited_data[0] + f"/({self.hostname}, {self.ip}, {self.port})-" + f"{count}"

                connection_package = Package(src=self.ip, dst=None, token=False, type=CONNECTION, data=data)
                self.send_package(connection_package)

            package = self.recv_package()
            if package.type == LIST:
                machines = package.data.split("/")[1:]
                self._get_machines_dict(machines)
                
                self._send_full_connection_list(machines)
                print("Conexao estabelecia - O jogo pode comecar!")
    
    
    def _get_machines_dict(self, machines):
        for machine in machines:
            values = [item.strip() for item in machine.strip("()").split(",")]
            self.machines.append(dict(zip(KEYS, values)))


    def _send_full_connection_list(self, machines):
        data = "/".join([machine for index, machine in enumerate(machines) 
                            if self.machines[index]["port"] != self.neighbor_port 
                            and self.machines[index]["name"] != self.neighbor])
        data += f"/({self.hostname}, {self.ip}, {self.port})"
        list_package = Package(src=self.ip, dst=None, token=False, type=LIST, data=data)
        self.send_package(list_package)