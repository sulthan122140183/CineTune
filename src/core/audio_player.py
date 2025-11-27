import pygame
import os

class AudioPlayer:
    def __init__(self):
        """Initialize audio player"""
        try:
            # Inisialisasi mixer dengan setting standar
            pygame.mixer.init(frequency=44100, size=-16, channels=2)
            self.is_initialized = True
            self.current_sound = None

            print("[AUDIO] Mixer initialized ->", pygame.mixer.get_init())
        except Exception as e:
            print(f"[WARNING] Pygame mixer tidak tersedia: {e}")
            self.is_initialized = False

    def play_question_audio(self, file_path: str):
        """
        Putar audio pertanyaan.
        Di sini kita pakai pygame.mixer.music supaya simpel.
        file_path sudah absolut dari data_loader.
        """
        if not self.is_initialized:
            print("[AUDIO] Mixer belum siap, tidak bisa play question.")
            return

        if not file_path:
            print("[AUDIO] file_path kosong.")
            return

        exists = os.path.exists(file_path)
        print(f"[AUDIO] QUESTION -> {file_path} | exists={exists}")

        if not exists:
            print(f"[WARNING] File audio tidak ditemukan: {file_path}")
            return

        try:
            # Hentikan audio yang sebelumnya
            try:
                pygame.mixer.music.stop()
            except:
                pass

            # Load & play
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print("[AUDIO] Question audio PLAY.")
        except Exception as e:
            print(f"[ERROR] Gagal memutar question audio: {e}")
        
    def is_question_playing(self) -> bool:
        """
        Cek apakah audio pertanyaan masih diputar.
        True  -> masih bunyi
        False -> sudah selesai / tidak sedang main
        """
        if not self.is_initialized:
            return False

        try:
            return pygame.mixer.music.get_busy()
        except Exception as e:
            print(f"[AUDIO] Gagal cek status audio: {e}")
            return False


    # --- efek benar/salah masih boleh pakai Sound / beep ---

    def play_sound_effect(self, file_path: str):
        """Play sound effect sederhana (kalau mau pakai file .wav lain)"""
        if not self.is_initialized:
            return

        if not os.path.exists(file_path):
            print(f"[WARNING] SFX file tidak ditemukan: {file_path}")
            return

        try:
            sound = pygame.mixer.Sound(file_path)
            sound.play()
        except Exception as e:
            print(f"[ERROR] Gagal play SFX: {e}")

    def play_correct_sound(self, base_dir):
        """Play sound effect untuk jawaban benar"""
        if not self.is_initialized:
            return
        path = os.path.join(base_dir, "assets", "audio", "correct.wav")
        if os.path.exists(path):
            self.play_sound_effect(path)
        else:
            self.play_beep(1000, 200)

    def play_wrong_sound(self, base_dir):
        """Play sound effect untuk jawaban salah"""
        if not self.is_initialized:
            return
        path = os.path.join(base_dir, "assets", "audio", "wrong.wav")
        if os.path.exists(path):
            self.play_sound_effect(path)
        else:
            self.play_beep(300, 300)

    def play_beep(self, frequency=440, duration=200, sample_rate=22050):
        """Generate and play a simple beep sound"""
        if not self.is_initialized:
            return

        try:
            import math
            import numpy as np

            frames = int(duration * sample_rate / 1000)
            t = np.linspace(0, duration / 1000, frames)
            arr = np.sin(2.0 * math.pi * frequency * t)
            arr = (arr * 32767).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)

            sound = pygame.sndarray.make_sound(arr)
            sound.play()
            print("[AUDIO] Beep sound played.")
        except Exception as e:
            print(f"[WARNING] Tidak bisa generate beep: {e}")

    def stop(self):
        """Stop semua audio (music + SFX)"""
        if not self.is_initialized:
            return
        try:
            # stop musik utama (yang dipakai play_question_audio)
            pygame.mixer.music.stop()

            # stop semua channel audio lain (SFX, sound effect, dll)
            pygame.mixer.stop()

            print("[AUDIO] Stop all sounds (music + SFX).")
        except Exception as e:
            print(f"[ERROR] Gagal stop audio: {e}")

    def quit(self):
        """Stop dan quit mixer"""
        if self.is_initialized:
            try:
                pygame.mixer.quit()
                print("[AUDIO] Mixer quit.")
            except Exception as e:
                print(f"[WARNING] Error saat quit audio: {e}")


if __name__ == "__main__":
    # Test mandiri
    import time

    player = AudioPlayer()
    print("[TEST] Mixer ready:", player.is_initialized)

    if player.is_initialized:
        player.play_beep(440, 500)
        time.sleep(1)

    player.quit()
