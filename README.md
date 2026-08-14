# 🛸 SIMULATOR DRONE MANGKRAK 3D (V3)

**Pembuat Utama (Lead Creator & Developer):** **Ilham Purnomo**  
Aplikasi simulator penerbangan quadcopter 3D interaktif berbasis **Python** dan **PySide6 QPainter** yang mendukung koneksi transmitter remote control fisik via Serial (Arduino / ESP32).

---

## 👤 Pembuat Utama & Kredit Proyek

- **Pembuat Utama (Original Creator & Lead Developer)**: **Ilham Purnomo**  
  Merancang, membuat, dan mengonsep arsitektur dasar simulator drone serta sistem komunikasi transmisi remote control fisik.

---

## 📋 Fitur Unggulan Perangkat Lunak (Versi 3)

- **Engine Rendering 3D Faceted**: Model quadcopter 3D Dark Carbon FPV, directional sunlighting (Lambertian + Specular shading), 4 landing skids, serta depth sorting tanpa dependensi library 3D eksternal (Pure PySide6 Vector Graphics).
- **Siklus Tema Waktu (Day / Sunset / Night Cyberpunk)**:
  - *Day*: Siang cerah dengan awan bergerak (*procedural clouds*).
  - *Sunset*: Nuansa senja emas (*golden hour*) dengan cahaya matahari hangat.
  - *Night*: Malam berbintang dengan lampu neon menyala kontras tinggi.
  - *Hotkey*: Tekan **`T`** untuk mengganti tema.
- **3D Drone Spotlight / Searchlight**: Sorot lampu 3D memancar dari moncong kamera drone ke tanah (*illuminated ground light pool*). Tekan **`L`** untuk toggle on/off.
- **Objek Lingkungan 3D**: Pohon pinus 3D *low-poly* dan kincir angin 3D (*wind turbine*) berputar di kejauhan.
- **Sistem Multi-Kamera 3D**: Mode `CHASE` (kamera kejar halus), `ORBIT` (free look 360° dengan *inertia damping*), `FPV` (cockpit moncong drone + vignette), dan `TOP-DOWN` (taktis overhead). Tekan **`C`** untuk mengganti mode.
- **Dynamic Speed Lines & Alerts**: Efek garis akselerasi (*speed lines*) saat kecepatan tinggi ($> 6.5\text{m/s}$), denyut merah low-battery alert, dan peringatan *pull up*.
- **Mini Telemetry Sparkline Graph**: Grafik strip mini real-time di HUD yang memplot ketinggian (*altitude*) dan kecepatan (*speed*).
- **2D Mini-Map Radar Overlay**: Radar bundar taktis 35m di pojok layar yang menampilkan posisi drone, heading, helipad, dan racing gates secara real-time. Tekan **`M`** untuk toggle.
- **FPV Betaflight Style OSD**: Interface FPV OSD dengan crosshair reticle, telemetri hijau neon, dan opsi scanline video noise (Tekan **`O`**).

---

## 🛠️ Arsitektur Perangkat Lunak

| Module | Peran & Deskripsi |
|--------|-------------------|
| `main.py` | Entry point utama aplikasi |
| `main_window.py` | Window GUI PySide6, pengatur layout, telemetry panel, & event hotkey handler |
| `widgets.py` | Engine visual 3D (`SimView`), tema lingkungan, kamera, lighting, spotlight, props 3D, FPV OSD, & Radar |
| `drone_model.py` | Simulasi fisika drone, Altitude Hold, tilt angles, drag velocity, & battery system |
| `serial_reader.py` | Asynchronous QThread parsing data serial RC 4-channel (Baud 115200) |
| `style.py` | Stylesheet Cyber-Dark QSS modern dengan aksen cyan neon & oranye |

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
| **`T`** | Ganti Tema Waktu (`DAY` $\rightarrow$ `SUNSET` $\rightarrow$ `NIGHT`) |
| **`L`** | Toggle Lampu Sorot 3D Drone (*Spotlight*) |
| **`M`** | Toggle Mini-Map Radar 2D (On / Off) |
| **`H`** | Toggle Tampilan HUD (On / Off) |
| **`O`** | Toggle FPV Scanlines Video Noise |
| **`Left Drag Mouse`** | Rotasi Orbit Kamera 360° (dengan Inertia Damping) |
| **`Scroll Wheel`** | Zoom In / Zoom Out Kamera |
| **`R`** | Reset drone ke koordinat HOME (0,0,0) |
| **`ESC`** | Keluar dari aplikasi |
