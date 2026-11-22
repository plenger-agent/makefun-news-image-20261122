#!/usr/bin/env python3
"""gen.py -- renders entry.png: "THE WORLD IN ONE DAY", a broadsheet front
page summing up the world news of Sunday 22 November 2026.

Original renderer written for the make.fun news-image-20261122 entry.
Draws with Pillow at 2x supersampling, then downscales to 1024x1024.
Deterministic: no clock, no network, no randomness.
"""

from PIL import Image, ImageDraw, ImageFont

SS = 2                      # supersample factor
W = H = 1024                # final logical size
PAPER = (247, 242, 228)
PANEL = (255, 252, 244)
INK = (26, 26, 32)
NAVY = (18, 38, 76)
RED = (168, 30, 38)
GOLD = (178, 132, 44)
GREY = (110, 100, 84)
HAIR = (150, 138, 112)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF = FONT_DIR + "/liberation/LiberationSerif-Regular.ttf"
SERIF_B = FONT_DIR + "/liberation/LiberationSerif-Bold.ttf"
SERIF_I = FONT_DIR + "/liberation/LiberationSerif-Italic.ttf"
SANS = FONT_DIR + "/liberation/LiberationSans-Regular.ttf"
SANS_B = FONT_DIR + "/liberation/LiberationSans-Bold.ttf"

_cache = {}


def F(path, size):
    """Font at logical size (scaled by SS)."""
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, int(size * SS))
    return _cache[key]


class Page:
    def __init__(self):
        self.img = Image.new("RGB", (W * SS, H * SS), PAPER)
        self.d = ImageDraw.Draw(self.img)

    # -- primitives (logical coordinates) ---------------------------------
    def rect(self, x, y, w, h, fill=None, outline=None, width=1):
        box = [x * SS, y * SS, (x + w) * SS, (y + h) * SS]
        self.d.rectangle(box, fill=fill, outline=outline,
                         width=max(1, int(width * SS)))

    def line(self, x1, y1, x2, y2, fill=INK, width=1):
        self.d.line([x1 * SS, y1 * SS, x2 * SS, y2 * SS], fill=fill,
                    width=max(1, int(width * SS)))

    def ellipse(self, x, y, w, h, fill=None, outline=None, width=1):
        box = [x * SS, y * SS, (x + w) * SS, (y + h) * SS]
        self.d.ellipse(box, fill=fill, outline=outline,
                       width=max(1, int(width * SS)))

    def poly(self, pts, fill=None, outline=None):
        self.d.polygon([(px * SS, py * SS) for px, py in pts],
                       fill=fill, outline=outline)

    def text(self, x, y, s, font, fill=INK, anchor="la"):
        self.d.text((x * SS, y * SS), s, font=font, fill=fill, anchor=anchor)

    def textw(self, s, font):
        return self.d.textlength(s, font=font) / SS

    def save(self, path):
        out = self.img.resize((W, H), Image.LANCZOS)
        out.save(path, optimize=True)


def fit_font(page, s, path, size, maxw):
    """Shrink font size until the string fits maxw (logical px)."""
    while size > 8 and page.textw(s, F(path, size)) > maxw:
        size -= 0.5
    return F(path, size), size


