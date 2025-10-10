from piezas import PIEZAS

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

def FEN_to_setup(piezas):
    ocupadas = {}
    reyes = {}
    filas = piezas.split("/")
    for i,seq in enumerate(filas):
        j=0
        for caracter in seq:
            pieza_num = caracter_to_pnum.get(caracter)

            if pieza_num:
                color = "w" if pieza_num > 0 else "b"
                pieza_obj = PIEZAS[abs(pieza_num)](color, (j,i))
                ocupadas[(j,i)] = pieza_obj
                if abs(pieza_num) == 17:
                    reyes[color] = pieza_obj
                j += 1

            else:
                n = int(caracter)
                if n == 8:
                    j += n-1
                else:
                    j += n

    return ocupadas, reyes

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

    ocupadas, reyes = FEN_to_setup(piezas)

    castle = FEN_castling(castling)

    al_paso = FEN_en_passant(en_passant)

    return ocupadas, reyes, to_play, castle, al_paso, int(halfmoves), int(turn)