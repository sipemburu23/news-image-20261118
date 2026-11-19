#!/usr/bin/env python3
"""Draw the Wednesday 18 November 2026 front page (news-image-20261118, round 2).

Redesign ala #1: dark navy masthead band + calendar chip, 3 leads, 8 wide cards,
dotted map + 27 briefs, 4 big numbers, DATE CHECK, footer.
Deterministic: no timestamps, no unseeded randomness. PIL only.
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
X0, X1 = 24, 1000          # content span
HERE = os.path.dirname(os.path.abspath(__file__))

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (31, 42, 68)
NAVY_DARK = (16, 35, 63)
RED = (180, 35, 24)
GREEN = (30, 107, 58)
GOLD = (217, 180, 91)
GRAY = (102, 102, 102)
HAIR = (180, 172, 152)
MAP_DOT = (168, 159, 131)

# region colours: fills / dots / brief numbers only, never small coloured text
REG = {
    "apac": (37, 99, 235),
    "me": (180, 35, 24),
    "eu": (14, 116, 144),
    "am": (30, 107, 58),
    "af": (194, 94, 30),
    "space": (107, 79, 161),
    "global": (102, 102, 102),
}

PF = os.path.join(HERE, "fonts", "PlayfairDisplay.ttf")
DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DJSI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"


def pf(size, wght=700):
    f = ImageFont.truetype(PF, size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def dj(size, bold=False):
    return ImageFont.truetype(DJB if bold else DJ, size)


def tw(font, text):
    return font.getlength(text)


def wrap(text, font, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if tw(font, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_center(d, cx, y, text, font, fill):
    d.text((cx, y), text, font=font, fill=fill, anchor="ma")


def chip(d, x, y, text, fill, font=None, pad_x=7, pad_y=4):
    """Meaning-coded chip: white bold text on coloured fill, thin white outline.
    Returns the chip width. Asserts it fits on the page."""
    font = font or dj(10, bold=True)
    w = int(math.ceil(tw(font, text))) + 2 * pad_x
    h = font.size + 2 * pad_y
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill,
                        outline=(255, 255, 255), width=1)
    d.text((x + pad_x, y + pad_y - 1), text, font=font, fill=(255, 255, 255))
    return w


def banner(d, x, y, w, text, font=None):
    """Bottom-of-art banner: dark navy band, gold top rule, white centred text."""
    font = font or dj(10, bold=True)
    assert tw(font, text) <= w - 16, f"banner too wide: {text!r} {tw(font, text):.1f} > {w - 16}"
    d.rectangle([x, y, x + w, y + 17], fill=NAVY_DARK)
    d.line([x, y, x + w, y], fill=GOLD, width=1)
    draw_center(d, x + w / 2, y + 3, text, font, (255, 255, 255))


def label_fit(font, text, max_w, what):
    w = tw(font, text)
    assert w <= max_w, f"{what}: label {text!r} {w:.1f}px > {max_w}px"
    return w


def badge(d, cx, cy, num, color, r=13):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color,
              outline=(255, 255, 255), width=2)
    d.text((cx, cy), str(num), font=dj(r + 1, bold=True), fill=(255, 255, 255),
           anchor="mm")


def kicker(d, x, y, text, color, font=None):
    """Region dot + kicker text in ink (never coloured 11px text)."""
    font = font or dj(11, bold=True)
    label_fit(font, text, 317, "kicker")
    d.ellipse([x, y + 2, x + 7, y + 9], fill=color)
    d.text((x + 11, y), text, font=font, fill=INK)


def star5(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


# ---------------------------------------------------------------- data
# Continent polygons (lon, lat) — reference data for the dotted map.
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

LEADS = [
    dict(num=1, region="me", kicker="MIDDLE EAST · IRAN WAR · REUTERS · AP",
         head="Iran widens the Gulf war to Kuwait and Bahrain",
         deck=("Tehran says it hit US sites at Kuwait's Ali Al Salem base overnight, after "
               "the US struck an IRGC site on Qeshm on Tuesday. Bahrain intercepts a third "
               "attack this week; an ADNOC vessel is hit in Hormuz — 11 injured, 1 missing. "
               "Brent ~$91.68.")),
    dict(num=2, region="apac", kicker="ASIA · SUMMIT · AFP · AP · BBC",
         head="Xi greets Trump in Shenzhen as the trilateral looms",
         deck=("Xi meets Trump on the tarmac — a gesture he skipped in Beijing in May — then "
               "holds his fifth talks this year with Putin. APEC opens; the first "
               "Trump–Xi–Putin trilateral is Thursday. Trump is the first US president to "
               "visit Shenzhen in office.")),
    dict(num=3, region="space", kicker="SPACE · SCIENCE · NASA",
         head="Voyager 1 reaches one light-day from Earth",
         deck=("NASA's probe is the first human-made object to get 25.9 billion km away, at "
               "10:16 UTC. A command sent today arrives tomorrow — 49 years after launch.")),
]

CARDS = [
    dict(num=4, region="eu", kicker="EUROPE · UKRAINE WAR · AIR FORCE",
         head="Russia fires 141 drones at Ukraine; 126 downed",
         deck="Hits at seven sites; four killed in Donetsk, its governor says.",
         chip=("141 FIRED / 126 DOWNED", RED)),
    dict(num=5, region="am", kicker="AMERICAS · MARKETS · FED · AP",
         head="Fed minutes: almost all officials see more hikes",
         deck="A December rise is priced as certain; the hold vote was 10–2.",
         chip=("DEC HIKE CERTAIN", GREEN)),
    dict(num=6, region="apac", kicker="ASIA · WEATHER · IMD",
         head="Cyclone Akvan veers north toward Odisha",
         deck="Landfall near Puri on 20 Nov; gusts 145 km/h, 200,000 evacuated.",
         chip=("LANDFALL 20 NOV", NAVY)),
    dict(num=7, region="af", kicker="AFRICA · SUDAN WAR · UN · OHCHR",
         head="UN: 2,230 civilians killed in Sudan this year",
         deck="At least 2,230 killed Jan–Oct 2026, over 1,630 by drones.",
         chip=("2,230 KILLED", RED)),
    dict(num=8, region="eu", kicker="EUROPE · UKRAINE AID · EU",
         head="EU proposes a €45bn loan to fund Ukraine in 2027",
         deck="Two-thirds of Kyiv's €70bn gap, repaid once Russia pays reparations.",
         chip=("€45BN FOR 2027", NAVY)),
    dict(num=9, region="eu", kicker="EUROPE · ECONOMY · ONS",
         head="UK inflation climbs to 3.6%, a one-year high",
         deck="Fuel prices pushed October CPI up from 3.5%; diesel 199.5p, a record.",
         chip=("3.5% SEP → 3.6% OCT", GREEN)),
    dict(num=10, region="me", kicker="MIDDLE EAST · GAZA · REUTERS",
         head="Board of Peace faults both sides on Gaza",
         deck="A UN report warns a ceasefire delivering nothing cannot last.",
         chip=("TRUCE AT RISK", NAVY)),
    dict(num=11, region="am", kicker="AMERICAS · US POLITICS · NPR · CBS",
         head="Jeffries wins Democrats' nod for House Speaker",
         deck="A 251–11 vote puts him on course to be first Black Speaker in January.",
         chip=("251–11 CAUCUS VOTE", NAVY)),
]

# briefs: (num, region, prefix, rest) — prefix bold, rest regular
BRIEFS = [
    (12, "apac", "Manila:", "biggest deal; none signed"),
    (13, "am", "Anthropic:", "IPO priced $83, ~$1.5tn"),
    (14, "apac", "Ethiopia:", "troops mass on border"),
    (15, "apac", "Australia:", "sanctions Weiss; UK: 8 firms"),
    (16, "global", "Gold:", "$3,792, down 1.5%"),
    (17, "af", "Mozambique:", "Mondlane trial, day two"),
    (18, "eu", "Serbia:", "elects speaker Čupić"),
    (19, "apac", "Xavier:", "Cat 5 nears Pukapuka"),
    (20, "apac", "Danang:", "Russian bombers land"),
    (21, "am", "California:", "2nd storm, 70 mph gusts"),
    (22, "apac", "Carney:", "meets Trump 20 min, no deal"),
    (23, "eu", "ICJ:", "to rule Thu on Myanmar case"),
    (24, "am", "Waymo:", "pulls robotaxis off freeways"),
    (25, "am", "Measles:", "US loses status, ruling Tue"),
    (26, "am", "OpenAI:", "launches GPT-6.2 Astra, Sol"),
    (27, "me", "Yemen:", "coalition hits 60 Houthi targets"),
    (28, "eu", "Siberia:", "An-12 crash kills 19"),
    (29, "me", "Knesset:", "elects Kahana, 66–52"),
    (30, "apac", "China–Canada:", "tariff cuts, C$400m"),
    (31, "am", "US:", "no cyberattack behind outages"),
    (32, "apac", "Trump:", "first US president in Shenzhen"),
    (33, "af", "Kenya:", "discharges last Ebola patient"),
    (34, "me", "Yemen PLC:", "labels Houthis terrorists"),
    (35, "apac", "GTA VI:", "on sale, NZ first — 17.1m"),
    (36, "af", "DR Congo:", "Ebola 11,536 cases"),
    (37, "apac", "Bangladesh:", "132 factories shut"),
    (38, "apac", "India:", "Dhoni retires to mentor CSK"),
]

BIG = [
    ("141", "DRONES FIRED"),
    ("€45BN", "EU FOR UKRAINE"),
    ("25.9BN KM", "VOYAGER 1"),
    ("251–11", "JEFFRIES VOTE"),
]

DATE_CHECK = ("DATE CHECK — Left out on purpose, first reported Tuesday 17 November: "
              "Kerch Bridge span collapse · Nvidia's $115.8bn quarter · Mongolia's president "
              "resigning · Prague train crash · Japan airspace breach.")

# ---------------------------------------------------------------- masthead
def draw_masthead(d):
    d.rectangle([0, 0, W, 80], fill=NAVY)
    # calendar chip: red box NOV 18, WED · 2026 below in white
    d.rectangle([24, 8, 116, 44], fill=RED)
    d.text((70, 12), "NOV 18", font=dj(17, bold=True), fill=(255, 255, 255), anchor="ma")
    d.text((70, 50), "WED · 2026", font=dj(12, bold=True), fill=(255, 255, 255), anchor="ma")
    # gold kicker, letterspaced, top centre-left
    kick = "THE DAY IN WORLD NEWS"
    kf = dj(11, bold=True)
    x = 132
    for ch in kick:
        d.text((x, 6), ch, font=kf, fill=GOLD)
        x += int(tw(kf, ch)) + 2
    # count line top right
    cnt = "38 STORIES · 6 CONTINENTS · ONE PAGE"
    d.text((1000, 6), cnt, font=dj(11, bold=True), fill=(255, 255, 255), anchor="ra")
    # masthead: largest size that fits x=132..1000 (868px) with its INK box
    # below the kicker (ink top y=20) and inside the band (ink bottom <= 78).
    # 62px ink is 58px tall and collides with the kicker; 60px = 833px wide
    # and fits with ink top 20 / bottom ~76.
    mf = pf(60, 800)
    label_fit(mf, "Wednesday 18 November 2026", 868, "masthead")
    bb = mf.getbbox("Wednesday 18 November 2026")
    assert bb[3] - bb[1] <= 60, f"masthead ink {bb[3] - bb[1]}px too tall"
    y_top = 20 - bb[1]
    d.text((132, y_top), "Wednesday 18 November 2026", font=mf, fill=(255, 255, 255))


def draw_veracity(d):
    d.text((24, 84), "Everything on this page happened, or was first reported, on "
                     "Wednesday 18 November 2026.",
           font=ImageFont.truetype(DJSI, 12), fill=INK)


# ---------------------------------------------------------------- lead art
def art_gulf(d, x, y, w, h):
    # night sky over the Gulf, gradient bands
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip((13, 22, 44), (31, 42, 68)))
        d.line([x, y + i, x + w, y + i], fill=c)
    # stars (fixed)
    for sx, sy in [(18, 8), (60, 16), (110, 6), (150, 14), (200, 8), (250, 18),
                   (285, 6), (40, 28), (170, 26), (230, 30), (300, 26)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # sea band
    d.rectangle([x, y + h - 26, x + w, y + h - 17], fill=(10, 18, 38))
    # radar dome (left)
    dx, dy = x + 52, y + h - 26
    d.pieslice([dx - 34, dy - 34, dx + 34, dy], 180, 360, fill=(232, 232, 228))
    d.rectangle([dx - 38, dy - 2, dx + 38, dy + 2], fill=(200, 200, 195))
    d.line([dx, dy - 30, dx + 22, dy - 44], fill=(255, 255, 255), width=2)
    # dashed routes with arrowheads: L-shaped to Kuwait (up, then right —
    # keeps clear of the TUE STRIKE tag) and diagonal to Bahrain
    def dashed_h(x1, y1, x2, y2, fill):
        n = int(math.hypot(x2 - x1, y2 - y1) / 7)
        for i in range(n):
            t0, t1 = i / n, (i + 0.55) / n
            d.line([x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0,
                    x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1], fill=fill, width=2)
    qx, qy = x + 240, y + 68          # Qeshm strike point
    dashed_h(qx, qy, qx, y + 30, (217, 180, 91))
    dashed_h(qx, y + 30, x + 290, y + 30, (217, 180, 91))
    d.polygon([(x + 290, y + 30), (x + 281, y + 26), (x + 281, y + 34)],
              fill=(217, 180, 91))
    dashed_h(qx, qy, x + 195, y + 48, (217, 180, 91))
    ang = math.atan2(48 - 68, 195 - 240)
    d.polygon([(x + 195, y + 48),
               (x + 195 - 9 * math.cos(ang - 0.42), y + 48 - 9 * math.sin(ang - 0.42)),
               (x + 195 - 9 * math.cos(ang + 0.42), y + 48 - 9 * math.sin(ang + 0.42))],
              fill=(217, 180, 91))
    d.ellipse([qx - 3, qy - 3, qx + 3, qy + 3], fill=(217, 180, 91))
    # two ships on the sea band (hulls lightened: dark hulls were invisible
    # against the dark sea band)
    for sx in (x + 100, x + 170):
        d.polygon([(sx, y + h - 26), (sx + 52, y + h - 26), (sx + 46, y + h - 17),
                   (sx + 6, y + h - 17)], fill=(90, 105, 135))
        d.line([sx, y + h - 26, sx + 52, y + h - 26], fill=(255, 255, 255), width=1)
        d.rectangle([sx + 14, y + h - 33, sx + 30, y + h - 26], fill=(200, 200, 195))
        d.ellipse([sx + 20, y + h - 36, sx + 24, y + h - 32], fill=RED)
    # drones: small dark silhouettes with red dots, clear of the chips
    for dx2, dy2 in [(x + 120, y + 48), (x + 175, y + 58)]:
        d.ellipse([dx2 - 7, dy2 - 3, dx2 + 7, dy2 + 3], fill=(5, 8, 18))
        d.line([dx2 - 12, dy2, dx2 + 12, dy2], fill=(5, 8, 18), width=2)
        d.ellipse([dx2 - 1, dy2 - 1, dx2 + 1, dy2 + 1], fill=RED)
    # labels
    f11 = dj(11, bold=True)
    label_fit(f11, "IRAN", 60, "gulf IRAN")
    d.text((x + 32, y + 10), "IRAN", font=f11, fill=(255, 255, 255))
    d.text((x + 252, y + 70), "HORMUZ", font=dj(10, bold=True), fill=(255, 255, 255))
    d.text((x + 246, y + 56), "QESHM", font=dj(10, bold=True), fill=(255, 255, 255))
    # TUE STRIKE tag (navy outline, white text)
    tf = dj(8, bold=True)
    tw_ = int(tw(tf, "TUE STRIKE"))
    d.rectangle([x + 246, y + 44, x + 246 + tw_ + 8, y + 54], outline=(255, 255, 255), width=1)
    d.text((x + 250, y + 45), "TUE STRIKE", font=tf, fill=(255, 255, 255))
    # chips top-right (stacked)
    w1 = chip(d, x + w - 118, y + 6, "KUWAIT HIT", RED)
    chip(d, x + w - 158, y + 24, "BAHRAIN INTERCEPTS", NAVY)


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    star5(d, x + 9, y + 9, 6, (255, 222, 89))
    for sx, sy in [(22, 5), (27, 9), (27, 15), (22, 19)]:
        star5(d, x + sx, y + sy, 2, (255, 222, 89))


def flag_us(d, x, y, w, h):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.42, y + h * 4 / 7], fill=(60, 59, 110))
    for r in range(4):
        for c in range(5):
            d.ellipse([x + 3 + c * 7, y + 2 + r * 4.5, x + 5 + c * 7, y + 4 + r * 4.5],
                      fill=(255, 255, 255))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


def art_shenzhen(d, x, y, w, h):
    # pale sky
    d.rectangle([x, y, x + w, y + h], fill=(223, 232, 242))
    # skyline along the bottom FIRST (flags are drawn over it, not under it)
    base = y + h - 17
    heights = [8, 12, 6, 16, 10, 14, 7, 11, 9, 15, 8, 12, 6, 10]
    bx = x + 4
    for i, hh in enumerate(heights):
        bw = 20 if i % 3 else 24
        col = (120, 138, 160) if i % 2 else (96, 116, 142)
        d.rectangle([bx, base - hh, bx + bw, base], fill=col)
        for wy in range(0, hh - 6, 9):
            d.rectangle([bx + 4, base - hh + 4 + wy, bx + 8, base - hh + 8 + wy],
                        fill=(255, 230, 150))
        bx += bw + 2
    # plane, horizontal, top-left flying right
    px, py = x + 12, y + 8
    d.polygon([(px, py + 8), (px + 78, py + 8), (px + 92, py + 12), (px + 78, py + 16),
               (px, py + 16)], fill=(255, 255, 255))
    d.polygon([(px + 62, py + 8), (px + 70, py - 2), (px + 76, py + 8)], fill=(31, 42, 68))
    d.polygon([(px + 40, py + 16), (px + 48, py + 26), (px + 54, py + 16)], fill=(200, 205, 212))
    for wx in range(14, 62, 9):
        d.rectangle([px + wx, py + 10, px + wx + 4, py + 13], fill=(31, 42, 68))
    d.text((x + 12, y + 40), "SHENZHEN", font=dj(10, bold=True), fill=INK)
    # flags row with poles; poles run through to the skyline, but the name
    # gets a backing-rect erase so the pole never crosses a name glyph
    flags = [(flag_cn, "CHINA"), (flag_us, "UNITED STATES"), (flag_ru, "RUSSIA")]
    fx = x + 112
    nf = dj(8, bold=True)   # 8px: "UNITED STATES" (69px) fits its 80px slot
    for fn, name in flags:
        d.line([fx, y + 26, fx, y + 82], fill=(90, 90, 90), width=2)
        fn(d, fx, y + 38, 46, 22)
        nw = int(tw(nf, name))
        d.rectangle([fx - 2, y + 62, fx + nw + 2, y + 72], fill=(223, 232, 242))
        d.text((fx, y + 62), name, font=nf, fill=INK)
        fx += 80
    # chip top-right
    chip(d, x + w - 138, y + 8, "3-WAY TALKS · THU", NAVY)


def art_voyager(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 21, 38))
    for sx, sy in [(20, 10), (70, 22), (130, 8), (190, 18), (250, 10), (300, 22),
                   (40, 44), (150, 40), (280, 44), (100, 60), (220, 58)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # Earth, left
    ex, ey, er = x + 46, y + 62, 26
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(43, 110, 196))
    d.ellipse([ex - 12, ey - 14, ex + 2, ey - 2], fill=(74, 160, 90))
    d.ellipse([ex + 2, ey + 6, ex + 16, ey + 18], fill=(74, 160, 90))
    d.arc([ex - er, ey - er, ex + er, ey + er], 200, 320, fill=(255, 255, 255), width=2)
    d.text((ex - 18, ey + er + 4), "EARTH", font=dj(10, bold=True), fill=(255, 255, 255))
    # dashed gold line Earth -> probe
    px, py = x + w - 52, y + 30
    n = 16
    for i in range(n):
        t0, t1 = i / n, (i + 0.55) / n
        d.line([ex + 22 + (px - ex - 22) * t0, ey - 8 + (py - ey + 8) * t0,
                ex + 22 + (px - ex - 22) * t1, ey - 8 + (py - ey + 8) * t1],
               fill=GOLD, width=2)
    # probe: gold dish + grey body + antenna
    d.ellipse([px - 14, py - 6, px + 14, py + 10], fill=(217, 180, 91))
    d.ellipse([px - 14, py - 6, px + 14, py + 2], fill=(232, 200, 120))
    d.rectangle([px - 4, py + 8, px + 4, py + 20], fill=(200, 200, 195))
    d.line([px, py + 20, px + 12, py + 30], fill=(200, 200, 195), width=2)
    d.text((px - 30, py + 32), "VOYAGER 1", font=dj(10, bold=True), fill=(255, 255, 255))
    d.text((px - 24, py + 44), "10:16 UTC", font=dj(9, bold=True), fill=GOLD)
    # chip top-centre
    chip(d, x + 128, y + 8, "25.9BN KM", GREEN)


LEAD_ART = {1: art_gulf, 2: art_shenzhen, 3: art_voyager}
LEAD_BANNER = {1: "GULF WAR WIDENS · KUWAIT HIT",
               2: "APEC OPENS · TRILATERAL THU",
               3: "ONE LIGHT-DAY · 25.9BN KM"}


def draw_leads(d):
    xs = [24, 353, 682]
    lw = 317
    y = 99
    art_h = 110
    for lead, lx in zip(LEADS, xs):
        LEAD_ART[lead["num"]](d, lx, y, lw, art_h)
        banner(d, lx, y + art_h - 17, lw, LEAD_BANNER[lead["num"]])
        badge(d, lx + 14, y + 14, lead["num"], REG[lead["region"]], r=13)
        kicker(d, lx, y + art_h + 4, lead["kicker"], REG[lead["region"]])
        hf = pf(21, 700)
        lines = wrap(lead["head"], hf, lw)
        assert len(lines) <= 2, f"lead {lead['num']} headline wraps to {len(lines)}"
        hy = y + art_h + 20
        for ln in lines:
            d.text((lx, hy), ln, font=hf, fill=INK)
            hy += 24
        df = dj(12)
        dlines = wrap(lead["deck"], df, lw)
        assert len(dlines) <= 5, f"lead {lead['num']} deck wraps to {len(dlines)}: {dlines}"
        dy = 279
        for ln in dlines:
            d.text((lx, dy), ln, font=df, fill=INK)
            dy += 12
    return 341

# ---------------------------------------------------------------- card art
def art_drones(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 22, 44))
    for sx, sy in [(16, 10), (60, 18), (120, 8), (200, 14), (40, 30), (150, 26)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # explosion star, centre-right
    star5(d, x + 168, y + 38, 15, (240, 180, 60))
    star5(d, x + 168, y + 38, 8, (240, 110, 40))
    # three drone silhouettes
    for dx2, dy2 in [(x + 42, y + 26), (x + 96, y + 18), (x + 200, y + 52)]:
        d.ellipse([dx2 - 8, dy2 - 3, dx2 + 8, dy2 + 3], fill=(5, 8, 18))
        d.line([dx2 - 13, dy2, dx2 + 13, dy2], fill=(5, 8, 18), width=2)
        d.ellipse([dx2 - 1, dy2 - 1, dx2 + 1, dy2 + 1], fill=RED)
    # ground line + tracer dots
    d.line([x, y + h - 8, x + w, y + h - 8], fill=(60, 70, 95), width=2)
    for tx in (30, 90, 150, 210):
        d.ellipse([x + tx, y + h - 12, x + tx + 3, y + h - 9], fill=(240, 180, 60))


def art_fed(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 216))
    # Fed building, left
    bx, by = x + 14, y + 14
    d.polygon([(bx, by + 12), (bx + 34, by), (bx + 68, by + 12)], fill=(250, 250, 246))
    d.rectangle([bx + 2, by + 12, bx + 66, by + 16], fill=(220, 220, 214))
    for i in range(4):
        cx = bx + 8 + i * 16
        d.rectangle([cx, by + 16, cx + 7, by + 44], fill=(250, 250, 246))
    d.rectangle([bx, by + 44, bx + 68, by + 48], fill=(220, 220, 214))
    d.rectangle([bx - 4, by + 48, bx + 72, by + 52], fill=(200, 200, 192))
    # rising arrow chart, right
    pts = [(x + 108, y + 58), (x + 138, y + 46), (x + 158, y + 50), (x + 188, y + 28),
           (x + 216, y + 16)]
    d.line(pts, fill=GREEN, width=4, joint="curve")
    ang = math.atan2(16 - 28, 216 - 188)
    d.polygon([(x + 216, y + 16),
               (x + 216 - 12 * math.cos(ang - 0.42), y + 16 - 12 * math.sin(ang - 0.42)),
               (x + 216 - 12 * math.cos(ang + 0.42), y + 16 - 12 * math.sin(ang + 0.42))],
              fill=GREEN)
    d.text((x + 112, y + 62), "+50bp?", font=dj(9, bold=True), fill=GREEN)


def art_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(27, 74, 90))
    # coast land strip, bottom-right
    d.polygon([(x + 150, y + h), (x + 235, y + h), (x + 235, y + 46), (x + 196, y + 58),
               (x + 168, y + 66)], fill=(214, 196, 150))
    d.text((x + 178, y + 60), "ODISHA", font=dj(9, bold=True), fill=(90, 70, 40))
    # cyclone spiral: white arcs
    cx, cy = x + 96, y + 40
    for r, a0, a1 in [(10, 0, 300), (18, 40, 340), (26, 80, 30), (34, 120, 70)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=(255, 255, 255), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    # rain streaks
    for rx, ry in [(30, 14), (52, 22), (150, 12), (176, 20), (210, 10)]:
        d.line([x + rx, y + ry, x + rx - 4, y + ry + 10], fill=(180, 210, 220), width=2)


def art_sudan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 217, 184))
    # simplified Sudan shape
    poly = [(x + 84, y + 12), (x + 128, y + 8), (x + 156, y + 22), (x + 148, y + 48),
            (x + 158, y + 62), (x + 120, y + 72), (x + 92, y + 58), (x + 80, y + 34)]
    d.polygon(poly, fill=(198, 168, 120), outline=(150, 120, 80))
    # red location markers
    for mx, my in [(112, 30), (132, 46), (106, 56)]:
        d.ellipse([x + mx - 4, y + my - 4, x + mx + 4, y + my + 4], fill=RED,
                  outline=(255, 255, 255), width=1)
    # damaged building, left
    d.polygon([(x + 18, y + 34), (x + 52, y + 26), (x + 56, y + 62), (x + 22, y + 62)],
              fill=(150, 120, 90))
    d.line([x + 18, y + 34, x + 52, y + 26], fill=(90, 70, 50), width=2)
    d.rectangle([x + 30, y + 44, x + 38, y + 52], fill=(60, 45, 30))
    d.text((x + 14, y + 66), "KHARTOUM", font=dj(8, bold=True), fill=(90, 70, 50))


def art_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(43, 74, 143))
    # circle of 12 stars
    cx, cy = x + 52, y + 40
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        star5(d, cx + 27 * math.cos(ang), cy + 27 * math.sin(ang), 4.5, (255, 215, 0))
    d.text((cx - 12, cy - 6), "EU", font=dj(11, bold=True), fill=(255, 255, 255))
    # Ukraine flag, right
    fx, fy, fw, fh = x + 128, y + 20, 88, 40
    d.rectangle([fx, fy, fx + fw, fy + fh / 2], fill=(0, 91, 187))
    d.rectangle([fx, fy + fh / 2, fx + fw, fy + fh], fill=(255, 213, 0))
    d.rectangle([fx, fy, fx + fw, fy + fh], outline=(255, 255, 255), width=1)


def art_uk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(239, 233, 216))
    # shopping basket, left
    bx, by = x + 18, y + 34
    d.polygon([(bx, by), (bx + 56, by), (bx + 48, by + 30), (bx + 8, by + 30)],
              fill=(150, 100, 50))
    d.arc([bx + 10, by - 16, bx + 46, by + 10], 180, 360, fill=(120, 80, 40), width=3)
    d.text((bx + 16, by + 8), "199.5p", font=dj(9, bold=True), fill=(255, 255, 255))
    # rising price bars, right
    for i, bh in enumerate((16, 26, 38)):
        xx = x + 108 + i * 34
        d.rectangle([xx, y + 62 - bh, xx + 22, y + 62], fill=GREEN)
    d.line([x + 100, y + 62, x + 214, y + 62], fill=(120, 110, 90), width=2)
    d.text((x + 108, y + 66), "SEP 3.5% → OCT 3.6%", font=dj(8, bold=True), fill=GREEN)


def art_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(223, 233, 242))
    # UN flag, LEFT (chip stays top-right, never covers the flag)
    fx, fy, fw, fh = x + 10, y + 14, 52, 34
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(91, 146, 196))
    d.ellipse([fx + 18, fy + 8, fx + 34, fy + 24], outline=(255, 255, 255), width=2)
    d.line([fx + 8, fy + 26, fx + 44, fy + 26], fill=(255, 255, 255), width=2)
    d.line([fx + 2, fy, fx + 2, fy + 46], fill=(120, 120, 120), width=2)
    d.text((fx - 2, fy + 50), "UN", font=dj(9, bold=True), fill=(60, 90, 130))
    # negotiation table + two chairs, right
    tx, ty = x + 96, y + 44
    d.rectangle([tx, ty, tx + 96, ty + 8], fill=(120, 84, 50))
    d.rectangle([tx + 6, ty + 8, tx + 12, ty + 26], fill=(100, 70, 40))
    d.rectangle([tx + 84, ty + 8, tx + 90, ty + 26], fill=(100, 70, 40))
    d.rectangle([tx + 78, ty - 14, tx + 86, ty], fill=(90, 90, 90))
    d.rectangle([tx + 116, ty - 14, tx + 124, ty], fill=(90, 90, 90))
    # olive branch on the table
    d.line([tx + 30, ty - 2, tx + 60, ty - 2], fill=GREEN, width=2)
    for ox in (36, 46, 56):
        d.ellipse([tx + ox, ty - 7, tx + ox + 6, ty - 1], fill=GREEN)


def art_jeffries(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(239, 233, 216))
    # ballot box, left
    bx, by = x + 16, y + 20
    d.rectangle([bx, by, bx + 52, by + 42], fill=NAVY)
    d.rectangle([bx + 8, by - 8, bx + 44, by], fill=(255, 255, 255),
                outline=(31, 42, 68), width=1)
    d.line([bx + 18, by - 8, bx + 34, by - 8], fill=NAVY, width=2)
    d.text((bx + 12, by + 14), "VOTE", font=dj(11, bold=True), fill=(255, 255, 255))
    # tally bars, right — start below the chip (the chip used to cover "251")
    for i, (bl, col, lab) in enumerate(((96, (37, 99, 235), "251"),
                                        (18, (180, 35, 24), "11"),
                                        (40, (150, 150, 150), ""))):
        yy = y + 30 + i * 18
        d.rectangle([x + 96, yy, x + 96 + bl, yy + 11], fill=col)
        if lab:
            d.text((x + 96 + bl + 5, yy - 1), lab, font=dj(10, bold=True), fill=INK)


CARD_ART = {4: art_drones, 5: art_fed, 6: art_akvan, 7: art_sudan, 8: art_eu,
            9: art_uk, 10: art_gaza, 11: art_jeffries}


def draw_cards(d):
    xs = [24, 271, 518, 765]
    cw = 235
    rows = [347, 513]
    for ri, ry in enumerate(rows):
        for ci, card in enumerate(CARDS[ri * 4:(ri + 1) * 4]):
            cx = xs[ci]
            CARD_ART[card["num"]](d, cx, ry, cw, 80)
            badge(d, cx + 13, ry + 13, card["num"], REG[card["region"]], r=11)
            ctext, cfill = card["chip"]
            cw_chip = int(math.ceil(tw(dj(10, bold=True), ctext))) + 14
            chip(d, cx + cw - cw_chip - 6, ry + 6, ctext, cfill)
            kf = dj(10, bold=True)
            label_fit(kf, card["kicker"], cw, f"card {card['num']} kicker")
            d.ellipse([cx, ry + 87, cx + 7, ry + 94], fill=REG[card["region"]])
            d.text((cx + 11, ry + 84), card["kicker"], font=kf, fill=INK)
            hf = pf(16, 700)
            lines = wrap(card["head"], hf, cw)
            assert len(lines) <= 2, f"card {card['num']} headline wraps to {len(lines)}"
            hy = ry + 100
            for ln in lines:
                d.text((cx, hy), ln, font=hf, fill=INK)
                hy += 17
            df = dj(12)
            dlines = wrap(card["deck"], df, cw)
            assert len(dlines) <= 2, f"card {card['num']} deck wraps to {len(dlines)}: {dlines}"
            dy = ry + 136
            for ln in dlines:
                d.text((cx, dy), ln, font=df, fill=INK)
                dy += 12
    return 673

# ---------------------------------------------------------------- map
MAP_X0, MAP_X1, MAP_Y0, MAP_Y1 = 24, 384, 694, 850


def proj(lon, lat):
    x = MAP_X0 + (lon + 180.0)
    y = MAP_Y0 + (84.0 - lat) * (MAP_Y1 - MAP_Y0) / 142.0
    return x, y


def inside(lon, lat, poly):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xin = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xin:
                ins = not ins
        j = i
    return ins


# pins: (num, region, disp lon/lat, true lon/lat) — display may be offset with
# a leader line where the true spot is too crowded (London/Brussels, DC x2,
# Gaza/Gulf, Manila/Shenzhen).
PINS = [
    (1, "me", 48, 26, 48, 26),
    (2, "apac", 114, 22, 114, 22),
    (4, "eu", 32, 49, 32, 49),
    (5, "am", -86, 42, -77, 39),
    (6, "apac", 86, 20, 86, 20),
    (7, "af", 30, 8, 30, 13),
    (8, "eu", 4.4, 50.8, 4.4, 50.8),
    (9, "eu", -16, 58, -0.1, 51.5),
    (10, "me", 28, 30, 34.5, 31.5),
    (11, "am", -66, 37, -77, 39),
    (12, "apac", 130, 10, 121, 14.6),
    (13, "am", -122.4, 37.8, -122.4, 37.8),
]

# dots: (num, region, lon, lat) — story 3 (Voyager) has no Earth spot; it is
# annotated at the map's bottom-right corner instead, as in the #1 reference.
DOTS = [
    (14, "apac", 122, 11), (15, "apac", 134, -25), (16, "global", -74, 40.7),
    (17, "af", 35, -19), (18, "eu", 21, 44), (19, "apac", -166, -11),
    (20, "apac", 108, 16), (21, "am", -122, 37), (22, "apac", 114, 22.5),
    (23, "eu", 4.3, 52.1), (24, "am", -121, 37.5), (25, "am", -84.4, 33.7),
    (26, "am", -122.4, 37.8), (27, "me", 45, 15), (28, "eu", 87, 55.4),
    (29, "me", 35.2, 31.8), (30, "am", -75.7, 45.4), (31, "am", -77, 39),
    (32, "apac", 112, 24), (33, "af", 37, -1), (34, "me", 45, 12.8),
    (35, "apac", 174, -41), (36, "af", 23, -3), (37, "apac", 90.4, 23.8),
    (38, "apac", 80.3, 13.1),
]

NUDGES = [(10, 0), (-10, 0), (0, 10), (0, -10), (12, 8), (-12, -8), (14, -6),
          (-14, 6), (8, 12), (-8, -12), (16, 0), (-16, 0), (0, 16), (0, -16),
          (18, 8), (-18, -8), (20, -10), (-20, 10)]


def draw_map(d):
    # dotted halftone continents
    lon = -178.0
    while lon <= 178.0:
        lat = 82.0
        while lat >= -56.0:
            if any(inside(lon, lat, p) for p in POLYS):
                x, y = proj(lon, lat)
                d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=MAP_DOT)
            lat -= 4.5
        lon += 5.0
    # pins (drawn LAST, over the dots)
    pin_xy = {}
    for num, region, dlon, dlat, tlon, tlat in PINS:
        x, y = proj(dlon, dlat)
        pin_xy[num] = (x, y)
        if (dlon, dlat) != (tlon, tlat):
            tx, ty = proj(tlon, tlat)
            d.line([x, y, tx, ty], fill=(120, 120, 120), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=REG[region])
        d.ellipse([x - 10.5, y - 10.5, x + 10.5, y + 10.5], fill=REG[region],
                  outline=(255, 255, 255), width=2)
        d.text((x, y), str(num), font=dj(11, bold=True), fill=(255, 255, 255), anchor="mm")
    # pin min distance (assert + report)
    nums = sorted(pin_xy)
    pin_min = 999.0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            a, b = pin_xy[nums[i]], pin_xy[nums[j]]
            pin_min = min(pin_min, math.hypot(a[0] - b[0], a[1] - b[1]))
    assert pin_min >= 20.0, f"pin min distance {pin_min:.1f} < 20"
    # dots with deterministic collision nudging
    placed = []
    dot_min_pin, dot_min_dot = 999.0, 999.0
    for num, region, lon, lat in DOTS:
        x, y = proj(lon, lat)
        for dx, dy in [(0, 0)] + NUDGES:
            cx, cy = x + dx, y + dy
            if not (MAP_X0 + 4 <= cx <= MAP_X1 - 4 and MAP_Y0 + 4 <= cy <= MAP_Y1 - 4):
                continue
            ok = all(math.hypot(cx - px, cy - py) >= 15 for px, py in pin_xy.values())
            ok = ok and all(math.hypot(cx - px, cy - py) >= 8 for px, py in placed)
            if ok:
                x, y = cx, cy
                break
        else:
            raise AssertionError(f"dot {num} could not be placed without collision")
        for px, py in pin_xy.values():
            dot_min_pin = min(dot_min_pin, math.hypot(x - px, y - py))
        for px, py in placed:
            dot_min_dot = min(dot_min_dot, math.hypot(x - px, y - py))
        placed.append((x, y))
        d.ellipse([x - 3.5, y - 3.5, x + 3.5, y + 3.5], fill=REG[region],
                  outline=(255, 255, 255), width=1)
    # Voyager annotation (story 3 has no Earth location)
    d.text((288, 836), "3 → VOYAGER 1", font=dj(9, bold=True), fill=REG["space"])
    return pin_min, dot_min_pin, dot_min_dot


# ---------------------------------------------------------------- lower half
def draw_lower(d):
    # section labels + hairline
    lab = dj(11, bold=True)
    d.text((24, 678), "WHERE IT HAPPENED", font=lab, fill=INK)
    d.text((396, 678), "ALSO ON WEDNESDAY 18 NOVEMBER", font=lab, fill=INK)
    d.line([24, 692, 1000, 692], fill=HAIR, width=1)
    pin_min, dot_min_pin, dot_min_dot = draw_map(d)
    # 4 big numbers, 2x2, below the map
    d.line([24, 852, 384, 852], fill=HAIR, width=1)
    d.line([24, 906, 384, 906], fill=HAIR, width=1)
    cells = [(24, 856), (204, 856), (24, 909), (204, 909)]
    for (val, lab_txt), (cx, cy) in zip(BIG, cells):
        nf = pf(28, 700)
        label_fit(nf, val, 180, f"big number {val!r}")
        d.text((cx, cy), val, font=nf, fill=INK)
        d.text((cx, cy + 34), lab_txt, font=dj(9, bold=True), fill=GRAY)
    # briefs, 2 columns, 13px (15px does not fit the specified texts in a
    # 288px column — measured; 13px is still larger than #1's ~11px briefs)
    bf, bfb = dj(13), dj(13, bold=True)
    cols = [(396, BRIEFS[:14]), (712, BRIEFS[14:])]
    for col_x, items in cols:
        by = 694
        for num, region, prefix, rest in items:
            ntxt = f"{num}. "
            wtot = (tw(bfb, ntxt) + tw(bfb, prefix + " ") + tw(bf, rest))
            assert wtot <= 288, f"brief {num} too wide: {wtot:.1f}"
            x = col_x
            d.text((x, by), ntxt, font=bfb, fill=REG[region])
            x += tw(bfb, ntxt)
            d.text((x, by), prefix + " ", font=bfb, fill=INK)
            x += tw(bfb, prefix + " ")
            d.text((x, by), rest, font=bf, fill=INK)
            by += 19
    # DATE CHECK: red left bar + tinted box, 2 lines
    d.rectangle([24, 968, 1000, 994], fill=(250, 240, 235))
    d.rectangle([24, 968, 28, 994], fill=RED)
    bold_pre = "DATE CHECK — "
    b11, r11 = dj(11, bold=True), dj(11)
    rest = DATE_CHECK[len(bold_pre):]
    first_w = 996 - 36 - tw(b11, bold_pre)
    lines = wrap(rest, r11, first_w)
    assert len(lines) <= 2, f"DATE CHECK wraps to {len(lines)}"
    d.text((36, 970), bold_pre, font=b11, fill=RED)
    x = 36 + tw(b11, bold_pre)
    d.text((x, 970), lines[0], font=r11, fill=INK)
    if len(lines) > 1:
        d.text((36, 983), lines[1], font=r11, fill=INK)
    # footer, single line 9px
    f9 = dj(9)
    left = ("All 38 stories happened, or were first reported, on Wednesday 18 November "
            "2026. Original drawings.")
    right = "Sources: AP · Reuters · AFP · BBC · CNN · CNBC · NPR · ONS · IMD · NASA · Amnesty"
    assert tw(f9, left) + tw(f9, right) <= 976 - 24, "footer too wide"
    d.text((24, 998), left, font=f9, fill=GRAY)
    d.text((1000, 998), right, font=f9, fill=GRAY, anchor="ra")
    return pin_min, dot_min_pin, dot_min_dot


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_veracity(d)
    leads_end = draw_leads(d)
    cards_end = draw_cards(d)
    pin_min, dot_min_pin, dot_min_dot = draw_lower(d)
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG")
    import hashlib
    data = open(out, "rb").read()
    print(f"entry.png: {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
    print(f"leads_end={leads_end} cards_end={cards_end} max_y=1010")
    print(f"pin_min={pin_min:.1f}px dot_min_pin={dot_min_pin:.1f}px "
          f"dot_min_dot={dot_min_dot:.1f}px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
