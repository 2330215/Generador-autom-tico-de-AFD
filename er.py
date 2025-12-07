import pygame
import sys
import subprocess
from collections import deque

pygame.init()
info = pygame.display.Info()
W, H = info.current_w - 100, info.current_h - 100
win = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Conversor ER -> AFND -> AFD")
pygame.scrap.init()
pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

WHITE, BLACK, GRAY, LIGHT = (255,255,255), (0,0,0), (200,200,200), (230,230,230)
BLUE, GREEN, RED = (100,150,255), (100,200,100), (255,100,100)

ft, fl, fs, fi = [pygame.font.SysFont(None, s) for s in [48,32,24,28]]

class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
    
    def epsilon_closure(self, state_set):
        closure = set(state_set)
        stack = list(state_set)
        while stack:
            state = stack.pop()
            if state in self.transitions and 'ε' in self.transitions[state]:
                for next_state in self.transitions[state]['ε']:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        return closure
    
    def process_input(self, input_string):
        current_states = self.epsilon_closure({self.start_state})
        for symbol in input_string:
            if symbol not in self.alphabet and symbol != 'ε':
                return False, f"Símbolo '{symbol}' no está en el alfabeto"
            next_states = set()
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    next_states.update(self.transitions[state][symbol])
            current_states = self.epsilon_closure(next_states)
            if not current_states:
                return False, "Sin estados activos"
        accepted = any(state in self.accept_states for state in current_states)
        return accepted, "Aceptado" if accepted else "Rechazado"
    
    def to_dfa(self):
        dfa_states = set()
        dfa_transitions = {}
        dfa_start_state = frozenset(self.epsilon_closure({self.start_state}))
        dfa_accept_states = set()
        queue = deque([dfa_start_state])
        dfa_states.add(dfa_start_state)
        if any(state in self.accept_states for state in dfa_start_state):
            dfa_accept_states.add(dfa_start_state)
        while queue:
            current_dfa_state = queue.popleft()
            dfa_transitions[current_dfa_state] = {}
            for symbol in self.alphabet:
                if symbol == 'ε':
                    continue
                next_nfa_states = set()
                for nfa_state in current_dfa_state:
                    if nfa_state in self.transitions and symbol in self.transitions[nfa_state]:
                        next_nfa_states.update(self.transitions[nfa_state][symbol])
                next_dfa_state = frozenset(self.epsilon_closure(next_nfa_states))
                if not next_dfa_state:
                    next_dfa_state = frozenset(['qT'])
                    if next_dfa_state not in dfa_states:
                        dfa_states.add(next_dfa_state)
                        queue.append(next_dfa_state)
                dfa_transitions[current_dfa_state][symbol] = next_dfa_state
                if next_dfa_state not in dfa_states:
                    dfa_states.add(next_dfa_state)
                    queue.append(next_dfa_state)
                    if any(state in self.accept_states for state in next_dfa_state):
                        dfa_accept_states.add(next_dfa_state)
        for state in list(dfa_states):
            if state == frozenset(['qT']):
                if state not in dfa_transitions:
                    dfa_transitions[state] = {}
                for symbol in self.alphabet:
                    if symbol != 'ε':
                        dfa_transitions[state][symbol] = state
        state_mapping = {state: f"q{i}" for i, state in enumerate(sorted(dfa_states, key=str))}
        readable_transitions = {}
        for state, transitions in dfa_transitions.items():
            readable_state = state_mapping[state]
            readable_transitions[readable_state] = {
                symbol: state_mapping[next_state] 
                for symbol, next_state in transitions.items()
            }
        return {
            'states': set(state_mapping.values()),
            'alphabet': self.alphabet - {'ε'},
            'transitions': readable_transitions,
            'start_state': state_mapping[dfa_start_state],
            'accept_states': {state_mapping[s] for s in dfa_accept_states}
        }

