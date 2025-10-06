import numpy as np

color_to_meth = {'w' : -1, 'b' : 1}

salida_cond = {'w' : 6, 'b' : 1}

coronacion = {"w" : 0, "b" : 7}

enroque = {"w" : [[[(6,7), (5,7)], (7,7)], [[(2,7), (3,7)], (0,7)]], "b" : [[[(6,0), (5,0)], (7,0)], [[(2,0), (3,0)], (0,0)]]}

rey_origen = {"w" : (4,7), "b" : (4,0)}


########################################

prueba = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def FEN_to_array(fen):
    datos = fen.split(" ")
    filas = datos[0].split("/")