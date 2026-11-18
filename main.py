#!/usr/bin/env python3
"""THE WORLD - Diplomacy Day front page, 18 November 2026.
Pure stdlib PNG encoder + hand-typed 5x7 bitmap font. Deterministic.
Run: python3 -P -s main.py  ->  $MAKEFUN_OUTPUT_DIR/entry.png
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---- palette ----
PAPER = (245, 239, 224)
INK = (20, 20, 22)
TEAL = (15, 76, 92)
TEAL_LT = (27, 110, 130)
GOLD = (198, 148, 44)
RED = (178, 44, 36)
BLUE = (38, 84, 160)
WHITE = (255, 255, 255)
GREY = (90, 90, 88)
LTGREY = (226, 220, 205)
DARK = (32, 44, 52)
GREEN = (46, 125, 70)
SKIN = (232, 190, 150)
SUIT = (38, 52, 74)
SUIT2 = (84, 44, 44)

# ---- 5x7 bitmap font, each glyph 7 rows of 5 bits (MSB = left) ----
def _g(*rows):
    return tuple(int(r, 2) for r in rows)

FONT = {
    "A": _g("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": _g("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": _g("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": _g("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": _g("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": _g("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": _g("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": _g("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": _g("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": _g("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": _g("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": _g("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": _g("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": _g("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": _g("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": _g("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": _g("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": _g("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": _g("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": _g("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": _g("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": _g("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": _g("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": _g("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": _g("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": _g("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": _g("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": _g("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": _g("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": _g("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": _g("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": _g("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": _g("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": _g("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": _g("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": _g("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": _g("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": _g("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": _g("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": _g("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": _g("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": _g("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": _g("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": _g("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": _g("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": _g("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": _g("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": _g("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": _g("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": _g("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": _g("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": _g("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": _g("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}

# ---- canvas ----
buf = bytearray(W * H * 3)
for _i in range(W * H):
    buf[_i * 3] = PAPER[0]
    buf[_i * 3 + 1] = PAPER[1]
    buf[_i * 3 + 2] = PAPER[2]


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def tri(x1, y1, x2, y2, x3, y3, c):
    # scanline fill for a triangle
    ys = sorted([y1, y2, y3])
    for yy in range(ys[0], ys[2] + 1):
        xs = []
        for (ax, ay, bx, by) in ((x1, y1, x2, y2), (x2, y2, x3, y3), (x3, y3, x1, y1)):
            if ay == by:
                continue
            if min(ay, by) <= yy < max(ay, by) or (yy == ys[2] and yy == max(ay, by)):
                t = (yy - ay) / (by - ay)
                xs.append(ax + t * (bx - ax))
        if len(xs) >= 2:
            a, b = int(min(xs)), int(max(xs))
            for xx in range(a, b + 1):
                px(xx, yy, c)


def text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def text_centre(cx, y, s, scale, c):
    return text(cx - text_w(s, scale) // 2, y, s, scale, c)


def wrap(s, scale, max_w):
    words = s.split(" ")
    lines = []
    cur = ""
    max_chars = max(1, max_w // (6 * scale))
    for wrd in words:
        trial = (cur + " " + wrd).strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wrd
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, scale, c, max_w, leading=None):
    if leading is None:
        leading = 9 * scale
    for ln in wrap(s, scale, max_w):
        text(x, y, ln, scale, c)
        y += leading
    return y


def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(buf[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")


def draw_flag_us(x, y, w, h):
    rect(x, y, w, h, WHITE)
    for i in range(7):
        if i % 2 == 0:
            rect(x, y + i * h // 7, w, h // 7 + 1, RED)
    rect(x, y, w * 2 // 5, h * 4 // 7, BLUE)
    for r in range(3):
        for c in range(4):
            px(x + 4 + c * 7, y + 4 + r * 6, WHITE)
            px(x + 5 + c * 7, y + 4 + r * 6, WHITE)


def draw_flag_ph(x, y, w, h):
    rect(x, y, w, h // 2, BLUE)
    rect(x, y + h // 2, w, h - h // 2, RED)
    tri(x, y, x, y + h, x + w // 3, y + h // 2, WHITE)
    circle(x + w // 6, y + h // 2, 4, GOLD)


def draw_flag_cn(x, y, w, h):
    rect(x, y, w, h, RED)
    for (sx, sy) in ((6, 5), (16, 3), (20, 8), (20, 14), (16, 18)):
        px(x + sx, y + sy, GOLD)
        px(x + sx + 1, y + sy, GOLD)
        px(x + sx, y + sy + 1, GOLD)


def draw_summit(x, y, w, h):
    rect(x, y, w, h, (214, 232, 228))
    rect(x, y, w, 4, TEAL)
    rect(x, y + h - 4, w, 4, TEAL)
    # flags on poles, left to right: US, Philippines, China
    for (fx, fn) in ((x + 60, draw_flag_us), (x + 200, draw_flag_ph), (x + 340, draw_flag_cn)):
        vline(fx + 2, y + 12, 80, INK, 3)
        fn(fx + 5, y + 14, 84, 48)
    # conference table
    rect(x + 480, y + 128, 420, 16, (122, 82, 52))
    rect(x + 500, y + 144, 14, 40, (90, 60, 38))
    rect(x + 866, y + 144, 14, 40, (90, 60, 38))
    # papers on table
    rect(x + 540, y + 116, 70, 12, WHITE)
    rect(x + 660, y + 116, 70, 12, WHITE)
    rect(x + 780, y + 116, 70, 12, WHITE)
    # three seated figures: heads + suits, torsos end at the table top
    for (hx, suit) in ((560, SUIT), (700, SUIT2), (840, SUIT)):
        circle(hx, y + 64, 24, SKIN)
        rect(hx - 32, y + 90, 64, 38, suit)
        rect(hx - 6, y + 90, 12, 38, WHITE)
        tri(hx - 8, y + 92, hx + 8, y + 92, hx, y + 108, RED)


def story(x, y, w, kick, head, body, hcol=RED):
    rect(x, y, 52, 6, hcol)
    text(x, y + 12, kick, 2, hcol)
    y2 = para(x, y + 34, head, 3, INK, w, leading=26)
    y3 = para(x, y2 + 4, body, 2, (52, 52, 50), w, leading=17)
    return y3


def draw_page():
    rect(0, 0, W, 10, TEAL)
    rect(0, H - 10, W, 10, TEAL)
    # masthead
    text_centre(512, 26, "THE WORLD", 10, TEAL)
    hline(36, 108, 952, INK, 3)
    text_centre(512, 120, "WEDNESDAY, 18 NOVEMBER 2026", 3, INK)
    text_centre(512, 146, "DIPLOMACY DAY  -  MANILA TO SHENZHEN", 2, RED)
    hline(36, 172, 952, INK, 2)
    # lead headline
    text(36, 186, "TRUMP IN MANILA,", 4, INK)
    text(36, 220, "THEN TO SHENZHEN", 4, INK)
    para(36, 254, "PRESIDENT MEETS MARCOS JR. IN MANILA, THEN FLIES TO THE APEC SUMMIT HOSTED BY XI JINPING.", 2, (52, 52, 50), 952, leading=17)
    # summit scene
    draw_summit(36, 296, 952, 196)
    # timeline strip
    ty = 504
    text(36, ty, "THE TALKS TIMELINE", 2, TEAL)
    hline(36, ty + 20, 952, TEAL, 2)
    boxes = [
        ("MANILA - WED", "TRUMP + MARCOS JR.", "BILATERAL TALKS", "AND WORKING LUNCH"),
        ("SHENZHEN - APEC", "XI HOSTS SUMMIT", "CANADA + CHINA", "EXTEND TRADE DEALS"),
        ("THURSDAY - 19 NOV", "US - CHINA - RUSSIA", "ARMS CONTROL + THE", "WARS IN UKRAINE, IRAN"),
    ]
    bx = 36
    for (t1, t2, t3, t4) in boxes:
        rect(bx, ty + 30, 300, 82, WHITE)
        rect(bx, ty + 30, 300, 82, TEAL)
        rect(bx + 2, ty + 32, 296, 78, WHITE)
        text(bx + 12, ty + 38, t1, 2, RED)
        text(bx + 12, ty + 58, t2, 2, INK)
        text(bx + 12, ty + 76, t3, 2, (52, 52, 50))
        text(bx + 12, ty + 90, t4, 2, (52, 52, 50))
        bx += 326
    # two-column briefs
    hline(36, 624, 952, INK, 2)
    y = 636
    y = story(36, y, 460, "UKRAINE", "BRIDGE HIT, KYIV POUNDED",
              "UKRAINE HIT THE CRIMEA BRIDGE. GERMANY PLANS $300M FOR PAC-2, PAC-3.")
    y = story(36, y + 12, 460, "IRAN", "DRONE ATTACK IN BAHRAIN",
              "IRAN HIT A US RADAR IN BAHRAIN. THE US WARNS OF A BOMB THREAT TO WASHINGTON.", hcol=TEAL)
    y = story(36, y + 12, 460, "TAIWAN", "FLIGHT ROW AT THE UN",
              "THE US PRESSES A UN AGENCY OVER TAIWAN FLIGHT RULES. CHINA HITS BACK.", hcol=GOLD)
    y = 636
    y = story(528, y, 460, "ISRAEL", "NO JOINT GOVERNMENT",
              "OPPOSITION RULES OUT JOINT RULE WITH NETANYAHU. NEW SPEAKER LIKELY.")
    y = story(528, y + 12, 460, "WORLD COURT", "MYANMAR RULING DUE",
              "THE INTERNATIONAL COURT OF JUSTICE IS TO RULE ON MYANMAR.", hcol=TEAL)
    y = story(528, y + 12, 460, "MANILA", "PROTESTS AND AI CASH",
              "PROTESTS OVER THE IRAN WAR AND PAX SILICA. TRUMP ANNOUNCED $85M FOR AI.", hcol=GOLD)
    # footer: midterms + Kim meeting floated
    hline(36, 960, 952, INK, 2)
    para(36, 970, "ALSO: REPUBLICANS SUFFERED SWEEPING MIDTERM DEFEATS BEFORE TRUMP FLEW TO ASIA. A KIM JONG UN MEETING IS FLOATED.", 2, (52, 52, 50), 952, leading=17)


def main():
    draw_page()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes()
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
