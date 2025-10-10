import pygame

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 100, 150)
ROJO = (255,0,0)
# Dimensiones del tablero y de cada celda
ANCHO, ALTO = 420, 420
CELDA_SIZE = ANCHO // 8

class Tablero_sprite:
    def __init__(self):
        self.piezas_group = pygame.sprite.Group()
        self.tablero_surf = self.start_tablero()

    def update(self, piezas):
        self.piezas_group.empty()
        for key in piezas:
            pieza = piezas[key]
            self.piezas_group.add(pieza)
        self.piezas_group.update()

    def start_tablero(self):
        self.tablero_pos = (0,0)
        tablero_surf = pygame.Surface((ANCHO, ALTO))

        for fila in range(8):
            for columna in range(8):
                color = BLANCO if (fila+columna) % 2 == 0 else NEGRO
                pygame.draw.rect(tablero_surf, color, (columna * CELDA_SIZE, fila * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))

        return tablero_surf        

    def pintar_tablero(self, screen):
        screen.blit(self.tablero_surf, self.tablero_pos)
        self.piezas_group.draw(screen)

