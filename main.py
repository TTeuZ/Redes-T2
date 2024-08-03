import argparse
from src.Node import Node

def main(args):
    node = Node(args.port, args.neighbor, args.neighbor_port, args.token)
    node.establish_connection()

    print(node.machines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Token Ring Network", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--port", type=int, required=True)
    parser.add_argument("-n", "--neighbor", type=str, required=True)
    parser.add_argument("-np", "--neighbor_port", type=int, required=True)
    parser.add_argument("-t", "--token", type=int, required=True)

    main(parser.parse_args())
