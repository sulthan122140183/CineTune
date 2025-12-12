# 4 Implementasi CineTune

## 4.1 Instalasi Library

### 4.1.1 Menggunakan Virtual Environment

File konfigurasi otomatis yang dibuat saat membuat virtual environment dengan venv. File ini menyimpan informasi seperti versi Python dan pengaturan environment.

```bash
python -m venv venv
```

**Kode 1: Perintah create virtual environment**

### 4.1.2 Menggunakan Requirements.txt

Daftar library yang digunakan dalam proyek. File ini digunakan untuk menginstal semua dependensi secara otomatis dengan perintah pip install -r requirements.txt.

```bash
pip install -r requirements.txt
```

**Kode 2: Perintah install requirements.txt**

Dependensi utama proyek CineTune:

```
opencv-python==4.10.0.84
mediapipe==0.10.21
pygame==2.6.1
numpy==1.26.4
scipy==1.15.3
sounddevice==0.5.3
matplotlib==3.10.7
pillow==12.0.0
```

**Kode 3: Dependensi Utama**

---

## 4.2 Modul data_loader.py

Modul ini berfungsi untuk memuat data pertanyaan dan pemetaan gesture dari file CSV.

### 4.2.1 Import Library dan Resolusi Path

```python
import csv
import os

# ==========================================
# RESOLVE PATHS (lebih aman & fleksibel)
# ==========================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
QUESTIONS_CSV = os.path.join(BASE_DIR, "data", "questions.csv")
GESTURES_CSV  = os.path.join(BASE_DIR, "data", "gestures.csv")
```

**Kode 4: Import Library dan Resolusi Path**

### 4.2.2 Fungsi Load Questions

Memuat data pertanyaan dari file CSV yang berisi:
- ID pertanyaan
- Path gambar film
- Path audio
- 4 opsi jawaban (A, B, C, D)
- Jawaban benar

```python
def load_questions():
    questions = []
    try:
        with open(QUESTIONS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append({
                    "id": int(row["id"]),
                    "image": os.path.join(BASE_DIR, row["image_path"]),
                    "audio": os.path.join(BASE_DIR, row["audio_path"]),
                    "options": {
                        "A": row["option_a"],
                        "B": row["option_b"],
                        "C": row["option_c"],
                        "D": row["option_d"],
                    },
                    "answer": row["answer"].strip().upper(),
                })
    except Exception as e:
        print("[ERROR] Gagal load questions:", e)
    return questions
```

**Kode 5: Fungsi Load Questions**

### 4.2.3 Fungsi Load Gesture Map

Memuat pemetaan gesture ke jawaban dari file CSV.

```python
def load_gesture_map():
    gestures = {}
    try:
        with open(GESTURES_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                gestures[row["gesture_name"]] = row["answer"].strip().upper()
        print("[DEBUG] Gesture map loaded:", gestures)
    except Exception as e:
        print("[ERROR] Gagal load gestures:", e)
    return gestures
```

**Kode 6: Fungsi Load Gesture Map**

---

## 4.3 Modul gesture_detector.py

Modul ini berfungsi untuk mendeteksi landmark tangan menggunakan MediaPipe.

### 4.3.1 Import Library

```python
import cv2
import mediapipe as mp

class GestureDetector:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.drawer = mp.solutions.drawing_utils
```

**Kode 7: Inisialisasi MediaPipe Hand Detection**

### 4.3.2 Fungsi Detect Landmarks

Mendeteksi dan menggambar 21 landmark tangan dari frame.

```python
def detect(self, frame):
    """
    Input: frame BGR (opencv)
    Output:
        - landmarks: list berisi 21 titik (x, y)
        - frame: frame dengan landmark digambar
    """
    
    # Convert BGR → RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Proses tangan
    results = self.hands.process(rgb)
    
    landmarks = None
    
    # Jika ada tangan
    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]
        
        # Draw landmarks di frame
        self.drawer.draw_landmarks(
            frame, 
            handLms,
            mp.solutions.hands.HAND_CONNECTIONS
        )
        
        # Extract koordinat setiap titik
        h, w, _ = frame.shape
        landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in handLms.landmark]
    
    return landmarks, frame
```

