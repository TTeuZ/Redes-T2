import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import Constants

class Package:
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            values = args[0].split("|")[1:6]
            self.src = values[0]
            self.dst = values[1]
            self.dealer = bool(values[2])
            self.type = int(values[3])
            self.data = values[4]
        else:
            self.src = kwargs.get('src', 0)
            self.dst = kwargs.get('dst', 0)
            self.dealer = bool(kwargs.get('dealer', 0))
            self.type = int(kwargs.get('type', 0))
            self.data = kwargs.get('data', 0)

    
    def get_message(self):
        message = f"{Constants.DELIMITER}|{self.src}|{self.dst}|{self.dealer}|{self.type}|{self.data}|{Constants.DELIMITER}"

        return message