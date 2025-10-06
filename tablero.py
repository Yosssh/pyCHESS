import numpy as np
import pygame
from piezas import PIEZAS
from tools import enroque, coronacion, color_to_meth
from menu import mostrar_menu_coronacion


# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 100, 150)

# Dimensiones del tablero y de cada celda
ANCHO, ALTO = 420, 420
CELDA_SIZE = ANCHO // 8

class Tablero():
    def __init__(self, setup=None):
        if not setup:
            self.tablero = [
                [-11,-5,-7,-13,-17,-7,-5,-11],
                [-3,-3,-3,-3,-3,-3,-3,-3],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [11, 5, 7, 13, 17, 7, 5, 11]
                ]
            
        else:
            self.tablero = setup

        self.to_play = "w"

        self.ocupadas = {}
        self.reyes = {}
        self.controladas = {"w" : set(), "b" : set()}
        self.al_paso_casilla = {"w" : [], "b" : []}
        self.al_paso_peon = None

        self.piezas_x_color = {"w" : [], "b" : []}
        self.piezas = self.get_piezas()
        self.all_cmoves = {"w" : {}, "b" : {}}


    def get_piezas(self):
        piezas = pygame.sprite.Group()
        for f, fila in enumerate(self.tablero):
            for c, valor in enumerate(fila):
                if valor == 1:
                    continue
                color = 'w' if valor > 0 else 'b'
                pieza = abs(valor)
                x,y = CELDA_SIZE*c+CELDA_SIZE//2, CELDA_SIZE*f+CELDA_SIZE//2
                idx = np.array([c,f])

                pieza_obj = PIEZAS[pieza](color, idx, (x,y))
                self.piezas_x_color[pieza_obj.color] += [pieza_obj]
                if pieza==17:
                    self.reyes[pieza_obj.color] = pieza_obj
                piezas.add(pieza_obj)
                self.ocupadas[(c,f)] = pieza_obj
        
        return piezas

    def get_all_moves(self, color):
        all_moves = {}

        otro = "b" if color == "w" else "w"
        self.reyes[otro].amenazas.clear()
        self.reyes[otro].is_in_check = False

        for p in self.piezas_x_color[color]:
            if p.pieza == 3:
                p_moves, self.controladas[color] = p.get_moves(self.ocupadas, self.al_paso_casilla[otro], self.controladas[color])
                all_moves[p] = p_moves
            elif p.pieza == 17:
                p_moves, self.controladas[color] = p.get_moves(self.ocupadas, self.controladas[color], self.controladas[otro])
                all_moves[p] = p_moves
            else:
                p_moves, self.controladas[color] = p.get_moves(self.ocupadas, self.controladas[color])
                all_moves[p] = p_moves

        self.all_cmoves[color] = all_moves

    def is_valid_move(self, pieza, move):
        if move not in self.all_cmoves[pieza.color][pieza]:
            return None
        
        otro = "b" if self.to_play == "w" else "w"
        origen = tuple(map(int, pieza.idx))
        capturada = self.ocupadas.get(move)

        self.ocupadas.pop(origen, None)
        self.ocupadas[move] = pieza
        pieza.idx = np.array(move)

        if capturada:
            self.piezas_x_color[otro].remove(capturada)

        self.get_all_moves(otro)
        in_check = self.reyes[pieza.color].is_in_check

        self.ocupadas.pop(move, None)
        pieza.idx = np.array(origen)
        self.ocupadas[origen] = pieza

        if capturada:
            self.piezas_x_color[otro].append(capturada)
            self.ocupadas[move] = capturada
        
        self.get_all_moves(otro)

        return None if in_check else move

    def get_legal_moves(self, color):
        legal_moves = {}

        for p in self.all_cmoves[color]:
            p_legal = []
            moves = self.all_cmoves[color][p]

            for m in moves:
                move = self.is_valid_move(p,m)

                if move:
                    p_legal.append(m)

            if len(p_legal)>0:
                legal_moves[p] = p_legal

        return legal_moves

    def check_checkmate(self):
        legales = self.get_legal_moves(self.to_play)

        if self.reyes[self.to_play].is_in_check:
            if not legales:
                print("CHECKMATE!")
        
        else:
            if not legales:
                print("Ahogado :(")

    def make_move(self, pieza, move, screen, sprites):
        if abs(pieza.pieza) == 17 and (move == enroque[self.to_play][0][0][0] or move == enroque[self.to_play][1][0][0]):
            if move == enroque[self.to_play][0][0][0]:
                if pieza.enroques[0]:
                    #movimiento del rey
                    self.ocupadas[move] = pieza
                    pieza.idx = move

                    #movimiento torre
                    torre_key = enroque[self.to_play][0][1]
                    torre = self.ocupadas[torre_key]
                    x,y = move
                    torre.idx = (x-1,y)

            if move == enroque[self.to_play][1][0][0]:
                if pieza.enroques[0]:
                    #movimiento del rey
                    self.ocupadas[move] = pieza
                    pieza.idx = move

                    #movimiento torre
                    torre_key = enroque[self.to_play][1][1]
                    torre = self.ocupadas[torre_key]
                    x,y = move
                    torre.idx = (x+1,y)
        
        else:
            if move in self.ocupadas:
                capturada = self.ocupadas.pop(move)
                self.piezas.remove(capturada)

            self.ocupadas[move] = pieza
            origen = pieza.idx
            pieza.idx = move

            if abs(pieza.pieza) == 3: #es peon
                move_arr = np.array(move)
                delta_pos = move_arr-origen
                if abs(delta_pos[1])==2:
                    casilla = move_arr + np.array([0,-1*color_to_meth.get(pieza.color)])
                    self.al_paso_casilla[self.to_play] += [tuple(map(int,casilla))]
                    self.al_paso_peon = pieza

                otro = "b" if self.to_play == "w" else "w"
                if move in self.al_paso_casilla[otro]:
                    self.piezas.remove(self.al_paso_peon)
                
                if move[1] == coronacion[pieza.color]:
                    clave = mostrar_menu_coronacion(screen, pieza.color, ANCHO//2, ALTO//2, sprites)
                    self.piezas.remove(pieza)
                    pieza = pieza.coronar(clave)
                    self.piezas.add(pieza)

        if abs(pieza.pieza) == 5 or abs(pieza.pieza) == 17:
            pieza.moved = True

    def update(self):
        self.ocupadas = {}
        self.piezas_x_color = {"w": [], "b": []}
        for p in self.piezas:
            p.update()
            key = tuple(map(int, p.idx))
            self.ocupadas[key] = p
            self.piezas_x_color[p.color].append(p)
        for c in ["w", "b"]:
            self.controladas[c] = set()
            self.get_all_moves(c)

        self.to_play = 'b' if self.to_play=='w' else 'w'
        self.al_paso_casilla[self.to_play].clear()


    def dibujar_tablero(self, screen):
        tablero_pos = (0,0)
        tablero_surface = pygame.Surface((ANCHO, ALTO))
        for fila in range(8):
            for columna in range(8):
                color = BLANCO if (fila + columna) % 2 == 0 else NEGRO
                pygame.draw.rect(
                    tablero_surface,
                    color,
                    (columna * CELDA_SIZE, fila * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE)
                )
        screen.blit(tablero_surface, tablero_pos)

        self.piezas.draw(screen)



