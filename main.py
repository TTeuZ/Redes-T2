import src.Constants as Constants
from src.Node import Node
from src.Game import Game
import argparse
import time

def main(args):
    node = Node(args.machine, args.port, args.neighbor, args.neighbor_port, args.token)
    node.establish_connection()

    game = Game(node.machines, node)
    while not game.ended:
        if game.lifes >= 0:
            game.clear_state()
            print(f"Iniciando round: {game.rounds}")

            if node.token: 
                game.shuffle_and_distribute()
            else: 
                game.receive_cards()

            time.sleep(1)
            while game.phase == Constants.GAME:     
                game.bet_wins()
                game.show_bets()

                print(f"Vira da rodade eh: {game.turn}")
                for g_round in range(Constants.ROUNDS):
                    print("fazer a jogada")

                game.phase = Constants.PREPARE

            game.ended = True # Temporary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Token Ring Network", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--machine", type=str, required=True)
    parser.add_argument("-p", "--port", type=int, required=True)
    parser.add_argument("-n", "--neighbor", type=str, required=True)
    parser.add_argument("-np", "--neighbor_port", type=int, required=True)
    parser.add_argument("-t", "--token", type=int, required=True)

    main(parser.parse_args())
