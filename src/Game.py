import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from Constants import PREPARE, DECK, CARDS_BY_HAND, CARDS, GAME
from Package import Package
import random

class Game:
    def __init__(self, machines, node):
        self.lifes, self.point = 12, 0
        self.phase, self.rounds = PREPARE, 1
        self.ended = False
        self.node = node
        
        self.players_alive = {}
        for machine in machines:
            self.players_alive[machine] = {"bet": 0, "points": 0}

        self.my_cards = []
        self.turn = ""

    
    def clear_state(self):
        for player in self.players_alive:
            self.players_alive[player] = {"bet": 0, "points": 0}


    def shuffle_and_distribute(self):
        print("Distribuindo as cartas...\n")
        shuffled_deck = random.sample(DECK, len(DECK))

        hands = []
        for index in range(len(self.players_alive) + 1):
            start_index = index * CARDS_BY_HAND
            end_index = start_index + CARDS_BY_HAND
            hands.append(shuffled_deck[start_index:end_index])
        self.turn = shuffled_deck[end_index + 1]
        self.my_cards = hands[-1]

        data = ""
        for index in range(len(self.players_alive)):
            data += f"{'-'.join(hands[index])}/"
        data += f"{self.turn}"
        
        cards_package = Package(src=self.node.ip, dst=None, token=False, type=CARDS, data=data)
        self.node.send_package(cards_package)

        response = self.node.recv_package()
        if response.type == CARDS and (len(response.data.split("/")) == 1):
            print("Cartas distribuidas, iniciando a rodada...")
            self.phase = GAME

    
    def receive_cards(self):
        print("Esperando as cartas...\n")
        card_package = self.node.recv_package()

        if card_package.type == CARDS:
            splited_data = card_package.data.split("/")
            self.my_cards = splited_data[0].split("-")
            self.turn = splited_data[-1]

            data = ""
            for index in range(1, (len(splited_data) - 1)):
                data += f"{splited_data[index]}/"
            data += f"{self.turn}"

            cards_package = Package(src=self.node.ip, dst=None, token=False, type=CARDS, data=data)
            self.node.send_package(cards_package)
        
        print("Cartas recebidas, iniciando a rodada...")
        self.phase = GAME


    def bet_wins(self):
        print(self.my_cards)