**Kode 8: Fungsi Deteksi Landmarks**

---

## 4.4 Modul gesture_mapper.py

Modul ini berfungsi untuk memetakan landmark tangan ke gesture tertentu menggunakan klasifikasi berbasis rule-based atau machine learning.

### 4.4.1 Fitur Utama

- Menghitung jarak dan sudut antar landmark
- Mendeteksi posisi jari terbuka atau tertutup
- Mendeteksi gesture khusus (Thumbs Up, Pointing, V-Sign, dll)
- Memetakan gesture ke jawaban (A, B, C, D)

### 4.4.2 Struktur Klasifikasi Gesture

```python
class GestureMapper:
    def __init__(self):
        # Dictionary untuk menyimpan hasil deteksi gesture
        self.last_gesture = None
        self.confidence = 0.0
    
    def classify(self, landmarks):
        """
        Input: landmarks (21 titik)
        Output: gesture_name (string), confidence (float)
        """
        if landmarks is None or len(landmarks) < 21:
            return None, 0.0
        
        # Proses klasifikasi gesture
        # ... logika deteksi gesture ...
        
        return gesture_name, confidence
```

**Kode 9: Struktur Klasifikasi Gesture**

---

## 4.5 Modul game_manager.py

Modul ini mengatur logika permainan, termasuk pengelolaan state, skor, dan timer.

### 4.5.1 Enum Game Phase

```python
from enum import Enum

class GamePhase(Enum):
    IDLE = 0
    WAITING_ANSWER = 1
    SHOWING_RESULT = 2
    GAME_OVER = 3
```

**Kode 10: Game Phase Enum**

### 4.5.2 Inisialisasi Game Manager

```python
class GameManager:
    def __init__(self, questions):
        """
        Initialize game manager
        
        Args:
            questions: List of question dicts
        """
        self.questions = questions if questions else []
        self.current_question_idx = 0
        self.score = 0
        self.answered_count = 0
        self.phase = GamePhase.IDLE
        
        # Konfigurasi timer per soal
        self.question_duration = 10.0  # detik per soal
        self.current_question_start_time = None
        
        # Shuffle questions
        if self.questions:
            random.shuffle(self.questions)
```

**Kode 11: Inisialisasi Game Manager**

### 4.5.3 Fungsi Start Game

```python
def start_game(self):
    """Start the game"""
    self.current_question_idx = 0
    self.score = 0
    self.answered_count = 0
    self.phase = GamePhase.WAITING_ANSWER
    
    if self.questions:
        random.shuffle(self.questions)
        self.start_question()
```

**Kode 12: Fungsi Start Game**

### 4.5.4 Fungsi Check Answer

```python
def check_answer(self, player_answer):
    """
    Periksa jawaban pemain
    
    Args:
        player_answer: string (A/B/C/D)
    
    Returns:
        bool: True jika benar, False jika salah
    """
    if self.current_question is None:
        return False
    
    is_correct = (player_answer == self.current_question['answer'])
    
    if is_correct:
        self.score += 1
        self.phase = GamePhase.SHOWING_RESULT
    
    self.answered_count += 1
    return is_correct
```

**Kode 13: Fungsi Check Answer**

---

## 4.6 Modul audio_player.py

Modul ini mengatur pemutaran audio untuk feedback pertanyaan dan jawaban.

### 4.6.1 Inisialisasi Audio Player

```python
import sounddevice as sd
import soundfile as sf

class AudioPlayer:
    def __init__(self):
        """Initialize audio player"""
        self.is_playing = False
    
    def play_audio(self, audio_path):
        """
        Play audio file
        
        Args:
            audio_path: string path ke file audio
        """
        try:
            data, samplerate = sf.read(audio_path)
            self.is_playing = True
            sd.play(data, samplerate)
            sd.wait()
            self.is_playing = False
        except Exception as e:
            print(f"[ERROR] Gagal play audio: {e}")
```

**Kode 14: Inisialisasi dan Fungsi Audio Player**

