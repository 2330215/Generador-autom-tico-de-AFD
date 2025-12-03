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
class App:
    def __init__(self):
        self.dfa = self.dfa_min = None
        self.msg = ""
        self.fase = "entrada"
        self.inputs = {'estados':'', 'alfabeto':'', 'inicial':'', 'finales':'', 'trans':''}
        self.activo = None

    def minimizar(self):
        if not AUTOMATA:
            self.msg = " pip install automata-lib"
            return
        try:
            est = {e.strip() for e in self.inputs['estados'].split(',') if e.strip()}
            alf = {s.strip() for s in self.inputs['alfabeto'].split(',') if s.strip()}
            ini = self.inputs['inicial'].strip()
            fin = {f.strip() for f in self.inputs['finales'].split(',') if f.strip()}
            
            if not est or not alf or not ini or not fin:
                self.msg = " Complete todos los campos"
                return
            if ini not in est or not fin.issubset(est):
                self.msg = "Estados inválidos"
                return

            trans = {}
            for t in self.inputs['trans'].split(';'):
                if not t.strip():
                    continue
                p = [x.strip() for x in t.split(',')]
                if len(p) != 3:
                    self.msg = f" Formato: {t}"
                    return
                o, s, d = p
                if o not in est or d not in est or s not in alf:
                    self.msg = f" Error en: {t}"
                    return
                if o not in trans:
                    trans[o] = {}
                trans[o][s] = d
            
            self.dfa = DFA(states=est, input_symbols=alf,
                           transitions=trans,
                           initial_state=ini,
                           final_states=fin)

            self.dfa_min = self.dfa.minify()
            self.fase = "resultado"
            self.msg = "Completado"

        except Exception as e:
            self.msg = f" {e}"

    def draw_input(self):
        y = 20

        t = ft.render("Minimización AFD", True, BLACK)
        win.blit(t, (W//2 - t.get_width()//2, y))
        y += 60

        info = fs.render("✓ automata-lib" if AUTOMATA else " pip install automata-lib",
                         True, GREEN if AUTOMATA else RED)
        win.blit(info, (W//2 - info.get_width()//2, y))
        y += 40

        labels = [
            ('estados','Estados (q0,q1,q2):'),
            ('alfabeto','Alfabeto (a,b):'),
            ('inicial','Inicial (q0):'),
            ('finales','Finales (q2):'),
            ('trans','Trans (q0,a,q1;q1,b,q2):')
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
        ej = fs.render(
            "Ej: q0,q1,q2,q3 | a,b | q0 | q3 | "
            "q0,a,q1;q0,b,q2;q1,a,q3;q1,b,q3;q2,a,q3;q2,b,q3;q3,a,q3;q3,b,q3",
            True, DARK
        )
        win.blit(ej, (50, y+15))

        btn = pygame.Rect(W//2-150, H-100, 300, 50)
        pygame.draw.rect(win, GREEN if AUTOMATA else GRAY, btn, border_radius=10)
        win.blit(fl.render("MINIMIZAR", True, WHITE), (btn.centerx-60, btn.centery-12))
                # Botón MENÚ (inicio)
        btn_menu = pygame.Rect(20, 20, 140, 40)
        pygame.draw.rect(win, RED, btn_menu, border_radius=10)
        win.blit(fs.render("MENÚ", True, WHITE), (btn_menu.x+25, btn_menu.y+10))
        self.btn_menu_input = btn_menu
        if self.msg:
            m = fs.render(self.msg, True, RED if "mu mal" in self.msg else GREEN)
            win.blit(m, (W//2 - m.get_width()//2, H-140))
        return btn if AUTOMATA else None
    def draw_result(self):
        y, c1, c2 = 20, 50, W//2 + 50

        win.blit(ft.render("Resultado", True, BLACK), (W//2-100, y))
        y += 60

        win.blit(fl.render("Original:", True, BLACK), (c1, y))
        y += 40

        for txt in [
            f"Estados: {','.join(map(str, sorted(self.dfa.states)))}",
            f"Inicial: {self.dfa.initial_state}",
            f"Estados: {','.join(map(str, sorted(self.dfa.states)))}",
            f"Total: {len(self.dfa.states)}"
        ] + [
            f"δ({e},{s})={d}"
            for e,t in list(self.dfa.transitions.items())[:8]
            for s,d in t.items()
        ]:
            win.blit(fs.render(txt, True, BLACK), (c1+20, y))
            y += 28
            if y > H-200:
                break
        y = 100
        win.blit(fl.render("Minimizado:", True, GREEN), (c2, y))
        y += 40

        red = len(self.dfa.states) - len(self.dfa_min.states)
        for txt in [
            f"Estados: {','.join(map(str, sorted(self.dfa_min.states)))}",
            f"Inicial: {self.dfa_min.initial_state}",
            f"Finales: {','.join(map(str, sorted(self.dfa_min.final_states)))}",
            f"Total: {len(self.dfa_min.states)}",
            f"✓ Reducción: {red}" if red > 0 else "✓ Ya minimizado"
        ] + [
            f"δ({e},{s})={d}"
            for e,t in list(self.dfa_min.transitions.items())
            for s,d in t.items()
        ]:
            c = GREEN if "✓" in txt else BLACK
            win.blit(fs.render(txt, True, c), (c2+20, y))
            y += 28
            if y > H-200:
                break
        # Botón VOLVER (reinicia)
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
                y = 160
                for k in ['estados','alfabeto','inicial','finales','trans']:
                    if pygame.Rect(50, y, W-100, 40).collidepoint(e.pos):
                        self.activo = k
                        return
                    y += 90

                if AUTOMATA and pygame.Rect(W//2-150, H-100, 300, 50).collidepoint(e.pos):
                    self.minimizar()
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
