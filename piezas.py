import numpy as np
import tools
import pygame

ANCHO, ALTO = 420, 420
CELDA_SIZE = ANCHO // 8

class Pieza: #clase principal pieza
    def __init__(self, color, valor, idx, iter=True):
        self.color = color
        self.iter = iter
        self.valor = valor
        self.idx = idx
        self.movimientos = None
        self.acceso = None

    def get_moves(self, ocupadas, controladas):
        movimientos = []
        for m in self.movimientos: #Para cada direccion
            dir_moves = []
            c0 = self.idx
            coord = c0 + m
            while np.all(0 <= coord) and np.all(coord < 8):

                key = tuple(map(int,coord))
                if key in ocupadas:

                    objetivo = ocupadas[key]
                    if objetivo.color != self.color:
                        dir_moves.append(key)
                        movimientos += dir_moves

                        if isinstance(objetivo, Rey):
                            amenazas = [tuple(map(int,self.idx))]
                            amenazas += dir_moves 
                            objetivo.manejar_checks(amenazas)
                        break
                    elif ocupadas[tuple(key)].color == self.color:
                        break
                else:
                    dir_moves.append(key)
                movimientos += dir_moves

                if not self.iter:
                    break

                c0 = coord
                coord = c0 + m
                controladas.update(movimientos)

        return movimientos, controladas
    
class Alfil(Pieza): 
    def __init__(self, color, idx, valor=3):
        super().__init__(color, valor, idx)
        self.pieza = 7
        self.movimientos = [np.array([1, 1]), np.array([-1, 1]), np.array([1, -1]), np.array([-1, -1])]

class Torre(Pieza):
    def __init__(self, color, idx, valor=5):
        super().__init__(color, valor, idx)
        self.pieza = 11
        self.movimientos = [np.array([1, 0]), np.array([0, 1]), np.array([-1, 0]), np.array([0, -1])]
        self.moved = False

class Reina(Pieza):
    def __init__(self, color, idx, valor=9):
        super().__init__(color, valor, idx)
        self.pieza = 13
        self.movimientos = [np.array([1, 1]), np.array([-1, 1]), np.array([1, -1]), np.array([-1, -1]),
                            np.array([1, 0]), np.array([0, 1]), np.array([-1, 0]), np.array([0, -1])]
        
class Rey(Pieza):
    def __init__(self, color, idx, valor=100):
        super().__init__(color, valor, idx, False)
        self.pieza = 17
        self.movimientos = [np.array([1, 1]), np.array([-1, 1]), np.array([1, -1]), np.array([-1, -1]),
                            np.array([1, 0]), np.array([0, 1]), np.array([-1, 0]), np.array([0, -1])]
        self.especiales = tools.enroque[color]
        self.is_in_check = False
        self.amenazas = []
        self.moved = False
        self.enroques = [False, False]

    def get_moves(self, ocupadas, controladas, controladas_enemigo):
        movimientos, controladas = super().get_moves(ocupadas, controladas)

        if not self.moved and not self.is_in_check:
            for i,m in enumerate(self.especiales):
                se_puede = True
                casillas, torre = m
                for c in casillas:
                    if c in controladas_enemigo:
                        se_puede = False
                    elif c in ocupadas:
                        se_puede = False

                if torre in ocupadas:
                    la_torre = ocupadas[torre]
                    if la_torre.pieza==11 and la_torre.color == self.color:
                        if la_torre.moved:
                            se_puede = False

                    else:
                        se_puede = False
                
                else:
                    se_puede = False

                if se_puede:
                    self.enroques[i] = se_puede
                    movimientos.append(casillas[0])
        
        return movimientos, controladas


    def manejar_checks(self, amenazas):
        self.is_in_check = True
        self.amenazas += amenazas

class Caballo(Pieza):
    def __init__(self, color, idx, valor=3):
        super().__init__(color, valor, idx, False)
        self.pieza = 5
        self.movimientos = [np.array([2,1]), np.array([2,-1]), np.array([-2,1]), np.array([-2,-1]), np.array([1,2]), np.array([1,-2]), np.array([-1,2]), np.array([-1,-2])]