---

## 4.7 Modul tampilan.py (GameUI)

Modul ini menangani render UI menggunakan pygame.

### 4.7.1 Enum Game State

```python
from enum import Enum

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    RESULT = 2
    GAME_OVER = 3
```

**Kode 15: Game State Enum**

### 4.7.2 Inisialisasi GameUI

```python
import pygame

class GameUI:
    def __init__(self, width=None, height=None):
        """
        Initialize game UI dengan responsive resolution
        
        Args:
            width: lebar screen (default: 1280)
            height: tinggi screen (default: 800)
        """
        # Set default resolution yang lebih compatible untuk berbagai device
        self.width = width if width else 1280
        self.height = height if height else 800
        
        # Gunakan window yang dapat di-resize untuk compatibility lebih baik
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("CineTune - Tebak Film Lewat Gesture")
        
        # Load fonts dengan scaling berbasis height
        self.font_title = pygame.font.Font(None, int(self.height * 0.08))
        self.font_text = pygame.font.Font(None, int(self.height * 0.06))
        self.font_small = pygame.font.Font(None, int(self.height * 0.04))
        
        # Initialize state
        self.state = GameState.MENU
```

**Kode 16: Inisialisasi GameUI (Responsive)**

### 4.7.2.1 Optimasi Resolusi untuk Berbagai Device

Untuk memastikan UI tidak terpotong di berbagai device, gunakan:

```python
# Deteksi resolusi layar monitor
import pygame
pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

# Tentukan resolusi optimal (85% dari resolusi layar)
optimal_width = int(screen_width * 0.85)
optimal_height = int(screen_height * 0.85)

# Batasi agar tidak terlalu besar (max 1920x1080)
max_width = min(optimal_width, 1920)
max_height = min(optimal_height, 1080)

# Batasi agar tidak terlalu kecil (min 1024x768)
min_width = max(max_width, 1024)
min_height = max(max_height, 768)

ui = GameUI(width=min_width, height=min_height)
```

**Kode 16a: Deteksi dan Optimasi Resolusi Otomatis**

### 4.7.3 Fungsi Render Pertanyaan

```python
def render_question(self, screen, image_surface, options, timer_text, score_text):
    """
    Render tampilan pertanyaan dengan layout responsive
    
    Args:
        screen: pygame surface
        image_surface: gambar film
        options: dict {A: text, B: text, C: text, D: text}
        timer_text: teks timer
        score_text: teks skor
    """
    screen.fill((0, 0, 0))
    
    # Display image dengan padding responsive
    padding = int(self.width * 0.04)
    if image_surface:
        screen.blit(image_surface, (padding, padding))
    
    # Display options dengan spacing responsive
    y_offset = int(self.height * 0.65)
    option_spacing = int(self.height * 0.08)
    for key, text in options.items():
        option_text = self.font_text.render(f"{key}: {text}", True, (255, 255, 255))
        screen.blit(option_text, (padding, y_offset))
        y_offset += option_spacing
    
    # Display timer and score dengan positioning responsive
    timer_surf = self.font_small.render(timer_text, True, (255, 200, 0))
    score_surf = self.font_small.render(score_text, True, (0, 255, 0))
    screen.blit(timer_surf, (1000, 50))
    screen.blit(score_surf, (1000, 100))
    
    pygame.display.flip()
```

**Kode 17: Fungsi Render Pertanyaan**

---

## 4.8 Modul frame_utama.py (CineTuneApp)

Modul utama yang mengintegrasikan semua komponen.

### 4.8.1 Inisialisasi Aplikasi

```python
class CineTuneApp:
    def __init__(self):
        """Initialize the application"""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize pygame
        pygame.init()
        
        # Initialize components
        print("[INIT] Loading data...")
        self.questions = load_questions()
        self.gesture_map = load_gesture_map()
        
        # Initialize managers
        self.game_manager = GameManager(self.questions)
        self.audio_player = AudioPlayer()
        self.ui = GameUI()
        
        # Initialize vision components
        print("[INIT] Initializing gesture detection...")
        self.gesture_detector = GestureDetector()
        self.gesture_mapper = GestureMapper()
        self.cap = cv2.VideoCapture(0)
```

