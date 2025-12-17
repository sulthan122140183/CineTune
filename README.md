# 🚀 CineTune: Tebak Film Lewat Gesture

**Sebuah Proyek Tugas Besar Mata Kuliah Sistem Teknologi Multimedia**

---

## 📝 Deskripsi Singkat

**CineTune** adalah sebuah game interaktif yang menantang pengetahuan sinematik pengguna melalui teka-teki visual. Proyek ini mengimplementasikan konsep multimedia dengan menggabungkan elemen audio, gambar, dan interaksi kamera (gesture recognition) dalam satu sistem yang kohesif.

Program akan menampilkan gambar yang merepresentasikan sebuah film, dan pemain harus menebak judul film yang benar. Uniknya, pemain akan menjawab menggunakan **gesture tangan** yang ditangkap oleh kamera secara *real-time* menggunakan MediaPipe, menciptakan pengalaman bermain yang imersif dan modern.

## ✨ Fitur Utama

* **Kuis Film Interaktif:** Database pertanyaan berbasis gambar film yang menantang.
* **Kontrol Gesture Real-time:** Sistem deteksi gerakan tangan *real-time* menggunakan MediaPipe untuk memilih jawaban:
  - 👍 **Thumb Up** → Pilihan A
  - ✋ **Open Palm** → Pilihan B
  - ✌️ **Two Fingers** → Pilihan C
  - ✊ **Fist** → Pilihan D
* **Multimedia Terintegrasi:** Menggabungkan elemen audio (sound effect benar/salah) dan visual (gambar film, feed kamera) secara bersamaan.
* **Sistem Skor:** Melacak poin pengguna untuk setiap jawaban yang benar.
* **UI Interaktif:** Antarmuka berbasis OpenCV dan Pygame yang responsif dan mudah dipahami.

## 🛠️ Tumpukan Teknologi (Technology Stack)

* **Bahasa Pemrograman:** Python 3.x
* **Computer Vision & Gesture Recognition:** 
  - OpenCV (cv2) - untuk processing video dan manipulasi gambar
  - MediaPipe - untuk deteksi hand landmarks secara akurat
* **UI & Grafis:** Pygame - untuk render grafis dan game loop
* **Audio Processing:** 
  - Pygame.mixer - untuk playback audio
  - SoundDevice - untuk pengolahan audio
* **Data Processing:** NumPy, Pandas - untuk manipulasi data
* **Lainnya:** Pillow, SciPy, Matplotlib

## 🚀 Instalasi & Cara Menjalankan

### Prasyarat
- Python 3.7 atau lebih tinggi
- Webcam/kamera yang berfungsi dengan baik
- Ruang yang cukup untuk gesture recognition

### Langkah-langkah

1. **Clone atau download repository:**
   ```bash
   git clone https://github.com/sulthan122140183/CineTune.git
   cd CineTune
   ```

2. **Buat virtual environment (opsional tapi disarankan):**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Instal dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi:**
   ```bash
   python src/main.py
   ```

## 🎮 Cara Bermain

1. Pastikan kameramu menyala dan memiliki pencahayaan yang cukup baik.
2. Jalankan aplikasi dengan perintah di atas.
3. Posisikan tanganmu di depan kamera pada area yang ditentukan (di dalam ROI).
4. Sebuah gambar film dan 4 pilihan jawaban (A, B, C, D) akan muncul di layar.
5. Tunjukkan gesture tangan yang sesuai dengan pilihan jawabanmu:
   - Jempol ke atas untuk jawaban **A**
   - Telapak tangan terbuka untuk jawaban **B**
   - Dua jari (V) untuk jawaban **C**
   - Genggaman tertutup untuk jawaban **D**
6. Sistem akan mendeteksi gesture dan menampilkan hasilnya beserta poin yang diperoleh.
7. Lanjutkan hingga semua pertanyaan selesai. Semoga berhasil! 🎬

## 📁 Struktur Proyek

```
CineTune/
├── src/
│   ├── main.py                  # Entry point aplikasi
│   ├── test.py                  # Unit tests
│   ├── core/
│   │   ├── data_loader.py       # Load pertanyaan dari CSV
│   │   ├── game_manager.py      # Logika game
│   │   └── audio_player.py      # Playback audio
│   ├── ui/
│   │   ├── frame_utama.py       # Main application class
│   │   └── tampilan.py          # UI rendering
│   └── vision/
│       ├── gesture_detector.py  # MediaPipe hand detection
│       └── gesture_mapper.py    # Pemetaan gesture ke jawaban
├── data/
│   ├── questions.csv            # Database pertanyaan film
│   └── gestures.csv             # Pemetaan gesture ke opsi
├── assets/
│   ├── audio/                   # File audio (SFX, musik)
│   └── images/                  # Gambar film untuk kuis
├── requirements.txt             # Dependensi Python
├── README.md                    # File ini
└── IMPLEMENTATION_GUIDE.md      # Dokumentasi teknis detail
```

## 📚 Dokumentasi Lengkap

Untuk dokumentasi teknis yang lebih detail tentang implementasi, silakan lihat:

- **[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** - Panduan implementasi teknis mendalam
- **[Demo Video](https://youtu.be/JQCAkjntTkc)** - Demonstrasi gameplay
- **[Dokumentasi Lengkap (Google Docs)](https://docs.google.com/document/d/14GlNimjzLjYy69Swh4L9bKkv_ktO28zDJuB_xmCCAR4/edit?tab=t.0#heading=h.lwpve7khmwdz)** - Spesifikasi proyek dan analisis mendalam

## 🔧 Dependency Utama

```
opencv-python==4.10.0.84
mediapipe==0.10.21
pygame==2.6.1
numpy==1.26.4
scipy==1.15.3
sounddevice==0.5.3
```

Lihat [requirements.txt](./requirements.txt) untuk daftar lengkap.

## 🧑‍🤝‍🧑 Anggota Kelompok

Proyek ini disusun dan dikembangkan oleh:

| Nama Lengkap | NIM |
| :--- | :--- |
| Sulthan Fatih Pradewa | 122140183 |
| Muhammad Fauzi Azizi | 122140106 |
| Ihya Razky Hidayat | 122140167 |

---
*Proyek ini dibuat untuk memenuhi Tugas Besar Mata Kuliah Sistem Teknologi Multimedia (IF25-40305), Semester 7.*
