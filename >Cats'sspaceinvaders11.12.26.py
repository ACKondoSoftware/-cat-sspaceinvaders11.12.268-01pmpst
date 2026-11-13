#!/usr/bin/env python3
# ============================================================
#  program.py  --  Cat's Space Invaders 1.x
#  single file / files = off  (no assets, no saves, all synth)
#  tkinter window (600x400) + pygame surface/mixer core
#  HUD / graphics / speed / OST / menu : Atari 2600 flavour
#  60 FPS fixed timestep
# ------------------------------------------------------------
#  keys:  <- -> / A D  move     SPACE  fire / start
#         TAB / G  game select  P  pause   M  mute
#         BACKSPACE  back to menu          ESC  quit
# ============================================================
import os
import time
import array
import random
import tkinter as tk

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

TITLE = "Cat's Space Invaders 1.x"
W, H = 150, 200            # logical playfield (Atari-style wide pixels)
SX, SY = 4, 2              # 150*4 x 200*2 = 600x400
FPS = 60
DT = 1.0 / FPS
RATE = 22050

# ---- palette (NTSC-ish 2600 tones) -------------------------
BG      = (0, 0, 0)
C_INV   = (210, 210, 64)
C_P1    = (80, 156, 64)
C_HI    = (214, 114, 50)
C_SHLD  = (198, 108, 58)
C_GND   = (134, 134, 29)
C_GTXT  = (40, 40, 0)
C_UFO   = (160, 80, 190)
C_SHOT  = (236, 236, 236)
C_BOMB  = (200, 72, 72)
C_TXT   = (170, 170, 170)
CYCLE   = [(210, 210, 64), (200, 72, 72), (214, 114, 50),
           (80, 156, 64), (66, 114, 194), (160, 80, 190)]

# ---- bitmaps (8 wide, hex rows) ----------------------------
INVADERS = [
    ([0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0xFF, 0x24, 0x5A, 0xA5, 0x42],
     [0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0xFF, 0x24, 0x5A, 0x5A, 0x81]),
    ([0x24, 0x24, 0x7E, 0xDB, 0xFF, 0xFF, 0xBD, 0xA5, 0x24, 0x66],
     [0x24, 0xA5, 0xFF, 0xDB, 0xFF, 0x7E, 0x3C, 0x24, 0x42, 0x81]),
    ([0x3C, 0x7E, 0xFF, 0x99, 0xFF, 0xFF, 0x66, 0xDB, 0x81, 0x42],
     [0x3C, 0x7E, 0xFF, 0x99, 0xFF, 0xFF, 0x66, 0xDB, 0x42, 0x81]),
    ([0x81, 0x42, 0x3C, 0x7E, 0x5A, 0x7E, 0xFF, 0xA5, 0xA5, 0x42],
     [0x42, 0x42, 0x3C, 0x7E, 0x5A, 0x7E, 0xFF, 0xA5, 0x5A, 0x81]),
    ([0x7E, 0xFF, 0x99, 0x99, 0xFF, 0x7E, 0x3C, 0x66, 0xC3, 0xC3],
     [0x7E, 0xFF, 0x99, 0x99, 0xFF, 0x7E, 0x3C, 0x66, 0x66, 0x24]),
    ([0x3C, 0x3C, 0xFF, 0xBD, 0xBD, 0xFF, 0xFF, 0x66, 0xC3, 0x66],
     [0x3C, 0x3C, 0xFF, 0xBD, 0xBD, 0xFF, 0xFF, 0x66, 0x66, 0xC3]),
]
CANNON = [0x18, 0x18, 0x3C, 0x7E, 0xFF, 0xFF, 0xFF, 0xFF]
BOOM_A = [0x92, 0x54, 0x28, 0xC6, 0x28, 0x54, 0x92, 0x00]
BOOM_B = [0x44, 0x82, 0x10, 0x28, 0x10, 0x82, 0x44, 0x00]
POP    = [0x00, 0x49, 0x2A, 0x14, 0x63, 0x14, 0x2A, 0x49, 0x00, 0x00]
UFO    = [0x3C, 0x7E, 0xDB, 0xFF, 0x66, 0x24]
BUNKER = ["001111111100", "011111111110"] + ["111111111111"] * 6 + \
         ["111100001111"] + ["111000000111"] * 3

