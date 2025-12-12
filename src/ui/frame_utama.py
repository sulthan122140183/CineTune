import sys
import os
import cv2
import pygame
import numpy as np
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_loader import load_questions, load_gesture_map
from core.game_manager import GameManager, GamePhase
from core.audio_player import AudioPlayer
from ui.tampilan import GameUI, GameState
from vision.gesture_detector import GestureDetector
from vision.gesture_mapper import GestureMapper

# ==========================================
# MAIN APPLICATION CLASS
# ==========================================
class CineTuneApp:
    def __init__(self):
        """Initialize the application"""
        # Get base directory
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.last_question_id = None
        # Initialize pygame
        pygame.init()
        
        # Initialize components
        print("[INIT] Loading data...")
        self.questions = load_questions()
        self.gesture_map = load_gesture_map()
        
        print(f"[INIT] Loaded {len(self.questions)} questions")
        print(f"[INIT] Gesture map: {self.gesture_map}")
        
        # Initialize managers
        self.game_manager = GameManager(self.questions)
        self.audio_player = AudioPlayer()
        self.ui = GameUI()
        
        # Initialize vision components
        print("[INIT] Initializing gesture detection...")
        self.gesture_detector = GestureDetector()
        self.gesture_mapper = GestureMapper()
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("[WARNING] Camera tidak tersedia!")
        
        # Game state
        self.running = True
        self.current_gesture = None
        self.last_gesture_time = 0
        self.gesture_hold_time = 0.5  # seconds to hold gesture before registering
        
        # Result state
        self.showing_result = False
        self.result_data = None
        self.result_timer = 0
        self.result_show_duration = 2.0  # seconds

        # <<< ADDED: state untuk melacak audio pertanyaan yang sudah diputar
        self.last_question_index_for_audio = None
        # <<< END ADDED
        
        print("[INIT] CineTune initialized successfully!")
    
    def get_camera_frame(self):
        """Get current camera frame with gesture detection"""
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None
        
        # Flip frame
        frame = cv2.flip(frame, 1)
        # Detect landmarks on original (non-blurred) frame so detection is accurate
        landmarks, annotated = self.gesture_detector.detect(frame)

        # Map to gesture
        gesture = None
        if landmarks:
            gesture = self.gesture_mapper.map(landmarks)

        # Prepare a blurred copy for display (soft background / filter look)
        try:
            display_frame = annotated.copy()
            # Apply Gaussian blur for background aesthetic
            display_frame = cv2.GaussianBlur(display_frame, (21, 21), 0)
        except Exception:
            display_frame = annotated

        # Convert display frame to pygame surface
        frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.transpose(frame_rgb, (1, 0, 2))
        frame_surface = pygame.surfarray.make_surface(frame_rgb)

        return frame_surface, gesture, annotated
    
    def handle_menu_state(self):
        """Handle menu state"""
        button = self.ui.draw_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(event.pos):
                    print("[GAME] Starting game...")
                    self.game_manager.start_game()
                    # <<< ADDED: reset penanda audio saat mulai game baru
                    self.last_question_index_for_audio = None
                    # <<< END ADDED
                    self.ui.state = GameState.GAME
    
    def handle_game_state(self):
        """Handle game state"""
        # <<< TIMER-ADD: update timer 10 detik per soal >>>
        self.game_manager.update_timer(self.audio_player)
        # <<< END TIMER-ADD >>>
        if self.game_manager.is_game_over():
            self.ui.state = GameState.GAME_OVER
            return
        
        # Get current question
        current_q = self.game_manager.get_current_question()
        if not current_q:
            return

        # <<< ADDED: putar audio pertanyaan hanya sekali per question
        current_index = self.game_manager.current_question_idx
        if current_index != self.last_question_index_for_audio:
            audio_path = current_q.get("audio")
            if audio_path:
                print(f"[AUDIO] Play question audio: {audio_path}")
                self.audio_player.stop()  # hentikan audio sebelumnya
                self.audio_player.play_question_audio(audio_path)
            self.last_question_index_for_audio = current_index
        # <<< END ADDED
        
        # Get camera frame
        frame_surface, gesture, raw_frame = self.get_camera_frame()
        
        # Update current gesture
        self.current_gesture = gesture
        
        # Load and display question image
        question_image = self.ui.load_image(current_q["image"], max_width=400, max_height=400)
        
        # Draw game screen
        question_num = self.game_manager.get_current_question_number()
        total_questions = self.game_manager.get_total_questions()
        
        self.ui.draw_game(
            question_num=question_num,
            total_questions=total_questions,
            image_surface=question_image,
            options=current_q["options"],
            current_gesture=gesture,
            gesture_confidence=0.8 if gesture else 0,
            camera_frame=frame_surface
        )
        
        # Handle events and gesture detection
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # DEBUG: Manual answer submission with keys
                elif event.key in [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d]:
                    answer_map = {pygame.K_a: 'A', pygame.K_b: 'B', pygame.K_c: 'C', pygame.K_d: 'D'}
                    answer = answer_map[event.key]
                    print(f"[GAME] Answer submitted (DEBUG): {answer}")
                    self.submit_answer(answer)
        
        # Check if gesture was held long enough
        if gesture:
            import time
            current_time = time.time()
            
            if gesture != self.last_gesture:
                self.last_gesture = gesture
                self.gesture_hold_start = current_time
            elif (current_time - self.gesture_hold_start) >= self.gesture_hold_time:
                # Gesture held long enough, submit answer
                print(f"[GAME] Answer submitted: {gesture}")
                self.submit_answer(gesture)
                self.current_gesture = None
                self.last_gesture = None
    
    def submit_answer(self, gesture_answer):
        """Submit an answer"""
        if gesture_answer not in ['A', 'B', 'C', 'D']:
            return
        
        result = self.game_manager.submit_answer(gesture_answer)
        if result:
            print(f"[RESULT] {result}")

            # <<< TIMER-IMPORTANT: stop audio soal dulu >>>
            self.audio_player.stop()
            # <<< END ADDED >>>

            # Play audio feedback (correct / wrong)
            if result["is_correct"]:
                self.audio_player.play_correct_sound(self.base_dir)
            else:
                self.audio_player.play_wrong_sound(self.base_dir)
            
            self.showing_result = True
            self.result_data = result
            self.result_timer = 0
            self.ui.state = GameState.RESULT

    
    def handle_result_state(self):
        """Handle result state"""
        if not self.result_data:
            return
        
        current_q = self.game_manager.get_current_question()
        if not current_q:
            return
        
        # Load question image
        question_image = self.ui.load_image(current_q["image"], max_width=400, max_height=400)
        
        # Show result
        button = self.ui.draw_result(
            is_correct=self.result_data["is_correct"],
            answer_key=self.result_data["user_answer"],
            correct_answer=self.result_data["correct_answer"],
            feedback_text=f"Jawaban kamu: {self.result_data['user_answer']}"
        )
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(event.pos):
                    print("[GAME] Moving to next question...")
                    self.game_manager.next_question()
                    self.result_data = None
                    self.showing_result = False
                    
                    if self.game_manager.is_game_over():
                        self.ui.state = GameState.GAME_OVER
                    else:
                        self.ui.state = GameState.GAME
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("[GAME] Moving to next question...")
                    self.game_manager.next_question()
                    self.result_data = None
                    self.showing_result = False
                    
                    if self.game_manager.is_game_over():
                        self.ui.state = GameState.GAME_OVER
                    else:
                        self.ui.state = GameState.GAME
    
    def handle_game_over_state(self):
        """Handle game over state"""
        stats = self.game_manager.get_stats()
        
        retry_btn, menu_btn = self.ui.draw_game_over(
            score=stats["score"],
            total_questions=stats["total_questions"],
            correct_answers=stats["score"]
        )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    print("[GAME] Retry game from start...")
                    self.game_manager.reset()
                    self.game_manager.start_game()
                    self.ui.state = GameState.GAME
                elif menu_btn.collidepoint(event.pos):
                    print("[GAME] Returning to menu...")
                    self.game_manager.reset()
                    self.ui.state = GameState.MENU
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("[GAME] Returning to menu...")
                    self.game_manager.reset()
                    self.ui.state = GameState.MENU
    
    def run(self):
        """Main game loop"""
        import time
        
        self.last_gesture = None
        self.gesture_hold_start = time.time()
        
        while self.running:
            if self.ui.state == GameState.MENU:
                self.handle_menu_state()
            elif self.ui.state == GameState.GAME:
                self.handle_game_state()
            elif self.ui.state == GameState.RESULT:
                self.handle_result_state()
            elif self.ui.state == GameState.GAME_OVER:
                self.handle_game_over_state()
            
            self.ui.clock.tick(60)
    
    def cleanup(self):
        """Cleanup resources"""
        print("[CLEANUP] Cleaning up resources...")
        if self.cap:
            self.cap.release()
        self.audio_player.quit()
        self.ui.quit()
        cv2.destroyAllWindows()
        pygame.quit()
        print("[CLEANUP] Done!")


if __name__ == "__main__":
    try:
        app = CineTuneApp()
        app.run()
    except Exception as e:
        print(f"[ERROR] Application error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            app.cleanup()
        except:
            pass
