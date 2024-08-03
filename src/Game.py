import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from Constants import PREPARE, DECK, CARDS_BY_HAND, CARDS, GAME
from Package import Package
import random

class Game:
    def __init__(self, machines):
        self.lifes, self.point = 12, 0

        self.phase = PREPARE
        self.ended = False
        self.rounds = 1

        self.players_alive = machines
        self.my_cards = []
        self.turn = ""

    
    def shuffle_and_distribute(self, node):
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
        
        cards_package = Package(src=node.ip, token=False, type=CARDS, data=data)
        node.send_package(cards_package)

        response = node.recv_package()
        if response.type == CARDS and (len(response.data.split("/")) == 1):
            print("Cartas distribuidas, iniciando a rodada...")
            self.phase = GAME

    
    def receive_cards(self, node):
        print("Esperando as cartas...\n")
        card_package = node.recv_package()

        if card_package.type == CARDS:
            splited_data = card_package.data.split("/")
            self.my_cards = splited_data[0].split("-")
            self.turn = splited_data[-1]

            data = ""
            for index in range(1, (len(splited_data) - 1)):
                data += f"{splited_data[index]}/"
            data += f"{self.turn}"

            cards_package = Package(src=node.ip, token=False, type=CARDS, data=data)
            node.send_package(cards_package)
        
        print("Cartas recebidas, iniciando a rodada...")
        self.phase = GAME