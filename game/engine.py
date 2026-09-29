# game/engine.py
import pygame
import cv2
import random
from game.settings import *
from game.dino import Dino
from game.obstacle import GroundTree, FlyingDino
from game.background import BackgroundManager
from vision.camera import Camera
from vision.gesture import GestureDetector

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("MotionDino ")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier", 20, bold=True)
        self.large_font = pygame.font.SysFont("Courier", 28, bold=True)
        
        # Subsystems
        self.background = BackgroundManager()
        self.camera = Camera(camera_index=0, width=640, height=480)
        self.detector = GestureDetector()
        self.use_webcam = self.camera.is_available()
        
        self.reset_game()
        self.state = "START"
        self.high_score = 0
        self.last_action = "NEUTRAL"

    def reset_game(self):
        self.dino = Dino()
        self.obstacles = []
        self.score = 0
        self.game_speed = 8
        self.spawn_timer = 0
        self.last_action = "NEUTRAL"

    def cv_frame_to_surface(self, frame, width=160, height=120):
        resized = cv2.resize(frame, (width, height))
        rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        return pygame.image.frombuffer(rgb_frame.tobytes(), (width, height), "RGB")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                if self.state == "START":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.state = "CALIBRATE" if self.use_webcam else "PLAY"
                        if not self.use_webcam:
                            self.reset_game()
                            
                elif self.state == "GAMEOVER":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.reset_game()
                        self.state = "PLAY"
                
                elif self.state == "PLAY":
                    if event.key in [pygame.K_SPACE, pygame.K_UP]:
                        self.dino.jump()
                        self.last_action = "KEY JUMP"

        return True

    def process_vision(self):
        if not self.use_webcam:
            return None

        frame = self.camera.get_frame()
        if frame is None:
            return None

        results, annotated_frame = self.detector.process_frame(frame)

        if results and results.pose_landmarks:
            landmarks = results.pose_landmarks

            if self.state == "CALIBRATE":
                if self.detector.calibrate(landmarks):
                    self.reset_game()
                    self.state = "PLAY"

            elif self.state == "PLAY":
                if self.detector.detect_jump(landmarks):
                    self.dino.jump()
                    self.last_action = "MOTION JUMP"
                elif not self.dino.is_jumping:
                    self.last_action = "NEUTRAL"

        return annotated_frame

    def update(self):
        # Update background with score to trigger day/night cycle
        self.background.update(self.game_speed if self.state == "PLAY" else 2, self.score)
        
        if self.state != "PLAY":
            return

        self.dino.update()
        
        # Spawn Obstacles
        self.spawn_timer += 1
        if self.spawn_timer > max(35, 90 - int(self.game_speed * 2)):
            if random.randint(0, 10) > 3:
                if self.score > 100 and random.random() < 0.35:
                    self.obstacles.append(FlyingDino(WIDTH, self.game_speed))
                else:
                    self.obstacles.append(GroundTree(WIDTH, self.game_speed))
                self.spawn_timer = 0

        # Update obstacles
        for obs in self.obstacles[:]:
            obs.update()
            
            # Collision Check
            if self.dino.rect.colliderect(obs.rect):
                self.state = "GAMEOVER"
                if self.score > self.high_score:
                    self.high_score = self.score
            
            # Clear passed obstacles & update score
            if obs.x < -obs.width:
                self.obstacles.remove(obs)
                self.score += 10
                if self.score % 150 == 0:
                    self.game_speed += 0.5

    def draw(self, frame_pip=None):
        # Draw sky, moon, stars, clouds, ground
        self.background.draw(self.screen)
        
        # Dynamic text color matching day/night mode
        text_color = self.background.get_text_color()
        
        if self.state == "START":
            title = self.large_font.render("MOTION DINO", True, text_color)
            prompt = self.font.render("Press SPACE / ENTER to Start", True, text_color)
            mode = self.font.render("Mode: WEBCAM" if self.use_webcam else "Mode: KEYBOARD ONLY", True, text_color)
            
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2))
            self.screen.blit(mode, (WIDTH//2 - mode.get_width()//2, HEIGHT//2 + 45))

        elif self.state == "CALIBRATE":
            msg = self.large_font.render("CALIBRATING BODY POSITION...", True, (230, 60, 60))
            sub = self.font.render("Stand still facing your camera", True, text_color)
            self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//3))
            self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2))

        elif self.state in ["PLAY", "GAMEOVER"]:
            self.dino.draw(self.screen)
            for obs in self.obstacles:
                obs.draw(self.screen)
                
            score_txt = self.font.render(f"SCORE: {int(self.score)}  HI: {int(self.high_score)}", True, text_color)
            self.screen.blit(score_txt, (20, 20))
            
            if self.state == "GAMEOVER":
                over = self.large_font.render("GAME OVER", True, (230, 60, 60))
                restart = self.font.render("Press SPACE to Restart", True, text_color)
                self.screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//3))
                self.screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2))

        # Camera PiP Overlay
        if frame_pip is not None:
            pip_surf = self.cv_frame_to_surface(frame_pip, width=160, height=120)
            pip_x, pip_y = WIDTH - 170, 10
            pygame.draw.rect(self.screen, text_color, (pip_x - 2, pip_y - 2, 164, 124), 2)
            self.screen.blit(pip_surf, (pip_x, pip_y))
            
            action_txt = self.font.render(f"ACTION: {self.last_action}", True, (230, 60, 60))
            self.screen.blit(action_txt, (pip_x, pip_y + 128))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            frame_pip = self.process_vision()
            self.update()
            self.draw(frame_pip)
            self.clock.tick(FPS)
            
        self.camera.release()
        pygame.quit()