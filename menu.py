import pygame
import sys

def mostrar_menu_coronacion(pantalla, color_peon, centro_x, centro_y, sprites_piezas):
    """
    Muestra un menú de coronación de peón en el centro de la pantalla y espera la selección del usuario.

    Parámetros:
        pantalla (pygame.Surface): Superficie donde se dibuja el menú.
        color_peon (str): "blanco" o "negro".
        centro_x, centro_y (int): Coordenadas del centro donde se ubicará el menú.
        sprites_piezas (dict): Diccionario con claves como "blanco_reina", "negro_torre", etc.
    """

    # Orden y valores de retorno
    piezas = [("reina", 13), ("torre", 11), ("alfil", 7), ("caballo", 5)]

    # Tamaños y estilo
    borde = 2
    margen = 5
    color_borde = (30, 170, 30)
    color_fondo = (200, 200, 200)

    # Asumimos que todos los sprites tienen el mismo tamaño
    ejemplo_sprite = sprites_piezas[f"{color_peon}_reina"]
    sprite_w, sprite_h = ejemplo_sprite.get_size()

    # Calcular dimensiones del menú
    total_w = 4 * sprite_w + 3 * margen + 2 * borde * 4
    total_h = sprite_h + 2 * borde
    menu_x = centro_x - total_w // 2
    menu_y = centro_y - total_h // 2

    # Crear superficie del menú
    menu_surface = pygame.Surface((total_w, total_h))
    menu_surface.fill(color_fondo)

    # Dibujar las 4 piezas en fila
    posiciones = []
    x_actual = borde
    for nombre_pieza, _ in piezas:
        sprite = sprites_piezas[f"{color_peon}_{nombre_pieza}"]
        rect = pygame.Rect(x_actual, borde, sprite_w, sprite_h)
        pygame.draw.rect(menu_surface, color_borde, rect.inflate(borde * 2, borde * 2), border_radius=3)
        menu_surface.blit(sprite, rect)
        posiciones.append(rect.move(menu_x, menu_y))  # Rect global
        x_actual += sprite_w + margen + 2 * borde

    # Mostrar el menú
    pantalla.blit(menu_surface, (menu_x, menu_y))
    pygame.display.flip()

    # Esperar selección del usuario
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                for i, rect in enumerate(posiciones):
                    if rect.collidepoint(mouse_x, mouse_y):
                        return piezas[i][1]  # Devuelve el código correspondiente