def tracked(page, cx, y, s, font, fill, tracking=2.0):
    """Draw a letterspaced string centred on cx."""
    widths = [page.textw(ch, font) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, wch in zip(s, widths):
        page.text(x, y, ch, font, fill)
        x += wch + tracking
    return total


def wrap(page, s, font, maxw):
    """Greedy word wrap; returns list of lines that fit maxw."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if page.textw(trial, font) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- scenes
def scene_cop31(p, x, y, w, h):
    """Dawn over the Antalya conference halls: sun rising, dome, flags."""
    bands = [(24, 36, 74), (52, 62, 110), (110, 84, 110),
             (196, 108, 74), (238, 164, 92)]
    bh = h / len(bands)
    for i, c in enumerate(bands):
        p.rect(x, y + i * bh, w, bh + 1, fill=c)
    # rising sun
    p.ellipse(x + w * 0.40, y + h * 0.30, w * 0.20, w * 0.20,
              fill=(250, 205, 110))
    # distant hills
    p.poly([(x, y + h * 0.78), (x + w * 0.25, y + h * 0.60),
            (x + w * 0.48, y + h * 0.78)], fill=(70, 60, 88))
    p.poly([(x + w * 0.45, y + h * 0.78), (x + w * 0.72, y + h * 0.58),
            (x + w, y + h * 0.78)], fill=(60, 52, 82))
    # conference hall: long block + dome
    base = y + h * 0.80
    p.rect(x + w * 0.08, base - h * 0.16, w * 0.84, h * 0.16,
           fill=(238, 230, 214))
    p.poly([(x + w * 0.38, base - h * 0.16), (x + w * 0.50, base - h * 0.34),
            (x + w * 0.62, base - h * 0.16)], fill=(214, 200, 172))
    for i in range(9):  # windows
        wx = x + w * (0.13 + i * 0.088)
        p.rect(wx, base - h * 0.11, w * 0.045, h * 0.06, fill=(90, 110, 140))
    # flag row
    flag_cols = [(200, 40, 44), (30, 90, 160), (240, 190, 60),
                 (40, 140, 70), (230, 230, 230), (200, 110, 30)]
    for i, c in enumerate(flag_cols):
        fx = x + w * (0.16 + i * 0.115)
        p.line(fx, base, fx, base - h * 0.30, fill=(240, 238, 230), width=1.4)
        p.poly([(fx, base - h * 0.30), (fx + w * 0.055, base - h * 0.265),
                (fx, base - h * 0.23)], fill=c)
    p.rect(x, base, w, h - (base - y), fill=(30, 34, 52))


def scene_bahrain(p, x, y, w, h):
    """Night over the base: radar dish, launcher, missile trails, bursts."""
    p.rect(x, y, w, h, fill=(16, 22, 44))
    for i in range(26):  # stars, fixed pattern
        sx = x + ((i * 53) % int(w))
        sy = y + ((i * 29) % int(h * 0.5))
        p.ellipse(sx, sy, 2.2, 2.2, fill=(220, 226, 240))
    ground = y + h * 0.82
    # radar dish on a tower (left)
    tx = x + w * 0.16
    p.poly([(tx - 12, ground), (tx, y + h * 0.40), (tx + 12, ground)],
           fill=(120, 130, 150))
    p.poly([(tx - 24, y + h * 0.20), (tx + 24, y + h * 0.30),
            (tx + 4, y + h * 0.44), (tx - 6, y + h * 0.40)],
           fill=(170, 180, 200))
    p.line(tx + 1, y + h * 0.33, tx + 15, y + h * 0.245,
           fill=(200, 208, 224), width=1.6)
    p.ellipse(tx + 13, y + h * 0.245 - 2.5, 5, 5, fill=(230, 236, 248))
    # launcher vehicle (right)
    lx = x + w * 0.58
    p.rect(lx, ground - h * 0.13, w * 0.30, h * 0.13, fill=(96, 106, 88))
    for i in range(3):
        p.ellipse(lx + 8 + i * w * 0.095, ground - h * 0.045,
                  w * 0.062, w * 0.062, fill=(30, 30, 34))
    p.poly([(lx + w * 0.05, ground - h * 0.13), (lx + w * 0.16, ground - h * 0.34),
            (lx + w * 0.22, ground - h * 0.32), (lx + w * 0.11, ground - h * 0.12)],
           fill=(130, 140, 118))
    # incoming trails + interception bursts
    bursts = [(0.46, 0.20), (0.68, 0.12), (0.84, 0.30)]
    for bx, by in bursts:
        cx, cy = x + w * bx, y + h * by
        for dx, dy in [(-11, 0), (11, 0), (0, -11), (0, 11),
                       (-8, -8), (8, -8), (-8, 8), (8, 8)]:
            p.line(cx, cy, cx + dx, cy + dy, fill=(250, 190, 90), width=1.6)
        p.ellipse(cx - 3, cy - 3, 6, 6, fill=(255, 220, 150))
    for i, (tx2, ty2) in enumerate([(0.52, 0.52), (0.74, 0.44), (0.90, 0.58)]):
        sx, sy = x + w * tx2, y + h * ty2
        p.line(sx, sy, sx - w * 0.10, sy - h * 0.20, fill=(240, 160, 90),
               width=1.6)
        p.poly([(sx, sy), (sx - 6, sy - 3), (sx - 2, sy + 5)], fill=(240, 200, 160))
    p.rect(x, ground, w, h - (ground - y), fill=(10, 12, 24))


def scene_drones(p, x, y, w, h):
    """Dusk sky over Kyiv: drone swarm, searchlights, skyline."""
    bands = [(38, 44, 84), (84, 66, 100), (168, 92, 76), (226, 138, 84)]
    bh = h / len(bands)
    for i, c in enumerate(bands):
        p.rect(x, y + i * bh, w, bh + 1, fill=c)
    ground = y + h * 0.84
    # searchlight beams
    for bx in (0.18, 0.80):
        sx = x + w * bx
        p.poly([(sx, ground), (sx - w * 0.05, y + h * 0.10),
                (sx + w * 0.07, y + h * 0.06)], fill=(250, 240, 190))
    # skyline silhouette
    blocks = [(0.00, 0.20), (0.10, 0.30), (0.22, 0.16), (0.32, 0.36),
              (0.46, 0.22), (0.56, 0.30), (0.68, 0.18), (0.78, 0.34),
              (0.90, 0.24)]
    for bx, bh2 in blocks:
        bw = w * 0.115
        p.rect(x + w * bx, ground - h * bh2, bw, h * bh2, fill=(24, 24, 36))
        for r in range(3):
            for cix in range(2):
                if (int(bx * 100) + r + cix) % 3 != 0:
                    p.rect(x + w * bx + 5 + cix * bw * 0.42,
                           ground - h * bh2 + 5 + r * h * 0.075,
                           4.5, 4.5, fill=(250, 205, 110))
    # dome silhouette (centre)
    p.poly([(x + w * 0.44, ground - h * 0.22), (x + w * 0.50, ground - h * 0.36),
            (x + w * 0.56, ground - h * 0.22)], fill=(24, 24, 36))
    # drones: small x-silhouettes with dotted trails
    drones = [(0.10, 0.16), (0.24, 0.10), (0.38, 0.20), (0.55, 0.12),
              (0.66, 0.22), (0.78, 0.14), (0.90, 0.20), (0.30, 0.30),
              (0.60, 0.32), (0.86, 0.34)]
    for dx, dy in drones:
        cx, cy = x + w * dx, y + h * dy
        for k in range(1, 5):
            p.ellipse(cx + k * 7, cy - k * 6, 2, 2, fill=(240, 220, 190))
        p.line(cx - 6, cy - 5, cx + 6, cy + 5, fill=(20, 20, 28), width=2.2)
        p.line(cx - 6, cy + 5, cx + 6, cy - 5, fill=(20, 20, 28), width=2.2)
        p.ellipse(cx - 2.5, cy - 2.5, 5, 5, fill=(16, 16, 22))
    p.rect(x, ground, w, h - (ground - y), fill=(16, 16, 24))


# ---------------------------------------------------------------- layout
MX = 26                     # side margin
CW = W - 2 * MX             # content width = 972


def masthead(p):
    y = 12
    p.text(W / 2, y, "ONE DAY · ONE PAGE · THE WHOLE WORLD",
           F(SANS_B, 11.5), GREY, anchor="ma")
    y += 17
    p.line(MX, y, W - MX, y, INK, 2.6)
    y += 8
    f, _ = fit_font(p, "THE WORLD IN ONE DAY", SERIF_B, 54, CW)
    p.text(W / 2, y, "THE WORLD IN ONE DAY", f, NAVY, anchor="ma")
    y += 60
    p.line(MX, y, W - MX, y, INK, 1.2)
    p.line(MX, y + 3.5, W - MX, y + 3.5, INK, 2.6)
    y += 10
    f, _ = fit_font(p, "Sunday 22 November 2026", SERIF_B, 44, CW)
    p.text(W / 2, y, "Sunday 22 November 2026", f, RED, anchor="ma")
    y += 50
    tracked(p, W / 2, y,
            "35 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
            F(SANS_B, 14.5), INK, tracking=1.1)
    y += 24
    # ticker band
    p.rect(MX, y, CW, 29, fill=NAVY)
    tick = ("COP31 FINAL TEXT AT DAWN, ~03:00 GMT   •   186 DRONES OVER "
            "UKRAINE   •   856 CANDIDATES IN HONG KONG   •   720/9: INDIA'S "
            "RECORD TOTAL IN NZ")
    f, _ = fit_font(p, tick, SANS_B, 14.5, CW - 24)
    p.text(W / 2, y + 6, tick, f, (248, 244, 232), anchor="ma")
    y += 35
    # region strip
    p.rect(MX, y, CW, 25, fill=(238, 230, 208))
    reg = ("EUROPE 7   ·   MIDDLE EAST 6   ·   ASIA-PACIFIC 8   ·   "
           "AMERICAS 8   ·   AFRICA 2   ·   OCEANIA 1   ·   WORLD & SCIENCE 3")
    f, _ = fit_font(p, reg, SANS_B, 14, CW - 24)
    p.text(W / 2, y + 5, reg, f, NAVY, anchor="ma")
    return y + 31


def lead_panel(p, x, y, w, h, num, kicker, band, scene, headline, summary,
               tag):
    p.rect(x, y, w, h, fill=PANEL, outline=HAIR, width=1)
    p.rect(x, y, w, 25, fill=band)
    p.text(x + 9, y + 5.5, kicker, F(SANS_B, 12.5), (250, 247, 238))
    p.ellipse(x + w - 31, y + 3, 19, 19, fill=GOLD)
    p.text(x + w - 21.5, y + 5.5, str(num), F(SANS_B, 12.5), (30, 26, 18),
           anchor="ma")
    scene(p, x + 1, y + 26, w - 2, 78)
    ty = y + 111
    for ln in wrap(p, headline, F(SERIF_B, 19.5), w - 20):
        p.text(x + 10, ty, ln, F(SERIF_B, 19.5), INK)
        ty += 23
    ty += 3
    for ln in wrap(p, summary, F(SERIF, 13), w - 20):
        p.text(x + 10, ty, ln, F(SERIF, 13), (52, 50, 46))
        ty += 16.5
    f, _ = fit_font(p, tag, SANS_B, 11, w - 20)
    p.text(x + 10, y + h - 19, tag, f, RED)


LEADS = [
    ("ANTALYA, TÜRKIYE · CLIMATE SUMMIT", NAVY, scene_cop31,
     "COP31's final text lands at dawn — with no mention of fossil fuels",
     "After two days of overtime, nearly 200 countries were handed a "
     "ten-page deal that recalls the Dubai pact but never names fossil "
     "fuels. It targets electricity at 35% of final energy by 2035.",
     "FINAL TEXT AT DAWN · 10 PAGES · OVERSHOOT OF 1.5°C CONCEDED"),
    ("MANAMA, BAHRAIN · GULF SECURITY", RED, scene_bahrain,
     "Iran claims strikes on US bases in Bahrain; two bases hit",
     "The IRGC said missiles and drones hit US Patriot radars at the "
     "Al-Riffa and Awali bases. Bahrain said its defences intercepted "
     "them; an industrial site caught fire, no casualties.",
     "IRGC CLAIM · BAHRAIN: INTERCEPTED · NO CASUALTIES"),
    ("KYIV, UKRAINE · THE WAR", NAVY, scene_drones,
     "Russia's overnight barrage: 186 drones, 161 downed",
     "Ukraine's air force said 161 of 186 Russian drones — 72 of them "
     "jet-powered — were shot down or jammed by 08:00. Strikes were "
     "still recorded at 18 locations as the attack went on.",
     "AIR FORCE FIGURES · STRIKES AT 18 LOCATIONS"),
]


def leads(p, y):
    w = (CW - 24) / 3
    h = 266
    for i, (kick, band, scene, head, summ, tag) in enumerate(LEADS):
        lead_panel(p, MX + i * (w + 12), y, w, h, i + 1, kick, band,
                   scene, head, summ, tag)
    return y + h


TEN = [
    ("Hong Kong elects its Election Committee",
     "856 candidates chase 723 seats across 31 subsectors."),
    ("Verstappen wins a Las Vegas thriller",
     "0.639s clear of Norris after 35 lead changes; Piastri 3rd."),
    ("India declare at 720/9 — a record in NZ",
     "Pant 128, Rahul 136 at Wellington; NZ 119/2, trail by 233."),
    ("Bayelsa boat toll rises to 24",
     "24 bodies recovered, 24 rescued; governor orders a probe."),
    ("Iran begins rationing electricity",
     "Rolling cuts of up to two hours a day as fuel runs short."),
    ("'El Chapo Isidro' caught in Sinaloa",
     "FBI top-ten fugitive seized in Guasave after a gunfight."),
    ("Hamas seeks urgent talks after strike",
     "Three soup-kitchen workers killed delivering food in Gaza."),
    ("SEC probes Nvidia's accounting",
     "Watchdog scrutinises the chipmaker's books, Reuters says."),
    ("BepiColombo enters Mercury orbit",
     "ESA–JAXA craft arrives after an eight-year journey."),
    ("Bolsonaro in intensive care",
     "Stable, 71, with an acute abdominal obstruction in Brasília."),
]


def day_in_ten(p, y):
    p.rect(MX, y, CW, 24, fill=RED)
    p.text(W / 2, y + 3.5, "THE DAY IN TEN — SUNDAY 22 NOVEMBER 2026",
           F(SERIF_B, 16), (252, 248, 238), anchor="ma")
    y += 29
    colw = (CW - 12) / 2
    rowh = 38
    for i, (head, brief) in enumerate(TEN):
        cx = MX + (i % 2) * (colw + 12)
        cy = y + (i // 2) * rowh
        if i % 2 == 0 and i > 0:
            p.line(MX, cy - 3, W - MX, cy - 3, HAIR, 0.8)
        p.ellipse(cx, cy + 2, 21, 21, fill=NAVY)
        p.text(cx + 10.5, cy + 5.5, str(i + 1), F(SANS_B, 12), (250, 247, 238),
               anchor="ma")
        f, _ = fit_font(p, head, SANS_B, 15, colw - 34)
        p.text(cx + 30, cy, head, f, INK)
        f, _ = fit_font(p, brief, SANS, 12.5, colw - 34)
        p.text(cx + 30, cy + 19, brief, f, (70, 66, 58))
    return y + 5 * rowh


# ------------------------------------------------------------- world map
# Coarse continent polygons in (lon, lat); the strip rasterises them to a
# dot matrix and marks the lead stories' places with numbered pins.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-108, 68), (-95, 69), (-85, 66),
     (-78, 68), (-76, 60), (-65, 60), (-56, 52), (-64, 46), (-70, 43),
     (-74, 39), (-76, 35), (-80, 31), (-81, 26), (-84, 29), (-89, 29),
     (-94, 29), (-97, 26), (-96, 20), (-92, 15), (-86, 13), (-83, 9),
     (-88, 14), (-96, 16), (-104, 20), (-110, 23), (-114, 29), (-117, 33),
     (-123, 38), (-124, 46), (-131, 55), (-146, 61), (-158, 58), (-166, 61)],
    # Greenland
    [(-45, 60), (-31, 68), (-22, 70), (-21, 76), (-32, 82), (-55, 80),
     (-58, 73), (-53, 64)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-39, -13), (-40, -20), (-47, -24), (-52, -30), (-57, -35),
     (-62, -39), (-65, -43), (-67, -49), (-68, -53), (-71, -54), (-73, -48),
     (-73, -40), (-72, -32), (-70, -21), (-75, -15), (-79, -8), (-81, -4),
     (-80, 1), (-77, 5)],
    # Europe
    [(-10, 36), (-9, 43), (-5, 48), (0, 50), (5, 53), (8, 57), (13, 55),
     (18, 56), (21, 60), (19, 64), (24, 71), (31, 70), (30, 64), (26, 60),
     (28, 57), (22, 55), (15, 54), (8, 54), (3, 53), (-2, 50), (-5, 46),
     (-2, 43), (-9, 37)],
    # Britain
    [(-5, 50), (-3, 53), (-4, 56), (-6, 58), (-8, 55), (-7, 52), (-5, 51)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (12, 34), (22, 33), (30, 31), (33, 28),
     (35, 24), (38, 21), (40, 15), (43, 12), (48, 11), (51, 12), (48, 5),
     (42, -2), (40, -9), (40, -16), (36, -21), (33, -27), (27, -31),
     (20, -35), (17, -33), (15, -27), (13, -18), (12, -10), (13, -5),
     (9, -1), (9, 4), (3, 6), (-3, 5), (-8, 5), (-13, 8), (-17, 13),
     (-17, 16), (-16, 21), (-15, 26), (-13, 29), (-10, 31)],
    # Madagascar
    [(44, -16), (49, -15), (50, -20), (47, -24), (45, -25), (43, -22),
     (44, -18)],
    # Asia (mainland incl. Siberia)
    [(26, 36), (40, 36), (55, 38), (70, 36), (85, 35), (100, 32),
     (110, 30), (120, 34), (126, 38), (128, 41), (133, 44), (140, 46),
     (142, 52), (150, 59), (160, 64), (170, 66), (179, 67), (179, 71),
     (150, 72), (120, 73), (95, 74), (75, 72), (60, 69), (45, 67),
     (33, 64), (30, 57), (27, 48), (28, 41)],
    # India
    [(66, 25), (72, 20), (76, 10), (78, 8), (80, 14), (84, 19), (88, 22),
     (91, 24), (90, 28), (84, 33), (76, 34), (68, 28)],
    # Arabia
    [(34, 31), (39, 22), (43, 12), (48, 14), (55, 17), (59, 22), (56, 26),
     (50, 29), (48, 30), (42, 38), (36, 36)],
    # South-east Asia
    [(92, 22), (95, 16), (98, 10), (100, 7), (102, 9), (104, 12),
     (106, 10), (108, 15), (106, 20), (102, 22), (98, 24)],
    # Indonesia / New Guinea
    [(94, 6), (105, 6), (112, 1), (118, -2), (112, -4), (100, -2), (95, 2)],
    [(109, 1), (113, 4), (118, 2), (117, -2), (110, -3)],
    [(131, -1), (138, -2), (145, -5), (150, -9), (143, -8), (136, -4),
     (131, -3)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44),
     (140, 43), (138, 38), (135, 34), (131, 32)],
    # Australia
    [(113, -22), (114, -29), (115, -33), (119, -35), (126, -32), (132, -32),
     (135, -35), (139, -37), (144, -38), (148, -38), (150, -37), (153, -31),
     (153, -27), (150, -23), (146, -19), (142, -15), (142, -11), (137, -12),
     (136, -15), (135, -12), (132, -11), (129, -13), (126, -14), (122, -17),
     (118, -20)],
    # New Zealand
    [(167, -45), (171, -42), (174, -41), (176, -38), (174, -37), (172, -41),
     (169, -44), (167, -46)],
]


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            xin = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < xin:
                inside = not inside
    return inside


PINS = [  # (number, lon, lat, nudge_x, nudge_y)
    (1, 30.7, 36.9, 13, 6),      # Antalya
    (2, 50.6, 26.2, 0, 0),       # Manama
    (3, 30.5, 50.4, -11, -3),    # Kyiv
    (4, 114.2, 22.3, 0, 0),      # Hong Kong
    (5, -115.1, 36.2, 0, 0),     # Las Vegas
    (6, 174.8, -41.3, -7, -9),   # Wellington
    (7, 6.1, 4.9, 0, 0),         # Bayelsa
]


def world_map(p, y, h=46):
    p.rect(MX, y, CW, h, fill=(238, 230, 208))
    cols, rows = 168, 13
    for r in range(rows):
        lat = 80 - (r + 0.5) * (130 / rows)
        for c in range(cols):
            lon = -180 + (c + 0.5) * (360 / cols)
            if any(_in_poly(lon, lat, poly) for poly in CONTINENTS):
                cx = MX + (c + 0.5) * CW / cols
                cy = y + (r + 0.5) * h / rows
                p.ellipse(cx - 1.7, cy - 1.7, 3.4, 3.4, fill=(66, 78, 108))
    for num, lon, lat, nx, ny in PINS:
        cx = MX + (lon + 180) / 360 * CW
        cy = y + (80 - lat) / 130 * h
        if nx or ny:
            p.line(cx, cy, cx + nx, cy + ny, fill=RED, width=1)
        p.ellipse(cx + nx - 7.5, cy + ny - 7.5, 15, 15, fill=RED)
        p.text(cx + nx, cy + ny - 5.5, str(num), F(SANS_B, 10),
               (255, 250, 240), anchor="ma")
    return y + h


ALSO = [
    "Europe wins a seat at Russia–Ukraine talks in Berlin",
    "EU plastic-waste export ban to non-OECD states begins",
    "Houthis strike Saudi Arabia after Hodeida operation",
    "Leeds stun Chelsea 4–1, first win at the Bridge since 1999",
    "Magnitude 6.8 quake strikes Banda Sea off Timor-Leste",
    "Myanmar rejects UN court ruling on Rohingya as 'unfair'",
    "China opposes US ban on its telecoms' number access",
    "Nepal's PM Shah begins first India visit, meets Modi",
    "British swimmer completes three-day Hormuz swim",
    "Historic rain floods Satellite Beach, Florida",
    "151 humanoid robots dance in sync in Shenzhen — a record",
    "Amazon nears $7.5bn deal for Israeli AI firm Decart",
    "Trump confirms breach of FBI fingerprint database",
    "IBM unveils 520-qubit 'Nighthawk r3' processor",
    "Pakistan says 15 militants killed in Mastung",
    "China renews UN bid to blacklist BLA, Majeed Brigade",
    "Israeli army launches new attacks in south Lebanon",
    "Sevastopol rations petrol after Crimea Bridge strikes",
    "Russian cargo ship burns in the Gulf of Finland",
    "NATO troops practise Neman River crossing in Lithuania",
    "Gas explosion rocks Awoyaya bus station in Lekki, Nigeria",
    "WHO warns antibiotic resistance is outpacing new drugs",
]


def also_list(p, y):
    p.rect(MX, y, CW, 21, fill=NAVY)
    p.text(MX + 9, y + 4, "ALSO ON SUNDAY 22 NOVEMBER — 22 MORE STORIES",
           F(SANS_B, 12.5), (250, 247, 238))
    y += 26
    colw = (CW - 12) / 2
    for i, item in enumerate(ALSO):
        cx = MX + (i % 2) * (colw + 12)
        cy = y + (i // 2) * 13.2
        label = f"{i + 14}. {item}"
        f, _ = fit_font(p, label, SANS, 11.5, colw - 4)
        p.text(cx, cy, label, f, (44, 42, 38))
    return y + 11 * 13.2


def footer(p, y):
    p.line(MX, y, W - MX, y, INK, 1.6)
    y += 6
    note = ("DATE CHECK — READ THIS FIRST: every story on this page "
            "happened, or was first reported, on Sunday 22 November 2026 "
            "in some time zone. Claims are labelled as claims; figures "
            "are as reported by the officials and agencies named.")
    for ln in wrap(p, note, F(SERIF_I, 12), CW - 60):
        p.text(W / 2, y, ln, F(SERIF_I, 12), (60, 56, 48), anchor="ma")
        y += 14.5
    src = ("Sources: Reuters · AP · AFP · Xinhua · Anadolu · ESA · GFZ · "
           "NEMA · Ukrainian Air Force · Hong Kong Electoral Affairs "
           "Commission · Formula 1 — drawn and typeset by program; "
           "no photographs.")
    f, _ = fit_font(p, src, SANS, 10.5, CW - 40)
    p.text(W / 2, y + 1, src, f, GREY, anchor="ma")
    return y + 15


def main():
    p = Page()
    y = masthead(p)
    y = leads(p, y + 6)
    y = day_in_ten(p, y + 5)
    y = world_map(p, y + 4, 42)
    y = also_list(p, y + 5)
    y = footer(p, y + 4)
    assert y <= H - 4, f"page overflow: content ends at {y}"
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    p.save(out)
    print("wrote", out, "content ends at y =", round(y, 1))


if __name__ == "__main__":
    main()
