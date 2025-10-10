import numpy as np
import pygame
from tools import enroque, color_to_meth, rey_origen, salida_cond
from FEN import pnum_to_caracter, FEN_translate, FEN_to_setup
from tablero_sprite import Tablero_sprite

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 100, 150)

# Dimensiones del tablero y de cada celda
ANCHO, ALTO = 420, 420
CELDA_SIZE = ANCHO // 8


class Tablero():
    def __init__(self, FEN=None, visual=True):
        self.registro = []

        self.piezas_x_color = {"w" : [], "b" : []}
        self.reyes = {}

        self.al_paso_casilla = {"w" : [], "b" : []}
        self.al_paso_peon = None
        self.controladas = {"w" : set(), "b" : set()}

        if not FEN:
            self.ocupadas, self.reyes = FEN_to_setup("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
            self.to_play = "w"
            self.halfmoves = 0
            self.turn = 1

        else:
            self.ocupadas, self.reyes, self.to_play, castle, al_paso_casilla, self.halfmoves, self.turn = FEN_translate(FEN)

            for i,c in enumerate(["w", "b"]):
                enroques = castle[i]

                if all(not e for e in enroques):
                    self.reyes[c].moved = True
                else:
                    for j,cond in enumerate(enroques):
                        if not cond:
                            la_torre = self.ocupadas.get(enroque[c][j][1])
                            if la_torre and abs(la_torre.pieza) == 11 and la_torre.color == c:
                                la_torre.moved = True

            if al_paso_casilla:
                otro = "b" if self.to_play == "w" else "w"
                self.al_paso_casilla[otro] = al_paso_casilla
                al_paso_peon_key = (al_paso_casilla[0] + color_to_meth[otro], al_paso_casilla[1])
                self.al_paso_peon = self.ocupadas[al_paso_peon_key]

        for key in self.ocupadas:
            pieza = self.ocupadas[key]
            self.piezas_x_color[pieza.color].append(pieza)

        self.FEN = self.to_FEN()
        self.estado = " ".join(self.FEN.split(" ")[:-2])
        self.registro.append(self.estado)

        if visual:
            self.tablero_sprite = Tablero_sprite()
            for key in self.ocupadas:
                self.tablero_sprite.piezas_group.add(self.ocupadas[key])
        else:
            self.tablero_sprite = None

    def get_all_color_moves(self, color):
        otro = "b" if color == "w" else "w"
        self.reyes[otro].amenazas.clear()
        self.reyes[otro].is_in_check = False

        for p in self.piezas_x_color[color]:
            if p.pieza == 3:
                self.controladas[color] = p.get_moves(self.ocupadas, self.al_paso_casilla[otro], self.controladas[color])
            elif p.pieza == 17:
                self.controladas[color] = p.get_moves(self.ocupadas, self.controladas[color], self.controladas[otro])
            else:
                self.controladas[color] = p.get_moves(self.ocupadas, self.controladas[color])
    
    def is_valid_move(self, pieza, move):
        if move not in pieza.acceso:
            return None

        if len(move)==3:
            coronacion = True
            x,y,clave = move
            move = (x,y)
        else:
            coronacion = False

        otro = "b" if self.to_play == "w" else "w"
        origen = pieza.idx
        capturada = self.ocupadas.get(move) 

        self.ocupadas.pop(origen, None)
        self.ocupadas[move] = pieza

        if capturada and capturada.color != pieza.color:
            self.piezas_x_color[otro].remove(capturada)

        self.get_all_color_moves(otro)
        in_check = self.reyes[pieza.color].is_in_check

        self.ocupadas[origen] = pieza
        self.ocupadas.pop(move, None)

        if capturada:
            self.piezas_x_color[otro].append(capturada)
            self.ocupadas[move] = capturada

        self.get_all_color_moves(otro)

        if coronacion:
            move = (x,y,clave)

        return None if in_check else move
    
    def get_legal_moves(self, color):
        legales = {}

        for p in self.piezas_x_color[color]:
            p_legal = []
            for m in p.acceso:
                move = self.is_valid_move(p, m)

                if move:
                    p_legal.append(move)

            if len(p_legal)>0:
                legales[p] = p_legal

        return legales
    
    def check_state(self):
        legales = self.get_legal_moves(self.to_play)

        if not legales:
            if self.reyes[self.to_play].is_in_check:
                    print("Checkmate!")
                    score = 1 if self.to_play == "b" else -1
                    return False, score
            
            else:
                    print("Stalemate :(")
                    return False, 0.5
        
        if self.halfmoves == 50:
            print("tablas por 50 movimientos")
            return False, 0.5
        
        if self.registro.count(self.estado) == 3:
            print("tablas por repetición")
            return False, 0.5

        else:
            return True, None

    def make_move(self, pieza, move, clave=None):
        self.halfmoves += 1
        if pieza.color == "b":
            self.turn += 1

        if len(move) == 3:
            x,y,clave = move
            move = (x,y)

        if pieza.pieza == 17 and (move == enroque[self.to_play][0][0][0] or move == enroque[self.to_play][1][0][0]) and pieza.idx== rey_origen[self.to_play]:
            if move == enroque[self.to_play][0][0][0]:
                if pieza.enroques[0]:
                    #movimiento del rey
                    self.ocupadas.pop(pieza.idx, None)
                    self.ocupadas[move] = pieza

                    #movimiento torre
                    torre_key = enroque[self.to_play][0][1]
                    torre = self.ocupadas.pop(torre_key)
                    x,y = move[0]-1,move[1]
                    self.ocupadas[(x,y)] = torre

            if move == enroque[self.to_play][1][0][0]:
                if pieza.enroques[0]:
                    #movimiento del rey
                    self.ocupadas.pop(pieza.idx, None)
                    self.ocupadas[move] = pieza

                    #movimiento torre
                    torre_key = enroque[self.to_play][1][1]
                    torre = self.ocupadas.pop(torre_key)
                    x,y = move[0]+1,move[1]
                    self.ocupadas[(x,y)] = torre
        
        else:
            if move in self.ocupadas:
                self.halfmoves = 0
                capturada = self.ocupadas.pop(move)


            origen = pieza.idx

            if pieza.pieza == 3:
                self.halfmoves = 0

                if origen[1] == salida_cond[pieza.color]:
                    move_arr = np.array(move)
                    delta_pos = move_arr - np.array(origen)
                    if abs(delta_pos[1])==2:
                        casilla = move_arr + np.array([0,-1*color_to_meth.get(pieza.color)])
                        self.al_paso_casilla[self.to_play] += [tuple(map(int,casilla))]
                        self.al_paso_peon = pieza

                otro = "b" if self.to_play == "w" else "w"
                if move in self.al_paso_casilla[otro]:
                    self.ocupadas.pop(self.al_paso_peon.idx)

                if clave:
                    pieza = pieza.coronar(clave)

            self.ocupadas[move] = pieza
            self.ocupadas.pop(pieza.idx, None)             

        if pieza.pieza == 11 or pieza.pieza == 17:
            pieza.moved = True

    def update(self):
        self.piezas_x_color = {"w" : [], "b" : []}

        if self.tablero_sprite:
            self.tablero_sprite.piezas_group.empty()
        
        for key in self.ocupadas:
            pieza = self.ocupadas[key]
            self.piezas_x_color[pieza.color].append(pieza)
            pieza.idx = key


        if self.tablero_sprite:
            self.tablero_sprite.update(self.ocupadas)

        for c in ["w", "b"]:
            self.controladas[c] = set()
            self.get_all_color_moves(c)

        self.to_play = 'b' if self.to_play=='w' else 'w'
        self.al_paso_casilla[self.to_play].clear()

        self.FEN = self.to_FEN()
        self.estado = " ".join(self.FEN.split(" ")[:-2])
        self.registro.append(self.estado)

    def get_piezas_array(self):
        p_arr = np.ones(shape=(8,8), dtype=int)

        for i,color in enumerate(["w", "b"]):
            for p in self.piezas_x_color[color]:
                columna,fila = p.idx
                if color == "w":
                    p_arr[fila,columna] = p.pieza
                else:
                    p_arr[fila,columna] = -p.pieza
        
        return p_arr

    def ocupadas_to_FEN(self):
        tablero_arr = self.get_piezas_array()
        tablero_str = []
        for fila in tablero_arr.tolist():
            fila_str = ""
            espacio = 0
            for casilla in fila:
                if casilla == 1:
                    espacio += 1

                else:
                    if espacio > 0:
                        fila_str += str(espacio)
                        espacio = 0
                    fila_str += pnum_to_caracter[casilla]
                
            if espacio > 0:
                fila_str += str(espacio)

            tablero_str.append(fila_str)
        
        return "/".join(tablero_str)

    def tablero_castle_to_FEN(self):
        enroques_code = {"w" : ["K", "Q"], "b" : ["k", "q"]}
        castl_str = ""

        for c in ["w", "b"]:
            if not self.reyes[c].moved:
                for i,info in enumerate(enroque[c]):
                    torre_pos = info[1]
                    
                    la_torre = self.ocupadas.get(torre_pos)

                    if la_torre and abs(la_torre.pieza) == 11 and la_torre.color == c:
                        if not la_torre.moved:
                            castl_str += enroques_code[c][i]
        
        if len(castl_str) > 0:
            return castl_str
        else:
            return "-"
        
    def en_passant_to_FEN(self):
        columna_to_car = {
            0 : "a",
            1 : "b",
            2 : "c",
            3 : "d",
            4 : "e",
            5 : "f",
            6 : "g",
            7 : "h"
        }
        otro = "b" if self.to_play == "w" else "w"
        if len(self.al_paso_casilla[otro]) > 0:
            fila,columna = self.al_paso_casilla[otro][0]
            return columna_to_car[fila]+str(8-columna)
        else:
            return "-"

    def to_FEN(self):
        posicion = self.ocupadas_to_FEN()
        to_play = self.to_play
        castling = self.tablero_castle_to_FEN()
        en_passant = self.en_passant_to_FEN()
        halfmoves = str(self.halfmoves)
        turno = str(self.turn)

        return " ".join([posicion, to_play, castling, en_passant, halfmoves, turno])
