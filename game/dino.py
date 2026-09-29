# game/dino.py
import pygame
import os
from game.settings import GROUND_HEIGHT, GRAVITY, JUMP_VELOCITY, DINO_COLOR

class Dino:
    def __init__(self):
        self.width = 48
        self.height = 52
        self.x = 50
        self.y = GROUND_HEIGHT - self.height
        
        self.vel_y = 0
        self.is_jumping = False
        
        # Animation state
        self.anim_frame = 0
        self.anim_timer = 0
        
        # Load Animation Images
        self.frames = []
        img1 = os.path.join("assets", "dino_run1.png")
        img2 = os.path.join("assets", "dino_run2.png")
        
        if os.path.exists(img1) and os.path.exists(img2):
            f1 = pygame.transform.scale(pygame.image.load(img1).convert_alpha(), (self.width, self.height))
            f2 = pygame.transform.scale(pygame.image.load(img2).convert_alpha(), (self.width, self.height))
            self.frames = [f1, f2]
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_VELOCITY
            self.is_jumping = True

    def update(self):
        # Physics
        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self.y >= GROUND_HEIGHT - self.height:
            self.y = GROUND_HEIGHT - self.height
            self.vel_y = 0
            self.is_jumping = False

        # Update animation timer
        self.anim_timer += 1
        if self.anim_timer >= 6:  # Toggle frame every 6 ticks
            self.anim_frame = (self.anim_frame + 1) % 2
            self.anim_timer = 0

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface):
        if self.frames:
            surface.blit(self.frames[self.anim_frame], (self.x, self.y))
        else:
            # Procedural Animated Dino Fallback
            pygame.draw.rect(surface, DINO_COLOR, self.rect, border_radius=6)
            
            # Draw eyes
            pygame.draw.circle(surface, (255, 255, 255), (self.x + 36, self.y + 12), 4)
            pygame.draw.circle(surface, (0, 0, 0), (self.x + 38, self.y + 12), 2)
            
            # Animate legs when running
            leg_offset = 6 if self.anim_frame == 0 else -6
            if not self.is_jumping:
                pygame.draw.rect(surface, (40, 40, 40), (self.x + 10, self.y + self.height, 6, 8 + leg_offset))
                pygame.draw.rect(surface, (40, 40, 40), (self.x + 28, self.y + self.height, 6, 8 - leg_offset))
            else:
                # Tucked legs during jump
                pygame.draw.rect(surface, (40, 40, 40), (self.x + 12, self.y + self.height, 6, 4))
                pygame.draw.rect(surface, (40, 40, 40), (self.x + 26, self.y + self.height, 6, 4))