import pygame
import os
import math
import random
from enum import Enum

# ==========================================
# CONSTANTS & COLORS
# ==========================================
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_GRAY = (30, 30, 30)
    LIGHT_GRAY = (200, 200, 200)
    BLUE = (0, 102, 204)
    DARK_BLUE = (0, 51, 102)
    GREEN = (0, 200, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)

class GameState(Enum):
    MENU = 1
    GAME = 2
    RESULT = 3
    GAME_OVER = 4

# ==========================================
# UI UTILITIES
# ==========================================
def draw_text(surface, text, font, color, rect):
    """Draw text centered in a rect"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_button(surface, text, rect, font, bg_color, text_color, hover=False):
    """Draw a button with optional hover effect"""
    if hover:
        pygame.draw.rect(surface, (min(bg_color[0] + 30, 255), 
                                   min(bg_color[1] + 30, 255), 
                                   min(bg_color[2] + 30, 255)), rect, border_radius=10)
    else:
        pygame.draw.rect(surface, bg_color, rect, border_radius=10)
    
    pygame.draw.rect(surface, text_color, rect, 3, border_radius=10)
    draw_text(surface, text, font, text_color, rect)

def scale_preserve_aspect_ratio(surface, target_width, target_height, bg_color=(0, 0, 0)):
    """
    Scale surface sambil maintain aspect ratio (letterboxing)
    
    Args:
        surface: pygame surface dari kamera
        target_width: lebar target screen
        target_height: tinggi target screen
        bg_color: warna background untuk letterbox
    
    Returns:
        scaled surface dengan aspect ratio terjaga
    """
    if surface is None:
        return None
    
    try:
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
        
        # Create background dengan letterbox
        result = pygame.Surface((target_width, target_height))
        result.fill(bg_color)
        
        # Hitung offset untuk center
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Blit scaled surface ke center
        result.blit(scaled, (x_offset, y_offset))
        
        return result
    except Exception as e:
        print(f"[ERROR] Scale preserve aspect ratio: {e}")
        return surface

# ==========================================
# UI CLASS
# ==========================================
class GameUI:
    def __init__(self, width=540, height=960):
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        
        # Initialize font module if not already initialized
        if not pygame.font.get_init():
            pygame.font.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("CineTune - Tebak Film Lewat Gesture")
        
        # Fonts (dikecilkan agar pas di layar 540x960 dan konsisten)
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 38)
        self.font_small = pygame.font.Font(None, 22)
        self.font_tiny = pygame.font.Font(None, 16)
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Current state
        self.state = GameState.MENU
        # Animation / transition helpers
        self._last_state = self.state
        self._state_change_time = pygame.time.get_ticks()
        # Elegant, modern palette (fokus biru/cybertron)
        self.accent_cyan = (80, 200, 255)    # neon blue utama
        self.accent_pink = (30, 160, 220)    # biru sekunder
        self.accent_yellow = (120, 220, 255) # biru muda lembut
        self.accent_gray = (160, 170, 190)
        self.bg_dark = (8, 10, 18)
        self.bg_panel = (14, 20, 34)
        self.card_bg = (18, 26, 46)
        self.card_border = (40, 80, 140)
        self.shadow = (0, 0, 0, 60)
        # particles/decoration disabled for elegant minimal UI
        self._particles = []
        self._last_particle_time = 0
        self._particle_rate_ms = 999999
        self._decor_phase = 0.0
        self._fade_alpha = 0
        
    def draw_menu(self):
        """Draw main menu screen with animated gradient + neon title + styled start button"""
        # Flat elegant background
        self.screen.fill(self.bg_dark)
        # Title
        title_s = self.font_large.render("CineTune", True, self.accent_cyan)
        self.screen.blit(title_s, (self.width // 2 - title_s.get_width() // 2, 170))
        # Subtitle
        subtitle = self.font_small.render("Tebak Gestur & Film", True, self.accent_gray)
        subtitle_x = self.width // 2 - subtitle.get_width() // 2
        subtitle_y = 212
        self.screen.blit(subtitle, (subtitle_x, subtitle_y))

        # Start button diposisikan di tengah antara subtitle dan kartu petunjuk
        btn_w = 220
        btn_h = 56
        btn_x = self.width // 2 - btn_w // 2
        margin = 28
        btn_y = subtitle_y + subtitle.get_height() + margin
        start_button = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        # Elegant button: soft shadow, rounded, muted accent
        shadow_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, self.shadow, shadow_surf.get_rect(), border_radius=20)
        self.screen.blit(shadow_surf, (btn_x + 2, btn_y + 6))
        pygame.draw.rect(self.screen, self.accent_cyan, start_button, border_radius=20)
        btn_text = self.font_medium.render("Mulai", True, Colors.WHITE)
        self.screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + btn_h // 2 - btn_text.get_height() // 2))

        # Detailed gesture explanation area (per-gesture) below button
        gestures = [
            {"icon": "👍", "name": "Thumb Up", "key": "A", "desc": "Jempol naik - Pilih opsi A"},
            {"icon": "✋", "name": "Open Palm", "key": "B", "desc": "Telapak terbuka - Pilih opsi B"},
            {"icon": "✌️", "name": "Two Fingers", "key": "C", "desc": "Dua jari (V) - Pilih opsi C"},
            {"icon": "✊", "name": "Fist", "key": "D", "desc": "Genggaman - Pilih opsi D"},
        ]

        # Layout vertikal satu kolom di tengah bawah tombol
        card_w = int(self.width * 0.88)
        card_h = 78
        gap = 12
        gx = (self.width - card_w) // 2
        gy = btn_y + btn_h + 28
        for i, gesture in enumerate(gestures):
            x = gx
            y = gy + i * (card_h + gap)
            card_rect = pygame.Rect(x, y, card_w, card_h)
            # Card shadow
            card_shadow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_shadow, self.shadow, card_shadow.get_rect(), border_radius=16)
            self.screen.blit(card_shadow, (x + 2, y + 8))
            # Card background
            pygame.draw.rect(self.screen, self.card_bg, card_rect, border_radius=16)
            pygame.draw.rect(self.screen, self.card_border, card_rect, 1, border_radius=16)
            # Icon
            icon_s = self.font_medium.render(gesture["icon"], True, self.accent_cyan)
            self.screen.blit(icon_s, (card_rect.x + 18, card_rect.y + (card_rect.height - icon_s.get_height()) // 2))
            # Name
            name_s = self.font_small.render(f"{gesture['name']} ({gesture['key']})", True, Colors.WHITE)
            self.screen.blit(name_s, (card_rect.x + 78, card_rect.y + 14))
            # Description
            desc_s = self.font_tiny.render(gesture['desc'], True, self.accent_gray)
            self.screen.blit(desc_s, (card_rect.x + 78, card_rect.y + 40))
        # All broken/unused code below this block is removed for clarity and correctness

        pygame.display.flip()
        return start_button
    
    def draw_game(self, question_num, total_questions, image_surface, options, current_gesture=None, gesture_confidence=0, camera_frame=None):
        """Draw game screen in a TikTok-like style:
        - camera_frame as full background (maintain aspect ratio, no stretch)
        - translucent top panel with question/thumbnail
        - bottom semi-transparent option cards
        - floating gesture pill on right
        """
        # Background: camera preview fill (if available), fallback ke tema gelap menu
        if camera_frame:
            try:
                # Use preserve aspect ratio to avoid stretching
                bg = scale_preserve_aspect_ratio(camera_frame, self.width, self.height, self.bg_dark)
                self.screen.blit(bg, (0, 0))
            except Exception:
                self.screen.fill(self.bg_dark)
        else:
            self.screen.fill(self.bg_dark)

        # Draw film image at the absolute top center, larger and with border
        # dan simpan posisi bawah gambar untuk referensi panel
        img_bottom = 40  # default kalau tidak ada image
        if image_surface:
            img_rect = image_surface.get_rect()
            max_w, max_h = self.width // 2, 180
            scale = min(max_w / img_rect.width, max_h / img_rect.height, 1.0)
            img_size = (int(img_rect.width * scale), int(img_rect.height * scale))
            img_surf = pygame.transform.scale(image_surface, img_size)
            img_x = (self.width - img_size[0]) // 2
            img_y = 96  # geser lebih ke bawah agar blok konten mendekati tengah
            border_rect = pygame.Rect(img_x-6, img_y-6, img_size[0]+12, img_size[1]+12)
            pygame.draw.rect(self.screen, self.accent_cyan, border_rect, 4, border_radius=16)
            self.screen.blit(img_surf, (img_x, img_y))
            img_bottom = img_y + img_size[1] + 10

        # Draw top panel sedikit lebih turun; seluruh blok gambar+panel digeser ke bawah
        panel_h = 70
        panel_y = img_bottom + 40
        panel_w = int(self.width * 0.75)  # panel lebih pendek, lebih minimalis
        panel_x = (self.width - panel_w) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surf.fill(self.bg_panel + (220,))
        pygame.draw.rect(panel_surf, self.card_border, panel_surf.get_rect(), 1, border_radius=18)
        # Question info di tengah panel
        q_text = f"Soal {question_num}/{total_questions}"
        q_surf = self.font_large.render(q_text, True, self.accent_cyan)
        q_x = panel_rect.width // 2 - q_surf.get_width() // 2
        q_y = panel_rect.height // 2 - q_surf.get_height() // 2
        panel_surf.blit(q_surf, (q_x, q_y))
        self.screen.blit(panel_surf, (panel_rect.x, panel_rect.y))
        now = pygame.time.get_ticks()
        if self.state != self._last_state:
            self._state_change_time = now
            self._last_state = self.state
        # Define card layout variables untuk opsi, disusun agar memanfaatkan ruang kosong
        card_w = int(self.width * 0.72)  # lebar kartu opsi
        card_h = 56
        gap = 8
        base_start_y = panel_rect.bottom + 24

        raw_progress = min(1.0, (now - self._state_change_time) / 550.0)
        # ease-out cubic for smoother feel
        anim_progress = 1 - pow(1 - raw_progress, 3)
        slide_offset = int((1.0 - anim_progress) * 140)  # cards start lower and slide up

        # Hitung tinggi total stack card dan posisikan di tengah ruang antara panel dan bawah layar
        total_cards_h = len(options) * card_h + (len(options) - 1) * gap
        max_bottom = self.height - 40

        # ruang vertikal yang tersedia di bawah panel
        available_space = max_bottom - panel_rect.bottom
        # ideal_start: center-kan stack kartu di ruang available_space
        ideal_offset = max(16, (available_space - total_cards_h) // 2)
        start_y = panel_rect.bottom + ideal_offset

        # kalau masih overflow (misalnya pada layar sangat pendek), geser sedikit ke atas
        if start_y + total_cards_h > max_bottom:
            overflow = (start_y + total_cards_h) - max_bottom
            start_y = max(panel_rect.bottom + 16, start_y - overflow // 2)

        option_buttons = {}
        for idx, (key, text) in enumerate(options.items()):
            y = start_y + idx * (card_h + gap) + slide_offset
            card_x = (self.width - card_w) // 2
            card_rect = pygame.Rect(card_x, y, card_w, card_h)

            # Simple card tanpa shadow/box berlapis
            pygame.draw.rect(self.screen, self.card_bg, card_rect, border_radius=16)
            pygame.draw.rect(self.screen, self.card_border, card_rect, 1, border_radius=16)

            # Option text: left side large key, then option text
            key_surf = self.font_large.render(key, True, Colors.WHITE)
            self.screen.blit(key_surf, (card_rect.x + 36, card_rect.y + (card_h - key_surf.get_height()) // 2))

            txt_surf = self.font_small.render(text, True, Colors.LIGHT_GRAY)
            self.screen.blit(txt_surf, (card_rect.x + 130, card_rect.y + (card_h - txt_surf.get_height()) // 2))

            option_buttons[key] = card_rect

        pygame.display.flip()
        return option_buttons

    def _draw_gesture_legend(self, x=24, y=24):
        """Draw a small persistent legend showing gesture -> answer mapping"""
        legend_w = 260
        legend_h = 140
        rect = pygame.Rect(x, y, legend_w, legend_h)
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surf.fill((12, 12, 12, 180))
        pygame.draw.rect(surf, (255, 255, 255, 16), surf.get_rect(), border_radius=12)

        entries = [
            ("👍", "A"),
            ("✋", "B"),
            ("✌️", "C"),
            ("✊", "D"),
        ]
        ex = 12
        ey = 12
        for icon, key in entries:
            icon_s = self.font_small.render(icon, True, Colors.WHITE)
            key_s = self.font_tiny.render(key, True, Colors.LIGHT_GRAY)
            surf.blit(icon_s, (ex, ey))
            surf.blit(key_s, (ex + 40, ey + (icon_s.get_height() - key_s.get_height()) // 2))
            ey += icon_s.get_height() + 8

        self.screen.blit(surf, (rect.x, rect.y))

    def _draw_confetti(self, correct_answers, total_questions):
        """Draw a lightweight confetti effect determined by score."""
        # seed by score for deterministic effect during a session
        seed = int((correct_answers / max(1, total_questions)) * 1000)
        random.seed(seed + pygame.time.get_ticks() // 500)
        count = 40
        for i in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, int(self.height * 0.4))
            size = random.randint(4, 10)
            col = random.choice([self.accent_cyan, self.accent_pink, Colors.YELLOW, Colors.ORANGE])
            pygame.draw.circle(self.screen, col, (x, y), size)

    # ------------------ Particle + Decorative helpers ------------------
    def _spawn_particle(self, x=None, y=0):
        """Spawn a subtle floating particle for background depth"""
        if x is None:
            x = random.randint(0, self.width)
        part = {
            "x": float(x),
            "y": float(y if y else random.randint(0, int(self.height*0.4))),
            "vy": random.uniform(0.2, 0.8),
            "size": random.uniform(2.0, 6.0),
            "alpha": random.randint(30, 90),
            "life": random.randint(1800, 4200),
            "t": pygame.time.get_ticks()
        }
        self._particles.append(part)

    def _update_particles(self):
        now = pygame.time.get_ticks()
        keep = []
        for p in self._particles:
            dt = now - p["t"]
            p["y"] += p["vy"]
            # fade slowly
            life_ratio = dt / max(1, p["life"])
            if life_ratio < 1.0 and p["y"] < self.height * 0.9:
                keep.append(p)
        self._particles = keep

    def _draw_particles(self):
        for p in self._particles:
            a = max(8, min(255, int(p["alpha"])))
            col = (255, 255, 255, a)
            surf = pygame.Surface((int(p["size"]*2), int(p["size"]*2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, col, (int(p["size"]), int(p["size"])), int(p["size"]))
            self.screen.blit(surf, (int(p["x"] - p["size"]), int(p["y"] - p["size"])))

    def _draw_decorative_icons(self):
        # floating film icons at left/right edges
        t = pygame.time.get_ticks() / 800.0
        left_y = int(self.height * 0.28 + math.sin(t) * 18)
        right_y = int(self.height * 0.34 + math.cos(t*1.2) * 18)
        film = self.font_medium.render("🎬", True, Colors.WHITE)
        clap = self.font_medium.render("👏", True, Colors.WHITE)
        self.screen.blit(film, (36, left_y))
        self.screen.blit(clap, (self.width - 72, right_y))
    
    def draw_result(self, is_correct, answer_key, correct_answer, feedback_text=""):
        """Draw result screen after answering"""
        # Gunakan tema background gelap yang sama dengan menu
        self.screen.fill(self.bg_dark)
        
        if is_correct:
            result_color = Colors.GREEN
            result_text = "✓ BENAR!"
        else:
            result_color = Colors.RED
            result_text = "✗ SALAH!"
        
        # Result title
        result_rect = pygame.Rect(0, 150, self.width, 100)
        draw_text(self.screen, result_text, self.font_large, result_color, result_rect)
        
        # Feedback
        if feedback_text:
            feedback_surface = self.font_small.render(feedback_text, True, Colors.LIGHT_GRAY)
            feedback_rect = feedback_surface.get_rect(center=(self.width // 2, 300))
            self.screen.blit(feedback_surface, feedback_rect)
        
        # Show correct answer
        correct_text = f"Jawaban Benar: {correct_answer}"
        correct_surface = self.font_medium.render(correct_text, True, Colors.YELLOW)
        correct_rect = correct_surface.get_rect(center=(self.width // 2, 400))
        self.screen.blit(correct_surface, correct_rect)
        
        # Continue button (accent)
        continue_button = pygame.Rect(self.width // 2 - 150, 550, 300, 70)
        # custom styled button
        cb_surf = pygame.Surface((continue_button.width, continue_button.height), pygame.SRCALPHA)
        pygame.draw.rect(cb_surf, self.accent_cyan + (220,), cb_surf.get_rect(), border_radius=14)
        pygame.draw.rect(cb_surf, (255,255,255,18), cb_surf.get_rect(), width=2, border_radius=14)
        self.screen.blit(cb_surf, (continue_button.x, continue_button.y))
        label = self.font_medium.render("LANJUT", True, Colors.WHITE)
        self.screen.blit(label, (continue_button.x + (continue_button.width - label.get_width())//2,
                     continue_button.y + (continue_button.height - label.get_height())//2))
        
        pygame.display.flip()
        return continue_button
    
    def draw_game_over(self, score, total_questions, correct_answers):
        """Draw game over screen"""
        # Elegant flat background
        self.screen.fill(self.bg_dark)

        # Center score card
        card_w, card_h = int(self.width * 0.9), 260
        card_x = (self.width - card_w) // 2

        # Hitung posisi vertikal blok (card + tombol) agar lebih proporsional
        btn_w, btn_h = int(self.width * 0.6), 56
        spacing = 18
        total_block_h = card_h + 24 + btn_h * 2 + spacing
        card_y = (self.height - total_block_h) // 2
        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card.fill(self.bg_panel + (230,))
        pygame.draw.rect(card, self.card_border, card.get_rect(), border_radius=20)

        # Large percentage (centered at top)
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        perc_text = f"{percentage:.0f}%"
        perc_font = pygame.font.Font(None, 96)
        perc_surf = perc_font.render(perc_text, True, self.accent_cyan)
        perc_x = (card_w - perc_surf.get_width()) // 2
        perc_y = 22
        card.blit(perc_surf, (perc_x, perc_y))

        # Title under percentage
        title_s = self.font_large.render("Game Selesai", True, Colors.WHITE)
        title_x = (card_w - title_s.get_width()) // 2
        title_y = perc_y + perc_surf.get_height() + 8
        card.blit(title_s, (title_x, title_y))

        # Score details
        score_text = f"Skor: {score} / {total_questions}"
        score_s = self.font_medium.render(score_text, True, Colors.LIGHT_GRAY)
        score_x = (card_w - score_s.get_width()) // 2
        score_y = title_y + title_s.get_height() + 12
        card.blit(score_s, (score_x, score_y))

        correct_text = f"Jawaban Benar: {correct_answers}"
        corr_s = self.font_small.render(correct_text, True, Colors.LIGHT_GRAY)
        corr_x = (card_w - corr_s.get_width()) // 2
        corr_y = score_y + score_s.get_height() + 6
        card.blit(corr_s, (corr_x, corr_y))

        # Message / badge
        if percentage >= 80:
            message = "Luar Biasa! 🌟"
            badge_col = self.accent_cyan
        elif percentage >= 60:
            message = "Bagus! 👍"
            badge_col = self.accent_pink
        else:
            message = "Coba lagi! 💪"
            badge_col = (255, 165, 0)

        msg_s = self.font_medium.render(message, True, badge_col)
        msg_x = (card_w - msg_s.get_width()) // 2
        msg_y = corr_y + corr_s.get_height() + 10
        card.blit(msg_s, (msg_x, msg_y))

        # Draw card to screen
        self.screen.blit(card, (card_x, card_y))

        # Action buttons under card (dua tombol vertikal di tengah)
        bx = (self.width - btn_w) // 2
        by = card_y + card_h + 24

        # Retry button (atas)
        retry_btn = pygame.Rect(bx, by, btn_w, btn_h)
        retry_s = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(retry_s, (34, 34, 34, 220), retry_s.get_rect(), border_radius=14)
        pygame.draw.rect(retry_s, (255,255,255,18), retry_s.get_rect(), width=2, border_radius=14)
        self.screen.blit(retry_s, (retry_btn.x, retry_btn.y))
        r_label = self.font_medium.render("ULANGI", True, Colors.WHITE)
        self.screen.blit(r_label, (retry_btn.x + (btn_w - r_label.get_width())//2, retry_btn.y + (btn_h - r_label.get_height())//2))

        # Menu button (bawah)
        menu_btn = pygame.Rect(bx, by + btn_h + spacing, btn_w, btn_h)
        menu_s = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(menu_s, self.accent_pink + (220,), menu_s.get_rect(), border_radius=14)
        pygame.draw.rect(menu_s, (255,255,255,18), menu_s.get_rect(), width=2, border_radius=14)
        self.screen.blit(menu_s, (menu_btn.x, menu_btn.y))
        m_label = self.font_medium.render("KEMBALI KE MENU", True, Colors.WHITE)
        self.screen.blit(m_label, (menu_btn.x + (btn_w - m_label.get_width())//2, menu_btn.y + (btn_h - m_label.get_height())//2))

        pygame.display.flip()
        # Return both buttons so caller can handle clicks
        return retry_btn, menu_btn
    
    def draw_camera_preview(self, frame_surface, x=0, y=100):
        """Draw camera preview (for gesture detection)"""
        if frame_surface:
            self.screen.blit(frame_surface, (x, y))
            # Draw border dengan accent cyan agar konsisten dengan tema menu
            pygame.draw.rect(self.screen, self.accent_cyan, 
                           (x, y, frame_surface.get_width(), frame_surface.get_height()), 3)
    
    def load_image(self, image_path, max_width=400, max_height=400):
        """Load and scale image for display"""
        try:
            img = pygame.image.load(image_path)
            img.set_colorkey(Colors.BLACK)  # Remove black background if any
            
            # Scale image
            img_rect = img.get_rect()
            scale_factor = min(max_width / img_rect.width, max_height / img_rect.height)
            new_size = (int(img_rect.width * scale_factor), int(img_rect.height * scale_factor))
            img = pygame.transform.scale(img, new_size)
            
            return img
        except Exception as e:
            print(f"[ERROR] Gagal load image {image_path}: {e}")
            return None
    
    def quit(self):
        """Cleanup"""
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    ui = GameUI()
    
    # Test menu
    running = True
    while running:
        button = ui.draw_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(event.pos):
                    print("Start button clicked!")
        
        ui.clock.tick(60)
    
    ui.quit()
