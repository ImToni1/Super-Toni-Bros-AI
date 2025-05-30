# src/core/player.py

import pygame
import os

class Player:
    def __init__(self, x, y, width, height):
        scale_factor = 1.5
        original_width = int(width * scale_factor)
        original_height = int(height * scale_factor)

        self.rect = pygame.Rect(x, y, original_width, original_height)
        self.vel_y = 0
        self.on_ground = False
        self.facing_left = False

        # AŽURIRANA PUTANJA DO SLIKE
        base_path = os.path.dirname(os.path.abspath(__file__)) # src/core
        # Treba ići dva nivoa gore (do Super-Toni-Bros-AI) pa u images
        image_path = os.path.join(base_path, "..", "..", "images", "Player.png")


        try:
            self.image_right = pygame.image.load(image_path).convert_alpha()
            self.image_right = pygame.transform.scale(self.image_right, (original_width, original_height))
            self.image_left = pygame.transform.flip(self.image_right, True, False)
            self.image = self.image_right
        except pygame.error as e:
            print(f"Greška pri učitavanju slike igrača: {e}")
            print(f"Pokušana putanja: {image_path}")
            self.image = pygame.Surface((original_width, original_height))
            self.image.fill((255,0,0))
            self.image_right = self.image
            self.image_left = self.image


    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.on_ground = False
        self.facing_left = False
        self.image = self.image_right

    def jump(self, jump_strength):
        if self.on_ground:
            self.vel_y = jump_strength
            self.on_ground = False

    def apply_gravity(self, gravity):
        self.vel_y += gravity
        if self.vel_y > 15:
            self.vel_y = 15
        self.rect.y += int(self.vel_y)


    def collide_with_platform(self, platform_rect):
        if not self.rect.colliderect(platform_rect):
            return False

        previous_bottom = self.rect.bottom - int(self.vel_y)
        epsilon = 1

        if self.vel_y >= 0 and \
           self.rect.bottom >= platform_rect.top and \
           previous_bottom <= (platform_rect.top + epsilon):
            
            if self.rect.bottom > platform_rect.top:
                self.rect.bottom = platform_rect.top
                self.vel_y = 0
                self.on_ground = True
                return True

        previous_top = self.rect.top - int(self.vel_y)
        if self.vel_y < 0 and \
           self.rect.top <= platform_rect.bottom and \
           previous_top >= (platform_rect.bottom - epsilon):
            self.rect.top = platform_rect.bottom
            self.vel_y = 0
            return True
            
        return False


    def update_image_direction(self):
        if self.facing_left:
            self.image = self.image_left
        else:
            self.image = self.image_right

    def draw(self, screen):
        self.update_image_direction()
        screen.blit(self.image, (self.rect.x, self.rect.y))
