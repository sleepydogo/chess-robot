
import pickle

class Partida: 
    def __init__(self):
        self.FEN = None
        self.MATRIZ1 = None
        self.MATRIZ2 = None
        self.TABLERO = None

    def setParams(self, fen, matriz1, matriz2, tablero):    
        self.FEN = fen
        self.MATRIZ1 = matriz1
        self.MATRIZ2 = matriz2 
        self.TABLERO = tablero
        with open("config.pk", 'wb') as archivo: 
            pickle.dump(self, archivo)
        return 0
    
    def getParams(self):
        with open('config.pk', 'rb') as arch:
            obj = pickle.load(arch)
        return obj