**Kode 18: Inisialisasi CineTuneApp**

### 4.8.2 Main Game Loop

Aplikasi menjalankan loop utama yang:
- Membaca frame dari kamera
- Mendeteksi gesture tangan
- Memperbarui UI dengan frame dan informasi pertanyaan
- Mengevaluasi jawaban berdasarkan gesture yang terdeteksi
- Menampilkan hasil dan melanjutkan ke pertanyaan berikutnya

```python
def run(self):
    """Main game loop"""
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Capture frame dari kamera
        ret, frame = self.cap.read()
        if not ret:
            continue
        
        # Deteksi gesture
        landmarks, frame_with_landmarks = self.gesture_detector.detect(frame)
        gesture, confidence = self.gesture_mapper.classify(landmarks)
        
        # Update UI
        # ... render frame, pertanyaan, dan feedback ...
        
        clock.tick(30)  # 30 FPS
```

**Kode 19: Main Game Loop**

### 4.8.3 Cleanup Resources

```python
def cleanup(self):
    """Release resources"""
    if self.cap is not None:
        self.cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    print("[INFO] Application cleanup complete")
```

**Kode 20: Cleanup Resources**

---

## 4.9 Struktur Folder Proyek

```
CineTune/
├── src/
│   ├── main.py                 # Entry point aplikasi
│   ├── test.py                 # Testing scripts
│   ├── core/
│   │   ├── audio_player.py     # Pengelolaan audio
│   │   ├── data_loader.py      # Load data dari CSV
│   │   ├── game_manager.py     # Logika game
│   │   └── __pycache__/
│   ├── ui/
│   │   ├── frame_utama.py      # Main app class
│   │   ├── tampilan.py         # UI rendering
│   │   └── __pycache__/
│   └── vision/
│       ├── gesture_detector.py # MediaPipe detection
│       ├── gesture_mapper.py   # Gesture classification
│       └── __pycache__/
├── assets/
│   ├── audio/                  # File audio pertanyaan
│   └── images/                 # Gambar film untuk pertanyaan
├── data/
│   ├── gestures.csv            # Pemetaan gesture ke jawaban
│   └── questions.csv           # Data pertanyaan
├── requirements.txt            # Dependensi Python
├── README.md
└── IMPLEMENTATION_GUIDE.md     # Dokumentasi ini
```

**Kode 21: Struktur Folder Proyek CineTune**

---

## 4.10 File Data Format

### 4.10.1 Format questions.csv

| id | image_path | audio_path | option_a | option_b | option_c | option_d | answer |
|---|---|---|---|---|---|---|---|
| 1 | assets/images/film1.jpg | assets/audio/q1.wav | Opsi A | Opsi B | Opsi C | Opsi D | A |
| 2 | assets/images/film2.jpg | assets/audio/q2.wav | Opsi A | Opsi B | Opsi C | Opsi D | B |

**Kode 22: Format questions.csv**

### 4.10.2 Format gestures.csv

| gesture_name | answer |
|---|---|
| thumbs_up | A |
| pointing_up | B |
| v_sign | C |
| open_palm | D |

**Kode 23: Format gestures.csv**

---

## 4.11 Cara Menjalankan Aplikasi

### 4.11.1 Langkah-Langkah Instalasi

1. **Clone atau download project**
   ```bash
   cd d:\Programming\SEMESTER_6\CineTune
   ```

