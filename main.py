from tablero import Tablero, ANCHO, ALTO, CELDA_SIZE
import pygame
import sys
import numpy as np
from tools import color_to_meth, coronacion, enroque, rey_origen


from menu import mostrar_menu_coronacion


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("CHE$$")
        self.clock = pygame.time.Clock()
        self.tablero = Tablero()
        self.game = True
        self.to_play = 'w'
        self.selected = None
        self.something = False

        self.sprites_piezas = {
            "w_reina": pygame.transform.scale(pygame.image.load("C:/Users/Josh/Desktop/CHE$$/2.0/sprites/wq.png").convert_alpha(), (45,45)),
            "w_torre": pygame.transform.scale(pygame.image.load("C:/Users/Josh/Desktop/CHE$$/2.0/sprites/wr.png").convert_alpha(), (45,45)),
            "w_alfil": pygame.transform.scale(pygame.image.load("C:/Users/Josh/Desktop/CHE$$/2.0/sprites/wb.png").convert_alpha(), (45,45)),
            "w_caballo": pygame.transform.scale(pygame.image.load("C:/Users/Josh/Desktop/CHE$$/2.0/sprites/wk.png").convert_alpha(), (45,45)),
            "b_reina": pygame.transform.scale(pygame.image.load("C:/Users/Josh/Desktop/CHE$$/2.0/sprites/bq.png").convert_alpha(), (45,45)),
            "b_torre": pygame.transform.scale(pygame.image.load("C:/Users/Josh/Desktop/CHE$$/2.0/sprites/br.png").convert_alpha(), (45,45)),
            "b_alfil": pygame.transform.scale(pygame.image.load("C:/Users/Josh/Desktop/CHE$$/2.0/sprites/bb.png").convert_alpha(), (45,45)),
            "b_caballo": pygame.transform.scale(pygame.image.load("C:/Users/Josh/Desktop/CHE$$/2.0/sprites/bk.png").convert_alpha(), (45,45)),
        }


    def select_pieza(self, event):
        for p in self.tablero.piezas:
            if p.rect.collidepoint(event.pos) and p.color == self.to_play:
                self.selected = p
                self.selected.offset_x = self.selected.rect.x - event.pos[0]
                self.selected.offset_y = self.selected.rect.y - event.pos[1]
                break

    def dragging(self, event_pos):
        if self.selected:
            mouse_x,mouse_y = event_pos
            self.selected.rect.x = mouse_x + self.selected.offset_x
            self.selected.rect.y = mouse_y + self.selected.offset_y

    def make_move(self, move):
        if self.selected.pieza == 17 and (move == enroque[self.to_play][0][0][0] and tuple(map(int,self.selected.idx)) == rey_origen[self.to_play] or move == enroque[self.to_play][1][0][0] and tuple(map(int,self.selected.idx)) == rey_origen[self.to_play]):
            if move == enroque[self.to_play][0][0][0] and tuple(map(int,self.selected.idx)) == rey_origen[self.to_play]:
                if self.selected.enroques[0]:
                    #esto para el rey
                    self.tablero.ocupadas[move] = self.selected
                    origen = self.selected.idx
                    idx_x, idx_y = move
                    self.selected.rect.centerx = idx_x * CELDA_SIZE + CELDA_SIZE//2
                    self.selected.rect.centery = idx_y * CELDA_SIZE + CELDA_SIZE//2
                    self.selected.idx = (idx_x,idx_y)

                    #ahora pa la torre
                    torre_key = enroque[self.to_play][0][1]
                    torre = self.tablero.ocupadas[torre_key]
                    idx_x, idx_y = move
                    idx_x -= 1
                    torre.rect.centerx = idx_x * CELDA_SIZE + CELDA_SIZE//2
                    torre.rect.centery = idx_y * CELDA_SIZE + CELDA_SIZE//2
                    torre.idx = (idx_x,idx_y)

            if move == enroque[self.to_play][1][0][0] and tuple(map(int,self.selected.idx)) == rey_origen[self.to_play]:
                if self.selected.enroques[1]:
                    #esto para el rey
                    self.tablero.ocupadas[move] = self.selected
                    origen = self.selected.idx
                    idx_x, idx_y = move
                    self.selected.rect.centerx = idx_x * CELDA_SIZE + CELDA_SIZE//2
                    self.selected.rect.centery = idx_y * CELDA_SIZE + CELDA_SIZE//2
                    self.selected.idx = (idx_x,idx_y)

                    #ahora pa la torre
                    torre_key = enroque[self.to_play][1][1]
                    torre = self.tablero.ocupadas[torre_key]
                    idx_x, idx_y = move
                    idx_x += 1
                    torre.rect.centerx = idx_x * CELDA_SIZE + CELDA_SIZE//2
                    torre.rect.centery = idx_y * CELDA_SIZE + CELDA_SIZE//2
                    torre.idx = (idx_x,idx_y)
    
        else:
            if move in self.tablero.ocupadas:
                capturada = self.tablero.ocupadas.pop(move)
                self.tablero.piezas.remove(capturada)

            self.tablero.ocupadas[move] = self.selected
            origen = self.selected.idx
            idx_x, idx_y = move
            self.selected.rect.centerx = idx_x * CELDA_SIZE + CELDA_SIZE//2
            self.selected.rect.centery = idx_y * CELDA_SIZE + CELDA_SIZE//2
            self.selected.idx = (idx_x,idx_y)

            if abs(self.selected.pieza) == 3: #es peon
                move_arr = np.array(move)
                delta_pos = move_arr-origen
                if abs(delta_pos[1])==2:
                    casilla = move_arr + np.array([0,-1*color_to_meth.get(self.selected.color)])
                    self.tablero.al_paso_casilla[self.to_play] += [tuple(map(int,casilla))]
                    self.tablero.al_paso_peon = self.selected

                otro = "b" if self.to_play == "w" else "w"
                if move in self.tablero.al_paso_casilla[otro]:
                    self.tablero.piezas.remove(self.tablero.al_paso_peon)
                
                if move[1] == coronacion[self.selected.color]:
                    clave = mostrar_menu_coronacion(self.screen, self.selected.color, ANCHO//2, ALTO//2, self.sprites_piezas)
                    self.tablero.piezas.remove(self.selected)
                    self.selected = self.selected.coronar(clave)
                    self.tablero.piezas.add(self.selected)

        if abs(self.selected.pieza) == 5 or self.selected.pieza == 17:
            self.selected.moved = True


        self.tablero.update()
        self.to_play = 'b' if self.to_play=='w' else 'w'
        self.tablero.al_paso_casilla[self.to_play].clear() #aprovecho aquí para limpiar las casillas al paso del color que juega ahora

    def is_check(self):
        return self.tablero.reyes[self.to_play].is_in_check

    def validar_movimiento(self, idx_x, idx_y):
        move = (idx_x, idx_y)
        pieza = self.selected

        if move not in self.tablero.legal_moves[self.to_play][pieza]:
            return None

        otro = "b" if self.to_play == "w" else "w"

        origen = tuple(map(int, pieza.idx))
        capturada = self.tablero.ocupadas.get(move)


        self.tablero.ocupadas.pop(origen, None)
        self.tablero.ocupadas[move] = pieza
        pieza.idx = np.array(move)

        if capturada:
            self.tablero.piezas_x_color[otro].remove(capturada)

        self.tablero.get_all_moves(otro)
        en_jaque = self.tablero.reyes[self.to_play].is_in_check

        self.tablero.ocupadas.pop(move, None)
        pieza.idx = np.array(origen)
        self.tablero.ocupadas[origen] = pieza

        if capturada:
            self.tablero.piezas_x_color[capturada.color].append(capturada)
            self.tablero.ocupadas[move] = capturada

        self.tablero.get_all_moves(otro)

        return None if en_jaque else move

    def check_checkmate(self):
        movimientos = []
        for p in self.tablero.legal_moves[self.to_play]:
            self.selected = p
            moves = self.tablero.legal_moves[self.to_play][p]
            for m in moves:
                idx_x,idx_y = m
                move = self.validar_movimiento(idx_x,idx_y)
                if move:
                    movimientos.append(move)
                else:
                    continue
        if len(movimientos)==0:
            print("checkmate, mate")
            g = input("Nueva?\n[y/n]")
            if g == "y":
                self = Game()
                self.main()
            else:
                self.game = False
        self.selected = None

    def main(self):
        self.tablero.update()
        while self.game:

            if self.something and self.tablero.reyes[self.to_play].is_in_check:
                self.check_checkmate()

            self.something = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEMOTION:
                    self.dragging(event.pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.select_pieza(event)


                if event.type == pygame.MOUSEBUTTONUP:
                    if self.selected and event.button == 1:

                        idx_x,idx_y = event.pos[0]//CELDA_SIZE,event.pos[1]//CELDA_SIZE

                        move = self.validar_movimiento(idx_x,idx_y)

                        if move:
                            self.make_move(move)
                            self.tablero.update()
                            self.something = True
                                
                        else:
                            self.selected.rect.centerx = self.selected.idx[0]* CELDA_SIZE + CELDA_SIZE//2
                            self.selected.rect.centery = self.selected.idx[1]* CELDA_SIZE + CELDA_SIZE//2

                        self.selected = None

            self.screen.fill((0, 0, 0))
            self.tablero.dibujar_tablero(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.main()



