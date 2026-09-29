# game/background.py
import pygame
import os
import random
import math
from game.settings import WIDTH, GROUND_HEIGHT

def lerp_color(c1, c2, t):
    """Linear interpolation between two RGB colors based on factor t (0.0 to 1.0)."""
    t = max(0.0, min(1.0, t))
    return (
        max(0, min(255, int(c1[0] + (c2[0] - c1[0]) * t))),
        max(0, min(255, int(c1[1] + (c2[1] - c1[1]) * t))),
        max(0, min(255, int(c1[2] + (c2[2] - c1[2]) * t))),
    )

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(10, GROUND_HEIGHT - 60)
        self.size = random.choice([1, 2, 2, 3])
        self.twinkle_speed = random.uniform(0.02, 0.08)
        self.twinkle_phase = random.uniform(0, math.pi * 2)

    def draw(self, surface, night_factor):
        if night_factor <= 0.05:
            return
        
        self.twinkle_phase += self.twinkle_speed
        # Safe brightness range (0 to 255)
        brightness = max(0, min(255, int(128 + 127 * math.sin(self.twinkle_phase))))
        # Scale brightness with night factor so stars fade in/out smoothly
        final_brightness = max(0, min(255, int(brightness * night_factor)))
        
        color = (final_brightness, final_brightness, final_brightness)
        pygame.draw.circle(surface, color, (self.x, self.y), self.size)


class Cloud:
    def __init__(self):
        self.x = WIDTH + random.randint(0, 300)
        self.y = random.randint(30, 120)
        self.speed = random.uniform(1.2, 2.5)
        self.width = 60
        self.height = 25
        
        image_path = os.path.join("assets", "cloud.png")
        if os.path.exists(image_path):
            raw_img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw_img, (self.width, self.height))
        else:
            self.image = None

    def update(self):
        self.x -= self.speed

    def draw(self, surface, night_factor):
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            color = lerp_color((210, 210, 210), (70, 75, 95), night_factor)
            pygame.draw.ellipse(surface, color, (self.x, self.y, 40, 20))
            pygame.draw.ellipse(surface, color, (self.x + 15, self.y - 8, 30, 20))
            pygame.draw.ellipse(surface, color, (self.x + 25, self.y, 35, 18))


class BackgroundManager:
    def __init__(self):
        self.clouds = [Cloud() for _ in range(4)]
        self.stars = [Star() for _ in range(30)]
        self.ground_offset = 0
        
        self.night_factor = 0.0  
        self.target_night_factor = 0.0
        
        self.DAY_SKY = (247, 247, 247)
        self.NIGHT_SKY = (20, 24, 40)
        
        self.DAY_TEXT = (30, 30, 30)
        self.NIGHT_TEXT = (235, 235, 240)
        
        self.DAY_GROUND = (80, 80, 80)
        self.NIGHT_GROUND = (180, 180, 200)

    def update(self, game_speed, score=0):
        for cloud in self.clouds:
            cloud.update()
            if cloud.x < -100:
                cloud.x = WIDTH + random.randint(50, 200)
                cloud.y = random.randint(30, 120)
                
        self.ground_offset = (self.ground_offset + game_speed) % 40
        
        # Day/Night switch every 400 points
        if score > 0 and (score // 400) % 2 == 1:
            self.target_night_factor = 1.0
        else:
            self.target_night_factor = 0.0
            
        if self.night_factor < self.target_night_factor:
            self.night_factor = min(1.0, self.night_factor + 0.01)
        elif self.night_factor > self.target_night_factor:
            self.night_factor = max(0.0, self.night_factor - 0.01)

    def get_text_color(self):
        return lerp_color(self.DAY_TEXT, self.NIGHT_TEXT, self.night_factor)

    def draw(self, surface):
        sky_color = lerp_color(self.DAY_SKY, self.NIGHT_SKY, self.night_factor)
        surface.fill(sky_color)
        
        for star in self.stars:
            star.draw(surface, self.night_factor)
            
        if self.night_factor > 0.1:
            moon_x, moon_y = WIDTH - 120, 60
            moon_color = lerp_color(self.DAY_SKY, (240, 240, 210), self.night_factor)
            pygame.draw.circle(surface, moon_color, (moon_x, moon_y), 18)
            pygame.draw.circle(surface, sky_color, (moon_x + 7, moon_y - 4), 15)

        for cloud in self.clouds:
            cloud.draw(surface, self.night_factor)
            
        ground_color = lerp_color(self.DAY_GROUND, self.NIGHT_GROUND, self.night_factor)
        pygame.draw.line(surface, ground_color, (0, GROUND_HEIGHT), (WIDTH, GROUND_HEIGHT), 2)
        
        bump_color = lerp_color((180, 180, 180), (100, 100, 120), self.night_factor)
        for x in range(-20, WIDTH + 40, 40):
            draw_x = x - int(self.ground_offset)
            pygame.draw.line(surface, bump_color, (draw_x, GROUND_HEIGHT + 6), (draw_x + 10, GROUND_HEIGHT + 6), 2)