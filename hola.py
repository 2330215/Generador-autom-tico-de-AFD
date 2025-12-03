import pygame
import sys
import json
from collections import defaultdict
import pyperclip  # pip install pyperclip

pygame.init()

# Configuración de ventana - MAXIMIZADA (no fullscreen)
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w - 100, info.current_h - 100
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Minimización de AFD")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
BLUE = (100, 150, 255)
GREEN = (100, 200, 100)
RED = (255, 100, 100)
DARK_GRAY = (150, 150, 150)

# Fuentes
title_font = pygame.font.SysFont(None, 48)
label_font = pygame.font.SysFont(None, 32)
small_font = pygame.font.SysFont(None, 24)
input_font = pygame.font.SysFont(None, 28)


class AFD:
    def __init__(self):
        self.estados = set()
        self.alfabeto = set()
        self.transiciones = {}  # {(estado, simbolo): estado_destino}
        self.estado_inicial = None
        self.estados_finales = set()
    
    def agregar_estado(self, estado):
        self.estados.add(estado)
    
    def agregar_transicion(self, origen, simbolo, destino):
        self.transiciones[(origen, simbolo)] = destino
        self.alfabeto.add(simbolo)
    
    def eliminar_inalcanzables(self):
        """Elimina estados inalcanzables desde el estado inicial"""
        if not self.estado_inicial:
            return set()
        
        alcanzables = set()
        por_visitar = [self.estado_inicial]
        
        while por_visitar:
            actual = por_visitar.pop()
            if actual in alcanzables:
                continue
            alcanzables.add(actual)
            
            for simbolo in self.alfabeto:
                if (actual, simbolo) in self.transiciones:
                    destino = self.transiciones[(actual, simbolo)]
                    if destino not in alcanzables:
                        por_visitar.append(destino)
        
        # Eliminar estados inalcanzables
        inalcanzables = self.estados - alcanzables
        self.estados = alcanzables
        self.estados_finales = self.estados_finales & alcanzables
        
        # Limpiar transiciones
        nuevas_trans = {}
        for (origen, simbolo), destino in self.transiciones.items():
            if origen in alcanzables and destino in alcanzables:
                nuevas_trans[(origen, simbolo)] = destino
        self.transiciones = nuevas_trans
        
        return inalcanzables
    
    def minimizar(self):
        """Minimiza el AFD usando el algoritmo de partición"""
        # Paso 1: Eliminar inalcanzables
        inalcanzables = self.eliminar_inalcanzables()
        
        # Paso 2: Partición inicial
        finales = self.estados_finales
        no_finales = self.estados - finales
        
        particiones = []
        if no_finales:
            particiones.append(frozenset(no_finales))
        if finales:
            particiones.append(frozenset(finales))
        
        # Paso 3: Refinamiento
        cambio = True
        while cambio:
            cambio = False
            nuevas_particiones = []
            
            for particion in particiones:
                # Agrupar estados por su comportamiento
                grupos = defaultdict(list)
                
                for estado in particion:
                    firma = []
                    for simbolo in sorted(self.alfabeto):
                        if (estado, simbolo) in self.transiciones:
                            destino = self.transiciones[(estado, simbolo)]
                            # Encontrar a qué partición pertenece el destino
                            for i, p in enumerate(particiones):
                                if destino in p:
                                    firma.append(i)
                                    break
                        else:
                            firma.append(-1)  # Sin transición
                    
                    grupos[tuple(firma)].append(estado)
                
                # Si se dividió la partición, hay cambio
                if len(grupos) > 1:
                    cambio = True
                    for grupo in grupos.values():
                        nuevas_particiones.append(frozenset(grupo))
                else:
                    nuevas_particiones.append(particion)
            
            particiones = nuevas_particiones
        
        # Paso 4: Construir AFD minimizado
        afd_min = AFD()
        
        # Mapeo de estados viejos a particiones
        estado_a_particion = {}
        for i, particion in enumerate(particiones):
            nombre_particion = f"q{i}"
            afd_min.agregar_estado(nombre_particion)
            for estado in particion:
                estado_a_particion[estado] = nombre_particion
        
        # Estado inicial
        afd_min.estado_inicial = estado_a_particion[self.estado_inicial]
        
        # Estados finales
        for estado in self.estados_finales:
            afd_min.estados_finales.add(estado_a_particion[estado])
        
        # Transiciones
        for (origen, simbolo), destino in self.transiciones.items():
            part_origen = estado_a_particion[origen]
            part_destino = estado_a_particion[destino]
            afd_min.agregar_transicion(part_origen, simbolo, part_destino)
        
        return afd_min, particiones, inalcanzables


