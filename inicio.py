import pygame
import sys
import subprocess


pygame.init()

# Aca estan las dimesiones de la ventana, colores y la fuente que se usa
width, height = 1400, 780
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Menú Principal")
black = (0, 0, 0)
white = (255, 255, 255)
gray = (150, 150, 150)
title_font = pygame.font.SysFont(None, 96)
button_font = pygame.font.SysFont(None, 36)

#rutas de los archivos
PYTHON_FILE_1 = "pelea.py"
PYTHON_FILE_2 = "hola.py"
PYTHON_FILE_3 = "original.py"

# Esto sirve para abrir un archivo de python
def open_python_file(filepath):
    pygame.quit()
    subprocess.Popen([sys.executable, filepath])
    sys.exit()

# Esto crea los botoneses
def botones():
    # b1
    boton1 = pygame.Rect(500, 250, 400, 80)
    pygame.draw.rect(win, gray, boton1)
    win.blit(button_font.render("Modo pelea JcC", True, black), (620, 275))
    # b2
    boton2 = pygame.Rect(500, 360, 400, 80)
    pygame.draw.rect(win, gray, boton2)
    win.blit(button_font.render("Minimización de AFD", True, black), (610, 385))
    # b3
    boton3 = pygame.Rect(500, 470, 400, 80)
    pygame.draw.rect(win, gray, boton3)
    win.blit(button_font.render("Modo original", True, black), (590, 495))
    #b4
    boton4 = pygame.Rect(500, 580, 400, 80)
    pygame.draw.rect(win, gray, boton4)
    win.blit(button_font.render("Salir", True, black), (580, 605))
    return boton1, boton2, boton3, boton4

# Flujo principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            boton1, boton2, boton3, boton4 = botones()
            
            if boton1.collidepoint(event.pos):
                open_python_file(PYTHON_FILE_1)
            elif boton2.collidepoint(event.pos):
                open_python_file(PYTHON_FILE_2)
            elif boton3.collidepoint(event.pos):
                open_python_file(PYTHON_FILE_3)
            elif boton4.collidepoint(event.pos):
                 pygame.quit()
                 sys.exit()
    win.fill(white)
    #aca se crea el titulo y los botoneses
    title_text = title_font.render("MENÚ PRINCIPAL", True, black)
    title_rect = title_text.get_rect(center=(width // 2, 120))
    win.blit(title_text, title_rect)
    botones()
    
    pygame.display.flip()