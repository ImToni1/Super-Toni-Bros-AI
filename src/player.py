# src/player.py - AŽURIRANI KOD (KLJUČNO ZA KOLIZIJU)

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

        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_path, "../images/Player.png")

        self.image_right = pygame.image.load(image_path).convert_alpha()
        self.image_right = pygame.transform.scale(self.image_right, (original_width, original_height))
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right

    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.on_ground = False
        self.facing_left = False
        self.image = self.image_right

    def jump(self, jump_strength):
        self.vel_y = jump_strength
        self.on_ground = False

    def apply_gravity(self, gravity):
        self.vel_y += gravity
        self.rect.y += self.vel_y

    def collide_with_platform(self, platform_rect):
        # Provjeravamo koliziju s platformom općenito
        if not self.rect.colliderect(platform_rect):
            return False

        # Ako igrač pada (vel_y > 0)
        # I donji dio igrača je PRELAZIO ili je upravo na vrhu platforme
        # I gornji dio igrača je iznad vrha platforme (da spriječimo koliziju odozdo)
        if self.vel_y >= 0 and \
           self.rect.bottom >= platform_rect.top and \
           self.rect.top < platform_rect.top: # Dodatna provjera: igračev vrh je iznad platforme

            # Provjerite da li igrač pada na vrh platforme (nije s boka)
            # Dno igrača je bilo iznad platforme u prošlom koraku i sada je ispod ili na njoj
            # Ovo rješava problem "probijanja" ako se igrač kreće prebrzo
            player_bottom_at_prev_frame_y = self.rect.y - self.vel_y + self.rect.height

            if player_bottom_at_prev_frame_y <= platform_rect.top:
                self.rect.bottom = platform_rect.top # Postavi igrača točno na vrh platforme
                self.vel_y = 0 # Zaustavi vertikalno kretanje
                self.on_ground = True # Igrač je na zemlji
                return True
        
        # Ako igrač ide gore i udara platformu odozdo
        if self.vel_y < 0 and \
           self.rect.top <= platform_rect.bottom and \
           self.rect.bottom > platform_rect.bottom:
            self.rect.top = platform_rect.bottom # Postavi igrača točno ispod platforme
            self.vel_y = 0 # Zaustavi vertikalno kretanje
            return True # Vrati True jer je došlo do kolizije

        return False # Nema kolizije odozgo (tj. kolizija s boka)


    def update_image_direction(self):
        if self.facing_left:
            self.image = self.image_left
        else:
            self.image = self.image_right

    def draw(self, screen):
        self.update_image_direction()
        screen.blit(self.image, (self.rect.x, self.rect.y))