def er_to_nfa(regex):
    state_counter = [0]
    def new_state():
        state_counter[0] += 1
        return f"q{state_counter[0]}"
    def build_nfa(expr):
        if not expr:
            start = new_state()
            accept = new_state()
            return {'start': start,'accept': accept,'transitions': {start: {'ε': {accept}}},'states': {start, accept}}
        if len(expr) == 1 and expr.isalnum():
            start = new_state()
            accept = new_state()
            return {'start': start,'accept': accept,'transitions': {start: {expr: {accept}}},'states': {start, accept}}
        if expr.endswith('*'):
            base = build_nfa(expr[:-1])
            new_start = new_state()
            new_accept = new_state()
            transitions = base['transitions'].copy()
            transitions[new_start] = {'ε': {base['start'], new_accept}}
            transitions[base['accept']] = {'ε': {base['start'], new_accept}}
            return {'start': new_start,'accept': new_accept,'transitions': transitions,'states': base['states'] | {new_start, new_accept}}
        if '|' in expr:
            parts = expr.split('|', 1)
            left = build_nfa(parts[0])
            right = build_nfa(parts[1])
            new_start = new_state()
            new_accept = new_state()
            transitions = {**left['transitions'], **right['transitions']}
            transitions[new_start] = {'ε': {left['start'], right['start']}}
            transitions[left['accept']] = {'ε': {new_accept}}
            transitions[right['accept']] = {'ε': {new_accept}}
            return {'start': new_start,'accept': new_accept,'transitions': transitions,'states': left['states'] | right['states'] | {new_start, new_accept}}
        mid = len(expr) // 2
        left = build_nfa(expr[:mid])
        right = build_nfa(expr[mid:])
        transitions = {**left['transitions'], **right['transitions']}
        if left['accept'] not in transitions:
            transitions[left['accept']] = {}
        transitions[left['accept']]['ε'] = {right['start']}
        return {'start': left['start'],'accept': right['accept'],'transitions': transitions,'states': left['states'] | right['states']}
    try:
        nfa_data = build_nfa(regex)
        alphabet = {'ε'}
        for trans in nfa_data['transitions'].values():
            alphabet.update(trans.keys())
        return NFA(states=nfa_data['states'],alphabet=alphabet,transitions=nfa_data['transitions'],start_state=nfa_data['start'],accept_states={nfa_data['accept']})
    except:
        return None