FONT = {
    "A": "010101111101101", "B": "110101110101110", "C": "011100100100011",
    "D": "110101101101110", "E": "111100110100111", "F": "111100110100100",
    "G": "011100101101011", "H": "101101111101101", "I": "111010010010111",
    "J": "001001001101010", "K": "101101110101101", "L": "100100100100111",
    "M": "101111111101101", "N": "110101101101101", "O": "010101101101010",
    "P": "110101110100100", "Q": "010101101110011", "R": "110101110101101",
    "S": "011100010001110", "T": "111010010010010", "U": "101101101101111",
    "V": "101101101101010", "W": "101101111111101", "X": "101101010101101",
    "Y": "101101010010010", "Z": "111001010100111",
    "0": "111101101101111", "1": "010110010010111", "2": "111001111100111",
    "3": "111001011001111", "4": "101101111001001", "5": "111100111001111",
    "6": "111100111101111", "7": "111001001001001", "8": "111101111101111",
    "9": "111101111001111", "'": "010010000000000", ".": "000000000000010",
    "-": "000000111000000", "=": "000111000111000", " ": "000000000000000",
}

GAMES = ["NORMAL", "MOVING SHIELDS", "FAST BOMBS", "INVISIBLE"]

# layout
COLS, ROWS = 6, 6
CELL = 16
PY = 172          # cannon top
GY = 184          # ground band top
BUNK_Y = 148
BUNK_X = (25, 69, 113)


def sprite(rows, color, width=8):
    s = pygame.Surface((width, len(rows)), pygame.SRCALPHA)
    for y, r in enumerate(rows):
        for x in range(width):
            on = (r[x] == "1") if isinstance(r, str) else (r >> (width - 1 - x)) & 1
            if on:
                s.set_at((x, y), color)
    return s


# ---- audio: TIA-style square + 9-bit poly noise ------------
def wave(f0, f1, ms, vol=0.35, noise=False):
    n = int(RATE * ms / 1000)
    buf = array.array("h")
    amp = int(32767 * vol)
    phase, level, lfsr = 0.0, 1, 0x1FF
    for i in range(n):
        phase += (f0 + (f1 - f0) * i / n) / RATE
        if phase >= 0.5:
            phase -= 0.5
            if noise:
                bit = (lfsr ^ (lfsr >> 4)) & 1
                lfsr = (lfsr >> 1) | (bit << 8)
                level = 1 if lfsr & 1 else -1
            else:
                level = -level
        buf.append(level * amp)
    return buf


class Audio:
    def __init__(self):
        self.ok = False
        self.muted = False
        self.snd = {}
        try:
            pygame.mixer.init(frequency=RATE, size=-16, channels=1,
                              buffer=256, allowedchanges=0)
            mk = lambda b: pygame.mixer.Sound(buffer=b.tobytes())
            self.snd = {
                "shot": mk(wave(1300, 280, 170, 0.25)),
                "hit":  mk(wave(900, 200, 180, 0.35, True)),
                "die":  mk(wave(260, 40, 900, 0.45, True)),
                "ufo":  mk(wave(520, 880, 110, 0.18) + wave(880, 520, 110, 0.18)),
                "ufohit": mk(wave(300, 1500, 350, 0.3)),
                "sel":  mk(wave(660, 660, 50, 0.25)),
            }
            for i, f in enumerate((98, 87, 78, 73)):
                self.snd["m%d" % i] = mk(wave(f, f, 75, 0.5))
            self.ok = True
        except Exception:
            self.ok = False

    def play(self, name, loops=0):
        if self.ok and not self.muted:
            try:
                self.snd[name].play(loops=loops)
            except Exception:
                pass

    def stop(self, name=None):
        if not self.ok:
            return
        try:
            if name:
                self.snd[name].stop()
            else:
                pygame.mixer.stop()
        except Exception:
            pass

    def toggle(self):
        self.muted = not self.muted
        if self.muted:
            self.stop()


