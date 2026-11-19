#!/usr/bin/env python3
"""Draw the news-image-20261118 front page: Wednesday 18 November 2026.
Deterministic PIL render, 1024x1024 PNG. Run: python3 draw.py
Writes entry.png next to this script. No network, no timestamps.
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DEJAVU = "/usr/share/fonts/truetype/dejavu"

W, H = 1024, 1024
M = 24                      # side margin
CW = 976                    # content width

PAPER = (247, 243, 234)
INK = (26, 26, 26)
RED = (180, 35, 24)
NAVY = (31, 42, 68)
PURPLE = (107, 66, 140)
TEAL = (14, 110, 110)
GREEN = (30, 107, 58)
GREY = (110, 108, 100)
HAIR = (178, 176, 168)     # hairline grey (no alpha on RGB)
SEA = (205, 225, 235)
LAND = (232, 214, 178)
LAND_LINE = (200, 180, 140)
SAND = (235, 220, 180)
SKY = (205, 222, 236)
DARK = (15, 25, 55)

REGION = {
    "Europe": (31, 82, 180),
    "Middle East": (214, 106, 20),
    "Asia": (128, 68, 170),
    "Africa": (30, 140, 90),
    "Americas": (200, 40, 40),
    "Oceania": (0, 150, 160),
    "Global": (110, 110, 110),
}
CHIP_FILL = {"red": RED, "navy": NAVY, "green": GREEN}


def F(name, size):
    return ImageFont.truetype(os.path.join(DEJAVU, name), size)


def playfair(size, weight=800):
    f = ImageFont.truetype(os.path.join(HERE, "fonts", "PlayfairDisplay.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


F_KICK = F("DejaVuSans-Bold.ttf", 13)
F_STAT = F("DejaVuSans-Bold.ttf", 20)
F_STAT_LBL = F("DejaVuSans.ttf", 9)
F_CHIP = F("DejaVuSans-Bold.ttf", 11)
F_LEAD_K = F("DejaVuSans-Bold.ttf", 11)
F_LEAD_D = F("DejaVuSans.ttf", 12)
F_CARD_K = F("DejaVuSans-Bold.ttf", 11)
F_CARD_D = F("DejaVuSans.ttf", 12)
F_BAR = F("DejaVuSans-Bold.ttf", 10)
F_BRIEF = F("DejaVuSans.ttf", 15)
F_BRIEF_B = F("DejaVuSans-Bold.ttf", 15)
F_PIN = F("DejaVuSans-Bold.ttf", 10)
F_LEG = F("DejaVuSans.ttf", 10)
F_FOOT = F("DejaVuSans.ttf", 11)
F_SEC = F("DejaVuSans-Bold.ttf", 12)
F_LBL = F("DejaVuSans-Bold.ttf", 10)
F_DATE_T = F("DejaVuSans-Bold.ttf", 12)
F_DATE_B = F("DejaVuSans.ttf", 11)

# Masthead: largest Playfair ExtraBold size that fits the 976px content width.
F_MAST = None
MAST_SIZE = None
for _s in (78, 76, 74, 72, 70):
    _f = playfair(_s, 800)
    if _f.getlength("Wednesday 18 November 2026") <= CW:
        F_MAST, MAST_SIZE = _f, _s
        break
assert F_MAST is not None and MAST_SIZE >= 70, "masthead does not fit at 70px"
F_LEAD_H = playfair(21, 800)
F_CARD_H = playfair(16, 800)


def text_w(d, s, font):
    return d.textlength(s, font=font)


def wrap(d, text, font, max_w, max_lines, what):
    """Greedy word wrap; asserts the text fits in max_lines."""
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(d, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    assert len(lines) <= max_lines, f"{what} needs {len(lines)} lines: {text!r}"
    return lines


def _assert_no_overlap(boxes, what):
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            assert ox <= 0 or oy <= 0, f"overlap in {what}: {a} vs {b}"


def chip(d, x, y, text, font, fill):
    """Meaning-coded chip: white bold text on a solid fill. Returns its box."""
    w = int(text_w(d, text, font)) + 12
    h = 15
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    d.text((x + 6, y + 2), text, font=font, fill=(255, 255, 255))
    return (x, y, x + w, y + h)


def banner(d, x, y, w, text, font, fill, h=18):
    """Solid bottom banner with centred white bold text."""
    assert text_w(d, text, font) <= w - 8, f"banner too wide: {text!r}"
    d.rectangle([x, y, x + w, y + h], fill=fill)
    tw = text_w(d, text, font)
    d.text((x + (w - tw) / 2, y + 3), text, font=font, fill=(255, 255, 255))
    return (x, y, x + w, y + h)


def kicker(d, x, y, num, text, font, region):
    """Number + region-coloured 7px dot + INK bold kicker text."""
    d.ellipse([x, y + 2, x + 7, y + 9], fill=REGION[region])
    d.text((x + 11, y), f"{num} {text}", font=font, fill=INK)


def section_label(d, x, y, text, font=F_SEC):
    t = " ".join(list(text.replace(" ", "  "))) if False else text
    d.text((x, y), t, font=font, fill=INK)
    return text_w(d, t, font)


def jet(d, x, y, s, fill):
    """Horizontal aircraft: fuselage dart (nose right) + swept wings + fin."""
    d.polygon([(x, y + s * 0.45), (x + s * 0.75, y + s * 0.35),
               (x + s, y + s * 0.5), (x + s * 0.75, y + s * 0.65),
               (x + s * 0.55, y + s * 0.6), (x + s * 0.4, y + s),
               (x + s * 0.3, y + s * 0.6), (x + s * 0.1, y + s * 0.55)],
              fill=fill)


def dashed(d, p0, p1, fill, width=2, dash=7, gap=5):
    """Dashed line from p0 to p1."""
    x0, y0 = p0
    x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(length / (dash + gap)))
    for i in range(n):
        t0 = i / n
        t1 = min(1.0, (i * (dash + gap) + dash) / length)
        d.line([x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0,
                x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1], fill=fill, width=width)


def arrowhead(d, tip, angle_deg, size, fill):
    """Small filled arrowhead at tip, pointing along angle_deg (0 = east)."""
    a = math.radians(angle_deg)
    bx, by = tip[0] - size * math.cos(a), tip[1] - size * math.sin(a)
    px, py = -math.sin(a), math.cos(a)
    d.polygon([tip, (bx + size * 0.45 * px, by + size * 0.45 * py),
               (bx - size * 0.45 * px, by - size * 0.45 * py)], fill=fill)


# ---------------------------------------------------------------- data ----
STATS = [
    ("141", "DRONES FIRED"),
    ("€45BN", "EU FOR UKRAINE"),
    ("25.9BN KM", "VOYAGER 1"),
    ("251–11", "JEFFRIES VOTE"),
    ("$83", "ANTHROPIC IPO"),
]

LEADS = [
    {"n": 1, "kicker": "MIDDLE EAST · IRAN WAR", "region": "Middle East",
     "headline": "Iran widens Gulf war to Kuwait and Bahrain",
     "deck": "First attack on Kuwait since September; Bahrain intercepts a third time; ADNOC vessel hit.",
     "art": "gulf"},
    {"n": 2, "kicker": "ASIA · APEC SUMMIT", "region": "Asia",
     "headline": "Xi greets Trump on the tarmac in Shenzhen",
     "deck": "Fifth Xi–Putin meeting this year; first-ever Trump–Xi–Putin trilateral set for Thursday.",
     "art": "shenzhen"},
    {"n": 3, "kicker": "SPACE · SCIENCE", "region": "Oceania",
     "headline": "Voyager 1 reaches one light-day from Earth",
     "deck": "25.9 billion km at 10:16 UTC — first human-made object ever that far.",
     "art": "voyager"},
]

CARDS = [
    {"n": 4, "kicker": "EUROPE · UKRAINE AID", "region": "Europe",
     "headline": "EU pledges €45bn for Ukraine in 2027",
     "deck": "Two-thirds of Kyiv's €70bn gap; paid after reparations.",
     "scene": "eu", "chip": "€45BN", "fill": "green", "bar": "BRUSSELS · EU AID"},
    {"n": 5, "kicker": "ASIA · CYCLONE", "region": "Asia",
     "headline": "Cyclone Akvan bears down on India",
     "deck": "145 km/h gusts; 200,000 evacuated; landfall Fri.",
     "scene": "akvan", "chip": "145 KM/H", "fill": "red", "bar": "BAY OF BENGAL · AKVAN"},
    {"n": 6, "kicker": "GLOBAL · CLIMATE", "region": "Global",
     "headline": "COP31 draft deal draws fire",
     "deck": "EU envoy: 'untenable'; 75 nations back 35x35.",
     "scene": "cop31", "chip": "18-PAGE DRAFT", "fill": "navy", "bar": "COP31 ANTALYA · ENDS FRI"},
    {"n": 7, "kicker": "EUROPE · ECONOMY", "region": "Europe",
     "headline": "UK inflation hits 3.6%",
     "deck": "Highest in a year; cap up 26%, +£443 a year.",
     "scene": "uk", "chip": "3.6%", "fill": "green", "bar": "LONDON · PRICES"},
    {"n": 8, "kicker": "AMERICAS · POLITICS", "region": "Americas",
     "headline": "Jeffries nominated as first Black Speaker",
     "deck": "Democrats pick Jeffries 251–11; vote in January.",
     "scene": "jeffries", "chip": "251–11", "fill": "navy", "bar": "WASHINGTON · HOUSE"},
    {"n": 9, "kicker": "MIDDLE EAST · CEASEFIRE", "region": "Middle East",
     "headline": "Board of Peace faults both sides",
     "deck": "12-page UN report: truce 'cannot be sustained'.",
     "scene": "peace", "chip": "TRUCE AT RISK", "fill": "red", "bar": "GAZA · BOARD OF PEACE"},
    {"n": 10, "kicker": "CULTURE · GAMES", "region": "Global",
     "headline": "GTA 6 launches after 13 years",
     "deck": "Midnight launch in NZ; 17.1m sold by noon ET.",
     "scene": "gta", "chip": "17.1M SOLD", "fill": "green", "bar": "WORLDWIDE · GTA 6"},
    {"n": 11, "kicker": "AFRICA · HEALTH", "region": "Africa",
     "headline": "Ebola passes 11,500 cases",
     "deck": "CDC: 11,536 cases, 5,635 deaths; 2nd-largest.",
     "scene": "ebola", "chip": "11,536 CASES", "fill": "red", "bar": "DR CONGO · EBOLA"},
    {"n": 12, "kicker": "AMERICAS · TECH", "region": "Americas",
     "headline": "Nvidia shares fall as Congress closes in",
     "deck": "Down 2.5%; Senate seeks Huang testimony 3 Dec.",
     "scene": "nvidia", "chip": "−2.5%", "fill": "red", "bar": "SANTA CLARA · NVIDIA"},
    {"n": 13, "kicker": "ASIA · LABOUR", "region": "Asia",
     "headline": "Garment unrest shuts 132 factories",
     "deck": "Day 3 of clashes; ~300 arrested; demand Tk 30,000.",
     "scene": "dhaka", "chip": "TK 30,000", "fill": "green", "bar": "DHAKA · SAVAR · GAZIPUR"},
]

# briefs: (number, region, full text) — prefix before ":" is bold.
BRIEFS = [
    (14, "Americas", "Peltola: wins Alaska, 56–44"),
    (15, "Americas", "Anthropic: IPO priced at $83"),
    (16, "Asia", "Manila: no trade deal signed"),
    (17, "Africa", "Sudan: UN counts 2,230 dead"),
    (18, "Europe", "Ukraine: 141 drones, 126 down"),
    (19, "Africa", "Ethiopia–Eritrea: troops mass"),
    (20, "Oceania", "Australia sanctions Weiss"),
    (21, "Europe", "Gold: falls below $3,800"),
    (22, "Americas", "Fed: December hike certain"),
    (23, "Africa", "Mozambique: trial, day two"),
    (24, "Europe", "Serbia: Čupić elected speaker"),
    (25, "Oceania", "Xavier: Cat 5 near Pukapuka"),
    (26, "Asia", "Vietnam: Russian bombers land"),
    (27, "Americas", "California: second storm hits"),
    (28, "Americas", "Huawei: jury deliberates"),
    (29, "Americas", "Carney–Trump: 20 min, no deal"),
    (30, "Asia", "Myanmar: ICJ rules Thursday"),
    (31, "Americas", "Waymo: robotaxis off freeways"),
    (32, "Americas", "Measles: US status lost"),
    (33, "Americas", "OpenAI: GPT-6.2 Astra, Sol"),
    (34, "Middle East", "Yemen: coalition hits 60 sites"),
    (35, "Europe", "An-12: crash kills 19"),
    (36, "Middle East", "Knesset: Kahana wins 66–52"),
    (37, "Americas", "China–Canada: tariffs cut"),
    (38, "Americas", "US: no cyberattack in outages"),
    (39, "Asia", "Putin: sanctions 'past'"),
    (40, "Asia", "Trump: first US visit to Shenzhen"),
    (41, "Americas", "Alaska: Democrat governor wins"),
    (42, "Africa", "Kenya: last Ebola patient out"),
    (43, "Middle East", "Yemen: Houthis named terrorists"),
]

# map pins: (number, lon, lat, region, offset dx,dy) — offsets spread clusters.
PINS = [
    (1, 56, 26, "Middle East", (10, -6)),     # Gulf / Qeshm
    (2, 114, 22, "Asia", (0, 0)),             # Shenzhen
    (3, -80, 28, "Americas", (-12, 8)),       # Cape Canaveral
    (4, 30, 50, "Europe", (0, -10)),          # Kyiv
    (5, 80, 16, "Asia", (-10, 8)),            # Andhra coast
    (6, 30, 37, "Europe", (0, -6)),           # Antalya
    (7, -0.1, 51.5, "Europe", (0, 0)),        # London
    (8, -77, 39, "Americas", (0, 0)),         # Washington DC
    (9, 34.5, 31.5, "Middle East", (-10, 12)),  # Gaza
    (10, 174, -37, "Oceania", (-8, 0)),       # Auckland
    (11, 23, -2, "Africa", (0, 0)),           # DR Congo
    (12, -122, 37, "Americas", (0, 0)),       # Santa Clara
    (13, 90, 24, "Asia", (-4, -8)),           # Dhaka
]

# map dots for briefs 14-43: (number, lon, lat, region)
DOTS = [
    (14, -150, 64, "Americas"), (15, -122, 37, "Americas"),
    (16, 121, 14.6, "Asia"), (17, 30, 13, "Africa"),
    (18, 32, 49, "Europe"), (19, 39, 13, "Africa"),
    (20, 149, -35, "Oceania"), (21, -0.1, 51.5, "Europe"),
    (22, -77, 39, "Americas"), (23, 32, -18, "Africa"),
    (24, 21, 44, "Europe"), (25, -166, -10, "Oceania"),
    (26, 108, 16, "Asia"), (27, -121, 37, "Americas"),
    (28, -74, 40.6, "Americas"), (29, 114, 22, "Asia"),
    (30, 4.3, 52, "Europe"), (31, -122, 37, "Americas"),
    (32, -77, 39, "Americas"), (33, -122, 37, "Americas"),
    (34, 44, 15, "Middle East"), (35, 87, 60, "Europe"),
    (36, 35.2, 31.8, "Middle East"), (37, -75.7, 45.4, "Americas"),
    (38, -77, 39, "Americas"), (39, 114, 22, "Asia"),
    (40, 114, 22, "Asia"), (41, -150, 64, "Americas"),
    (42, 36.8, -1.3, "Africa"), (43, 44, 15, "Middle East"),
]

DATE_CHECK_TITLE = "DATE CHECK — LEFT OUT ON PURPOSE"
DATE_CHECK_BODY = ("First reported Tuesday 17 November, NOT today: Kerch Bridge span "
                   "collapse · Nvidia's $115.8bn quarter · Mongolia's president "
                   "resigning · Prague train crash · Japan airspace breach.")

FOOTER_1 = ("Every story here happened or was first reported on Wednesday 18 November 2026. "
            "Contested claims are marked as claims.")
FOOTER_2 = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. Original drawings."

# Continent polygons (lon, lat) — embedded reference data for the world map.
POLYS = [
    [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50), (1, 51), (4, 53), (8, 54), (8, 57), (10, 58), (7, 60), (5, 62), (10, 64), (14, 67), (19, 69), (24, 71), (30, 70), (35, 68), (42, 68), (48, 68), (54, 68), (60, 69), (66, 69), (72, 72), (78, 72), (85, 73), (95, 75), (105, 77), (112, 74), (120, 73), (128, 71), (138, 72), (148, 72), (158, 70), (162, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 59), (158, 52), (156, 51), (150, 59), (142, 59), (141, 52), (140, 47), (138, 43), (135, 43), (132, 43), (130, 42), (127, 40), (126, 38), (124, 40), (121, 37), (120, 32), (122, 30), (120, 25), (117, 23), (112, 22), (108, 18), (106, 11), (105, 9), (103, 7), (100, 6), (98, 10), (97, 15), (94, 16), (92, 21), (90, 22), (88, 22), (86, 20), (83, 18), (80, 15), (80, 10), (77, 8), (75, 10), (73, 16), (70, 20), (68, 23), (66, 25), (62, 25), (58, 25), (56, 26), (52, 26), (50, 29), (48, 30), (45, 29), (43, 28), (41, 27), (39, 21), (38, 18), (35, 28), (34, 28), (33, 29), (32, 31), (30, 31), (27, 37), (26, 38), (23, 36), (22, 37), (20, 39), (19, 42), (16, 40), (14, 38), (12, 38), (10, 37), (8, 37), (8, 39), (4, 39), (2, 41), (0, 38), (-2, 37), (-6, 36)],
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9), (-80, 8), (-77, 7), (-79, 9), (-81, 13), (-84, 16), (-87, 13), (-88, 18), (-90, 21), (-91, 19), (-96, 19), (-97, 22), (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 47), (-60, 52), (-65, 50), (-60, 55), (-65, 60), (-68, 58), (-75, 62), (-78, 62), (-85, 66), (-90, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68)],
    [(-80, 9), (-77, 4), (-75, 0), (-80, -3), (-81, -6), (-77, -12), (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54), (-66, -55), (-65, -45), (-62, -41), (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-52, 5), (-55, 6), (-60, 8), (-62, 9), (-68, 11), (-72, 12), (-75, 11), (-77, 8)],
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36), (10, 37), (11, 34), (20, 32), (25, 32), (30, 31), (33, 27), (35, 23), (37, 18), (39, 15), (43, 12), (48, 11), (51, 12), (46, 5), (42, 0), (40, -5), (40, -10), (37, -15), (35, -20), (32, -26), (28, -33), (20, -35), (17, -32), (15, -27), (13, -18), (12, -10), (13, -5), (9, 4), (6, 4), (-2, 5), (-8, 5), (-13, 8), (-17, 12)],
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)],
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 76), (-35, 77), (-50, 76), (-58, 74), (-55, 70), (-52, 64), (-48, 60)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37), (141, 39), (141, 41), (142, 43), (144, 44), (141, 45), (139, 41), (137, 38), (135, 34), (133, 34), (130, 33)],
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -24), (44, -25), (43, -21), (44, -17)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -36), (172, -35), (167, -45)],
]


# ------------------------------------------------------- lead art ----
def flag_cn(d, fx, fy, fw, fh):
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 16))
    cx, cy = fx + 10, fy + 8
    for dx, dy in [(0, 0), (8, 3), (10, 10), (4, 14), (-3, 9)]:
        d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                  fill=(255, 222, 0))


def flag_us(d, fx, fy, fw, fh):
    for i in range(7):
        d.rectangle([fx, fy + i * fh // 7, fx + fw, fy + (i + 1) * fh // 7],
                    fill=(200, 40, 40) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([fx, fy, fx + fw * 0.42, fy + fh * 0.55], fill=(31, 42, 90))
    for r in range(3):
        for c in range(4):
            d.ellipse([fx + 3 + c * 7, fy + 3 + r * 6, fx + 6 + c * 7, fy + 6 + r * 6],
                      fill=(255, 255, 255))


def flag_ru(d, fx, fy, fw, fh):
    for i, col in enumerate([(255, 255, 255), (0, 60, 170), (220, 30, 30)]):
        d.rectangle([fx, fy + i * fh // 3, fx + fw, fy + (i + 1) * fh // 3], fill=col)


def art_gulf(d, x, y, w, h):
    """Gulf war widens: Iran (sand, top) over sea; drone routes, ships, jet."""
    scene_h = h - 18
    d.rectangle([x, y, x + w, y + scene_h], fill=SKY)
    d.rectangle([x, y, x + w, y + 22], fill=SAND)
    d.text((x + 8, y + 4), "IRAN", font=F_LBL, fill=INK)
    d.text((x + 252, y + 4), "HORMUZ", font=F_LBL, fill=INK)
    # dashed drone routes with arrowheads (red: to Kuwait/Bahrain, navy: to Qeshm)
    dashed(d, (x + 80, y + 22), (x + 52, y + 30), RED)
    arrowhead(d, (x + 48, y + 31), 165, 7, RED)
    dashed(d, (x + 120, y + 22), (x + 96, y + 50), RED)
    arrowhead(d, (x + 93, y + 53), 115, 7, RED)
    dashed(d, (x + 210, y + 22), (x + 185, y + 48), NAVY)
    arrowhead(d, (x + 182, y + 50), 125, 7, NAVY)
    # ships (hull + red triangle sail), all relative to x,y
    for sx, sy in ((x + 205, y + 30), (x + 252, y + 58)):
        d.rectangle([sx, sy, sx + 34, sy + 7], fill=INK)
        d.polygon([(sx + 8, sy), (sx + 14, sy - 9), (sx + 20, sy)], fill=RED)
    jet(d, x + 220, y + 8, 24, INK)
    # chips
    b1 = chip(d, x + 8, y + 28, "KUWAIT HIT", F_CHIP, RED)
    b2 = chip(d, x + 8, y + 48, "BAHRAIN INTERCEPTS", F_CHIP, NAVY)
    # Qeshm label + TUE STRIKE tag (the US strike was Tuesday: background only)
    d.text((x + 170, y + 48), "QESHM", font=F_LBL, fill=INK)
    tag = "TUE STRIKE"
    tw = text_w(d, tag, F("DejaVuSans-Bold.ttf", 9))
    d.rectangle([x + 170, y + 62, x + 170 + tw + 8, y + 74], outline=NAVY, width=1)
    d.text((x + 174, y + 64), tag, font=F("DejaVuSans-Bold.ttf", 9), fill=NAVY)
    _assert_no_overlap([b1, b2, (x + 170, y + 48, x + 215, y + 60),
                        (x + 170, y + 62, x + 170 + tw + 8, y + 74),
                        (x + 205, y + 21, x + 239, y + 37),
                        (x + 252, y + 49, x + 286, y + 65)], "gulf art")
    banner(d, x, y + scene_h, w, "GULF WAR WIDENS · KUWAIT HIT", F_CHIP, NAVY)


def art_shenzhen(d, x, y, w, h):
    """APEC eve: plane on a runway + 3 flags (CN/US/RU) with country names."""
    scene_h = h - 18
    d.rectangle([x, y, x + w, y + scene_h], fill=(216, 226, 236))
    d.text((x + 8, y + 6), "SHENZHEN", font=F_LBL, fill=INK)
    # runway with centre dashes
    d.rectangle([x, y + 66, x + w, y + scene_h], fill=(90, 90, 96))
    for i in range(7):
        d.rectangle([x + 12 + i * 44, y + 73, x + 34 + i * 44, y + 75],
                    fill=(255, 255, 255))
    # plane, horizontal, nose right, on the sky above the runway
    d.polygon([(x + 28, y + 34), (x + 78, y + 28), (x + 108, y + 34),
               (x + 78, y + 40)], fill=INK)
    d.polygon([(x + 58, y + 30), (x + 74, y + 18), (x + 80, y + 30)], fill=INK)
    d.polygon([(x + 38, y + 30), (x + 44, y + 22), (x + 48, y + 30)], fill=INK)
    d.rectangle([x + 66, y + 40, x + 70, y + 46], fill=INK)
    d.rectangle([x + 92, y + 40, x + 96, y + 46], fill=INK)
    # three flags on poles that run down to the runway; names over the poles
    flags = [("CN", flag_cn), ("US", flag_us), ("RU", flag_ru)]
    fw, fh = 40, 28
    name_boxes = []
    for i, (nm, fn) in enumerate(flags):
        fx = x + 165 + i * 55
        fy = y + 8
        fn(d, fx, fy, fw, fh)
        d.rectangle([fx, fy, fx + fw, fy + fh], outline=(120, 120, 120), width=1)
        d.line([fx + fw // 2, fy + fh, fx + fw // 2, y + 66],
               fill=(120, 120, 120), width=2)
        tw = text_w(d, nm, F_LBL)
        nx0 = fx + (fw - tw) / 2
        ny0 = fy + fh + 2
        # backing rectangle in the sky colour: the pole never crosses a glyph
        d.rectangle([nx0 - 2, ny0 - 1, nx0 + tw + 2, ny0 + 11],
                    fill=(216, 226, 236))
        d.text((nx0, ny0), nm, font=F_LBL, fill=INK)
        name_boxes.append((nx0, ny0, nx0 + tw, ny0 + 10))
    _assert_no_overlap(name_boxes + [(x + 165 + i * 55, y + 8,
                                      x + 165 + i * 55 + fw, y + 36)
                                     for i in range(3)], "shenzhen flags")
    banner(d, x, y + scene_h, w, "APEC OPENS · TRILATERAL THU", F_CHIP, PURPLE)


def art_voyager(d, x, y, w, h):
    """Voyager 1, one light-day out: Earth (left) - - dashed line - - probe."""
    scene_h = h - 18
    d.rectangle([x, y, x + w, y + scene_h], fill=DARK)
    for sx, sy, r in ((x + 110, y + 12, 1), (x + 150, y + 26, 2), (x + 200, y + 10, 1),
                      (x + 260, y + 22, 2), (x + 290, y + 14, 1), (x + 130, y + 60, 1),
                      (x + 300, y + 60, 1), (x + 90, y + 70, 1)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    d.text((x + 24, y + 6), "EARTH", font=F_LBL, fill=(255, 255, 255))
    # Earth: blue disc + green land + white cloud arcs
    d.ellipse([x + 14, y + 22, x + 66, y + 74], fill=(40, 110, 200))
    d.ellipse([x + 24, y + 32, x + 40, y + 46], fill=(60, 160, 90))
    d.ellipse([x + 42, y + 52, x + 58, y + 64], fill=(60, 160, 90))
    d.arc([x + 18, y + 30, x + 62, y + 58], 200, 320, fill=(255, 255, 255), width=2)
    # dashed path Earth -> probe
    dashed(d, (x + 70, y + 48), (x + 240, y + 44), (255, 255, 255), width=2)
    # Voyager probe: bus + dish + antenna mast
    d.rectangle([x + 244, y + 36, x + 262, y + 52], fill=(200, 200, 210))
    d.polygon([(x + 262, y + 34), (x + 278, y + 30), (x + 278, y + 58),
               (x + 262, y + 54)], fill=(230, 230, 240))
    d.line([x + 253, y + 36, x + 253, y + 24], fill=(200, 200, 210), width=2)
    d.ellipse([x + 251, y + 20, x + 255, y + 24], fill=(255, 220, 0))
    d.text((x + 228, y + 60), "VOYAGER 1", font=F_LBL, fill=(255, 255, 255))
    b = chip(d, x + 150, y + 8, "25.9BN KM", F_CHIP, GREEN)
    _assert_no_overlap([b, (x + 14, y + 22, x + 66, y + 74),
                        (x + 228, y + 60, x + 300, y + 72),
                        (x + 244, y + 20, x + 278, y + 58)], "voyager art")
    banner(d, x, y + scene_h, w, "ONE LIGHT-DAY · 25.9BN KM", F_CHIP, NAVY)


ARTS = {"gulf": art_gulf, "shenzhen": art_shenzhen, "voyager": art_voyager}


# ------------------------------------------------------- card scenes --
def scene_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 230, 242))
    # EU flag: blue + ring of gold stars
    d.rectangle([x + 8, y + 6, x + 48, y + 34], fill=(30, 60, 160))
    for k in range(8):
        a = math.radians(k * 45)
        d.ellipse([x + 28 + 12 * math.cos(a) - 2, y + 20 + 10 * math.sin(a) - 2,
                   x + 28 + 12 * math.cos(a) + 2, y + 20 + 10 * math.sin(a) + 2],
                  fill=(255, 210, 0))
    # Ukraine flag: blue over yellow
    d.rectangle([x + 58, y + 6, x + 98, y + 20], fill=(40, 110, 200))
    d.rectangle([x + 58, y + 20, x + 98, y + 34], fill=(255, 210, 0))
    d.text((x + 108, y + 24), "€45bn", font=F("DejaVuSans-Bold.ttf", 18), fill=NAVY)


def scene_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(205, 222, 236))
    # India coast (tan) on the right
    d.polygon([(x + 130, y + 4), (x + 160, y + 4), (x + 150, y + 28),
               (x + 138, y + 48), (x + 128, y + 30)], fill=(232, 214, 178))
    # cyclone spiral: concentric arcs, white and grey
    cx, cy = x + 62, y + 26
    for r, col in ((20, (255, 255, 255)), (14, (160, 180, 200)),
                   (8, (255, 255, 255))):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    # rain streaks
    for rx in (x + 20, x + 100, x + 150):
        d.line([rx, y + 40, rx - 4, y + 50], fill=(120, 150, 180), width=2)


def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    # draft document with lines + red DRAFT stamp
    d.rectangle([x + 10, y + 6, x + 78, y + 46], fill=(255, 255, 255),
                outline=(150, 150, 150), width=1)
    for i in range(4):
        d.line([x + 16, y + 12 + i * 8, x + 72, y + 12 + i * 8],
               fill=(170, 170, 170), width=1)
    d.rectangle([x + 14, y + 36, x + 52, y + 44], outline=RED, width=2)
    d.text((x + 18, y + 37), "DRAFT", font=F("DejaVuSans-Bold.ttf", 8), fill=RED)
    # thermometer
    d.rectangle([x + 118, y + 8, x + 124, y + 34], fill=(255, 255, 255),
                outline=INK, width=1)
    d.rectangle([x + 119, y + 22, x + 123, y + 34], fill=RED)
    d.ellipse([x + 112, y + 32, x + 130, y + 48], fill=RED)
    d.text((x + 136, y + 28), "35x35", font=F("DejaVuSans-Bold.ttf", 11), fill=INK)


def scene_uk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 240, 232))
    # rising bar chart + £
    bars = [(x + 14, 14, GREEN), (x + 38, 22, NAVY), (x + 62, 30, GREEN),
            (x + 86, 38, RED)]
    for bx, bh, col in bars:
        d.rectangle([bx, y + 46 - bh, bx + 18, y + 46], fill=col)
    d.line([x + 8, y + 46, x + 112, y + 46], fill=INK, width=2)
    d.text((x + 124, y + 12), "£", font=F("DejaVuSans-Bold.ttf", 26), fill=NAVY)
    d.polygon([(x + 14, y + 32), (x + 47, y + 24), (x + 71, y + 16),
               (x + 95, y + 8), (x + 104, y + 8), (x + 95, y + 16)],
              fill=RED)


def scene_jeffries(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 232, 240))
    # Capitol dome (white) + ballot box
    d.rectangle([x + 10, y + 30, x + 80, y + 46], fill=(255, 255, 255),
                outline=(150, 150, 150), width=1)
    d.polygon([(x + 45, y + 8), (x + 62, y + 30), (x + 28, y + 30)], fill=(255, 255, 255))
    d.rectangle([x + 43, y + 4, x + 47, y + 10], fill=(255, 255, 255))
    for cx in (x + 20, x + 34, x + 48, x + 62, x + 74):
        d.rectangle([cx, y + 34, cx + 6, y + 44], fill=(180, 180, 180))
    d.rectangle([x + 118, y + 22, x + 158, y + 46], fill=NAVY)
    d.rectangle([x + 128, y + 18, x + 148, y + 22], fill=(255, 255, 255))
    d.line([x + 132, y + 24, x + 144, y + 24], fill=(255, 255, 255), width=2)


def scene_peace(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 232, 238))
    # UN building slab + windows + UN flag
    d.rectangle([x + 18, y + 6, x + 66, y + 46], fill=(120, 150, 200))
    for r in range(4):
        for c in range(3):
            d.rectangle([x + 24 + c * 14, y + 11 + r * 9,
                         x + 32 + c * 14, y + 17 + r * 9], fill=(230, 240, 250))
    # UN flag on a pole BELOW the chip (the chip covers y+4..19 on the right)
    d.line([x + 118, y + 24, x + 118, y + 46], fill=INK, width=2)
    d.rectangle([x + 118, y + 24, x + 142, y + 36], fill=(40, 110, 200))
    d.ellipse([x + 126, y + 27, x + 134, y + 33], fill=(255, 255, 255))
    # cracked ground line
    d.line([x + 110, y + 44, x + 130, y + 38, x + 150, y + 44, x + 172, y + 40],
           fill=RED, width=2)


def scene_gta(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 22, 34))
    # game controller
    d.rounded_rectangle([x + 12, y + 10, x + 96, y + 38], radius=8, fill=(60, 60, 80))
    d.ellipse([x + 22, y + 18, x + 30, y + 26], fill=(255, 255, 255))
    d.ellipse([x + 72, y + 14, x + 78, y + 20], fill=(255, 210, 0))
    d.ellipse([x + 80, y + 20, x + 86, y + 26], fill=RED)
    d.ellipse([x + 72, y + 26, x + 78, y + 32], fill=(40, 160, 80))
    d.ellipse([x + 64, y + 20, x + 70, y + 26], fill=(60, 120, 220))
    # clock at 00:00 (both hands up) — kept inside the 185px strip
    d.ellipse([x + 119, y + 21, x + 145, y + 47], fill=(255, 255, 255),
              outline=INK, width=1)
    d.line([x + 132, y + 34, x + 132, y + 24], fill=INK, width=2)
    d.line([x + 132, y + 34, x + 132, y + 27], fill=RED, width=2)
    d.text((x + 148, y + 28), "00:00", font=F("DejaVuSans-Bold.ttf", 10),
           fill=(255, 255, 255))


def scene_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 238, 226))
    # hospital building + red cross
    d.rectangle([x + 8, y + 8, x + 58, y + 46], fill=(255, 255, 255),
                outline=(150, 150, 150), width=1)
    d.rectangle([x + 28, y + 12, x + 38, y + 28], fill=RED)
    d.rectangle([x + 22, y + 18, x + 44, y + 22], fill=RED)
    d.rectangle([x + 16, y + 34, x + 26, y + 46], fill=(120, 120, 120))
    # tent
    d.polygon([(x + 65, y + 46), (x + 85, y + 22), (x + 105, y + 46)],
              fill=(170, 120, 60))
    d.rectangle([x + 80, y + 38, x + 90, y + 46], fill=(90, 60, 30))
    # DRC flag (blue, red diagonal band, yellow star)
    d.rectangle([x + 135, y + 22, x + 171, y + 46], fill=(40, 110, 200))
    d.polygon([(x + 135, y + 46), (x + 147, y + 46), (x + 171, y + 22),
               (x + 159, y + 22)], fill=RED)
    d.ellipse([x + 141, y + 26, x + 149, y + 34], fill=(255, 210, 0))


def scene_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 232))
    # falling chart: axes + descending red line + arrow
    d.line([x + 12, y + 8, x + 12, y + 44], fill=INK, width=2)
    d.line([x + 12, y + 44, x + 172, y + 44], fill=INK, width=2)
    pts = [(x + 16, y + 10), (x + 50, y + 14), (x + 84, y + 20),
           (x + 118, y + 26), (x + 152, y + 34), (x + 166, y + 40)]
    d.line(pts, fill=RED, width=3)
    arrowhead(d, (x + 168, y + 41), -35, 8, RED)
    d.line([x + 16, y + 10, x + 50, y + 14], fill=(120, 120, 120), width=1)


def scene_dhaka(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    # factory with chimneys + smoke (all coords relative to x,y)
    d.rectangle([x + 8, y + 16, x + 88, y + 46], fill=(150, 150, 155))
    d.rectangle([x + 16, y + 6, x + 24, y + 16], fill=(120, 120, 125))
    d.rectangle([x + 30, y + 2, x + 38, y + 16], fill=(120, 120, 125))
    d.ellipse([x + 14, y - 2, x + 26, y + 6], fill=(200, 200, 200))
    d.ellipse([x + 28, y - 6, x + 42, y + 2], fill=(210, 210, 210))
    for wx in (x + 18, x + 34, x + 50, x + 66):
        d.rectangle([wx, y + 24, wx + 10, y + 32], fill=(90, 90, 95))
    # two workers (head + navy body), relative to x
    for wx in (x + 112, x + 138):
        d.ellipse([wx, y + 18, wx + 12, y + 30], fill=(220, 180, 140))
        d.rectangle([wx - 2, y + 30, wx + 14, y + 46], fill=NAVY)


SCENES = {"eu": scene_eu, "akvan": scene_akvan, "cop31": scene_cop31,
          "uk": scene_uk, "jeffries": scene_jeffries, "peace": scene_peace,
          "gta": scene_gta, "ebola": scene_ebola, "nvidia": scene_nvidia,
          "dhaka": scene_dhaka}


# ------------------------------------------------------------ layout --
LEAD_W = (CW - 2 * 12) // 3            # 317 (12px gutters)
CARD_W = (CW - 4 * 12) // 5            # 185 (12px gutters)
CARD_H = 146
ART_H = 100
STRIP_H = 52
BAR_H = 15
MAP_X, MAP_W = M, 380
MAP_Y, MAP_H = 681, 180
BRIEF_X0 = 420
BRIEF_COL_W = 286
BRIEF_PITCH = 20


def proj(lon, lat):
    return (MAP_X + (lon + 180) * MAP_W / 360.0,
            MAP_Y + (85 - lat) * MAP_H / 145.0)


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    max_y = 0

    def note(y):
        nonlocal max_y
        max_y = max(max_y, y)

    # ---- kicker + masthead (Playfair ExtraBold, largest size that fits) ----
    d.text((M, 4), "THE WORLD'S NEWS IN ONE PICTURE", font=F_KICK, fill=RED)
    cnt = "43 STORIES · 6 CONTINENTS · ALL FROM WEDNESDAY"
    d.text((W - M - text_w(d, cnt, F_KICK), 4), cnt, font=F_KICK, fill=INK)
    mw = text_w(d, "Wednesday 18 November 2026", F_MAST)
    assert mw <= CW, f"masthead too wide: {mw}"
    d.text(((W - mw) / 2, 10), "Wednesday 18 November 2026", font=F_MAST, fill=INK)
    note(10 + MAST_SIZE)
    d.line([M, 114, W - M, 114], fill=INK, width=2)
    d.line([M, 118, W - M, 118], fill=INK, width=1)

    # ---- stat strip (5 numbers, hairline verticals between cells) ----
    sy = 123
    cell_w = (772 - M) / 5
    for i, (num, lbl) in enumerate(STATS):
        cx = M + i * cell_w
        d.text((cx + (cell_w - text_w(d, num, F_STAT)) / 2, sy + 3),
               num, font=F_STAT, fill=RED)
        d.text((cx + (cell_w - text_w(d, lbl, F_STAT_LBL)) / 2, sy + 26),
               lbl, font=F_STAT_LBL, fill=GREY)
        if i:
            d.line([cx, sy + 4, cx, sy + 34], fill=HAIR, width=1)
    note(sy + 38)

    # ---- section header: TOP STORIES (small caps + hairline rule) ----
    hy_sec = sy + 40
    lw = section_label(d, M, hy_sec, "TOP STORIES")
    d.line([M + lw + 8, hy_sec + 6, W - M, hy_sec + 6], fill=HAIR, width=1)

    # ---- leads (gap label -> art top is 13px; the v4 bug clipped it at 9px) ----
    ly = hy_sec + 13
    lead_end = ly
    for i, ld in enumerate(LEADS):
        x = M + i * (LEAD_W + 12)
        ARTS[ld["art"]](d, x, ly, LEAD_W, ART_H)
        ty = ly + ART_H + 3
        kicker(d, x, ty, ld["n"], ld["kicker"], F_LEAD_K, ld["region"])
        hy = ty + 14
        lines = wrap(d, ld["headline"], F_LEAD_H, LEAD_W, 2, "lead headline")
        for j, ln in enumerate(lines):
            d.text((x, hy + j * 22), ln, font=F_LEAD_H, fill=INK)
        dy = hy + len(lines) * 22 + 1
        dlines = wrap(d, ld["deck"], F_LEAD_D, LEAD_W, 2, "lead deck")
        for j, ln in enumerate(dlines):
            d.text((x, dy + j * 14), ln, font=F_LEAD_D, fill=INK)
        lead_end = max(lead_end, dy + len(dlines) * 14)
        note(dy + len(dlines) * 14)

    # ---- cards (2 rows x 5) ----
    cy0 = lead_end + 4
    d.line([M, cy0 - 3, W - M, cy0 - 3], fill=HAIR, width=1)
    for row in range(2):
        for col in range(5):
            c = CARDS[row * 5 + col]
            x = M + col * (CARD_W + 12)
            y = cy0 + row * (CARD_H + 4)
            SCENES[c["scene"]](d, x, y, CARD_W, STRIP_H)
            # data chip on the strip (right-aligned)
            chw = int(text_w(d, c["chip"], F_CHIP)) + 12
            assert chw <= CARD_W - 8, f"chip too wide: {c['chip']}"
            chip(d, x + CARD_W - 4 - chw, y + 4, c["chip"], F_CHIP,
                 CHIP_FILL[c["fill"]])
            # location bar under the strip
            by = y + STRIP_H
            d.rectangle([x, by, x + CARD_W, by + BAR_H], fill=NAVY)
            assert text_w(d, c["bar"], F_BAR) + 12 <= CARD_W, \
                f"bar too wide: {c['bar']}"
            d.text((x + 6, by + 2), c["bar"], font=F_BAR, fill=(255, 255, 255))
            # kicker (dot + ink) / headline / deck — baselines aligned by geometry
            ky = by + BAR_H + 2
            kicker(d, x, ky, c["n"], c["kicker"], F_CARD_K, c["region"])
            hy = ky + 14
            lines = wrap(d, c["headline"], F_CARD_H, CARD_W, 2, "card headline")
            for j, ln in enumerate(lines):
                d.text((x, hy + j * 17), ln, font=F_CARD_H, fill=INK)
            dy = hy + len(lines) * 17 + 1
            dlines = wrap(d, c["deck"], F_CARD_D, CARD_W, 2, "card deck")
            for j, ln in enumerate(dlines):
                d.text((x, dy + j * 14), ln, font=F_CARD_D, fill=INK)
            assert dy + len(dlines) * 14 <= y + CARD_H, f"card overflow: {c['n']}"
            note(y + CARD_H)
        if row == 0:
            d.line([M, cy0 + CARD_H + 2, W - M, cy0 + CARD_H + 2], fill=HAIR, width=1)
    cards_end = cy0 + 2 * CARD_H + 4

    # ---- bottom band headers ----
    byy = cards_end + 3
    lw1 = section_label(d, M, byy, "WHERE IT HAPPENED")
    lw2 = section_label(d, BRIEF_X0, byy, "ALSO ON WEDNESDAY 18 NOVEMBER")
    d.line([M + lw1 + 8, byy + 6, BRIEF_X0 - 12, byy + 6], fill=HAIR, width=1)
    d.line([BRIEF_X0 + lw2 + 8, byy + 6, W - M, byy + 6], fill=HAIR, width=1)

    # ---- map: solid continents on pale sea, dots, then pins LAST ----
    d.rectangle([MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H], fill=SEA)
    for poly in POLYS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    for n, lon, lat, reg in DOTS:
        px, py = proj(lon, lat)
        # round circles, r=3.5: a 5px PIL ellipse (r=2.5) renders as a DIAMOND
        d.ellipse([px - 3.5, py - 3.5, px + 3.5, py + 3.5], fill=REGION[reg])
    pin_xy = {}
    for n, lon, lat, reg, _off in PINS:
        px, py = proj(lon, lat)
        dx, dy = PIN_OFFSET.get(n, (0, 0))
        pin_xy[n] = (px + dx, py + dy)
    pts = list(pin_xy.values())
    mind = min(math.hypot(a[0] - b[0], a[1] - b[1])
               for i, a in enumerate(pts) for b in pts[i + 1:])
    assert mind >= 20, f"pins too close: min {mind:.1f}px"
    print(f"pin min distance: {mind:.1f}px")
    for n, lon, lat, reg, _off in PINS:
        px, py = pin_xy[n]
        d.ellipse([px - 7.5, py - 7.5, px + 7.5, py + 7.5],
                  fill=REGION[reg], outline=(255, 255, 255), width=1)
        tw = text_w(d, str(n), F_PIN)
        d.text((px - tw / 2, py - 5), str(n), font=F_PIN, fill=(255, 255, 255))
    note(MAP_Y + MAP_H)
    # caption + legend under the map
    d.text((MAP_X, MAP_Y + MAP_H + 4), "Pins: stories 1–13 · dots: 14–43",
           font=F_STAT_LBL, fill=GREY)
    lx, ly2 = MAP_X, MAP_Y + MAP_H + 20
    for row_items in (["Europe", "Middle East", "Asia", "Africa"],
                      ["Americas", "Oceania", "Global"]):
        cx = lx
        for reg in row_items:
            d.rectangle([cx, ly2 + 1, cx + 8, ly2 + 9], fill=REGION[reg])
            d.text((cx + 11, ly2), reg, font=F_LEG, fill=INK)
            cx += 11 + text_w(d, reg, F_LEG) + 12
        ly2 += 13
    note(ly2)

    # ---- DATE CHECK box (under the map) ----
    dc_x0, dc_y0, dc_x1, dc_y1 = M, 906, M + MAP_W, 974
    d.rectangle([dc_x0, dc_y0, dc_x1, dc_y1], outline=RED, width=2)
    d.text((dc_x0 + 10, dc_y0 + 5), DATE_CHECK_TITLE, font=F_DATE_T, fill=RED)
    blines = wrap(d, DATE_CHECK_BODY, F_DATE_B, dc_x1 - dc_x0 - 20, 3,
                  "date check body")
    for j, ln in enumerate(blines):
        d.text((dc_x0 + 10, dc_y0 + 21 + j * 13), ln, font=F_DATE_B, fill=INK)
    note(dc_y1)

    # ---- briefs: 2 columns x 15, pitch 20, region-coloured numbers, bold prefix ----
    for i, (n, reg, text) in enumerate(BRIEFS):
        col = i // 15
        row = i % 15
        bx = BRIEF_X0 + col * (BRIEF_COL_W + 8)
        ry = MAP_Y + row * BRIEF_PITCH
        num_s = str(n) + " "
        nw = text_w(d, num_s, F_BRIEF_B)
        d.text((bx, ry), num_s, font=F_BRIEF_B, fill=REGION[reg])
        if ":" in text:
            pre, rest = text.split(":", 1)
            pre += ":"
            pw = text_w(d, pre, F_BRIEF_B)
            d.text((bx + nw, ry), pre, font=F_BRIEF_B, fill=INK)
            d.text((bx + nw + pw, ry), rest, font=F_BRIEF, fill=INK)
            total = nw + pw + text_w(d, rest, F_BRIEF)
        else:
            d.text((bx + nw, ry), text, font=F_BRIEF, fill=INK)
            total = nw + text_w(d, text, F_BRIEF)
        assert total <= BRIEF_COL_W, f"brief too wide: {text} ({total:.0f})"
        note(ry + 14)

    # ---- footer ----
    fy = max_y + 6
    d.line([M, fy - 4, W - M, fy - 4], fill=HAIR, width=1)
    for j, ln in enumerate((FOOTER_1, FOOTER_2)):
        tw = text_w(d, ln, F_FOOT)
        assert tw <= CW, f"footer too wide: {ln[:40]}"
        d.text(((W - tw) / 2, fy + j * 13), ln, font=F_FOOT, fill=GREY)
    note(fy + 2 * 13)
    assert max_y <= 1010, f"page overflow: max_y={max_y}"
    print(f"masthead Playfair ExtraBold {MAST_SIZE}px, layout max_y: {max_y}")
    return img


PIN_OFFSET = {n: off for n, _lon, _lat, _reg, off in PINS}


def main():
    img = draw_page()
    out = os.path.join(HERE, "entry.png")
    img.save(out)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
