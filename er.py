import pygame
import sys
try:
    from automata.fa.dfa import DFA
    AUTOMATA = True
except:
    AUTOMATA = False
pygame.init()
info = pygame.display.Info()
W, H = info.current_w - 100, info.current_h - 100
win = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Minimización AFD")
pygame.scrap.init()
pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
# Colores
WHITE, BLACK, GRAY, LIGHT = (255,255,255), (0,0,0), (200,200,200), (230,230,230)
BLUE, GREEN, RED, DARK = (100,150,255), (100,200,100), (255,100,100), (150,150,150)
# Fuentes
ft, fl, fs, fi = [pygame.font.SysFont(None, s) for s in [48,32,24,28]]

class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        """
        Initialize an NFA
        
        Parameters:
        - states: set of state names (strings or integers)
        - alphabet: set of input symbols (strings)
        - transitions: dict of dicts: {state: {symbol: set of next states}}
        - start_state: the initial state
        - accept_states: set of accepting states
        """
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        
    def epsilon_closure(self, state_set):
        """Compute epsilon closure for a set of states (for NFAs with ε-transitions)"""
        closure = set(state_set)
        stack = list(state_set)
        
        while stack:
            state = stack.pop()
            # Check for ε-transitions (represented by 'ε' or '')
            if state in self.transitions:
                for symbol, next_states in self.transitions[state].items():
                    if symbol == 'ε' or symbol == '':
                        for next_state in next_states:
                            if next_state not in closure:
                                closure.add(next_state)
                                stack.append(next_state)
        return closure
    
    def process_input(self, input_string, verbose=False):
        """
        Process an input string through the NFA
        
        Returns:
        - True if the NFA accepts the string, False otherwise
        """
        # Start with epsilon closure of the start state
        current_states = self.epsilon_closure({self.start_state})
        
        if verbose:
            print(f"Start: {current_states}")
        
        # Process each symbol in the input string
        for i, symbol in enumerate(input_string):
            if verbose:
                print(f"Processing symbol '{symbol}'")
            
            # Check if symbol is in alphabet
            if symbol not in self.alphabet and symbol != 'ε':
                raise ValueError(f"Symbol '{symbol}' not in alphabet")
            
            # Compute next set of states
            next_states = set()
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    next_states.update(self.transitions[state][symbol])
            
            # Take epsilon closure of the new states
            current_states = self.epsilon_closure(next_states)
            if verbose:
                print(f"  After symbol '{symbol}': {current_states}")
            
            # If no states are active, reject early
            if not current_states:
                if verbose:
                    print(f"No active states after symbol {i+1}")
                return False
        
        if verbose:
            print(f"Final states: {current_states}")
            print(f"Accept states: {self.accept_states}")
        
        # Check if any of the current states is an accept state
        return any(state in self.accept_states for state in current_states)

    def to_dfa(self):
        """
        Convert NFA to DFA using subset construction (optional advanced feature)
        This is a simplified version without full optimization
        """
        from collections import deque
        
        # DFA components
        dfa_states = set()
        dfa_transitions = {}
        dfa_start_state = frozenset(self.epsilon_closure({self.start_state}))
        dfa_accept_states = set()
        
        # Queue for unprocessed DFA states
        queue = deque([dfa_start_state])
        dfa_states.add(dfa_start_state)
        
        # Check if start state is accepting
        if any(state in self.accept_states for state in dfa_start_state):
            dfa_accept_states.add(dfa_start_state)
        
        while queue:
            current_dfa_state = queue.popleft()
            
            # Initialize transitions for this DFA state
            dfa_transitions[current_dfa_state] = {}
            
            # For each symbol in alphabet (excluding epsilon)
            for symbol in self.alphabet:
                if symbol == 'ε':
                    continue
                    
                # Compute next NFA states
                next_nfa_states = set()
                for nfa_state in current_dfa_state:
                    if nfa_state in self.transitions and symbol in self.transitions[nfa_state]:
                        next_nfa_states.update(self.transitions[nfa_state][symbol])
                
                # Take epsilon closure
                next_dfa_state = frozenset(self.epsilon_closure(next_nfa_states))
                
                # Skip empty states
                if not next_dfa_state:
                    continue
                
                # Add transition
                dfa_transitions[current_dfa_state][symbol] = next_dfa_state
                
                # If new DFA state, add to queue
                if next_dfa_state not in dfa_states:
                    dfa_states.add(next_dfa_state)
                    queue.append(next_dfa_state)
                    
                    # Check if accepting
                    if any(state in self.accept_states for state in next_dfa_state):
                        dfa_accept_states.add(next_dfa_state)
        
        # Convert to string representation for readability
        state_mapping = {}
        for i, state in enumerate(dfa_states):
            state_name = f"q{i}"
            state_mapping[state] = state_name
        
        # Create readable DFA transitions
        readable_transitions = {}
        for state, transitions in dfa_transitions.items():
            readable_state = state_mapping[state]
            readable_transitions[readable_state] = {}
            for symbol, next_state in transitions.items():
                readable_transitions[readable_state][symbol] = state_mapping[next_state]
        
        return {
            'states': {state_mapping[s] for s in dfa_states},
            'alphabet': self.alphabet - {'ε'} if 'ε' in self.alphabet else self.alphabet,
            'transitions': readable_transitions,
            'start_state': state_mapping[dfa_start_state],
            'accept_states': {state_mapping[s] for s in dfa_accept_states}
        }


