# src/player.py

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
        # Pretpostavljamo da su slike u 'images' direktoriju, jedan nivo iznad 'src'
        image_path = os.path.join(base_path, "..", "images", "Player.png")


        try:
            self.image_right = pygame.image.load(image_path).convert_alpha()
            self.image_right = pygame.transform.scale(self.image_right, (original_width, original_height))
            self.image_left = pygame.transform.flip(self.image_right, True, False)
            self.image = self.image_right
        except pygame.error as e:
            print(f"Greška pri učitavanju slike igrača: {e}")
            print(f"Pokušana putanja: {image_path}")
            # Kreiraj zamjensku površinu ako slika nije pronađena
            self.image = pygame.Surface((original_width, original_height))
            self.image.fill((255,0,0)) # Crvena boja za zamjensku sliku
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
        # Dopusti skok samo ako je igrač na tlu
        if self.on_ground:
            self.vel_y = jump_strength
            self.on_ground = False

    def apply_gravity(self, gravity):
        self.vel_y += gravity
        # Ograniči maksimalnu brzinu pada (opcionalno, ali korisno)
        if self.vel_y > 15: # Npr. maksimalna brzina pada od 15
            self.vel_y = 15
        self.rect.y += int(self.vel_y) # Eksplicitno pretvaranje u int, iako += to radi implicitno za Rect


    def collide_with_platform(self, platform_rect):
        if not self.rect.colliderect(platform_rect):
            return False

        # Izračunaj prethodni donji rub igrača (prije ovog framea)
        # self.vel_y je brzina koja JE UPRAVO primijenjena da dovede do trenutnog self.rect.bottom
        # Stoga, da dobijemo gdje je bio self.rect.bottom PRIJE ovog pomaka, oduzimamo self.vel_y
        # Ako je self.rect.y bio float, ovo bi bilo preciznije. Ovako radimo s int(self.vel_y) koji je korišten za pomak.
        previous_bottom = self.rect.bottom - int(self.vel_y) # Koristimo int(self.vel_y) jer je to ono što je dodano na rect.y

        # Tolerancija za provjeru previous_bottom. Ponekad float greške mogu uzrokovati da previous_bottom bude npr. 550.0001 umjesto 550.
        epsilon = 1  # 1 piksel tolerancije

        # Provjera kolizije odozgo (slijetanje na platformu)
        # Uvjet 1: Igrač se kreće prema dolje ili miruje (vel_y >= 0)
        # Uvjet 2: Donji rub igrača je sada na ili ispod vrha platforme
        # Uvjet 3: Prethodni donji rub igrača bio je na ili IZNAD vrha platforme (ili unutar epsilon tolerancije)
        #            Ovo sprječava "hvatanje" za platformu ako igrač prolazi pored nje odozdo prema gore i onda počne padati unutar nje.
        
        # DEBUG ISPISI (ako su i dalje potrebni, otkomentiraj)
        # print(f"Collision Check: PlayerVelY={self.vel_y:.2f}, PlayerBottom={self.rect.bottom}, PlatformTop={platform_rect.top}, PrevBottomCalc={previous_bottom}")
        # cond1 = self.vel_y >= 0
        # cond2 = self.rect.bottom >= platform_rect.top
        # cond3 = previous_bottom <= platform_rect.top + epsilon # DODANA TOLERANCIJA
        # print(f"  Conditions: VelOk={cond1}, BottomOk={cond2}, PrevBottomOk={cond3} (PrevBottom={previous_bottom} <= PlatformTop+Epsilon={platform_rect.top + epsilon})")

        if self.vel_y >= 0 and \
           self.rect.bottom >= platform_rect.top and \
           previous_bottom <= (platform_rect.top + epsilon): # <-- IZMJENA: dodan epsilon
            
            # Dodatna provjera: Osiguraj da igrač nije preduboko u platformi prije nego ga "snapamo" na vrh.
            # Ako je igrač već npr. na pola puta kroz platformu, možda je došlo do tuneliranja.
            # Za sada, držimo se jednostavnog snap-a.
            if self.rect.bottom > platform_rect.top: # Samo ako je stvarno probio ili je na istoj razini
                self.rect.bottom = platform_rect.top
                self.vel_y = 0
                self.on_ground = True
                # print(f"  LANDED on platform {platform_rect}") # DEBUG
                return True

        # Provjera kolizije s donje strane platforme (ako igrač skače prema gore)
        previous_top = self.rect.top - int(self.vel_y) # Koristimo int(self.vel_y)
        if self.vel_y < 0 and \
           self.rect.top <= platform_rect.bottom and \
           previous_top >= (platform_rect.bottom - epsilon): # Tolerancija i ovdje
            self.rect.top = platform_rect.bottom
            self.vel_y = 0 # Zaustavi kretanje prema gore (udarac glavom)
            # print(f"  HIT HEAD on platform {platform_rect}") # DEBUG
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
        # Crtanje crvenog pravokutnika oko igrača za vizualni prikaz kolizijskog boxa
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)