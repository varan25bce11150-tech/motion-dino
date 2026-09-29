# game/obstacle.py
import pygame
import os
from game.settings import GROUND_HEIGHT, OBSTACLE_COLOR

class GroundTree:
    def __init__(self, x, speed):
        self.x = x
        self.width = 36
        self.height = 54
        self.y = GROUND_HEIGHT - self.height
        self.speed = speed
        self.type = "tree"
        
        image_path = os.path.join("assets", "tree.png")
        if os.path.exists(image_path):
            raw = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw, (self.width, self.height))
        else:
            self.image = None

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            # Procedural Tree / Cactus Fallback
            pygame.draw.rect(surface, (34, 139, 34), self.rect, border_radius=4)
            # Branch details
            pygame.draw.rect(surface, (34, 139, 34), (self.x - 6, self.y + 14, 8, 12), border_radius=2)
            pygame.draw.rect(surface, (34, 139, 34), (self.x + self.width - 2, self.y + 22, 8, 12), border_radius=2)


class FlyingDino:
    def __init__(self, x, speed):
        self.x = x
        self.width = 46
        self.height = 36
        # Flying height positioned so player must time their jump accurately
        self.y = GROUND_HEIGHT - 65
        self.speed = speed + 1.0  # Moves slightly faster than ground obstacles
        self.type = "flying"
        
        self.anim_frame = 0
        self.anim_timer = 0
        
        # Load wing flap animation frames
        self.frames = []
        img1 = os.path.join("assets", "bird1.png")
        img2 = os.path.join("assets", "bird2.png")
        if os.path.exists(img1) and os.path.exists(img2):
            f1 = pygame.transform.scale(pygame.image.load(img1).convert_alpha(), (self.width, self.height))
            f2 = pygame.transform.scale(pygame.image.load(img2).convert_alpha(), (self.width, self.height))
            self.frames = [f1, f2]

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x
        
        # Animate wing flap
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_frame = (self.anim_frame + 1) % 2
            self.anim_timer = 0

    def draw(self, surface):
        if self.frames:
            surface.blit(self.frames[self.anim_frame], (self.x, self.y))
        else:
            # Procedural Flying Dino Fallback
            color = (200, 50, 50)
            pygame.draw.ellipse(surface, color, self.rect)
            
            # Flapping Wing
            wing_y = self.y - 10 if self.anim_frame == 0 else self.y + 14
            pygame.draw.polygon(surface, (160, 30, 30), [
                (self.x + 18, self.y + 18),
                (self.x + 28, wing_y),
                (self.x + 36, self.y + 18)
            ])