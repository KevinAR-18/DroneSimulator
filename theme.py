"""Sumber tunggal warna untuk seluruh aplikasi.

Palet "Slate Gelap Lembut": dark mode dengan kontras dijaga di rentang
6-9:1 (nyaman dipandang lama, tetap memenuhi WCAG AA) alih-alih 14-16:1
seperti tema neon sebelumnya. Semua aksen berada di saturasi rendah.

Dipakai oleh:
  - style.py    -> stylesheet Qt (panel, tombol, input)
  - widgets.py  -> renderer 3D QPainter (HUD, lingkungan, drone)

Aturan: jangan menulis literal warna di file lain. Tambahkan token di sini.
"""

from PySide6.QtGui import QColor


# --------------------------------------------------------------- helpers
def _hex(rgb):
    """(r, g, b) -> '#rrggbb'"""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def qc(rgb, alpha=255):
    """(r, g, b) -> QColor, dengan alpha opsional."""
    return QColor(rgb[0], rgb[1], rgb[2], alpha)


def _relative_luminance(rgb):
    """Luminansi relatif WCAG 2.1."""
    channels = []
    for v in rgb:
        c = v / 255.0
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    """Rasio kontras WCAG antara dua tuple RGB. Dipakai untuk verifikasi."""
    l1 = _relative_luminance(fg)
    l2 = _relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ------------------------------------------------------- palet inti (RGB)
# Permukaan: naik bertahap dari window ke elemen interaktif.
SURFACE_0 = (27, 31, 39)     # #1b1f27  window / status bar
SURFACE_1 = (34, 39, 47)     # #22272f  groupbox / kartu
SURFACE_2 = (42, 47, 57)     # #2a2f39  input, tombol netral
SURFACE_3 = (52, 58, 69)     # #343a45  hover
BORDER = (52, 58, 69)        # #343a45  garis pemisah
BORDER_SOFT = (44, 49, 59)   # #2c313b  garis lebih halus

# Teks — target 7-8.5:1, bukan 12-17:1 seperti sebelumnya.
TEXT = (186, 194, 205)       # #babecd  utama      8.35:1 di SURFACE_1
TEXT_STRONG = (190, 197, 207)  # #bec5cf judul; luminansi ditahan <200
TEXT_DIM = (136, 146, 160)   # #8892a0  sekunder   4.76:1
TEXT_FAINT = (124, 133, 146)  # #7c8592 keterangan  4.5:1

# Aksen — teal redup sebagai aksen utama, oranye sebagai sekunder.
# Semua melewati WCAG AA (>= 4.5:1) tanpa menjadi neon.
ACCENT = (96, 170, 186)      # #60aaba  saturasi 32% (dulu #00e5ff, 100%)
ACCENT_DIM = (68, 126, 140)  # #447e8c
ACCENT_2 = (192, 138, 78)    # #c08a4e  oranye redup   4.99:1
ACCENT_2_DIM = (150, 108, 62)  # #966c3e

# Status
OK = (104, 172, 136)         # #68ac88  5.61:1
WARN = (196, 146, 78)        # #c4924e  5.41:1
DANGER = (202, 118, 118)     # #ca7676  4.55:1
IDLE = (112, 122, 136)       # #707a88

# Varian redup untuk latar tombol (teks terang di atasnya).
OK_DIM = (58, 104, 82)       # #3a6852
DANGER_DIM = (124, 68, 68)   # #7c4444

# Log: monospace redup, tidak biru terang seperti sebelumnya (#7dd3fc).
LOG_TEXT = (150, 164, 168)   # #96a4a8

# Channel bar: satu keluarga teal -> sage. Cukup beda untuk dibaca sekilas,
# tapi tidak terbaca sebagai pelangi seperti cyan/hijau/amber/violet.
CH_COLORS = {
    "ch1": (78, 138, 154),   # #4e8a9a  ROLL      teal
    "ch2": (91, 158, 138),   # #5b9e8a  THROTTLE  teal-sage
    "ch3": (106, 154, 134),  # #6a9a86  YAW       sage
    "ch4": (125, 154, 122),  # #7d9a7a  PITCH     sage-hijau
}

# Hex siap pakai untuk QSS.
H_SURFACE_0 = _hex(SURFACE_0)
H_SURFACE_1 = _hex(SURFACE_1)
H_SURFACE_2 = _hex(SURFACE_2)
H_SURFACE_3 = _hex(SURFACE_3)
H_BORDER = _hex(BORDER)
H_BORDER_SOFT = _hex(BORDER_SOFT)
H_TEXT = _hex(TEXT)
H_TEXT_STRONG = _hex(TEXT_STRONG)
H_TEXT_DIM = _hex(TEXT_DIM)
H_TEXT_FAINT = _hex(TEXT_FAINT)
H_ACCENT = _hex(ACCENT)
H_ACCENT_DIM = _hex(ACCENT_DIM)
H_ACCENT_2 = _hex(ACCENT_2)
H_OK = _hex(OK)
H_WARN = _hex(WARN)
H_DANGER = _hex(DANGER)
H_IDLE = _hex(IDLE)


# ------------------------------------------------ token QColor renderer 3D
# Material drone (matte, tanpa highlight tajam)
COLOR_HULL = QColor(48, 52, 60)
COLOR_CARBON = QColor(36, 40, 46)
COLOR_GUNMETAL = QColor(68, 74, 84)
COLOR_NOSE = QColor(88, 97, 109)
COLOR_ACCENT_ORANGE = qc(ACCENT_2)
COLOR_ACCENT_CYAN = qc(ACCENT)

