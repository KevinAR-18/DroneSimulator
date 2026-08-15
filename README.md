# 🛸 SIMULATOR DRONE MANGKRAK 3D (V3)

**Pembuat Utama (Lead Creator & Developer):** **Ilham Purnomo**  
Aplikasi simulator penerbangan quadcopter 3D interaktif berbasis **Python** dan **PySide6 QPainter** yang mendukung koneksi transmitter remote control fisik via Serial (Arduino / ESP32).
---

## 👤 Pembuat Utama & Kredit Proyek

- **Pembuat Utama (Original Creator & Lead Developer)**: **Ilham Purnomo**  
  Merancang, membuat, dan mengonsep arsitektur dasar simulator drone serta sistem komunikasi transmisi remote control fisik.

---

## 📋 Fitur Unggulan Perangkat Lunak (Versi 3)

- **Engine Rendering 3D Faceted**: Model quadcopter 3D matte gelap, directional lighting (Lambertian + specular lembut), serta depth sorting tanpa dependensi library 3D eksternal (Pure PySide6 Vector Graphics).
- **Siklus Tema Waktu (Day / Sunset / Night)**:
  - *Day*: Siang berkabut lembut.
  - *Sunset*: Nuansa senja hangat yang diredam.
  - *Night*: Malam berbintang dengan pencahayaan rendah.
  - *Hotkey*: Tekan **`T`** untuk mengganti tema.
- **3D Drone Spotlight / Searchlight**: Sorot lampu memancar dari moncong drone ke tanah (*illuminated ground light pool*). Tekan **`L`** untuk toggle on/off.
- **Objek Lingkungan 3D**: Pohon pinus 3D *low-poly* dan kincir angin 3D (*wind turbine*) berputar di kejauhan.
- **Sistem Multi-Kamera 3D**: Mode `CHASE` (kamera kejar halus), `ORBIT` (free look 360° dengan *inertia damping*), `FPV` (cockpit moncong drone), dan `TOP-DOWN` (taktis overhead). Tekan **`C`** untuk mengganti mode.
- **Mini Telemetry Sparkline Graph**: Grafik strip mini real-time di HUD yang memplot ketinggian (*altitude*) dan kecepatan (*speed*).
- **2D Mini-Map Radar Overlay**: Radar bundar taktis 35m di pojok layar yang menampilkan posisi drone, heading, helipad, dan racing gates secara real-time. Tekan **`M`** untuk toggle.
- **FPV OSD**: Interface FPV dengan crosshair reticle, telemetri, dan opsi scanline video noise (Tekan **`O`**).
- **Low-Battery Alert**: Denyut lembut di tepi viewport saat baterai di bawah 15%.

---

## 🎨 Sistem Tema & Warna

Seluruh warna aplikasi berasal dari satu modul: **`theme.py`**. Tidak ada literal warna yang ditulis di file lain.

- **Palet**: *Slate Gelap Lembut* — permukaan bertingkat (`#1b1f27` → `#22272f` → `#2a2f39`), teks `#babecd`, aksen teal redup `#60aaba` dan oranye redup `#c08a4e`.
- **Kontras**: dijaga di rentang **4.5–9:1** (nyaman dipandang lama, tetap memenuhi WCAG AA), bukan 12–17:1 seperti tema neon.
- **Tanpa titik menyilaukan**: tidak ada putih murni `#ffffff` maupun warna saturasi 100%. Tidak ada piksel di atas luminansi 200 pada rendering normal.
- **Tabel tema lingkungan**: `THEMES` di `theme.py` mendefinisikan langit, tanah, grid, dan border untuk `DAY` / `SUNSET` / `NIGHT`. Mengubah tema cukup di satu tempat.
- **Model pencahayaan**: konstanta `LIGHT_AMBIENT` / `LIGHT_DIFFUSE` / `LIGHT_SPECULAR` juga di `theme.py`. Ambient tinggi + diffuse rendah membuat rentang gelap-terang antar permukaan menyempit tanpa membuat model jadi gelap.

---

## 🛠️ Arsitektur Perangkat Lunak

| Module | Peran & Deskripsi |
|--------|-------------------|
| `main.py` | Entry point utama aplikasi |
| `theme.py` | **Sumber tunggal warna**: token palet, tabel tema lingkungan, konstanta pencahayaan |
| `style.py` | Generator stylesheet QSS panel kontrol dari token `theme.py` |
| `main_window.py` | Window GUI PySide6, pengatur layout, telemetry panel, & event hotkey handler |
| `widgets.py` | Engine visual 3D (`SimView`), lingkungan, kamera, lighting, spotlight, props 3D, FPV OSD, & Radar |
| `drone_model.py` | Simulasi fisika drone, Altitude Hold, tilt angles, drag velocity, & battery system |
| `serial_reader.py` | Asynchronous QThread parsing data serial RC 4-channel (Baud 115200) |

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
