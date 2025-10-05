import numpy as np
import pygame
from piezas import PIEZAS

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

        self.ocupadas = {}
        self.reyes = {}
        self.controladas = {"w" : set(), "b" : set()}
        self.al_paso_casilla = {"w" : [], "b" : []}
        self.al_paso_peon = None

        self.piezas_x_color = {"w" : [], "b" : []}
        self.piezas = self.get_piezas()
        self.legal_moves = {"w" : {}, "b" : {}}


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

        self.legal_moves[color] = all_moves
    
    def update(self):
        self.ocupadas = {}
        self.piezas_x_color = {"w": [], "b": []}
        for p in self.piezas:
            key = tuple(map(int, p.idx))
            self.ocupadas[key] = p
            self.piezas_x_color[p.color].append(p)
        for c in ["w", "b"]:
            self.controladas[c] = set()
            self.get_all_moves(c)


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