# HUD
COLOR_HUD_TEXT = qc(TEXT, 225)
COLOR_HUD_TEXT_DIM = qc(TEXT_DIM, 205)
COLOR_HUD_LINE = qc((192, 200, 210), 165)   # tick kompas / horizon (dulu putih murni)
COLOR_HUD_PANEL = QColor(24, 28, 36, 118)   # isi panel glass (dulu alpha 140)
COLOR_HUD_PANEL_EDGE = qc(ACCENT, 28)       # garis panel (dulu alpha 40)
COLOR_HUD_PANEL_EDGE_STRONG = qc(ACCENT, 58)  # ring radar
COLOR_OK = qc(OK)
COLOR_WARN = qc(WARN)
COLOR_DANGER = qc(DANGER)
COLOR_IDLE = qc(IDLE)

# Lampu & efek
COLOR_LED = QColor(210, 216, 224)           # LED aktif (dulu 255,255,255)
COLOR_LED_NAV_GREEN = QColor(96, 168, 118)
COLOR_LED_NAV_RED = QColor(178, 88, 88)
COLOR_LED_OFF = QColor(70, 75, 85)
COLOR_SPOTLIGHT = QColor(250, 244, 214)     # pool lampu sorot
SPOTLIGHT_ALPHA = 62                        # dulu 90
COLOR_ROTOR_BLUR = QColor(206, 214, 224)
COLOR_DUST = QColor(160, 155, 140)
COLOR_STAR = QColor(196, 210, 228)

# Props dunia
COLOR_GATE_OPEN = QColor(168, 106, 128)     # dulu magenta (220, 60, 140)
COLOR_GATE_PASSED = QColor(106, 154, 128)
COLOR_STRUCT = QColor(62, 69, 80)           # kaki helipad / tiang gate
COLOR_TOWER = QColor(138, 148, 160)
COLOR_TURBINE_BLADE = QColor(178, 188, 198)
COLOR_TRUNK = QColor(65, 48, 35)
COLOR_FOLIAGE_LOW = QColor(42, 74, 52)
COLOR_FOLIAGE_HIGH = QColor(52, 96, 66)
COLOR_FACET_EDGE = QColor(20, 24, 30, 100)
COLOR_PAD_FILL = QColor(28, 32, 40, 175)    # isi helipad HOME
COLOR_PAD_FILL_HIGH = QColor(32, 38, 46, 190)  # isi helipad elevasi

# Attitude indicator: biru & hijau diredam supaya dua blok besar ini tidak
# menjadi elemen paling terang di layar.
COLOR_AI_SKY = QColor(62, 96, 134, 155)
COLOR_AI_GROUND = QColor(50, 74, 54, 155)
COLOR_AI_EDGE = QColor(70, 75, 85, 190)
COLOR_HUD_TRACK = QColor(45, 55, 70)        # jalur kosong bar sinyal
COLOR_HUD_WELL = QColor(26, 34, 46)         # isi kosong ikon baterai
COLOR_OUTLINE = QColor(20, 22, 28)          # garis tepi ikon

# ------------------------------------------------------ tema lingkungan 3D
# Sebelumnya SUNSET & NIGHT hardcoded di dalam _draw_environment/_draw_grid
# sehingga tidak bisa diubah tanpa mengedit isi fungsi. Sekarang satu tabel.
THEMES = {
    "DAY": {
        # Langit siang diredam: sky_bottom dulu (165,195,225) — di mode FPV
        # langit mengisi hampir seluruh layar sehingga jadi sumber cahaya
        # terbesar. Sekarang lebih ke arah biru-abu berkabut.
        "sky_top": QColor(70, 98, 128),
        "sky_bottom": QColor(134, 158, 182),
        "ground_top": QColor(50, 70, 54),
        "ground_bottom": QColor(28, 40, 30),
        "grid": QColor(80, 112, 88, 48),
        "grid_major": QColor(98, 140, 110, 74),
        "border": qc(ACCENT, 120),
    },
    "SUNSET": {
        "sky_top": QColor(56, 42, 66),
        "sky_bottom": QColor(168, 118, 92),
        "ground_top": QColor(52, 44, 38),
        "ground_bottom": QColor(26, 22, 20),
        "grid": QColor(112, 88, 72, 48),
        "grid_major": QColor(156, 106, 68, 62),
        "border": qc(ACCENT_2, 120),
    },
    "NIGHT": {
        "sky_top": QColor(16, 20, 29),
        "sky_bottom": QColor(30, 38, 52),
        "ground_top": QColor(20, 26, 24),
        "ground_bottom": QColor(12, 16, 14),
        "grid": QColor(46, 66, 60, 42),
        "grid_major": QColor(60, 88, 82, 58),
        "border": qc(ACCENT_DIM, 110),
    },
}


def theme(name):
    """Ambil dict tema, jatuh ke DAY kalau nama tidak dikenal."""
    return THEMES.get(name, THEMES["DAY"])


# --------------------------------------------------------- model pencahayaan
# Ambient dinaikkan sementara diffuse & specular diturunkan: rentang
# gelap-terang antar permukaan menyempit (kontras turun) tanpa membuat
# model drone jadi gelap secara keseluruhan.
LIGHT_DIR = (0.45, -0.35, 0.85)
LIGHT_AMBIENT = 0.56      # dulu 0.50
LIGHT_DIFFUSE = 0.42      # dulu 0.50
LIGHT_SPECULAR = 0.22     # dulu 0.35
LIGHT_SPECULAR_POWER = 16  # dulu 14, sorot lebih kecil & tidak menyilaukan