def example_nfa_1():
    """Example 1: NFA that accepts strings ending with '01'"""
    # States
    states = {'q0', 'q1', 'q2'}
    
    # Alphabet
    alphabet = {'0', '1'}
    
    # Transitions
    transitions = {
        'q0': {
            '0': {'q0', 'q1'},  # From q0 on 0: can stay in q0 OR go to q1
            '1': {'q0'}
        },
        'q1': {
            '0': {'q1'},
            '1': {'q2'}
            
        },
        'q2': {
            '1': {'q2'}
        }  # No transitions from accept state
    }
    
    # Start and accept states
    start_state = 'q0'
    accept_states = {'q2'}
    
    return NFA(states, alphabet, transitions, start_state, accept_states)


def example_nfa_2():
    """Example 2: NFA with ε-transitions that accepts strings with 'ab' or 'ba'"""
    # States
    states = {'q0', 'q1', 'q2', 'q3', 'q4'}
    
    # Alphabet
    alphabet = {'a', 'b', 'ε'}
    
    # Transitions (including ε-transitions)
    transitions = {
        'q0': {
            'ε': {'q1', 'q3'}  # ε-transition to both q1 and q3
        },
        'q1': {
            'a': {'q2'}
        },
        'q2': {
            'b': {'q4'}
        },
        'q3': {
            'b': {'q4'}
        },
        'q4': {}  # Accept state
    }
    
    # Start and accept states
    start_state = 'q0'
    accept_states = {'q4'}
    
    return NFA(states, alphabet, transitions, start_state, accept_states)


def test_nfa():
    """Test the NFA implementation with examples"""
    
    print("=" * 60)
    print("EXAMPLE 1: NFA that accepts strings ending with '01'")
    print("=" * 60)
    
    nfa1 = example_nfa_1()
    
    test_strings = ["01", "001", "101", "0101", "100", "011", "00101", "010"]
    
    for test_str in test_strings:
        result = nfa1.process_input(test_str, verbose=False)
        print(f"String '{test_str}': {'ACCEPTED' if result else 'REJECTED'}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE 2: NFA with -transitions (accepts 'ab' or 'ba')")
    print("=" * 60)
    """
    nfa2 = example_nfa_2()
    
    test_strings = ["ab", "ba", "a", "b", "abc", "aba", "bab"]
    
    for test_str in test_strings:
        try:
            result = nfa2.process_input(test_str, verbose=False)
            print(f"String '{test_str}': {'ACCEPTED' if result else 'REJECTED'}")
        except ValueError as e:
            print(f"String '{test_str}': ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("VERBOSE EXAMPLE: Processing '00101' with NFA1")
    print("=" * 60)
    """
    nfa1.process_input("011", verbose=True)
    print(nfa1.to_dfa())

