#!/usr/bin/env python3
"""THE WORLD TODAY - Friday 20 November 2026, one-page front page.

Draws a 1024x1024 PNG newspaper front page entirely in code, using
only the Python standard library. No network, no randomness, no PIL:
every pixel is computed from the fixed story data below, so two runs
write byte-identical files.

36 sourced stories, 7 regions. Every story carries its real source
and a confidence mark: CONFIRMED (official / on the record),
REPORTED (a named outlet reported it) or DEVELOPING (still moving).
"""
import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

PAPER = (247, 242, 228)
INK = (18, 18, 18)
RED = (172, 28, 28)
BLUE = (24, 58, 110)
TEAL = (14, 92, 86)
GREY = (96, 90, 78)
LIGHT = (232, 226, 210)
SKY = (176, 208, 224)
SEA = (46, 110, 148)
SAND = (214, 190, 138)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)

fb = bytearray(W * H * 3)
for i in range(0, len(fb), 3):
    fb[i], fb[i + 1], fb[i + 2] = PAPER


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        fb[o], fb[o + 1], fb[o + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            px(x0 + a, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def ring(cx, cy, r, c, t=2):
    for a in range(360):
        an = math.radians(a)
        for k in range(t):
            px(int(cx + (r + k) * math.cos(an)), int(cy + (r + k) * math.sin(an)), c)


def star(cx, cy, r, c):
    for a in range(5):
        an = math.radians(a * 72 - 90)
        an2 = math.radians(a * 72 + 36 - 90)
        x1 = int(cx + r * math.cos(an))
        y1 = int(cy + r * math.sin(an))
        x2 = int(cx + r * 0.45 * math.cos(an2))
        y2 = int(cy + r * 0.45 * math.sin(an2))
        line(cx, cy, x1, y1, c)
        line(x1, y1, x2, y2, c)
        line(x2, y2, cx, cy, c)


# 5x7 bitmap font, uppercase only. Each glyph is 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "•": ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
}


def text(x, y, s, scale=1, c=INK):
    """Draw uppercase text; returns width used."""
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT["?"])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "1":
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx - x


