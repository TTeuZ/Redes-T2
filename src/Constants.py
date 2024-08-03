# Constants
DELIMITER = "~"
BUFFER_SIZE = 1024
TIMEOUT = 60
NUM_PLAYERS = 4

# Enum - Phases
PREPARE = -10
GAME = -11

# Enum - Types
CONNECTION = -1
LIST = -2
CARDS = -3

# Deck
CARDS_BY_HAND = 3
DECK = ['4C', '5C', '6C', '7C', '8C', '9C', '10C', 'QC', 'JC', 'KC', 'AC', '2C', '3C',
        '4E', '5E', '6E', '7E', '8E', '9E', '10E', 'QE', 'JE', 'KE', 'AE', '2E', '3E',
        '4O', '5O', '6O', '7O', '8O', '9O', '10O', 'QO', 'JO', 'KO', 'AO', '2O', '3O',
        '4P', '5P', '6P', '7P', '8P', '9P', '10P', 'QP', 'JP', 'KP', 'AP', '2P', '3P',]

POWER_SCALE = ['4', '5', '6', '7', '8', '9', '10', 'Q', 'J', 'K', 'A', '2', '3']
GOAT_SCALE = ['O', 'E', 'C', 'P']