def interactive_nfa():
    """Interactive mode to test custom NFAs"""
    print("\n" + "=" * 60)
    print("INTERACTIVE NFA BUILDER")
    print("=" * 60)
    
    # Get NFA parameters from user
    print("\nEnter states (comma-separated, e.g., q0,q1,q2):")
    states_input = input().strip()
    states = set(s.strip() for s in states_input.split(','))
    
    print("\nEnter alphabet symbols (comma-separated, e.g., 0,1):")
    alphabet_input = input().strip()
    alphabet = set(s.strip() for s in alphabet_input.split(','))
    
    print("\nEnter start state:")
    start_state = input().strip()
    
    print("\nEnter accept states (comma-separated):")
    accept_input = input().strip()
    accept_states = set(s.strip() for s in accept_input.split(','))
    
    # Build transitions
    transitions = {}
    print("\nDefine transitions (enter 'done' when finished):")
    print("Format: from_state symbol to_state1,to_state2,...")
    print("Example: q0 0 q0,q1")
    print("For ε-transitions, use 'ε' as symbol")
    
    while True:
        transition_input = input("Transition: ").strip()
        if transition_input.lower() == 'done':
            break
        
        parts = transition_input.split()
        if len(parts) != 3:
            print("Invalid format. Try again.")
            continue
        
        from_state, symbol, to_states_str = parts
        to_states = set(s.strip() for s in to_states_str.split(','))
        
        if from_state not in transitions:
            transitions[from_state] = {}
        
        transitions[from_state][symbol] = to_states
    
    # Create NFA
    nfa = NFA(states, alphabet, transitions, start_state, accept_states)
    
    # Test strings
    print("\n" + "=" * 60)
    print("TEST YOUR NFA")
    print("=" * 60)
    print("Enter strings to test (enter 'quit' to exit):")
    
    while True:
        test_str = input("\nTest string: ").strip()
        if test_str.lower() == 'quit':
            break
        
        try:
            verbose = input("Show detailed steps? (y/n): ").strip().lower() == 'y'
            result = nfa.process_input(test_str, verbose=verbose)
            print(f"\nResult: String '{test_str}' is {'ACCEPTED' if result else 'REJECTED'}")
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Run tests
    test_nfa()
    
    # Uncomment to run interactive mode
    #interactive_nfa()

