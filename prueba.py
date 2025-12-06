import pygame
import sys

try:
    from pyformlang.regular_expression import Regex
    LIB = True
except:
    LIB = False

pygame.init()

info = pygame.display.Info()
W, H = info.current_w - 100, info.current_h - 100
win = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Parser ER")
pygame.scrap.init()
pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

WHITE, BLACK, GRAY, LIGHT = (255,255,255), (0,0,0), (200,200,200), (230,230,230)
BLUE, GREEN, RED, DARK = (100,150,255), (100,200,100), (255,100,100), (150,150,150)

ft, fl, fs, fi = [pygame.font.SysFont(None, s) for s in [48,32,24,28]]

class App:
    def __init__(self):
        self.msg = ""
        self.input = ""
        self.activo = False

    def validar(self):
        try:
            _ = Regex(self.input)
            self.msg = "Expresion válida"
        except Exception as e:
            self.msg = "Error: " + str(e)

    def draw_input(self):
        y = 20
        t = ft.render("Parser de Expresiones Regulares", True, BLACK)
        win.blit(t, (W//2 - t.get_width()//2, y))
        y += 60

        info_lib = fs.render("✓ pyformlang" if LIB else " pip install pyformlang",
                             True, GREEN if LIB else RED)
        win.blit(info_lib, (W//2 - info_lib.get_width()//2, y))
        y += 50

        ej = fs.render("Soporta: concatenación, unión (|), cierre de Kleene (*)", True, DARK)
        win.blit(ej, (W//2 - ej.get_width()//2, y))
        y += 70

        win.blit(fl.render("Expresión:", True, BLACK), (50, y))
        y += 35

        self.rect_input = pygame.Rect(50, y, W-100, 50)
        pygame.draw.rect(win, LIGHT, self.rect_input)
        pygame.draw.rect(win, BLUE if self.activo else GRAY, self.rect_input, 3 if self.activo else 2)

        surf = fi.render(self.input, True, BLACK)
        if surf.get_width() > self.rect_input.width - 20:
            chars = max(1, int(len(self.input) * (self.rect_input.width - 20) / surf.get_width()))
            surf = fi.render("..." + self.input[-chars:], True, BLACK)

        win.blit(surf, (self.rect_input.x + 10, self.rect_input.y + 10))

        btn = pygame.Rect(W//2 - 150, H - 100, 300, 50)
        pygame.draw.rect(win, GREEN if LIB else GRAY, btn, border_radius=10)
        win.blit(fl.render("VALIDAR", True, WHITE), (btn.centerx - 55, btn.centery - 12))

        btn_menu = pygame.Rect(20, 20, 140, 40)
        pygame.draw.rect(win, RED, btn_menu, border_radius=10)
        win.blit(fs.render("MENÚ", True, WHITE), (btn_menu.x + 25, btn_menu.y + 10))
        self.btn_menu_input = btn_menu

        if self.msg:
            m = fs.render(self.msg, True, GREEN if "válida" in self.msg else RED)
            win.blit(m, (W//2 - m.get_width()//2, H - 150))

        return btn if LIB else None

    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            if self.rect_input.collidepoint(e.pos):
                self.activo = True
                return
            if LIB and pygame.Rect(W//2 - 150, H - 100, 300, 50).collidepoint(e.pos):
                self.validar()
                return
            if hasattr(self, "btn_menu_input") and self.btn_menu_input.collidepoint(e.pos):
                return "hola"
            self.activo = False

        elif e.type == pygame.KEYDOWN and self.activo:
            ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
            if ctrl and e.key == pygame.K_c:
                pygame.scrap.put(pygame.SCRAP_TEXT, self.input.encode())
                return
            if ctrl and e.key == pygame.K_v:
                try:
                    clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if clip:
                        self.input += clip.decode().replace("\x00", "")
                except:
                    pass
                return
            if ctrl and e.key == pygame.K_x:
                pygame.scrap.put(pygame.SCRAP_TEXT, self.input.encode())
                self.input = ""
                return
            if e.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            elif len(e.unicode) == 1:
                self.input += e.unicode


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
    app.draw_input()
    pygame.display.flip()
    clock.tick(60)