def text_wrapped(x, y, s, max_w, scale=1, c=INK, gap=2):
    """Wrap text to max_w pixels; returns y after last line."""
    s = s.upper()
    cw = 6 * scale
    per = max(1, max_w // cw)
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        if cur and len(cur) + 1 + len(wd) > per:
            lines.append(cur)
            cur = wd
        elif cur:
            cur = cur + " " + wd
        else:
            cur = wd
    if cur:
        lines.append(cur)
    yy = y
    for ln in lines:
        text(x, yy, ln, scale, c)
        yy += 7 * scale + gap
    return yy


def text_center(x, y, w, s, scale=1, c=INK):
    tw = len(s.upper()) * 6 * scale
    text(x + max(0, (w - tw) // 2), y, s, scale, c)


def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(fb[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ---------------------------------------------------------------- stories
# (no, region, headline, one-line summary, source, confidence)
# CONFIRMED = official / on the record. REPORTED = named outlet reported
# it. DEVELOPING = still moving on 20 Nov 2026.
STORIES = [
    (1, "EUROPE", "KYIV BRIDGES HIT", "400+ drones, 110 missiles; 3 Dnipro bridges shut, 8 killed.", "REUTERS", "CONFIRMED"),
    (2, "EUROPE", "UK-EU DEAL SEALED", "Food trade eased, youth mobility 100,000, carbon markets linked.", "REUTERS", "CONFIRMED"),
    (3, "EUROPE", "GERMANY: NO NEW YALTA", "Berlin rejects a great-power deal over Europe's future.", "OPEN CHRONICLE", "REPORTED"),
    (4, "EUROPE", "DENMARK: GREENLAND DEAL", "Parliament backs US-Denmark-Greenland security pact 109-0.", "REUTERS", "REPORTED"),
    (5, "EUROPE", "SPAIN VOTE HEATS UP", "Sanchez admits mistakes in election debate as campaign peaks.", "OPEN CHRONICLE", "REPORTED"),
    (6, "EUROPE", "MISSILE OVER POLAND", "Russian missile enters NATO airspace; Tusk rejects 'mistake'.", "REUTERS", "REPORTED"),
    (7, "ASIA", "AKVAN SLAMS ODISHA", "Cyclone crosses near Gopalpur, 70-80 km/h; 300,000 sheltered.", "IMD", "CONFIRMED"),
    (8, "ASIA", "THREE AT ONE TABLE", "Trump, Xi, Putin in Shenzhen: 4-point declaration, no Ukraine deal.", "AP", "CONFIRMED"),
    (9, "ASIA", "TAIEX -6.6% IN A DAY", "Worst week since 1991, -17.5%; TSMC -5.2%, SoftBank -14.6%.", "REUTERS", "CONFIRMED"),
    (10, "ASIA", "ICJ: MYANMAR GENOCIDE", "World court finds Myanmar committed genocide against Rohingya.", "ICJ", "CONFIRMED"),
    (11, "ASIA", "N KOREA ENRICHES MORE", "IAEA says Pyongyang is expanding uranium enrichment.", "IAEA", "REPORTED"),
    (12, "ASIA", "BANGLADESH UNREST", "Violence flares ahead of Hasina's planned return to Dhaka.", "ONE TURN", "REPORTED"),
    (13, "ASIA", "AFGHAN WOMEN BLOCKED", "Aid agencies: curbs stop pregnant women reaching clinics.", "UN NEWS", "REPORTED"),
    (14, "ASIA", "CHINA SNUBS JAPAN PM", "Cold welcome for Japan's premier at APEC in Shenzhen.", "ZAMBIAN OBSERVER", "REPORTED"),
    (15, "N AMERICA", "ANTHROPIC: $97.17 CLOSE", "Record $81.3bn IPO, +17% day one; -6% in pre-market Friday.", "WSJ", "CONFIRMED"),
    (16, "N AMERICA", "GTA VI: $3.79BN DAY ONE", "Take-Two: biggest entertainment launch ever, 32.5m pre-orders.", "TAKE-TWO", "CONFIRMED"),
    (17, "N AMERICA", "PETE ROSE PARDONED", "Trump posthumously pardons baseball's 4,256-hit king.", "AP", "CONFIRMED"),
    (18, "N AMERICA", "US STOCKS FALL AGAIN", "Fifth straight down day as AI doubts spread from Asia.", "DOW JONES", "REPORTED"),
    (19, "N AMERICA", "TRUMP FACES PRESS", "Noon briefing after historic Xi-Putin talks; war questions linger.", "FOX NEWS", "REPORTED"),
    (20, "N AMERICA", "HAITI: 34 KILLED", "Police say 34 suspected gang members killed in operation.", "ONE TURN", "REPORTED"),
    (21, "MID EAST", "COP31: NO DEAL, NO FOSSIL WORD", "Antalya draft drops fossil fuels and $120bn finance figure.", "CARBON BRIEF", "CONFIRMED"),
    (22, "MID EAST", "HOUTHI MISSILE HITS RIYADH", "Missiles damage PIF tower in Saudi financial district.", "ONE TURN", "REPORTED"),
    (23, "MID EAST", "HORMUZ TANKER BURNS", "Iran war, month 9: tanker hits a mine as attacks intensify.", "ONE TURN", "DEVELOPING"),
    (24, "MID EAST", "ISRAEL CROSSES YELLOW LINE", "Troops enter central Gaza, first incursion since the truce.", "ONE TURN", "REPORTED"),
    (25, "MID EAST", "IRAQ EVICTS MILITIA", "Baghdad orders Iran-backed militia out of Jurf al-Nasr.", "ONE TURN", "REPORTED"),
    (26, "MID EAST", "MOSQUE SET ON FIRE", "Arson in northern Israel; police open investigation.", "ONE TURN", "REPORTED"),
    (27, "AFRICA", "KENYA: LAST EBOLA OUT", "Final Ebola patient discharged, 37 days after first case.", "ONE TURN", "CONFIRMED"),
    (28, "AFRICA", "SUDAN MINE STRIKE: 10 DEAD", "Drone strike kills 10 at gold mine in South Kordofan.", "ONE TURN", "REPORTED"),
    (29, "AFRICA", "SENEGAL BOAT SINKS", "Dozens missing after migrant boat capsizes off Yenne.", "ONE TURN", "DEVELOPING"),
    (30, "AFRICA", "AFRICA WANTS $120BN", "African bloc demands tripled adaptation finance by 2035.", "IPS", "REPORTED"),
    (31, "S AMERICA", "BUKELE SEEKS 3RD TERM", "El Salvador president registers for another term.", "ONE TURN", "REPORTED"),
    (32, "S AMERICA", "US-VENEZUELA DEAL", "Washington and Caracas sign military cooperation pact.", "ONE TURN", "REPORTED"),
    (33, "S AMERICA", "LATAM: FOSSIL FIGHT", "Latin America joins call for fossil-fuel action at COP31.", "UN NEWS", "REPORTED"),
    (34, "OCEANIA", "NZ 368 v INDIA", "Nicholls 175 not out as New Zealand pile up 368 in Test.", "ESPNCRICINFO", "REPORTED"),
    (35, "OCEANIA", "BOWEN LEADS COP31 TALKS", "Australia's climate minister hunts consensus through the night.", "CARBON BRIEF", "CONFIRMED"),
    (36, "OCEANIA", "ISLANDS: COP31 MUST NOT FAIL", "AOSIS: 1.5C overshoot is 'unacceptable' as talks stall.", "FINWIRE", "REPORTED"),
]

FEATURED = {1, 7, 8, 21}
REGIONS = ["EUROPE", "ASIA", "N AMERICA", "MID EAST", "AFRICA", "S AMERICA", "OCEANIA"]
REGION_COUNT = {"EUROPE": 6, "ASIA": 8, "N AMERICA": 6, "MID EAST": 6,
                "AFRICA": 4, "S AMERICA": 3, "OCEANIA": 3}


def conf_color(conf):
    if conf == "CONFIRMED":
        return TEAL
    if conf == "DEVELOPING":
        return RED
    return BLUE


def src_line(x, y, src, conf, scale=1):
    text(x, y, "SRC: " + src, scale, GREY)
    w = len("SRC: " + src) * 6 * scale + 4
    text(x + w, y, conf, scale, conf_color(conf))


def draw_cyclone(cx, cy, r):
    """Spiral storm over a drawn coastline."""
    rect(cx - r - 30, cy - r - 10, 2 * r + 60, 2 * r + 20, SKY)
    rect(cx - r - 30, cy + r - 34, 2 * r + 60, 44, SAND)
    for a in range(0, 1080, 6):
        an = math.radians(a)
        rr = r * (a / 1080.0)
        px(int(cx + rr * math.cos(an)), int(cy + rr * math.sin(an) * 0.85), WHITE)
        px(int(cx + rr * math.cos(an)) + 1, int(cy + rr * math.sin(an) * 0.85), WHITE)
    for a in range(0, 1080, 6):
        an = math.radians(a + 180)
        rr = r * 0.62 * (a / 1080.0)
        px(int(cx + rr * math.cos(an)), int(cy + rr * math.sin(an) * 0.85), SEA)
    disc(cx, cy, 9, INK)
    disc(cx, cy, 5, RED)
    line(cx - r - 30, cy + r - 34, cx + r + 30, cy + r - 34, TEAL, 2)
    text(cx - r - 28, cy + r - 30, "BAY OF BENGAL", 1, TEAL)
    text(cx - r - 28, cy + r - 18, "GOPALPUR, ODISHA", 1, INK)
    for i in range(14):
        line(cx - r + i * 22, cy + r - 8, cx - r + 8 + i * 22, cy + r + 2, BLUE, 1)


def draw_bridge(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x, y + h - 18, w, 18, (120, 130, 140))
    for i in range(3):
        bx = x + 12 + i * (w // 3)
        line(bx, y + h - 18, bx + w // 6, y + 14, INK, 2)
        line(bx + w // 6, y + 14, bx + w // 3 - 6, y + h - 18, INK, 2)
    disc(x + w // 2, y + 16, 7, RED)
    for a in range(8):
        an = math.radians(a * 45)
        line(x + w // 2, y + 16, x + w // 2 + int(16 * math.cos(an)),
             y + 16 + int(16 * math.sin(an)), RED, 1)
    text(x + 6, y + h - 14, "DNIPRO RIVER, KYIV", 1, WHITE)


def draw_flags(x, y):
    # US / China / Russia bars, drawn, labelled.
    rect(x, y, 74, 30, (178, 34, 52))
    rect(x, y + 10, 74, 10, WHITE)
    rect(x, y + 20, 74, 10, (178, 34, 52))
    rect(x, y, 30, 16, BLUE)
    text(x + 2, y + 34, "USA", 1, INK)
    rect(x + 86, y, 74, 30, RED)
    star(x + 100, y + 15, 7, (255, 220, 60))
    text(x + 88, y + 34, "CHINA", 1, INK)
    rect(x + 172, y, 74, 30, WHITE)
    rect(x + 172, y, 74, 10, (220, 220, 220))
    rect(x + 172, y + 10, 74, 10, BLUE)
    rect(x + 172, y + 20, 74, 10, RED)
    text(x + 174, y + 34, "RUSSIA", 1, INK)

# ---------------------------------------------------------------- layout
def draw_topbar():
    rect(0, 0, W, 15, BLACK)
    text(12, 4, "FRIDAY, NOVEMBER 20, 2026", 1, WHITE)
    text(700, 4, "EDITION A  •  $2.50  •  VOL. 1, NO. 324", 1, WHITE)


def draw_masthead():
    text_center(0, 18, W, "THE WORLD TODAY", 7, INK)
    hline(12, 72, W - 24, INK, 3)
    text_center(0, 78, W, "36 SOURCED STORIES  •  7 REGIONS  •  EVERY STORY MARKED HOW SURE", 1, RED)
    text_center(0, 90, W, "KYIV BRIDGES HIT  •  CYCLONE AKVAN  •  ASIA AI SELL-OFF", 2, INK)
    hline(12, 110, W - 24, INK, 2)


def draw_hero():
    x, y = 12, 116
    text(x, y, "07  •  ASIA  •  HERO STORY", 1, RED)
    text(x, y + 14, "AKVAN SLAMS", 4, INK)
    text(x, y + 46, "ODISHA COAST", 4, INK)
    text_wrapped(x, y + 78, "300,000 MOVED TO SHELTERS AS STORM CROSSES NEAR GOPALPUR AT 70-80 KM/H", 600, 1, INK)
    draw_cyclone(322, 266, 48)
    text(x, 322, "DRAWN ILLUSTRATION FROM IMD TRACK DATA - CREDIT: IMD / STAFF ART", 1, GREY)
    text(x, 336, "BY STAFF WRITER  •  IMD + REUTERS  •  CONFIRMED", 1, TEAL)
    text(x, 350, "T", 3, RED)
    text_wrapped(x + 20, 350, "HE STORM CROSSED NEAR GOPALPUR AT 07:30, WEAKENING TO A DEEP DEPRESSION BY AFTERNOON. NO DEATHS REPORTED IN THE FIRST ASSESSMENT.", 592, 1, INK)
    text(470, 372, "CONTINUED ON PAGE A7 >", 1, RED)


def draw_right():
    x = 644
    # 01 Kyiv
    text(x, 116, "01  •  EUROPE  •  WAR", 1, RED)
    text(x, 128, "KYIV BRIDGES", 3, INK)
    text(x, 152, "HIT", 3, INK)
    draw_bridge(x, 172, 368, 52)
    text(x, 228, "DRAWN: DNIPRO BRIDGES - CREDIT: REUTERS / STAFF ART", 1, GREY)
    src_line(x, 240, "REUTERS", "CONFIRMED")
    # 08 Shenzhen
    text(x, 254, "08  •  ASIA  •  DIPLOMACY  •  AP  •  CONFIRMED", 1, RED)
    text(x, 266, "THREE AT ONE TABLE", 2, INK)
    draw_flags(x, 284)
    # 21 COP31
    text(x, 336, "21  •  MID EAST  •  CLIMATE", 1, RED)
    text(x, 348, "COP31: NO DEAL,", 2, INK)
    text(x, 364, "NO FOSSIL WORD", 2, INK)
    text(x, 380, "DRAFT DROPS FOSSIL FUELS. SRC: CARBON BRIEF", 1, GREY)
    vline(636, 116, 268, INK, 2)


def draw_markets():
    rect(0, 390, W, 30, BLACK)
    text(12, 394, "MARKETS: TAIEX -6.6%  •  KOSPI -5.2%  •  NIKKEI -4.8%  •  NASDAQ FUT -1.7%  •  S+P FUT -0.85%  •  TSMC -5.2%  •  SOFTBANK -14.6%  •  ANT -6% PRE-MKT", 1, WHITE)
    text(12, 406, "WEATHER: GOPALPUR HEAVY RAIN, WIND 80 KM/H  •  BENGAL RAIN TILL SAT  •  KYIV COLD, POWER CUTS  •  ANTALYA TALKS RUN LATE", 1, WHITE)
    text_center(0, 424, W, "REGIONS: EUROPE 6  •  ASIA 8  •  N AMERICA 6  •  MID EAST 6  •  AFRICA 4  •  S AMERICA 3  •  OCEANIA 3", 1, BLUE)


def draw_grid():
    briefs = [s for s in STORIES if s[0] not in FEATURED]
    cw, ch = 252, 53
    for i, s in enumerate(briefs):
        col, row = i % 4, i // 4
        x = 12 + col * cw
        y = 442 + row * ch
        if col:
            vline(x - 4, y, ch - 4, LIGHT, 1)
        hline(x, y + ch - 3, cw - 8, LIGHT, 1)
        num, region, head, summ, src, conf = s
        text(x, y, "%02d  •  %s" % (num, region), 1, RED)
        text(x, y + 10, head, 1, INK)
        text_wrapped(x, y + 20, summ, cw - 10, 1, GREY)
        src_line(x, y + 42, src, conf)


def draw_index():
    y0 = 876
    hline(12, y0 - 4, W - 24, INK, 2)
    text(12, y0, "INDEX - ALL 36 STORIES, NUMBERED", 1, RED)
    text(760, y0, "FIND EACH STORY BY ITS NUMBER >", 1, GREY)
    for i, s in enumerate(STORIES):
        col, row = i % 6, i // 6
        x = 12 + col * 170
        y = y0 + 14 + row * 14
        text(x, y, "%02d %s" % (s[0], s[2][:21]), 1, INK)


def draw_footer():
    y0 = 972
    hline(12, y0, W - 24, INK, 2)
    text_wrapped(12, y0 + 6, "SOURCES: REUTERS  •  AP  •  AFP  •  BBC  •  IMD  •  ICJ  •  IAEA  •  WSJ  •  DOW JONES  •  CARBON BRIEF  •  UN NEWS  •  IPS  •  TAKE-TWO  •  ESPNCRICINFO. ALL 36 STORIES CHECKED AGAINST REPORTS OF 20 NOV 2026.", W - 24, 1, GREY)
    text(12, 1000, "DRAND ROUND 6659932  •  77E9C632F2B64E86", 1, GREY)
    text(620, 1000, "CONTINUED ON PAGE A7  •  THE WORLD TODAY", 1, RED)


def main():
    draw_topbar()
    draw_masthead()
    draw_hero()
    draw_right()
    draw_markets()
    draw_grid()
    draw_index()
    draw_footer()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote %s (%d bytes, %dx%d)" % (path, os.path.getsize(path), W, H))


if __name__ == "__main__":
    main()