class Peon(Pieza): 
    def __init__(self, color, idx, valor=1):
        super().__init__(color, valor, idx, False)
        self.pieza = 3
        self.movimientos = [np.array([0, tools.color_to_meth.get(self.color)]), np.array([0, 2*tools.color_to_meth.get(self.color)]), np.array([1, tools.color_to_meth.get(self.color)]), np.array([-1, tools.color_to_meth.get(self.color)])]
    
    def get_moves(self, ocupadas, al_paso, controladas):
        movimientos = []
        for m in self.movimientos:
            if np.array_equal(m,np.array([0, 2*tools.color_to_meth.get(self.color)])): #peones moviendo dos casillas
                if self.idx[1] == tools.salida_cond.get(self.color):
                    coord = self.idx + m
                    key = tuple(map(int,coord))
                    if np.all(0 <= coord) and np.all(coord < 8) and key not in ocupadas: #esto puede ser que sobre porque por las condiciones y el tipo de movimiento no debería poder salirse del tablero, pero bueno
                        movimientos.append(tuple(coord))

            elif np.array_equal(m,np.array([0, tools.color_to_meth.get(self.color)])):#mover uno
                coord = self.idx + m
                key = tuple(map(int,coord))
                if np.all(0 <= coord) and np.all(coord < 8) and key not in ocupadas:
                    movimientos.append(tuple(coord)) #y nada mas porque son peones

            else:#capturas
                coord = self.idx + m
                key = tuple(map(int, coord))
                if 0<=key[0]<8 and 0<=key[1]<8:
                    controladas.add(key)
                    if (key in ocupadas and ocupadas[key].color != self.color):
                        movimientos.append(tuple(coord))
                        if isinstance(ocupadas[key], Rey):
                            amenazas = [tuple(map(int,self.idx))]
                            amenazas += key 
                            ocupadas[key].manejar_checks(amenazas)    
                    elif key in al_paso:
                        movimientos.append(tuple(coord))                    

        return movimientos, controladas
    
    def coronar(self, tipo):
        x,y = CELDA_SIZE*self.idx[0]+CELDA_SIZE//2, CELDA_SIZE*self.idx[1]+CELDA_SIZE//2
        nuevo = PIEZAS[tipo](self.color, self.idx, (x,y))

        return nuevo



class Rey(Rey, pygame.sprite.Sprite):
    def __init__(self, color, idx, pos):
        super().__init__(color, idx)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(f"C:/Users/Josh/Desktop/CHE$$/2.0/sprites/{color}king.png").convert_alpha(), (45,45))
        self.rect = self.image.get_rect(center=pos)
        self.idx = idx

class Reina(Reina, pygame.sprite.Sprite):
    def __init__(self, color, idx, pos):
        super().__init__(color, idx)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(f"C:/Users/Josh/Desktop/CHE$$/2.0/sprites/{color}q.png").convert_alpha(), (45,45))
        self.rect = self.image.get_rect(center=pos)
        self.idx = idx

class Torre(Torre, pygame.sprite.Sprite):
    def __init__(self, color, idx, pos):
        super().__init__(color, idx)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(f"C:/Users/Josh/Desktop/CHE$$/2.0/sprites/{color}r.png").convert_alpha(), (45,45))
        self.rect = self.image.get_rect(center=pos)
        self.idx = idx

class Caballo(Caballo, pygame.sprite.Sprite):
    def __init__(self, color, idx, pos):
        super().__init__(color, idx)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(f"C:/Users/Josh/Desktop/CHE$$/2.0/sprites/{color}k.png").convert_alpha(), (45,45))
        self.rect = self.image.get_rect(center=pos)
        self.idx = idx

class Alfil(Alfil, pygame.sprite.Sprite):
    def __init__(self,color, idx, pos):
        super().__init__(color, idx)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(f"C:/Users/Josh/Desktop/CHE$$/2.0/sprites/{color}b.png").convert_alpha(), (45,45))
        self.rect = self.image.get_rect(center=pos)
        self.idx = idx

class Peon(Peon, pygame.sprite.Sprite):
    def __init__(self,color, idx, pos):
        super().__init__(color, idx)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(f"C:/Users/Josh/Desktop/CHE$$/2.0/sprites/{color}p.png").convert_alpha(), (45,45))
        self.rect = self.image.get_rect(center=pos)
        self.idx = idx

PIEZAS = {
    3 : Peon,
    5 : Caballo,
    7 : Alfil,
    11 : Torre,
    13 : Reina,
    17 : Rey
}
