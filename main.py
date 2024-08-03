from src.Node import Node
from src.Game import Game
import argparse


def main(args):
    node = Node(args.port, args.neighbor, args.neighbor_port, args.token)
    node.establish_connection()

    game = Game(node.machines)

    while not game.ended:
        print(f"Iniciando round: {game.rounds}\n")

        if game.lifes >= 0:
            if node.token:
                game.shuffle_and_distribute(node)
            else:
                game.receive_cards(node)

            print(game.my_cards)
            
            game.ended = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Token Ring Network", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--port", type=int, required=True)
    parser.add_argument("-n", "--neighbor", type=str, required=True)
    parser.add_argument("-np", "--neighbor_port", type=int, required=True)
    parser.add_argument("-t", "--token", type=int, required=True)

    main(parser.parse_args())
