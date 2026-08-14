# 🛸 SIMULATOR DRONE MANGKRAK 3D (V2)

**Pembuat Utama (Lead Creator & Developer):** **Ilham Purnomo**  
Aplikasi simulator penerbangan quadcopter 3D interaktif berbasis **Python** dan **PySide6 QPainter** yang mendukung koneksi transmitter remote control fisik via Serial (Arduino / ESP32).

---

## 👤 Pembuat Utama & Kredit Proyek

- **Pembuat Utama (Original Creator & Lead Developer)**: **Ilham Purnomo**  
  Merancang, membuat, dan mengonsep arsitektur dasar simulator drone serta sistem komunikasi transmisi remote control fisik.

---

## 📋 Fitur Utama Perangkat Lunak

- **Engine Rendering 3D Faceted**: Model quadcopter 3D polyhedral, directional sunlighting (Lambertian shading), & depth sorting tanpa dependensi library 3D eksternal (Pure PySide6 Vector Graphics).
- **Sistem Multi-Kamera 3D**: Mode `CHASE` (kamera sinematik), `ORBIT` (free look drag mouse 360°), `FPV` (cockpit moncong drone), dan `TOP-DOWN` (taktis overhead).
- **Arena Rintangan 3D (Flight Arena Props)**:
  - 3D Neon Racing Gates dengan sensor *gate pass detection*.
  - Platform helipad bertingkat `P1` (+3m) & `P2` (+5.5m) untuk latihan pendaratan presisi.
  - Penanda koordinat `HOME (0,0)`.
- **FPV Betaflight Style OSD & Scanlines**: Interface FPV OSD dengan crosshair reticle, telemetri hijau neon, dan opsi efek *scanline video noise*.
- **2D Mini-Map Radar Overlay**: Radar bundar taktis 35m di pojok layar yang menampilkan posisi drone, heading, helipad, dan racing gates secara real-time.
- **Visual Environment & Efek Partikel**: Efek debu tanah (*ground particle wash*), bayangan lembut dinamis (*dynamic soft shadow*), riakan angin baling-baling (*prop wash ripple*), dan *3D flight trail fade*.
- **Cyber-Dark QSS Theme**: Antarmuka visual gelap futuristik ber-accent cyan neon.

---

## 🛠️ Arsitektur Perangkat Lunak

| Module | Peran & Deskripsi |
|--------|-------------------|
| `main.py` | Entry point utama aplikasi |
| `main_window.py` | Window GUI PySide6, pengatur layout, telemetry panel, & event hotkey handler |
| `widgets.py` | Engine visual 3D (`SimView`), kamera, lighting, particle dust, FPV OSD, & 2D Radar |
| `drone_model.py` | Simulasi fisika drone, Altitude Hold, tilt angles, drag velocity, & battery system |
| `serial_reader.py` | Asynchronous QThread parsing data serial RC 4-channel (Baud 115200) |
| `style.py` | Stylesheet Cyber-Dark QSS modern dengan aksen cyan neon |

---

## 🔌 Spesifikasi Hardware & Remote Serial

Simulator terhubung ke Remote Controller kustom (ESP32 / Arduino / Joystick Test) melalui koneksi Serial:
- **Baud Rate**: `115200`
- **Format Data**: `CH1:<roll>,CH2:<throttle>,CH3:<yaw>,CH4:<pitch>`
- **Skema Channel (Joystick Mode 2)**:
  - `CH1`: Roll (0 - 255) $\rightarrow$ Kemiringan Kiri/Kanan
  - `CH2`: Throttle (0 - 255) $\rightarrow$ Kecepatan Vertikal Naik/Turun
  - `CH3`: Yaw (0 - 255) $\rightarrow$ Rotasi Putar Arah Hadap
  - `CH4`: Pitch (0 - 255) $\rightarrow$ Kemiringan Maju/Mundur

---

## 🚀 Panduan Instalasi & Jalankan

### 1. Prasyarat
Pastikan Python 3.10+ sudah terinstal pada sistem Anda.

### 2. Instalasi Dependensi
```powershell
pip install -r requirements.txt
```

### 3. Menjalankan Simulator
```powershell
python main.py
```

---

## ⌨️ Daftar Hotkeys & Kontrol

| Tombol Pintas | Fungsi |
|---------------|--------|
| **`SPASI`** | ARM / DISARM Drone |
| **`C`** | Ganti Mode Kamera (`CHASE` $\rightarrow$ `ORBIT` $\rightarrow$ `FPV` $\rightarrow$ `TOP-DOWN`) |
| **`M`** | Toggle Mini-Map Radar 2D (On / Off) |
| **`H`** | Toggle Tampilan HUD (On / Off) |
| **`O`** | Toggle FPV Scanlines Video Noise |
| **`Left Drag Mouse`** | Rotasi Orbit Kamera 360° |
| **`Scroll Wheel`** | Zoom In / Zoom Out Kamera |
| **`R`** | Reset drone ke koordinat HOME (0,0,0) |
| **`ESC`** | Keluar dari aplikasi |