class App:
    def __init__(self):
        self.dfa = self.dfa_min = None
        self.msg = ""
        self.result = ""
        self.fase = "entrada"
        self.inputs = {'estados':'', 'alfabeto':'', 'inicial':'', 'finales':'', 'trans':'', 'ER' :''}
        self.activo = None
        self.dfa = None

    def interactive_nfa(self):
        try:
            states_input = {e.strip() for e in self.inputs['estados'].split(',') if e.strip()}
            alphabet_input = {s.strip() for s in self.inputs['alfabeto'].split(',') if s.strip()}
            start_state = self.inputs['inicial'].strip()
            accept_input = {f.strip() for f in self.inputs['finales'].split(',') if f.strip()}
            er_input = self.inputs['ER'].strip()

        except Exception as e:
            self.msg = f" {e}"

        transitions = {}
        for t in self.inputs['trans'].split(';'):
            if not t.strip():
                continue
            parts = t.split()#x.strip() for x in t.split(',')]
            if len(parts) != 3:
                print(f"Invalid format. Try again. {parts}")
                self.msg = f" Formato: {t}"
                return
            from_state, symbol, to_states_str = parts
            to_states = set(s.strip() for s in to_states_str.split(','))
            
            if from_state not in transitions:
                transitions[from_state] = {}
            
            transitions[from_state][symbol] = to_states
        
        #transitions = trans
        print(transitions)
        # Create NFA
        nfa = NFA(states_input, alphabet_input, transitions, start_state, accept_input)
        
        # Test strings      
        test_str = er_input.strip()
        
        try:
            verbose = True
            result = nfa.process_input(test_str, verbose=verbose)
            self.dfa = nfa.to_dfa()
            print(f"\nResult: String '{test_str}' is {'ACCEPTED' if result else 'REJECTED'}")
            self.result = f"El resultado del String {test_str} es {'Aceptado' if result else 'Rechazado'}"
        except ValueError as e:
            print(f"Error: {e}")


    def draw_input(self):
        y = 20

        t = ft.render("Conversor de ER a AFND", True, BLACK)
        win.blit(t, (W//2 - t.get_width()//2, y))
        y += 60

        labels = [
            ('estados','Estados (q0,q1,q2):'),
            ('alfabeto','Alfabeto (a,b):'),
            ('inicial','Inicial (q0):'),
            ('finales','Finales (q2):'),
            ('trans','Trans (q0 0 q0,q1):'),
            ('ER','Expresion (1011)'),

        ]

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

        btn = pygame.Rect(W//2-150, H-120, 280, 50)
        pygame.draw.rect(win, GREEN, btn, border_radius=10)
        win.blit(fl.render("Convertir", True, WHITE), (btn.centerx-60, btn.centery-12))

        btn_dfa = pygame.Rect(W//2-110, H-60, 200, 30)
        pygame.draw.rect(win, GREEN, btn_dfa, border_radius=10)
        win.blit(fl.render("Convertir a DFA", True, WHITE), (btn_dfa.centerx-80, btn_dfa.centery-12))
                # Botón MENÚ (inicio)
        btn_menu = pygame.Rect(20, 20, 140, 40)
        pygame.draw.rect(win, RED, btn_menu, border_radius=10)
        win.blit(fs.render("MENÚ", True, WHITE), (btn_menu.x+25, btn_menu.y+10))
        self.btn_menu_input = btn_menu
        if self.msg:
            m = fs.render(self.msg, True, RED if "mu mal" in self.msg else GREEN)
            win.blit(m, (W//2 - m.get_width()//2, H-150))
        if self.result:
            m = fl.render(self.result, True, RED if "mu mal" in self.result else GREEN)
            win.blit(m, (W//2 - m.get_width()//2, H-150))
        return btn
    def draw_result(self):
        y = 20

        win.blit(ft.render("Resultado", True, BLACK), (W//2-100, y))
        y += 60

        labels = [
            ('states','Estados:'),
            ('alphabet','Alfabeto:'),
            ('transitions','Transiciones:'),
            ('start_state','Inicio:'),
            ('accept_states','Finales:'),
        ]

        for k, lbl in labels:
            win.blit(fl.render(lbl, True, BLACK), (50, y))
            y += 35
            if k == "transitions":
                win.blit(fl.render(str(self.dfa[k]), True, GREEN), (50, y))
            else:
                string_var = ', '.join(self.dfa[k])
                win.blit(fl.render(string_var, True, GREEN), (50, y))
            y += 55
        """
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
        """
        # Botón VOLVER (reiniciar)
        btn_volver = pygame.Rect(W//2-220, H-80, 200, 50)
        pygame.draw.rect(win, BLUE, btn_volver, border_radius=10)
        win.blit(fl.render("VOLVER", True, WHITE), (btn_volver.centerx-45, btn_volver.centery-12))

        # Botón MENÚ (abre inicio.py)
        btn_menu = pygame.Rect(W//2+20, H-80, 200, 50)
        pygame.draw.rect(win, RED, btn_menu, border_radius=10)
        win.blit(fl.render("MENÚ", True, WHITE), (btn_menu.centerx-45, btn_menu.centery-12))
        return btn_volver, btn_menu
    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            if self.fase == "entrada":
                y = 115
                for k in ['estados','alfabeto','inicial','finales','trans','ER']:
                    if pygame.Rect(50, y, W-100, 40).collidepoint(e.pos):
                        self.activo = k
                        return
                    y += 90

                if  pygame.Rect(W//2-150, H-120, 280, 50).collidepoint(e.pos):
                    self.interactive_nfa()
                    return
                if  self.result and pygame.Rect(W//2-120, H-60, 200, 30).collidepoint(e.pos):
                    self.fase = "Completopo"
                    return
                # Botón MENÚ en pantalla inicial
                if hasattr(self, 'btn_menu_input') and self.btn_menu_input.collidepoint(e.pos):
                    return "hola"

                self.activo = None

            else:
                btn_volver = pygame.Rect(W//2-220, H-80, 200, 50)
                btn_menu   = pygame.Rect(W//2+20, H-80, 200, 50)

                if btn_volver.collidepoint(e.pos):
                    self.__init__()   # Reset completo
                    return

                if btn_menu.collidepoint(e.pos):
                    return "hola"
        elif e.type == pygame.KEYDOWN and self.activo:
            # Detectar CTRL
            ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
            # Copiar
            if ctrl and e.key == pygame.K_c:
                pygame.scrap.put(pygame.SCRAP_TEXT, self.inputs[self.activo].encode())
                return
            # Pegar
            if ctrl and e.key == pygame.K_v:
                try:
                    clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if clip:
                        self.inputs[self.activo] += clip.decode().replace("\x00", "")
                except:
                    pass
                return
            # Cortar
            if ctrl and e.key == pygame.K_x:
                pygame.scrap.put(pygame.SCRAP_TEXT, self.inputs[self.activo].encode())
                self.inputs[self.activo] = ""
                return
            # Borrar
            if e.key == pygame.K_BACKSPACE:
                self.inputs[self.activo] = self.inputs[self.activo][:-1]
            # Cambiar campo
            elif e.key in (pygame.K_RETURN, pygame.K_TAB):
                keys = list(self.inputs.keys())
                self.activo = keys[(keys.index(self.activo)+1) % len(keys)]
            # Escribir
            else:
                self.inputs[self.activo] += e.unicode
app = App()
clock = pygame.time.Clock()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if app.event(e) == "hola":
            pygame.quit()
            import subprocess
            subprocess.Popen([sys.executable, "inicio.py"])
            sys.exit()
    
    win.fill(WHITE)
    app.draw_input() if app.fase == "entrada" else app.draw_result()
    pygame.display.flip()
    clock.tick(60)