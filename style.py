APP_STYLESHEET = """
* {
    font-family: "Segoe UI", "Inter", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}
QMainWindow {
    background: #0d1017;
}
QWidget#central {
    background: #0d1017;
}
QGroupBox {
    background: #151922;
    border: 1px solid #252d3c;
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 10px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 3px 10px;
    color: #00e5ff;
    background: #1a202c;
    border: 1px solid #00e5ff44;
    border-radius: 5px;
}
QLabel {
    color: #c5d1e0;
    background: transparent;
}
QPushButton {
    background: #1f2633;
    color: #e6f0ff;
    border: 1px solid #323d52;
    border-radius: 7px;
    padding: 7px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background: #283244;
    border-color: #00e5ffaa;
    color: #ffffff;
}
QPushButton:pressed {
    background: #171d28;
}
QPushButton:disabled {
    color: #525d70;
    background: #181d26;
    border-color: #222936;
}
QPushButton#connectBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0088cc, stop:1 #005580);
    border: 1px solid #00b0ff;
    color: #ffffff;
}
QPushButton#connectBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00a0e6, stop:1 #006699);
    border-color: #80d8ff;
}
QPushButton#armBtn[armed="true"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #047857);
    border: 1px solid #34d399;
    color: #ffffff;
}
QPushButton#armBtn[armed="false"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #b91c1c);
    border: 1px solid #f87171;
    color: #ffffff;
}
QComboBox {
    background: #1c2330;
    color: #e6f0ff;
    border: 1px solid #323d52;
    border-radius: 7px;
    padding: 5px 10px;
}
QComboBox:hover {
    border-color: #00e5ff88;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #00e5ff;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background: #181f2b;
    color: #e6f0ff;
    border: 1px solid #00e5ff44;
    selection-background-color: #0088cc;
    selection-color: #ffffff;
}
QProgressBar {
    background: #181f2b;
    border: 1px solid #2a3547;
    border-radius: 5px;
    min-height: 10px;
    max-height: 12px;
    text-align: center;
}
QProgressBar::chunk {
    border-radius: 4px;
}
QProgressBar#ch1::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06b6d4, stop:1 #22d3ee);
}
QProgressBar#ch2::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #34d399);
}
QProgressBar#ch3::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #fbbf24);
}
QProgressBar#ch4::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #a78bfa);
}
QCheckBox {
    color: #c5d1e0;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #3a475c;
    border-radius: 4px;
    background: #181f2b;
}
QCheckBox::indicator:hover {
    border-color: #00e5ff;
}
QCheckBox::indicator:checked {
    background: #0088cc;
    border-color: #00e5ff;
}
QTextEdit {
    background: #090c12;
    color: #7dd3fc;
    border: 1px solid #222c3d;
    border-radius: 7px;
    padding: 6px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px;
    selection-background-color: #0088cc;
}
QLabel#telValue {
    font-family: Consolas, "Courier New", monospace;
    font-size: 13px;
    font-weight: 700;
    color: #38bdf8;
}
QLabel#appTitle {
    font-size: 18px;
    font-weight: 800;
    color: #f0f6ff;
    letter-spacing: 0.5px;
}
QLabel#appSub {
    font-size: 11px;
    color: #64748b;
}
QScrollBar:vertical {
    background: #121620;
    width: 9px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a3547;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #00e5ffaa;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
QStatusBar {
    background: #0d1017;
    color: #64748b;
}
QStatusBar::item {
    border: none;
}
"""
