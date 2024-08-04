import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from Package import Package
import Constants
import random
import math
import copy

class Game:
    def __init__(self, machines, node):
        self.lifes, self.rounds, self.dead = 12, 1, False
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
            split_data = card_package.data.split("/")
            self.my_cards = split_data[0].split("-")
            self.turn = split_data[-1]

            data = ""
            for index in range(1, (len(split_data) - 1)):
                data += f"{split_data[index]}/"
            data += f"{self.turn}"

            card_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.CARDS, data=data)
            self.node.send_package(card_package)
        
        print("Cartas recebidas, iniciando a rodada...")
        self.phase = Constants.GAME


    def show_cards(self):
        print("Minhas cartas: ", end="")
        for card in self.my_cards:
            print(card, end=" ")
        print("", end="\n")


    def bet_wins(self):
        print("Esperando os demais jogares apostarem...")
        
        if self.node.token:
            bet_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.BET, data="")
            self.node.send_package(bet_package)

            response = self.node.recv_package()
            if response.type == Constants.BET:
                self.players_alive[self.node.hostname]["bet"] = self._make_bet()
                
                split_data = response.data.split("-")[:-1]
                bets = [(item.split(',')[0].strip("() "), int(item.split(',')[1].strip(") "))) for item in split_data]
                for bet in bets:
                    self.players_alive[bet[0]]["bet"] = bet[1]
            
        else:
            bet_package = self.node.recv_package()

            if bet_package.type == Constants.BET:
                bet = self._make_bet()
                print("Esperando demais apostas...\n")
                data = bet_package.data + f"({self.node.hostname}, {bet})-"

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
            show_package = self.node.recv_package()
            print("\nAs apostas feitas foram: ")

            if show_package.type == Constants.SHOW:
                split_data = show_package.data.split("-")[:-1]
                bets = [(item.split(',')[0].strip("() "), int(item.split(',')[1].strip(") "))) for item in split_data]
                for bet in bets:
                    print(f"{bet[0]}: {bet[1]} ", end=" ")
                print("", end="\n")

                show_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.SHOW, data=show_package.data)
                self.node.send_package(show_package)

                print("\nIniciando as rodadas...\n")


    def make_move(self):
        if self.node.token:
            move_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.MOVE, data="")
            self.node.send_package(move_package)

            response = self.node.recv_package()
            if response.type == Constants.MOVE:
                split_data = response.data.split("-")[:-1]
                moves = [(item.split(',')[0].strip("() "), item.split(',')[1].strip(") ")) for item in split_data]
                selected_card = self._select_card(moves)

                moves.append((self.node.hostname, selected_card))
                return moves
            
        else:
            move_package = self.node.recv_package()

            if move_package.type == Constants.MOVE:
                split_data = move_package.data.split("-")[:-1]
                moves = [(item.split(',')[0].strip("() "), item.split(',')[1].strip(") ")) for item in split_data]
                selected_card = self._select_card(moves)

                data = move_package.data + f"({self.node.hostname}, {selected_card})-"
                move_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.MOVE, data=data)
                self.node.send_package(move_package)

                return []


    def compute_results(self, moves):
        print("\nEsperando calculo do resultado...")

        if self.node.token:
            winner_index = self._get_winner_index(moves)
            winner = moves[winner_index]
            self.players_alive[winner[0]]["points"] += 1

            data = "-".join(f"({move[0]}, {move[1]})" for move in moves) + "#" + f"({winner[0]}, {winner[1]})"
            result_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.RESULTS, data=data)
            self.node.send_package(result_package)

            response = self.node.recv_package()
            if response.type == Constants.RESULTS:
                self._print_results(moves, winner)

        else:
            result_package = self.node.recv_package()

            if result_package.type == Constants.RESULTS:
                moves, winner = result_package.data.split("#")

                moves = [(item.split(',')[0].strip("() "), item.split(',')[1].strip(") ")) for item in moves.split("-")]
                winner =(winner.split(',')[0].strip("() "), winner.split(',')[1].strip(") "))
                self._print_results(moves, winner)

                result_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.RESULTS, data=result_package.data)
                self.node.send_package(result_package)


    def check_round_result(self):
        print("Avaliando resultado da rodada...")

        if self.node.token:
            players_results = {}
            for player, values in self.players_alive.items():
                players_results[player] = abs(values["bet"] - values["points"])
            
            self.lifes -= players_results[self.node.hostname]

            data = "-".join([f"({player}, {value})" for player, value in players_results.items()])
            round_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.ROUND, data=data)
            self.node.send_package(round_package)
            
            response = self.node.recv_package()
            if response.type == Constants.ROUND:
                print("Resultados transmitidos!\n")

        else:
            round_package = self.node.recv_package()

            if round_package.type == Constants.ROUND:
                split_data = round_package.data.split("-")
                round_results = [(item.split(',')[0].strip("() "), int(item.split(',')[1].strip(") "))) for item in split_data]

                result = next((item for item in round_results if item[0] == self.node.hostname), None)
                self.lifes -= result[1]

                print("Resultados recebido!\n")
                round_package = Package(src=self.node.ip, dst=None, token=False, type=Constants.ROUND, data=round_package.data)
                self.node.send_package(round_package)


    # ------------------------------------------------------ Internal --------------------------------------------------------------------

    def _make_bet(self):
        bet = math.inf
        while bet > Constants.PLAYER_MAX_BET:
            bet = int(input("Quantas voce vai ganhar? "))
            if bet > Constants.PLAYER_MAX_BET: print("Sua aposta tem que ser menor que 3...")
        
        return bet
    

    def _select_card(self, moves):
        if len(moves) > 0:
            print("Jogadas ja feitas: ")
            for move in moves:
                print(f"{move[0]}: {move[1]} ", end=" ")
            print("\n", end="\n")

        self.show_cards()
        selected = math.inf
        while selected >= len(self.my_cards):
            selected = int(input("Qual carta pretende jogar (index)? "))
            if  selected >= len(self.my_cards): print("Index fora do range...")
        
        return self.my_cards.pop(selected)
    

    def _get_winner_index(self, moves):
        local_power_scale = copy.copy(Constants.POWER_SCALE)

        goat_index = Constants.POWER_SCALE.index(self.turn[0]) + 1
        goat_index = goat_index if goat_index < len(local_power_scale) else 0
        goat = local_power_scale.pop(goat_index)
        local_power_scale.append(goat)

        moves_nipes = [move[1][1] for move in moves]
        moves_values = [move[1][0] for move in moves]
        moves_values = [local_power_scale.index(value) for value in moves_values]
        moves_values = [int(value == max(moves_values)) for value in moves_values]

        if sum(moves_values) == 1:
            return moves_values.index(1)
        
        moves_values = [0 if value == 0 else Constants.GOAT_SCALE.index(moves_nipes[index]) for index, value in enumerate(moves_values)]
        moves_values = [int(value == max(moves_values)) for value in moves_values]

        return moves_values.index(1)


    def _print_results(self, moves, winner):
        print("\nJogadas da rodada: ")

        for move in moves:
            print(f"{move[0]}: {move[1]} ", end=" ")
        print("", end="\n")

        print(f"Ganhador: {winner[0]}\n")