2. **Buat virtual environment** (optional tapi recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Pastikan kamera tersedia**
   - Periksa bahwa kamera USB atau built-in tersedia dan tidak digunakan oleh aplikasi lain

5. **Persiapkan data**
   - Pastikan file `data/questions.csv` dan `data/gestures.csv` sudah ada
   - Pastikan path ke gambar dan audio benar di CSV

### 4.11.2 Menjalankan Aplikasi

```bash
python src/main.py
```

**Kode 24: Menjalankan Aplikasi**

### 4.11.3 Opsi Debugging

Jika ada error, jalankan dengan verbose output:

```bash
python -u src/main.py
```

---

## 4.11.4 Menampilkan Kamera Tanpa Distorsi (Maintain Aspect Ratio) ✅

> **✅ STATUS**: Fitur ini **SUDAH DITERAPKAN** di [src/ui/tampilan.py](src/ui/tampilan.py)
> 
> Kamera sekarang menampilkan dengan aspect ratio yang terjaga, tidak akan stretch lagi!

Untuk mencegah kamera stretch/terdistorsi saat ditampilkan di pygame, gunakan letterboxing atau aspect ratio preservation:

### Solusi 1: Letterboxing (dengan black bars) - AKTIF ✅

```python
def scale_preserve_aspect_ratio(surface, target_width, target_height):
    """
    Scale surface sambil maintain aspect ratio (letterboxing)
    
    Args:
        surface: pygame surface dari kamera
        target_width: lebar target screen
        target_height: tinggi target screen
    
    Returns:
        tuple (scaled_surface, x_offset, y_offset)
    """
    # Hitung aspect ratio
    surf_width, surf_height = surface.get_size()
    target_aspect = target_width / target_height
    surf_aspect = surf_width / surf_height
    
    # Tentukan scaling berdasarkan aspect ratio
    if surf_aspect > target_aspect:
        # Surface lebih lebar, scale berdasarkan height
        new_height = target_height
        new_width = int(target_height * surf_aspect)
    else:
        # Surface lebih tinggi, scale berdasarkan width
        new_width = target_width
        new_height = int(target_width / surf_aspect)
    
    # Scale surface
    scaled = pygame.transform.scale(surface, (new_width, new_height))
    
    # Hitung offset untuk center
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    return scaled, x_offset, y_offset

# Penggunaan di draw_game():
if camera_frame:
    try:
        scaled_frame, x_offset, y_offset = scale_preserve_aspect_ratio(
            camera_frame, self.width, self.height
        )
        self.screen.fill(self.bg_dark)  # Fill background dengan warna gelap
        self.screen.blit(scaled_frame, (x_offset, y_offset))
    except Exception as e:
        print(f"[ERROR] Camera frame error: {e}")
        self.screen.fill(self.bg_dark)
else:
    self.screen.fill(self.bg_dark)
```

**Kode 24a: Scale Camera Maintain Aspect Ratio (Letterboxing)**

Implementasi lengkap sudah di [src/ui/tampilan.py](src/ui/tampilan.py) - tinggal jalankan aplikasi!

### Solusi 2: Cropping (potong bagian tepi)

```python
def crop_to_aspect_ratio(surface, target_width, target_height):
    """
    Crop surface ke target aspect ratio (tanpa black bars)
    
    Args:
        surface: pygame surface dari kamera
        target_width: lebar target
        target_height: tinggi target
    
    Returns:
        cropped surface
    """
    surf_width, surf_height = surface.get_size()
    target_aspect = target_width / target_height
    surf_aspect = surf_width / surf_height
    
    if surf_aspect > target_aspect:
        # Surface lebih lebar, crop samping
        crop_width = int(surf_height * target_aspect)
        crop_height = surf_height
        x = (surf_width - crop_width) // 2
        y = 0
    else:
        # Surface lebih tinggi, crop atas/bawah
        crop_width = surf_width
        crop_height = int(surf_width / target_aspect)
        x = 0
        y = (surf_height - crop_height) // 2
    
    # Create rect dan crop
    rect = pygame.Rect(x, y, crop_width, crop_height)
    cropped = surface.subsurface(rect).copy()
    
    # Scale ke ukuran target
    return pygame.transform.scale(cropped, (target_width, target_height))

# Penggunaan (jika ingin fullscreen tanpa letterbox):
if camera_frame:
    try:
        bg = crop_to_aspect_ratio(camera_frame, self.width, self.height)
        self.screen.blit(bg, (0, 0))
    except Exception as e:
        print(f"[ERROR] Camera frame error: {e}")
        self.screen.fill(self.bg_dark)
```

**Kode 24b: Crop Camera ke Aspect Ratio Target**

### Tabel Perbandingan Metode

| Metode | Kelebihan | Kekurangan | Status |
|--------|-----------|-----------|--------|
| **Scale Biasa** | Sederhana, cepat | Gambar stretch/distorsi | ❌ LAMA |
| **Letterboxing** | Tidak ada distorsi, maintain aspect | Ada black bars di sisi | ✅ **AKTIF** |
| **Cropping** | Fullscreen, tidak ada distorsi | Bagian gambar terpotong | 🔧 Optional |

**Status**: CineTune sekarang menggunakan **Letterboxing** (Kode 24a-Implemented) untuk hasil terbaik.

---

## 4.11.4 Menampilkan Kamera Tanpa Distorsi (Maintain Aspect Ratio)

Untuk mencegah kamera stretch/terdistorsi saat ditampilkan di pygame, gunakan letterboxing atau aspect ratio preservation:

### Solusi 1: Letterboxing (dengan black bars)

```python
def scale_preserve_aspect_ratio(surface, target_width, target_height):
    """
    Scale surface sambil maintain aspect ratio (letterboxing)
    
    Args:
        surface: pygame surface dari kamera
        target_width: lebar target screen
        target_height: tinggi target screen
    
    Returns:
        tuple (scaled_surface, x_offset, y_offset)
    """
    # Hitung aspect ratio
    surf_width, surf_height = surface.get_size()
    target_aspect = target_width / target_height
    surf_aspect = surf_width / surf_height
    
    # Tentukan scaling berdasarkan aspect ratio
    if surf_aspect > target_aspect:
        # Surface lebih lebar, scale berdasarkan height
        new_height = target_height
        new_width = int(target_height * surf_aspect)
    else:
        # Surface lebih tinggi, scale berdasarkan width
        new_width = target_width
        new_height = int(target_width / surf_aspect)
    
    # Scale surface
    scaled = pygame.transform.scale(surface, (new_width, new_height))
    
    # Hitung offset untuk center
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    return scaled, x_offset, y_offset

# Penggunaan di draw_game():
if camera_frame:
    try:
        scaled_frame, x_offset, y_offset = scale_preserve_aspect_ratio(
            camera_frame, self.width, self.height
        )
        self.screen.fill(self.bg_dark)  # Fill background dengan warna gelap
        self.screen.blit(scaled_frame, (x_offset, y_offset))
    except Exception as e:
        print(f"[ERROR] Camera frame error: {e}")
        self.screen.fill(self.bg_dark)
else:
    self.screen.fill(self.bg_dark)
```

**Kode 24a: Scale Camera Maintain Aspect Ratio (Letterboxing)**

### Solusi 2: Cropping (potong bagian tepi)

```python
def crop_to_aspect_ratio(surface, target_width, target_height):
    """
    Crop surface ke target aspect ratio (tanpa black bars)
    
    Args:
        surface: pygame surface dari kamera
        target_width: lebar target
        target_height: tinggi target
    
    Returns:
        cropped surface
    """
    surf_width, surf_height = surface.get_size()
    target_aspect = target_width / target_height
    surf_aspect = surf_width / surf_height
    
    if surf_aspect > target_aspect:
        # Surface lebih lebar, crop samping
        crop_width = int(surf_height * target_aspect)
        crop_height = surf_height
        x = (surf_width - crop_width) // 2
        y = 0
    else:
        # Surface lebih tinggi, crop atas/bawah
        crop_width = surf_width
        crop_height = int(surf_width / target_aspect)
        x = 0
        y = (surf_height - crop_height) // 2
    
    # Create rect dan crop
    rect = pygame.Rect(x, y, crop_width, crop_height)
    cropped = surface.subsurface(rect).copy()
    
    # Scale ke ukuran target
    return pygame.transform.scale(cropped, (target_width, target_height))

# Penggunaan:
if camera_frame:
    try:
        bg = crop_to_aspect_ratio(camera_frame, self.width, self.height)
        self.screen.blit(bg, (0, 0))
    except Exception as e:
        print(f"[ERROR] Camera frame error: {e}")
        self.screen.fill(self.bg_dark)
```

**Kode 24b: Crop Camera ke Aspect Ratio Target**

### Tabel Perbandingan Metode

| Metode | Kelebihan | Kekurangan |
|--------|-----------|-----------|
| **Scale Biasa** | Sederhana, cepat | Gambar stretch/distorsi |
| **Letterboxing** | Tidak ada distorsi, maintain aspect | Ada black bars di sisi |
| **Cropping** | Fullscreen, tidak ada distorsi | Bagian gambar terpotong |

**Rekomendasi**: Gunakan **Letterboxing** untuk produksi (terbaik untuk gesture detection) atau **Cropping** jika ingin fullscreen tanpa black bars.

---

## 4.12 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Kamera tidak terbuka | Periksa apakah kamera sedang digunakan aplikasi lain. Tutup aplikasi lain yang menggunakan kamera. |
| Error "ModuleNotFoundError" | Pastikan virtual environment sudah diaktifkan dan semua dependensi sudah di-install. |
| Gesture tidak terdeteksi | Pastikan tangan dalam frame dan lighting cukup baik. Sesuaikan confidence threshold di gesture_detector.py |
| Audio tidak terdengar | Periksa volume sistem. Pastikan file audio ada di path yang benar. |
| FPS rendah | Kurangi resolusi kamera atau optimalkan gesture detection. |
| UI terpotong di beberapa device | Gunakan responsive resolution dengan mendeteksi ukuran layar otomatis (lihat Kode 16a). |
| Kamera stretch/terdistorsi | Gunakan letterboxing atau cropping untuk maintain aspect ratio (lihat Kode 24a atau 24b). |

**Kode 25: Troubleshooting Guide**

## 4.13 Rekomendasi Resolusi untuk Berbagai Device

### 4.13.1 Resolusi Optimal Berdasarkan Device

```python
# Tabel resolusi rekomendasi
RESOLUTION_RECOMMENDATIONS = {
    "laptop_1080p": (1280, 800),      # Full HD - Safe default
    "laptop_768p": (1024, 768),       # Standard HD
    "monitor_1440p": (1440, 900),     # Wide 1440p
    "monitor_1600p": (1600, 1000),    # Extra wide
    "monitor_2k": (1920, 1080),       # 2K display
    "portable_small": (960, 720),     # Portable/small screen
}

# Auto-detect optimal resolution
def get_optimal_resolution():
    """Deteksi dan return resolusi optimal otomatis"""
    import pygame
    pygame.init()
    info = pygame.display.Info()
    
    screen_width = info.current_w
    screen_height = info.current_h
    
    # Hitung resolusi 85% dari layar, tapi jaga aspect ratio
    target_width = int(screen_width * 0.85)
    target_height = int(screen_height * 0.85)
    
    # Batasi range untuk consistency
    final_width = max(960, min(target_width, 1920))
    final_height = max(720, min(target_height, 1080))
    
    return (final_width, final_height)

# Gunakan di CineTuneApp
optimal_res = get_optimal_resolution()
ui = GameUI(width=optimal_res[0], height=optimal_res[1])
```

**Kode 26: Rekomendasi Resolusi Berdasarkan Device**

### 4.13.2 Tips untuk Berbagai Ukuran Layar

| Device | Resolusi | Catatan |
|--------|----------|---------|
| Laptop 11" | 960x720 | Ukuran minimal, cocok untuk portable |
| Laptop 13-14" | 1024x768 | Standard, paling kompatibel |
| Laptop 15-17" | 1280x800 | Rekomendasi default |
| Monitor 21-24" | 1440x900 | Good balance |
| Monitor 27"+ | 1600x1000 atau 1920x1080 | Maximum, gunakan scaling |
| Proyektor | Full Screen | Gunakan fullscreen mode |

**Kode 27: Tabel Ukuran Device dan Resolusi**

---

## End of Implementation Guide

Untuk informasi lebih lanjut, lihat dokumentasi lainnya:
- [README.md](README.md) - Overview proyek
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detail struktur proyek
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Panduan pengembangan
