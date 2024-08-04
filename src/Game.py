import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from Package import Package
import Constants
import random

class Game:
    def __init__(self, machines, node):
        self.lifes, self.point = 12, 0
        self.phase, self.rounds = Constants.PREPARE, 1
        self.ended = False
        self.node = node
        
        self.players_alive = {self.node.hostname: {"bet": 0, "points": 0}}
        for machine in machines:
            self.players_alive[machine] = {"bet": 0, "points": 0}

        self.my_cards = []
        self.turn = ""

    
    def clear_state(self):
        for player in self.players_alive:
            self.players_alive[player] = {"bet": 0, "points": 0}


    def shuffle_and_distribute(self):
        print("Distribuindo as cartas...\n")
        shuffled_deck = random.sample(Constants.DECK, len(Constants.DECK))

        hands = []
        for index in range(len(self.players_alive)):
            start_index = index * Constants.CARDS_BY_HAND
            end_index = start_index + Constants.CARDS_BY_HAND
            hands.append(shuffled_deck[start_index:end_index])
        self.turn = shuffled_deck[end_index + 1]
        self.my_cards = hands[-1]

        data = ""
        for index in range(len(self.players_alive) - 1):
            data += f"{'-'.join(hands[index])}/"
        data += f"{self.turn}"
        
        cards_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.CARDS, data=data)
        self.node.send_package(cards_package)

        response = self.node.recv_package()
        if response.type == Constants.CARDS and (len(response.data.split("/")) == 1):
            print("Cartas distribuidas, iniciando a rodada...")
            self.phase = Constants.GAME

    
    def receive_cards(self):
        print("Esperando as cartas...\n")
        card_package = self.node.recv_package()

        if card_package.type == Constants.CARDS:
            splited_data = card_package.data.split("/")
            self.my_cards = splited_data[0].split("-")
            self.turn = splited_data[-1]

            data = ""
            for index in range(1, (len(splited_data) - 1)):
                data += f"{splited_data[index]}/"
            data += f"{self.turn}"

            cards_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.CARDS, data=data)
            self.node.send_package(cards_package)
        
        print("Cartas recebidas, iniciando a rodada...")
        self.phase = Constants.GAME


    def bet_wins(self):
        print("Esperando os demais jogares apostarem...")
        
        if self.node.token:
            bet_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.BET, data="")
            self.node.send_package(bet_package)

            response = self.node.recv_package()
            if response.type == Constants.BET:
                self.players_alive[self.node.hostname]["bet"] = self._make_bet()
                
                splited_data = response.data.split("-")[:-1]
                bets = [(item.split(',')[0].strip("() "), int(item.split(',')[1].strip(") "))) for item in splited_data]
                for bet in bets:
                    self.players_alive[bet[0]]["bet"] = bet[1]
            
        else:
            response = self.node.recv_package()

            if response.type == Constants.BET:
                bet = self._make_bet()
                data = response.data + f"({self.node.hostname}, {bet})-"

                bet_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.BET, data=data)
                self.node.send_package(bet_package)


    def show_bets(self):
        if self.node.token:
            print("\nAs apostas feitas foram: ")

            data = ""
            for player, info in self.players_alive.items():
                print(f"{player}: {info['bet']} ", end=" ")
                data += f"({player}, {info['bet']})-"
            print("", end="\n")
        
            show_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.SHOW, data=data)
            self.node.send_package(show_package)

            response = self.node.recv_package()
            if response.type == Constants.SHOW:
                print("\nIniciando as rodadas...\n")
        
        else:
            response = self.node.recv_package()
            print("\nAs apostas feitas foram: ")

            if response.type == Constants.SHOW:
                splited_data = response.data.split("-")[:-1]
                bets = [(item.split(',')[0].strip("() "), int(item.split(',')[1].strip(") "))) for item in splited_data]
                for bet in bets:
                    print(f"{bet[0]}: {bet[1]} ", end=" ")
                print("", end="\n")

                show_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.SHOW, data=response.data)
                self.node.send_package(show_package)

                print("\nIniciando as rodadas...\n")


    # ------------------------------------------------------ Internal --------------------------------------------------------------------

    def _make_bet(self):
        bet = Constants.GAME_MAX_BET
        while bet > Constants.PLAYER_MAX_BET:
            bet = int(input("Quantas voce vai ganhar? "))
            if bet > Constants.PLAYER_MAX_BET: print("Sua aposta tem que ser menor que 3...")
        
        return bet