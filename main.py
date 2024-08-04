from src.Constants import GAME
from src.Node import Node
from src.Game import Game
import argparse

def main(args):
    node = Node(args.machine, args.port, args.neighbor, args.neighbor_port, args.token)
    node.establish_connection()

    game = Game(node.machines, node)
    print(game.players_alive)

    while not game.ended:
        if game.lifes >= 0:
            print(f"Iniciando round: {game.rounds}\n")

            if node.token:
                game.clear_state()
                game.shuffle_and_distribute()
            else:
                game.receive_cards()

            while game.phase == GAME:     
                game.bet_wins()  

                game.ended = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Token Ring Network", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--machine", type=str, required=True)
    parser.add_argument("-p", "--port", type=int, required=True)
    parser.add_argument("-n", "--neighbor", type=str, required=True)
    parser.add_argument("-np", "--neighbor_port", type=int, required=True)
    parser.add_argument("-t", "--token", type=int, required=True)

    main(parser.parse_args())
