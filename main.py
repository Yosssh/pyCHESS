from tablero import Tablero, ANCHO, ALTO, CELDA_SIZE
import pygame
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("CHE$$")
        self.clock = pygame.time.Clock()
        self.tablero = Tablero(FEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.game = True
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
            if p.rect.collidepoint(event.pos) and p.color == self.tablero.to_play:
                self.selected = p
                self.selected.offset_x = self.selected.rect.x - event.pos[0]
                self.selected.offset_y = self.selected.rect.y - event.pos[1]
                break

    def dragging(self, event_pos):
        if self.selected:
            mouse_x,mouse_y = event_pos
            self.selected.rect.x = mouse_x + self.selected.offset_x
            self.selected.rect.y = mouse_y + self.selected.offset_y

    def main(self):
        self.tablero.get_all_moves(self.tablero.to_play)
        while self.game:

            if self.something:
                self.tablero.check_checkmate()

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

                        move = self.tablero.is_valid_move(self.selected, (idx_x,idx_y))

                        if move:
                            self.tablero.make_move(self.selected, move, self.screen, self.sprites_piezas)
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



