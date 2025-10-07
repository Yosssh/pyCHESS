import numpy as np

color_to_meth = {'w' : -1, 'b' : 1}

salida_cond = {'w' : 6, 'b' : 1}

coronacion = {"w" : 0, "b" : 7}

enroque = {"w" : [[[(6,7), (5,7)], (7,7)], [[(2,7), (3,7)], (0,7)]], "b" : [[[(6,0), (5,0)], (7,0)], [[(2,0), (3,0)], (0,0)]]}

rey_origen = {"w" : (4,7), "b" : (4,0)}

########################################

notacion_to_index = {
    "a" : 0,
    "b" : 1,
    "c" : 2,
    "d" : 3,
    "e" : 4,
    "f" : 5,
    "g" : 6,
    "h" : 7,
}

caracter_to_pnum = {
    "p" : -3,
    "P" : 3,
    "n" : -5,
    "N" : 5,
    "b" : -7,
    "B" : 7,
    "r" : -11,
    "R" : 11,
    "q" : -13,
    "Q" : 13,
    "k" : -17,
    "K" : 17
}

pnum_to_caracter = {
    -3 : "p",
    3 : "P",
    -5 : "n",
    5 : "N",
    -7 : "b",
    7 : "B",
    -11 : "r",
    11 : "R",
    -13 : "q",
    13 : "Q",
    -17 : "k",
    17 : "K"
}

def FEN_to_array(piezas):
    tablero_arr = np.ones(shape=(8,8), dtype=int)
    filas = piezas.split("/")
    for i,seq in enumerate(filas):
        j=0
        for caracter in seq:
            pieza = caracter_to_pnum.get(caracter)

            if pieza:
                tablero_arr[i,j] = pieza
                j += 1

            else:
                n = int(caracter)
                j += (n-1)

    return tablero_arr

def FEN_castling(code):
    side = {"k" : 0, "q" : 1}
    white = [False, False]
    black = [False, False]

    try:
        for c in code:
            if c.isupper():
                white[side[c.lower()]] = True
            else:
                black[side[c]] = True
    except:
        pass

    return [white, black]

def FEN_en_passant(code):
    try:
        columna,fila = code
        return (int(fila)-1, notacion_to_index[columna])

    except:
        return None

def FEN_translate(fen):
    piezas, to_play, castling, en_passant, halfmoves, turn = fen.split(" ")

    tablero_arr = FEN_to_array(piezas)

    castle = FEN_castling(castling)

    al_paso = FEN_en_passant(en_passant)

    return tablero_arr, to_play, castle, al_paso, int(halfmoves), int(turn)