class App:
    def __init__(self):
        self.msg = ""
        self.result = ""
        self.fase = "entrada"
        self.inputs = {'regex': '', 'cadena': ''}
        self.activo = None
        self.nfa = None
        self.dfa = None
    
    def convertir_er_a_nfa(self):
        regex = self.inputs['regex'].strip()
        if not regex:
            self.msg = "Error: Ingresa una expresión regular"
            return
        self.nfa = er_to_nfa(regex)
        self.msg = f"AFND creado: {len(self.nfa.states)} estados" if self.nfa else "Error: No se pudo crear el AFND"
    
    def probar_cadena(self):
        if not self.nfa:
            self.msg = "Error: Primero convierte la ER a AFND"
            return
        cadena = self.inputs['cadena'].strip()
        aceptado, mensaje = self.nfa.process_input(cadena)
        self.result = f"Cadena '{cadena}': {mensaje}"
    
    def convertir_a_dfa(self):
        if not self.nfa:
            self.msg = "Error: Primero crea un AFND"
            return
        self.dfa = self.nfa.to_dfa()
        self.fase = "resultado"

    def draw_button_menu(self):
        btn_menu = pygame.Rect(20, 20, 140, 45)
        pygame.draw.rect(win, RED, btn_menu, border_radius=10)
        win.blit(fs.render("MENÚ", True, WHITE), (btn_menu.centerx-30, btn_menu.centery-10))
        return btn_menu

    def draw_input(self):
        btn_menu = self.draw_button_menu()
        y = 80
        t = ft.render("Conversor ER -> AFND -> AFD", True, BLACK)
        win.blit(t, (W//2 - t.get_width()//2, y))
        y += 60
        labels = [('regex', 'Expresión Regular (ej: ab|ba, a*b):'),('cadena', 'Cadena a probar:')]
        for k, lbl in labels:
            win.blit(fl.render(lbl, True, BLACK), (50, y))
            y += 35
            rect = pygame.Rect(50, y, W-100, 40)
            pygame.draw.rect(win, LIGHT, rect)
            pygame.draw.rect(win, BLUE if self.activo==k else GRAY, rect, 3 if self.activo==k else 2)
            txt = self.inputs[k]
            surf = fi.render(txt, True, BLACK)
            if surf.get_width() > rect.width - 20:
                chars = max(1, int(len(txt) * (rect.width-20) / surf.get_width()))
                surf = fi.render("..." + txt[-chars:], True, BLACK)
            win.blit(surf, (rect.x+10, rect.y+8))
            y += 55
        btn_convertir = pygame.Rect(W//2-300, H-120, 200, 50)
        btn_probar = pygame.Rect(W//2-90, H-120, 180, 50)
        btn_dfa = pygame.Rect(W//2+100, H-120, 200, 50)
        pygame.draw.rect(win, GREEN, btn_convertir, border_radius=10)
        pygame.draw.rect(win, BLUE, btn_probar, border_radius=10)
        pygame.draw.rect(win, RED, btn_dfa, border_radius=10)
        win.blit(fs.render("Crear AFND", True, WHITE), (btn_convertir.centerx-50, btn_convertir.centery-10))
        win.blit(fs.render("Probar", True, WHITE), (btn_probar.centerx-35, btn_probar.centery-10))
        win.blit(fs.render("Ver AFD", True, WHITE), (btn_dfa.centerx-45, btn_dfa.centery-10))
        if self.msg:
            m = fs.render(self.msg, True, GREEN if "creado" in self.msg else RED)
            win.blit(m, (W//2 - m.get_width()//2, H-70))
        if self.result:
            m = fl.render(self.result, True, GREEN if "Aceptado" in self.result else RED)
            win.blit(m, (W//2 - m.get_width()//2, H-40))
        return btn_menu, btn_convertir, btn_probar, btn_dfa
    
    def draw_result(self):
        btn_menu = self.draw_button_menu()
        y = 80
        win.blit(ft.render("AFD Resultante", True, BLACK), (W//2-120, y))
        y += 60
        labels = [
            ('states', 'Estados:'),
            ('alphabet', 'Alfabeto:'),
            ('start_state', 'Estado Inicial:'),
            ('accept_states', 'Estados Finales:'),
            ('transitions', 'Transiciones:')
        ]
        for k, lbl in labels:
            win.blit(fl.render(lbl, True, BLACK), (50, y))
            y += 35
            if k == "transitions":
                for state, trans in sorted(self.dfa[k].items()):
                    trans_str = f"{state}: {trans}"
                    win.blit(fs.render(trans_str, True, GREEN), (70, y))
                    y += 30
            else:
                string_var = ', '.join(sorted(self.dfa[k]))
                win.blit(fl.render(string_var, True, GREEN), (70, y))
            y += 40
        btn_volver = pygame.Rect(W//2-100, H-80, 200, 50)
        pygame.draw.rect(win, BLUE, btn_volver, border_radius=10)
        win.blit(fl.render("Volver", True, WHITE), (btn_volver.centerx-30, btn_volver.centery-12))
        return btn_menu, btn_volver
    
    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(20, 20, 140, 45).collidepoint(e.pos):
                pygame.quit()
                subprocess.Popen([sys.executable, "inicio.py"])
                sys.exit()

            if self.fase == "entrada":
                y = 115
                for k in ['regex', 'cadena']:
                    if pygame.Rect(50, y, W-100, 40).collidepoint(e.pos):
                        self.activo = k
                        return
                    y += 90
                if pygame.Rect(W//2-300, H-120, 200, 50).collidepoint(e.pos):
                    self.convertir_er_a_nfa()
                    return
                if pygame.Rect(W//2-90, H-120, 180, 50).collidepoint(e.pos):
                    self.probar_cadena()
                    return
                if pygame.Rect(W//2+100, H-120, 200, 50).collidepoint(e.pos):
                    self.convertir_a_dfa()
                    return
                self.activo = None
            else:
                if pygame.Rect(W//2-100, H-80, 200, 50).collidepoint(e.pos):
                    self.__init__()

        elif e.type == pygame.KEYDOWN and self.activo:
            ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
            if ctrl and e.key == pygame.K_c:
                pygame.scrap.put(pygame.SCRAP_TEXT, self.inputs[self.activo].encode())
            elif ctrl and e.key == pygame.K_v:
                try:
                    clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if clip:
                        self.inputs[self.activo] += clip.decode().replace("\x00", "")
                except:
                    pass
            elif ctrl and e.key == pygame.K_x:
                pygame.scrap.put(pygame.SCRAP_TEXT, self.inputs[self.activo].encode())
                self.inputs[self.activo] = ""
            elif e.key == pygame.K_BACKSPACE:
                self.inputs[self.activo] = self.inputs[self.activo][:-1]
            elif e.key in (pygame.K_RETURN, pygame.K_TAB):
                keys = list(self.inputs.keys())
                self.activo = keys[(keys.index(self.activo)+1) % len(keys)]
            else:
                self.inputs[self.activo] += e.unicode

app = App()
clock = pygame.time.Clock()

while True:
    win.fill(WHITE)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        app.event(e)
    if app.fase == "entrada":
        app.draw_input()
    else:
        app.draw_result()
    pygame.display.update()
    clock.tick(60)