# ---- game --------------------------------------------------
class Game:
    def __init__(self, root):
        self.root = root
        root.title(TITLE)
        root.resizable(False, False)
        # Explicitly size the content area; center after the window is mapped.
        root.geometry("600x400")
        root.configure(bg="black")
        self.canvas = tk.Canvas(root, width=W * SX, height=H * SY,
                                bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=False)
        root.after(0, self.center_window)
        self.item = self.canvas.create_image(0, 0, anchor="nw")
        self.img = None
        self.surf = pygame.Surface((W, H))
        self.hdr = b"P6 %d %d 255\n" % (W, H)
        self.tobytes = getattr(pygame.image, "tobytes", None) or pygame.image.tostring

        self.keys, self.pressed = set(), set()
        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.protocol("WM_DELETE_WINDOW", self.quit)
        root.focus_force()

        self.audio = Audio()
        self.s_inv = [(sprite(a, C_INV), sprite(b, C_INV)) for a, b in INVADERS]
        self.s_pop = sprite(POP, C_INV)
        self.s_can = sprite(CANNON, C_P1)
        self.s_boom = (sprite(BOOM_A, C_P1), sprite(BOOM_B, C_HI))
        self.s_ufo = sprite(UFO, C_UFO)

        self.running = True
        self.state = "menu"
        self.game_no = 0
        self.hi = 0
        self.score = 0
        self.frame = 0
        self.paused = False
        self.reset_game()

        self.acc = 0.0
        self.last = time.perf_counter()
        self.tick()

    def center_window(self):
        """Center the actual 600x400 client window, including on macOS Tk."""
        root = self.root
        root.update_idletasks()
        width, height = 600, 400
        # Use the window manager's current screen dimensions after mapping.
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.lift()
        root.focus_force()

    # ---- input ----
    def key_down(self, e):
        k = e.keysym.lower()
        self.keys.add(k)
        self.pressed.add(k)
        return "break"

    def key_up(self, e):
        self.keys.discard(e.keysym.lower())

    def quit(self):
        self.running = False
        self.audio.stop()
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        self.root.destroy()

    # ---- setup ----
    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.wave = 0
        self.px = W // 2 - 4
        self.dead_t = 0
        self.new_wave()

    def new_wave(self):
        self.alive = [[True] * COLS for _ in range(ROWS)]
        self.count = ROWS * COLS
        self.fx = 8.0
        self.fy = 30 + min(self.wave, 5) * 8
        self.dir = 1
        self.anim = 0
        self.note = 0
        self.move_t = 30
        self.shot = None
        self.bombs = []
        self.pops = []
        self.bomb_cd = 90
        self.ufo = None
        self.ufo_cd = random.randint(900, 1500)
        self.wave_t = 0
        self.flash = 40
        self.bunkers = [{"x": float(x), "s": sprite(BUNKER, C_SHLD, 12)} for x in BUNK_X]
        self.bunk_dir = 1
        self.audio.stop("ufo")

    def start(self):
        self.reset_game()
        self.state = "play"
        self.paused = False
        self.audio.play("sel")

    # ---- main loop (fixed 60 Hz step inside tk) ----
    def tick(self):
        if not self.running:
            return
        now = time.perf_counter()
        self.acc = min(self.acc + now - self.last, 0.25)
        self.last = now
        stepped = False
        while self.acc >= DT:
            self.update()
            self.acc -= DT
            stepped = True
            if not self.running:
                return
        if stepped:
            self.render()
        self.root.after(max(1, int((DT - self.acc) * 1000)), self.tick)

    def update(self):
        self.frame += 1
        p = self.pressed
        if "escape" in p:
            self.quit()
            return
        if "m" in p:
            self.audio.toggle()
        if self.state == "menu":
            if p & {"tab", "g"}:
                self.game_no = (self.game_no + 1) % len(GAMES)
                self.audio.play("sel")
            if p & {"space", "return"}:
                self.start()
        elif self.state == "play":
            if "backspace" in p:
                self.audio.stop()
                self.state = "menu"
            elif "p" in p:
                self.paused = not self.paused
                if self.paused:
                    self.audio.stop("ufo")
            if self.state == "play" and not self.paused:
                self.step_play()
        elif self.state == "over":
            self.over_t -= 1
            if self.over_t <= 0 or (self.over_t < 150 and p & {"space", "return"}):
                self.state = "menu"
        p.clear()

    # ---- gameplay ----
    def add_score(self, n):
        self.score += n
        self.hi = max(self.hi, self.score)

    def bunker_hit(self, x, y):
        for b in self.bunkers:
            dx, dy = int(x - int(b["x"])), int(y - BUNK_Y)
            if 0 <= dx < 12 and 0 <= dy < 12 and b["s"].get_at((dx, dy))[3]:
                for i in range(dx - 1, dx + 2):
                    for j in range(dy - 2, dy + 3):
                        if 0 <= i < 12 and 0 <= j < 12:
                            b["s"].set_at((i, j), (0, 0, 0, 0))
                return True
        return False

    def kill_player(self):
        self.lives -= 1
        self.dead_t = 100
        self.shot = None
        self.bombs = []
        self.audio.stop("ufo")
        self.ufo = None
        self.audio.play("die")

    def game_over(self):
        self.audio.stop()
        self.state = "over"
        self.over_t = 240

    def step_play(self):
        k = self.keys
        if self.dead_t > 0:                      # freeze field while cannon burns
            self.dead_t -= 1
            if self.dead_t == 0:
                if self.lives <= 0:
                    self.game_over()
                else:
                    self.px = W // 2 - 4
            return
        if self.wave_t > 0:                      # short breather between waves
            self.wave_t -= 1
            if self.wave_t == 0:
                self.wave += 1
                self.new_wave()
            return
        if self.flash > 0:
            self.flash -= 1

        # cannon
        if k & {"left", "a"}:
            self.px = max(4, self.px - 1)
        if k & {"right", "d"}:
            self.px = min(W - 12, self.px + 1)
        if self.shot is None and k & {"space", "up", "w"}:
            self.shot = [self.px + 4, PY - 2]
            self.audio.play("shot")

        # moving shields (game 2)
        if self.game_no == 1 and self.frame % 3 == 0:
            for b in self.bunkers:
                b["x"] += self.bunk_dir
            if self.bunkers[0]["x"] <= 6 or self.bunkers[-1]["x"] >= W - 18:
                self.bunk_dir = -self.bunk_dir

        # invader march
        self.move_t -= 1
        if self.move_t <= 0:
            self.move_t = max(2, 2 + self.count * 30 // (ROWS * COLS) - min(self.wave, 4) * 2)
            cols = [c for c in range(COLS) if any(self.alive[r][c] for r in range(ROWS))]
            if cols:
                lo = self.fx + cols[0] * CELL
                hi = self.fx + cols[-1] * CELL + 8
                if (self.dir > 0 and hi + 2 > W - 4) or (self.dir < 0 and lo - 2 < 4):
                    self.fy += 8
                    self.dir = -self.dir
                else:
                    self.fx += 2 * self.dir
                self.anim ^= 1
                self.audio.play("m%d" % self.note)
                self.note = (self.note + 1) % 4
                # crush shields / reach the ground
                rows = [r for r in range(ROWS) if any(self.alive[r])]
                bottom = self.fy + rows[-1] * CELL + 10
                if bottom >= BUNK_Y:
                    for b in self.bunkers:
                        for r in rows:
                            for c in cols:
                                if self.alive[r][c]:
                                    rx = int(self.fx + c * CELL - int(b["x"]))
                                    ry = int(self.fy + r * CELL - BUNK_Y)
                                    b["s"].fill((0, 0, 0, 0), (rx, ry, 8, 10))
                if bottom >= PY:
                    self.lives = 0
                    self.kill_player()
                    return

        # player shot
        if self.shot:
            sx = self.shot[0]
            for _ in range(4):
                self.shot[1] -= 1
                sy = self.shot[1]
                if sy < 17:
                    self.shot = None
                    break
                if self.bunker_hit(sx, sy):
                    self.shot = None
                    break
                if self.ufo and self.ufo[0] <= sx < self.ufo[0] + 8 and 18 <= sy < 24:
                    self.pops.append([int(self.ufo[0]), 16, 14])
                    self.ufo = None
                    self.audio.stop("ufo")
                    self.audio.play("ufohit")
                    self.add_score(200)
                    self.shot = None
                    break
                c, cx = divmod(sx - self.fx, CELL)
                r, ry = divmod(sy - self.fy, CELL)
                c, r = int(c), int(r)
                if 0 <= c < COLS and 0 <= r < ROWS and cx < 8 and ry < 10 and self.alive[r][c]:
                    self.alive[r][c] = False
                    self.count -= 1
                    self.add_score((ROWS - r) * 5)
                    self.pops.append([int(self.fx + c * CELL), int(self.fy + r * CELL), 10])
                    self.audio.play("hit")
                    self.flash = 30
                    self.shot = None
                    if self.count == 0:
                        self.wave_t = 80
                        self.bombs = []
                        self.audio.stop("ufo")
                        self.ufo = None
                    break

        # bombs
        self.bomb_cd -= 1
        if self.bomb_cd <= 0 and self.count and len(self.bombs) < 2 + (self.wave > 0):
            self.bomb_cd = random.randint(25, 70)
            c = random.choice([c for c in range(COLS) if any(self.alive[r][c] for r in range(ROWS))])
            r = max(r for r in range(ROWS) if self.alive[r][c])
            self.bombs.append([self.fx + c * CELL + 3, self.fy + r * CELL + 10.0])
        speed = 2.2 if self.game_no == 2 else 1.2
        for b in self.bombs[:]:
            b[1] += speed
            bx, by = int(b[0]), int(b[1])
            if by >= GY or self.bunker_hit(bx, by + 3):
                self.bombs.remove(b)
            elif self.px <= bx < self.px + 8 and PY <= by + 3 < PY + 8:
                self.kill_player()
                return

        # ufo
        if self.ufo:
            self.ufo[0] += self.ufo[1]
            if self.ufo[0] < -8 or self.ufo[0] > W:
                self.ufo = None
                self.audio.stop("ufo")
        else:
            self.ufo_cd -= 1
            if self.ufo_cd <= 0 and self.count > 6:
                self.ufo_cd = random.randint(1100, 1800)
                d = random.choice((-1, 1))
                self.ufo = [-8.0 if d > 0 else float(W), 0.5 * d]
                self.audio.play("ufo", loops=-1)

        for p in self.pops[:]:
            p[2] -= 1
            if p[2] <= 0:
                self.pops.remove(p)

    # ---- drawing ----
    def text(self, s, x, y, color, sx=1, sy=2):
        surf = self.surf
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for i, bit in enumerate(g):
                if bit == "1":
                    surf.fill(color, (x + (i % 3) * sx, y + (i // 3) * sy, sx, sy))
            x += 4 * sx

    def ctext(self, s, y, color, sx=1, sy=2):
        self.text(s, (W - len(s) * 4 * sx + sx) // 2, y, color, sx, sy)

    def draw_hud(self):
        self.text("%04d" % (self.score % 10000), 8, 3, C_P1, 2, 2)
        self.text("%04d" % (self.hi % 10000), W - 38, 3, C_HI, 2, 2)
        self.surf.fill(C_GND, (0, GY, W, H - GY))

    def draw_play(self):
        s = self.surf
        self.draw_hud()
        self.text(str(max(self.lives, 0)), 8, GY + 3, C_GTXT, 2, 2)
        for i in range(max(self.lives - 1, 0)):
            s.blit(self.s_can, (20 + i * 11, GY + 4), special_flags=pygame.BLEND_RGBA_SUB)
        self.text("G%d" % (self.game_no + 1), W - 22, GY + 3, C_GTXT, 2, 2)

        if self.ufo:
            s.blit(self.s_ufo, (int(self.ufo[0]), 18))
        if self.game_no != 3 or self.flash > 0:
            for r in range(ROWS):
                spr = self.s_inv[r][self.anim]
                y = int(self.fy + r * CELL)
                for c in range(COLS):
                    if self.alive[r][c]:
                        s.blit(spr, (int(self.fx + c * CELL), y))
        for x, y, _ in self.pops:
            s.blit(self.s_pop, (x, y))
        for b in self.bunkers:
            s.blit(b["s"], (int(b["x"]), BUNK_Y))
        if self.dead_t > 0:
            if self.lives > 0 or self.dead_t > 10:
                s.blit(self.s_boom[(self.dead_t // 5) & 1], (self.px, PY))
        else:
            s.blit(self.s_can, (self.px, PY))
        if self.shot:
            s.fill(C_SHOT, (self.shot[0], self.shot[1], 1, 4))
        for b in self.bombs:
            zig = (int(b[1]) // 3) & 1
            s.fill(C_BOMB, (int(b[0]) - zig, int(b[1]), 1, 2))
            s.fill(C_BOMB, (int(b[0]) - 1 + zig, int(b[1]) + 2, 1, 2))
        if self.paused:
            self.ctext("PAUSED", 96, C_TXT, 2, 4)

    def draw_menu(self):
        s = self.surf
        cyc = self.frame // 10
        self.ctext("CAT'S", 8, CYCLE[cyc % 6], 2, 2)
        self.ctext("SPACE INVADERS", 21, CYCLE[(cyc + 2) % 6], 2, 2)
        self.ctext("1.X", 34, C_TXT)
        y = 48
        s.blit(self.s_ufo, (46, y + 2))
        self.text("= 200 PTS", 60, y, C_UFO)
        fr = (self.frame // 30) & 1
        for r in range(ROWS):
            y += 12
            s.blit(self.s_inv[r][fr], (46, y))
            self.text("= %d PTS" % ((ROWS - r) * 5), 60, y, C_INV)
        self.ctext("GAME %d  %s" % (self.game_no + 1, GAMES[self.game_no]), 140, C_HI)
        if (self.frame // 30) & 1:
            self.ctext("PRESS FIRE", 154, C_P1)
        self.ctext("TAB GAME  M MUTE  ESC QUIT", 168, (100, 100, 100))
        s.fill(C_GND, (0, GY, W, H - GY))
        self.ctext("HI %04d" % (self.hi % 10000), GY + 3, C_GTXT, 2, 2)

    def render(self):
        self.surf.fill(BG)
        if self.state == "menu":
            self.draw_menu()
        else:
            self.draw_play()
            if self.state == "over":
                self.ctext("GAME OVER", 96, CYCLE[(self.frame // 10) % 6], 2, 4)
        data = self.tobytes(self.surf, "RGB")
        self.img = tk.PhotoImage(data=self.hdr + data, format="PPM").zoom(SX, SY)
        self.canvas.itemconfig(self.item, image=self.img)


def main():
    root = tk.Tk()
    game = Game(root)
    root.after(100, game.center_window)
    root.mainloop()


if __name__ == "__main__":
    main()
