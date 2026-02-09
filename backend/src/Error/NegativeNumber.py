class NegativeNumber(Exception):

    def __init__(self, number_type:str, number_value:float):
        self.number_type = number_type
        self.number_value = number_value

    def __str__(self):
        return f'The variable: {self.number_type} has the following negative value: {self.number_value}'