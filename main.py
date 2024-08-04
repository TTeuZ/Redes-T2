import src.Constants as Constants
from src.Node import Node
from src.Game import Game
import argparse
import time

def main(args):
    node = Node(args.machine, args.port, args.neighbor, args.neighbor_port, args.dealer)
    node.establish_connection()

    game = Game(node.machines, node)
    while not game.ended:
        print("\n--------------------------------------------------------------------------")
        if not game.dead:
            game.clear_state()
            print(f"Iniciando round: {game.rounds} - Minhas vidas: {game.lifes}")

            if node.dealer: 
                game.shuffle_and_distribute()
            else: 
                game.receive_cards()

            time.sleep(1)
            game.show_cards()
            print(f"Vira da rodade eh: {game.turn}\n")
            time.sleep(1)
            
            game.bet_wins()
            game.show_bets()

            for r_index in range(Constants.ROUNDS):
                print(f"Rodada {r_index + 1}")

                moves = game.make_move()
                game.compute_results(moves)

            game.check_round_result()
            game.rounds += 1
            # print("calcular as percas de vida")
            # print("mandar as percas na rede")
            # print("quando receber a perca, decrementar a sua vida")

        print("--------------------------------------------------------------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dealer Ring Network", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--machine", type=str, required=True)
    parser.add_argument("-p", "--port", type=int, required=True)
    parser.add_argument("-n", "--neighbor", type=str, required=True)
    parser.add_argument("-np", "--neighbor_port", type=int, required=True)
    parser.add_argument("-t", "--dealer", type=int, required=True)

    main(parser.parse_args())
