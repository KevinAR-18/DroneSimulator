"""Stylesheet Qt untuk panel kontrol.

Semua warna berasal dari theme.py — jangan menulis literal hex di sini.
Ciri tema: permukaan bertingkat (bukan hampir hitam), aksen teal saturasi
rendah, tanpa gradien tajam, dan focus ring agar navigasi keyboard terlihat.
"""

import theme as T


def _channel_bar_rules():
    """Fill progress bar 4 channel: satu keluarga teal -> sage."""
    rules = []
    for name, rgb in T.CH_COLORS.items():
        rules.append(
            "QProgressBar#%s::chunk { background: %s; }" % (name, T._hex(rgb))
        )
    return "\n".join(rules)


APP_STYLESHEET = """
* {{
    font-family: "Segoe UI", "Inter", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}}
QMainWindow, QWidget#central {{
    background: {surface0};
}}
QWidget#sidePanel {{
    background: {surface0};
}}
QScrollArea#sideScroll {{
    background: {surface0};
    border: none;
}}

/* ---------------------------------------------------------- group boxes */
QGroupBox {{
    background: {surface1};
    border: 1px solid {border_soft};
    border-radius: 9px;
    margin-top: 13px;
    padding: 11px 9px 9px 9px;
    font-weight: 600;
    color: {text};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 11px;
    padding: 2px 8px;
    color: {text_dim};
    background: {surface1};
    border: 1px solid {border_soft};
    border-radius: 5px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel {{
    color: {text};
    background: transparent;
}}
QLabel#fieldLabel {{
    color: {text_dim};
}}

/* -------------------------------------------------------------- buttons */
QPushButton {{
    background: {surface2};
    color: {text};
    border: 1px solid {border};
    border-radius: 7px;
    padding: 7px 10px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {surface3};
    border-color: {accent_dim};
}}
QPushButton:pressed {{
    background: {surface1};
}}
QPushButton:focus {{
    border: 1px solid {accent};
    outline: none;
}}
QPushButton:disabled {{
    color: {text_faint};
    background: {surface1};
    border-color: {border_soft};
}}
/* Tombol toggle sempit yang berbagi satu baris (Tema/Lampu/Radar) */
QPushButton#compactBtn {{
    padding: 7px 4px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton#connectBtn {{
    background: {accent_dim};
    border: 1px solid {accent};
    color: {text_strong};
}}
QPushButton#connectBtn:hover {{
    background: {accent};
    border-color: {accent};
    color: {surface0};
}}
QPushButton#connectBtn:pressed {{
    background: {accent_dim};
}}

QPushButton#armBtn {{
    font-size: 13px;
    letter-spacing: 0.4px;
}}
QPushButton#armBtn[armed="true"] {{
    background: {ok_dim};
    border: 1px solid {ok};
    color: {text_strong};
}}
QPushButton#armBtn[armed="true"]:hover {{
    background: {ok};
    color: {surface0};
}}
QPushButton#armBtn[armed="false"] {{
    background: {danger_dim};
    border: 1px solid {danger};
    color: {text_strong};
}}
QPushButton#armBtn[armed="false"]:hover {{
    background: {danger};
    color: {surface0};
}}

/* ------------------------------------------------------------- combobox */
QComboBox {{
    background: {surface2};
    color: {text};
    border: 1px solid {border};
    border-radius: 7px;
    padding: 5px 10px;
}}
QComboBox:hover {{
    border-color: {accent_dim};
}}
QComboBox:focus {{
    border-color: {accent};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {text_dim};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {surface1};
    color: {text};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 4px;
    selection-background-color: {accent_dim};
    selection-color: {text_strong};
    outline: none;
}}

/* --------------------------------------------------------- progress bar */
QProgressBar {{
    background: {surface0};
    border: 1px solid {border_soft};
    border-radius: 5px;
    min-height: 10px;
    max-height: 12px;
    text-align: center;
}}
QProgressBar::chunk {{
    border-radius: 4px;
    margin: 0px;
}}
{channel_bars}

/* ------------------------------------------------------------- checkbox */
QCheckBox {{
    color: {text_dim};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {border};
    border-radius: 4px;
    background: {surface2};
}}
QCheckBox::indicator:hover {{
    border-color: {accent_dim};
}}
QCheckBox::indicator:checked {{
    background: {accent_dim};
    border-color: {accent};
}}
QCheckBox:focus {{
    color: {text};
}}

/* ------------------------------------------------------------------ log */
QTextEdit {{
    background: {surface0};
    color: {log_text};
    border: 1px solid {border_soft};
    border-radius: 7px;
    padding: 6px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px;
    selection-background-color: {accent_dim};
    selection-color: {text_strong};
}}

/* ------------------------------------------------------- teks bernilai  */
QLabel#telValue {{
    font-family: Consolas, "Courier New", monospace;
    font-size: 13px;
    font-weight: 700;
    color: {accent};
}}
QLabel#appTitle {{
    font-size: 16px;
    font-weight: 700;
    color: {text_strong};
    letter-spacing: 0.3px;
}}
QLabel#appSub {{
    font-size: 11px;
    color: {text_faint};
}}
QLabel#helpText {{
    color: {text_dim};
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px;
}}

QLabel#statusDot[state="online"] {{
    color: {ok};
    font-weight: bold;
}}
QLabel#statusDot[state="offline"] {{
    color: {danger};
    font-weight: bold;
}}

QFrame#divider {{
    background: {border_soft};
    max-height: 1px;
    border: none;
}}

/* ----------------------------------------------------------- scroll bar */
QScrollBar:vertical {{
    background: transparent;
    width: 9px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {accent_dim};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ---------------------------------------------------------- status bar  */
QStatusBar {{
    background: {surface0};
    color: {text_dim};
    border-top: 1px solid {border_soft};
}}
QStatusBar::item {{
    border: none;
}}

QToolTip {{
    background: {surface2};
    color: {text};
    border: 1px solid {border};
    border-radius: 5px;
    padding: 4px 7px;
}}
""".format(
    surface0=T.H_SURFACE_0,
    surface1=T.H_SURFACE_1,
    surface2=T.H_SURFACE_2,
    surface3=T.H_SURFACE_3,
    border=T.H_BORDER,
    border_soft=T.H_BORDER_SOFT,
    text=T.H_TEXT,
    text_strong=T.H_TEXT_STRONG,
    text_dim=T.H_TEXT_DIM,
    text_faint=T.H_TEXT_FAINT,
    accent=T.H_ACCENT,
    accent_dim=T.H_ACCENT_DIM,
    ok=T.H_OK,
    ok_dim=T._hex(T.OK_DIM),
    danger=T.H_DANGER,
    danger_dim=T._hex(T.DANGER_DIM),
    log_text=T._hex(T.LOG_TEXT),
    channel_bars=_channel_bar_rules(),
)
