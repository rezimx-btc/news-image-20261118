#!/usr/bin/env python3
"""news-image-20261118 round 2 — one page of world news for Wednesday 18 Nov 2026.

Draws a 1024x1024 front page with a pure-stdlib PNG encoder, a 5x7 bitmap
font, a stylised world map with numbered story pins, a lead-story Gulf
schematic, a story grid, a markets strip and an in-brief footer.
Deterministic: no randomness, no time, no network. Same bytes every run.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (163, 30, 30)
BLUE = (31, 78, 121)
GRAY = (112, 108, 96)
OCEAN = (214, 228, 236)
LAND = (52, 68, 74)
LIGHT = (233, 226, 210)
GOLD = (176, 141, 60)
SEA = (188, 210, 224)
SAND = (226, 214, 182)


def _chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data
            + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))


def save_png(path, img, w, h):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw.extend(img[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x0, x1, y, c):
        if y < 0 or y >= self.h:
            return
        a = max(0, min(x0, x1))
        b = min(self.w - 1, max(x0, x1))
        for x in range(a, b + 1):
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def vline(self, x, y0, y1, c):
        if x < 0 or x >= self.w:
            return
        a = max(0, min(y0, y1))
        b = min(self.h - 1, max(y0, y1))
        for y in range(a, b + 1):
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def ring(self, cx, cy, r, c):
        steps = max(24, r * 6)
        for i in range(steps):
            a = 2 * 3.141592653589793 * i / steps
            x = int(cx + r * 0.999 * math.cos(a) + 0.5)
            y = int(cy + r * 0.999 * math.sin(a) + 0.5)
            self.set(x, y, c)
            self.set(x + 1, y, c)
            self.set(x, y + 1, c)

    def fill_poly(self, pts, c):
        if len(pts) < 3:
            return
        miny = min(p[1] for p in pts)
        maxy = max(p[1] for p in pts)
        n = len(pts)
        for y in range(miny, maxy + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, c)


# --- 5x7 bitmap font: each glyph is 7 rows, 5 bits, MSB is the left column ---
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x0E, 0x10, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x01, 0x0E),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "+": (0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "*": (0x00, 0x15, 0x0E, 0x15, 0x00, 0x00, 0x00),
    "•": (0x00, 0x00, 0x0C, 0x0C, 0x0C, 0x00, 0x00),
    "°": (0x0C, 0x12, 0x12, 0x0C, 0x00, 0x00, 0x00),
    "—": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
}


def glyph(ch):
    return FONT.get(ch, FONT.get(ch.upper(), (0, 0, 0, 0, 0, 0, 0)))


def text_w(text, s):
    return len(text) * 6 * s - s


def draw_text(cv, x, y, s, color, text):
    cx = x
    for ch in text:
        g = glyph(ch)
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits >> (4 - col) & 1:
                    cv.rect(cx + col * s, y + row * s, s, s, color)
        cx += 6 * s
    return cx


def draw_text_centered(cv, cx, y, s, color, text):
    draw_text(cv, cx - text_w(text, s) // 2, y, s, color, text)


def wrap_lines(text, s, maxw):
    words = text.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, s) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, s, color, text, maxw, leading):
    yy = y
    for ln in wrap_lines(text, s, maxw):
        draw_text(cv, x, yy, s, color, ln)
        yy += 7 * s + leading
    return yy


# --- world map: continent outlines as (lon, lat) polygons ---
CONTINENTS = [
    [(-168, 66), (-155, 71), (-125, 70), (-85, 66), (-60, 55), (-53, 48),
     (-65, 44), (-81, 26), (-90, 21), (-80, 9), (-105, 20), (-112, 28),
     (-122, 38), (-130, 55)],
    [(-45, 60), (-30, 70), (-20, 76), (-55, 76), (-58, 64)],
    [(-77, 11), (-62, 10), (-35, -8), (-40, -20), (-48, -28), (-58, -38),
     (-65, -45), (-70, -52), (-73, -37), (-80, -5), (-77, 2)],
    [(-6, 35), (10, 37), (32, 31), (51, 11), (48, -2), (40, -15),
     (35, -28), (19, -35), (12, -18), (9, 4), (-8, 5), (-15, 11), (-17, 15)],
    [(-9, 37), (-2, 48), (5, 58), (18, 69), (30, 70), (60, 69), (100, 76),
     (140, 72), (170, 66), (178, 65), (158, 56), (140, 45), (130, 42),
     (120, 38), (108, 20), (105, 10), (100, 8), (98, 16), (101, 3),
     (95, 15), (88, 22), (77, 8), (72, 20), (66, 25), (57, 26), (59, 22),
     (48, 17), (43, 12), (39, 21), (36, 36), (30, 36), (26, 40), (23, 36),
     (19, 42), (12, 44), (8, 44), (3, 43), (0, 39)],
    [(-5, 50), (-2, 58), (0, 58), (1, 52), (-3, 53)],
    [(130, 31), (137, 34), (140, 38), (141, 45), (139, 44), (132, 43),
     (130, 35)],
    [(114, -22), (124, -14), (136, -12), (142, -11), (147, -19), (153, -27),
     (150, -37), (140, -38), (129, -32), (115, -32), (113, -25)],
    [(167, -45), (174, -41), (178, -38), (173, -35)],
]

# (lon, lat, story number) — pins on the map
PINS = [
    (56, 27, "1"),
    (36.5, 45, "2"),
    (114, 22.5, "3"),
    (-150, 64, "4"),
    (23, -2, "5"),
    (-98, 39, "6"),
    (86, 55, "7"),
    (34.5, 31.5, "8"),
]


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    x = x0 + (lon + 180.0) / 360.0 * w
    y = y0 + (90.0 - lat) / 150.0 * h
    return int(x + 0.5), int(y + 0.5)


def draw_map(cv, x0, y0, w, h):
    cv.rect(x0, y0, w, h, OCEAN)
    # graticule
    for gx in range(1, 6):
        cv.vline(x0 + gx * w // 6, y0, y0 + h, (198, 214, 224))
    for gy in range(1, 4):
        cv.hline(x0, x0 + w, y0 + gy * h // 4, (198, 214, 224))
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, x0, y0, w, h) for lon, lat in poly]
        cv.fill_poly(pts, LAND)
    for lon, lat, num in PINS:
        px, py = lonlat_to_xy(lon, lat, x0, y0, w, h)
        cv.disc(px, py, 11, RED)
        cv.ring(px, py, 11, PAPER)
        tw = text_w(num, 2)
        draw_text(cv, px - tw // 2, py - 7, 2, PAPER, num)


def draw_gulf(cv, x0, y0, w, h):
    # schematic of the Persian Gulf: Iran above, sea below, three targets
    cv.rect(x0, y0, w, h, PAPER)
    cv.rect(x0, y0, w, 2, INK)
    cv.rect(x0, y0 + h - 2, w, 2, INK)
    cv.rect(x0, y0, w, 46, SAND)
    draw_text(cv, x0 + 12, y0 + 12, 2, INK, "IRAN")
    draw_text(cv, x0 + 12, y0 + 28, 2, GRAY, "MISSILE SITE")
    # sea
    cv.rect(x0, y0 + 46, w, h - 46, SEA)
    draw_text(cv, x0 + w - 118, y0 + h - 20, 2, BLUE, "GULF")
    # targets: Qeshm, Bahrain, Kuwait
    spots = [(0.30, "QESHM"), (0.58, "BAHRAIN"), (0.84, "KUWAIT")]
    for frac, name in spots:
        sx = x0 + int(w * frac)
        sy = y0 + 46 + (h - 46) // 2
        cv.line(x0 + int(w * 0.18), y0 + 40, sx, sy - 8, RED)
        cv.disc(sx, sy, 6, RED)
        draw_text(cv, sx - text_w(name, 2) // 2, sy + 12, 2, INK, name)
    draw_text(cv, x0 + 12, y0 + h - 20, 2, GRAY, "U.S. STRIKE")


# --- the day's stories (number, kicker, headline, one-line deck) ---
STORIES = [
    ("2", "UKRAINE — EUROPE",
     "UKRAINE HITS CRIMEA BRIDGE AGAIN",
     "Road span falls into the strait."),
    ("3", "ASIA — SUMMIT",
     "XI, PUTIN, TRUMP MEET IN SHENZHEN",
     "Three-leader summit set for Thursday."),
    ("4", "UNITED STATES",
     "PELTOLA WINS ALASKA SENATE SEAT",
     "Democrats take 56 seats in the Senate."),
    ("5", "AFRICA — HEALTH",
     "EBOLA IN CONGO MORE THAN DOUBLES",
     "11,000 cases and 5,400 deaths."),
    ("6", "UNITED STATES — HEALTH",
     "U.S. LOSES MEASLES-FREE STATUS",
     "5,400 cases end 26 years free."),
    ("7", "RUSSIA — DISASTER",
     "RUSSIAN PLANE CRASHES; 19 DEAD",
     "Military aircraft down in Siberia."),
    ("8", "GAZA — MIDDLE EAST",
     "COLD KILLS IN GAZA TENTS",
     "Four nations press Israel over aid."),
]

BRIEF_ITEMS = [
    "PNG hit by a 6.0 quake.",
    "Cyclone Xavier, Cat 5, hits Cooks.",
    "Waymo pulls taxis from U.S. freeways.",
    "Herzog taps Eisenkot in Israel.",
    "France: 4th weekend of protests.",
]


def draw_story(cv, x, y, num, kicker, headline, deck):
    cv.rect(x, y, 30, 30, RED)
    draw_text(cv, x + 10, y + 8, 2, PAPER, num)
    draw_text(cv, x + 40, y + 2, 2, RED, kicker)
    draw_block(cv, x + 40, y + 20, 3, INK, headline, 430, 3)
    draw_text(cv, x, y + 68, 2, INK, deck)


def draw_brief(cv, x, y):
    draw_text(cv, x, y + 2, 2, RED, "IN BRIEF")
    yy = y + 22
    for item in BRIEF_ITEMS:
        draw_text(cv, x, yy, 2, INK, "• " + item)
        yy += 15


def main():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(32, 8, 960, 2, INK)
    draw_text_centered(cv, 512, 16, 7, INK, "THE WORLD IN ONE DAY")
    cv.rect(32, 72, 960, 2, INK)
    draw_text_centered(cv, 512, 80, 4, RED, "WEDNESDAY 18 NOVEMBER 2026")
    cv.rect(32, 112, 960, 3, INK)
    # lead story
    draw_text(cv, 32, 128, 2, RED, "LEAD STORY — THE GULF")
    draw_block(cv, 32, 152, 5, INK,
               "U.S. STRIKES IRANIAN MISSILE SITE ON QESHM", 640, 6)
    draw_block(cv, 32, 246, 2, INK,
               "Iran answers with drones at Bahrain and Kuwait "
               "as the Gulf braces for a wider war.", 608, 4)
    draw_gulf(cv, 664, 130, 328, 156)
    cv.rect(32, 294, 960, 2, INK)
    # world map
    draw_text(cv, 32, 300, 2, INK,
              "THE WORLD AT A GLANCE — EIGHT STORIES, NUMBERED ON THE MAP")
    draw_map(cv, 32, 322, 960, 188)
    cv.rect(32, 518, 960, 2, INK)
    # story grid: 2 columns x 4 rows; last cell is IN BRIEF
    cells = [(32, 526), (522, 526), (32, 616), (522, 616),
             (32, 706), (522, 706), (32, 796), (522, 796)]
    for (x, y), (num, kicker, headline, deck) in zip(cells[:7], STORIES):
        draw_story(cv, x, y, num, kicker, headline, deck)
    draw_brief(cv, cells[7][0], cells[7][1])
    # markets strip
    cv.rect(32, 894, 960, 52, INK)
    draw_text(cv, 48, 904, 2, PAPER,
              "MARKETS — CAC 40 8,216.78 -1.62% • DAX 26,045.37 -2.08% • FTSE -1.76%")
    draw_text(cv, 48, 924, 2, PAPER,
              "S&P 500 7,340.53 -1.03% • NASDAQ 24,328.38 -0.74% • NIKKEI 225 59,024.28 +0.20%")
    # footer
    draw_text_centered(cv, 512, 962, 2, GRAY,
                       "All events happened, or were first reported, on Wednesday 18 November 2026.")
    draw_text_centered(cv, 512, 984, 2, INK,
                       "THE WORLD IN ONE DAY • news-image-20261118 • make.fun")
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    n = save_png(path, cv.px, W, H)
    print("wrote", path, n, "bytes")


if __name__ == "__main__":
    main()