class MinimizadorAFD:
    def __init__(self):
        self.afd_original = AFD()
        self.afd_minimizado = None
        self.particiones = []
        self.inalcanzables = set()
        self.mensaje = ""
        self.fase = "entrada"  # entrada, resultado
        
        # Inputs
        self.inputs = {
            'estados': '',
            'alfabeto': '',
            'inicial': '',
            'finales': '',
            'transiciones': ''
        }
        self.input_activo = None
        
    def parsear_afd(self):
        """Parsea los inputs y crea el AFD"""
        try:
            # Estados
            estados = self.inputs['estados'].strip().split(',')
            for e in estados:
                e = e.strip()
                if e:
                    self.afd_original.agregar_estado(e)
            
            # Alfabeto
            alfabeto = self.inputs['alfabeto'].strip().split(',')
            for s in alfabeto:
                s = s.strip()
                if s:
                    self.afd_original.alfabeto.add(s)
            
            # Estado inicial
            inicial = self.inputs['inicial'].strip()
            if inicial not in self.afd_original.estados:
                return False, "Estado inicial no está en el conjunto de estados"
            self.afd_original.estado_inicial = inicial
            
            # Estados finales
            finales = self.inputs['finales'].strip().split(',')
            for f in finales:
                f = f.strip()
                if f:
                    if f not in self.afd_original.estados:
                        return False, f"Estado final '{f}' no está en el conjunto de estados"
                    self.afd_original.estados_finales.add(f)
            
            # Transiciones (formato: q0,a,q1;q1,b,q2)
            trans_str = self.inputs['transiciones'].strip()
            if trans_str:
                transiciones = trans_str.split(';')
                for t in transiciones:
                    partes = t.strip().split(',')
                    if len(partes) == 3:
                        origen, simbolo, destino = [p.strip() for p in partes]
                        if origen not in self.afd_original.estados:
                            return False, f"Estado '{origen}' no existe"
                        if destino not in self.afd_original.estados:
                            return False, f"Estado '{destino}' no existe"
                        if simbolo not in self.afd_original.alfabeto:
                            return False, f"Símbolo '{simbolo}' no está en el alfabeto"
                        self.afd_original.agregar_transicion(origen, simbolo, destino)
            
            return True, "AFD parseado correctamente"
            
        except Exception as e:
            return False, f"Error al parsear: {str(e)}"
    
    def minimizar(self):
        """Ejecuta la minimización"""
        exito, msg = self.parsear_afd()
        if not exito:
            self.mensaje = msg
            return
        
        try:
            self.afd_minimizado, self.particiones, self.inalcanzables = self.afd_original.minimizar()
            self.fase = "resultado"
            self.mensaje = "Minimización completada"
        except Exception as e:
            self.mensaje = f"Error en minimización: {str(e)}"
    
    def dibujar_entrada(self):
        """Dibuja la interfaz de entrada"""
        y_offset = 80
        
        # Título
        titulo = title_font.render("Minimización de AFD", True, BLACK)
        win.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 20))
        
        # Instrucciones
        inst = small_font.render("Ingrese los datos del AFD (separados por comas) - Ctrl+C/Ctrl+V habilitado", True, DARK_GRAY)
        win.blit(inst, (50, y_offset))
        y_offset += 40
        
        # Campos de entrada
        campos = [
            ('estados', 'Estados (ej: q0,q1,q2):'),
            ('alfabeto', 'Alfabeto (ej: a,b):'),
            ('inicial', 'Estado inicial (ej: q0):'),
            ('finales', 'Estados finales (ej: q2,q3):'),
            ('transiciones', 'Transiciones (formato: origen,símbolo,destino;...)'),
        ]
        
        for key, label in campos:
            # Label
            label_surf = label_font.render(label, True, BLACK)
            win.blit(label_surf, (50, y_offset))
            y_offset += 35
            
            # Input box
            color = BLUE if self.input_activo == key else GRAY
            input_rect = pygame.Rect(50, y_offset, WIDTH - 100, 40)
            pygame.draw.rect(win, LIGHT_GRAY, input_rect)
            pygame.draw.rect(win, color, input_rect, 2)
            
            # Texto del input con scroll horizontal si es muy largo
            texto_completo = self.inputs[key]
            max_width = input_rect.width - 20
            texto_render = input_font.render(texto_completo, True, BLACK)
            
            # Si el texto es muy largo, mostrar solo el final
            if texto_render.get_width() > max_width:
                # Calcular cuántos caracteres caben
                chars_visible = int(len(texto_completo) * max_width / texto_render.get_width())
                texto_mostrar = "..." + texto_completo[-chars_visible:]
                texto_render = input_font.render(texto_mostrar, True, BLACK)
            
            win.blit(texto_render, (input_rect.x + 10, input_rect.y + 8))
            y_offset += 60
        
        # Ejemplo
        y_offset += 10
        ejemplo = small_font.render("Ejemplo de transiciones: q0,a,q1;q1,b,q2;q2,a,q0", True, DARK_GRAY)
        win.blit(ejemplo, (50, y_offset))
        
        # Botón minimizar
        boton_min = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 300, 50)
        pygame.draw.rect(win, GREEN, boton_min)
        texto_boton = label_font.render("MINIMIZAR", True, BLACK)
        win.blit(texto_boton, (boton_min.x + boton_min.width // 2 - texto_boton.get_width() // 2,
                                boton_min.y + 12))
        
        # Mensaje
        if self.mensaje:
            color_msg = RED if "Error" in self.mensaje else GREEN
            msg_surf = small_font.render(self.mensaje, True, color_msg)
            win.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, HEIGHT - 140))
        
        return boton_min
    
    def dibujar_resultado(self):
        """Dibuja los resultados de la minimización"""
        y = 20
        
        # Título
        titulo = title_font.render("Resultado de la Minimización", True, BLACK)
        win.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, y))
        y += 60
        
        # AFD Original
        col1_x = 50
        col2_x = WIDTH // 2 + 50
        
        # Columna 1: AFD Original
        texto = label_font.render("AFD Original:", True, BLACK)
        win.blit(texto, (col1_x, y))
        y += 35
        
        info_original = [
            f"Estados: {', '.join(sorted(self.afd_original.estados))}",
            f"Estado inicial: {self.afd_original.estado_inicial}",
            f"Estados finales: {', '.join(sorted(self.afd_original.estados_finales))}",
            f"Alfabeto: {', '.join(sorted(self.afd_original.alfabeto))}",
            f"Total estados: {len(self.afd_original.estados)}"
        ]
        
        for linea in info_original:
            texto = small_font.render(linea, True, BLACK)
            win.blit(texto, (col1_x, y))
            y += 28
        
        # Estados inalcanzables
        if self.inalcanzables:
            y += 10
            texto = small_font.render(f"Inalcanzables eliminados: {', '.join(sorted(self.inalcanzables))}", 
                                     True, RED)
            win.blit(texto, (col1_x, y))
            y += 28
        
        # Particiones
        y += 20
        texto = label_font.render("Particiones encontradas:", True, BLACK)
        win.blit(texto, (col1_x, y))
        y += 35
        
        for i, particion in enumerate(self.particiones):
            texto = small_font.render(f"P{i}: {{{', '.join(sorted(particion))}}}", True, DARK_GRAY)
            win.blit(texto, (col1_x, y))
            y += 28
        
        # Columna 2: AFD Minimizado
        y = 80
        texto = label_font.render("AFD Minimizado:", True, GREEN)
        win.blit(texto, (col2_x, y))
        y += 35
        
        info_min = [
            f"Estados: {', '.join(sorted(self.afd_minimizado.estados))}",
            f"Estado inicial: {self.afd_minimizado.estado_inicial}",
            f"Estados finales: {', '.join(sorted(self.afd_minimizado.estados_finales))}",
            f"Total estados: {len(self.afd_minimizado.estados)}"
        ]
        
        for linea in info_min:
            texto = small_font.render(linea, True, BLACK)
            win.blit(texto, (col2_x, y))
            y += 28
        
        # Transiciones minimizadas
        y += 20
        texto = label_font.render("Transiciones:", True, BLACK)
        win.blit(texto, (col2_x, y))
        y += 35
        
        for (origen, simbolo), destino in sorted(self.afd_minimizado.transiciones.items()):
            texto = small_font.render(f"δ({origen}, {simbolo}) = {destino}", True, DARK_GRAY)
            win.blit(texto, (col2_x, y))
            y += 28
            if y > HEIGHT - 150:
                break
        
        # Botón volver
        boton_volver = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 80, 200, 50)
        pygame.draw.rect(win, BLUE, boton_volver)
        texto_boton = label_font.render("VOLVER", True, BLACK)
        win.blit(texto_boton, (boton_volver.x + boton_volver.width // 2 - texto_boton.get_width() // 2,
                               boton_volver.y + 12))
        
        return boton_volver
    
    def manejar_evento(self, event):
        """Maneja eventos de pygame"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.fase == "entrada":
                # Verificar clicks en inputs
                y_offset = 160
                for key in ['estados', 'alfabeto', 'inicial', 'finales', 'transiciones']:
                    input_rect = pygame.Rect(50, y_offset, WIDTH - 100, 40)
                    if input_rect.collidepoint(event.pos):
                        self.input_activo = key
                        return None
                    y_offset += 95
                
                # Botón minimizar
                boton_min = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 300, 50)
                if boton_min.collidepoint(event.pos):
                    self.minimizar()
                    return None
                
                self.input_activo = None
                
            elif self.fase == "resultado":
                boton_volver = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 80, 200, 50)
                if boton_volver.collidepoint(event.pos):
                    return "menu"
        
        elif event.type == pygame.KEYDOWN and self.input_activo:
            # COPIAR: Ctrl+C
            if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                try:
                    pyperclip.copy(self.inputs[self.input_activo])
                    self.mensaje = "Texto copiado al portapapeles"
                except:
                    self.mensaje = "No se pudo copiar (instale pyperclip)"
            
            # PEGAR: Ctrl+V
            elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                try:
                    texto_pegado = pyperclip.paste()
                    self.inputs[self.input_activo] += texto_pegado
                    self.mensaje = "Texto pegado"
                except:
                    self.mensaje = "No se pudo pegar (instale pyperclip)"
            
            # BACKSPACE
            elif event.key == pygame.K_BACKSPACE:
                self.inputs[self.input_activo] = self.inputs[self.input_activo][:-1]
            
            # ENTER o TAB: siguiente campo
            elif event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                keys = list(self.inputs.keys())
                idx = keys.index(self.input_activo)
                self.input_activo = keys[(idx + 1) % len(keys)]
            
            # Caracteres normales
            else:
                self.inputs[self.input_activo] += event.unicode
        
        return None


def main():
    clock = pygame.time.Clock()
    minimizador = MinimizadorAFD()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            resultado = minimizador.manejar_evento(event)
            if resultado == "menu":
                pygame.quit()
                import subprocess
                subprocess.Popen([sys.executable, "menu.py"])
                sys.exit()
        
        win.fill(WHITE)
        
        if minimizador.fase == "entrada":
            minimizador.dibujar_entrada()
        else:
            minimizador.dibujar_resultado()
        
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()