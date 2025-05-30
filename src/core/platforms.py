# src/core/platforms.py
import pygame
import os

class PlatformManager:
    FIXED_PLATFORM_HEIGHT = 30

    def __init__(self, screen_width, screen_height, level_filepath):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.level_filepath = level_filepath # Putanja se prosljeđuje
        self.platforms = []
        self.goal = None

        # AŽURIRANE PUTANJE DO SLIKA
        base_path = os.path.dirname(os.path.abspath(__file__)) # src/core
        
        try:
            # Treba ići dva nivoa gore (do Super-Toni-Bros-AI) pa u images
            self.platform_image_original = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Platforms.png")).convert_alpha()
            self.ground_image_original = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Ground.png")).convert_alpha()
            self.flag_image = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Flag.png")).convert_alpha()
            self.flag_image = pygame.transform.scale(self.flag_image, (160, 160))
        except pygame.error as e:
            print(f"KRITIČNA GREŠKA pri učitavanju slika u PlatformManager: {e}")
            # Ispis putanja koje su se pokušale učitati
            print(f"  Pokušana putanja za Platforme: {os.path.join(base_path, '..', '..', 'images', 'Platforms.png')}")
            print(f"  Pokušana putanja za Tlo: {os.path.join(base_path, '..', '..', 'images', 'Ground.png')}")
            print(f"  Pokušana putanja za Zastavu: {os.path.join(base_path, '..', '..', 'images', 'Flag.png')}")
            self.platform_image_original = None
            self.ground_image_original = None
            self.flag_image = None

    def _load_platforms_from_file(self):
        loaded_platforms = []
        try:
            # self.level_filepath je već potpuna putanja proslijeđena iz start.py ili main_ai.py
            with open(self.level_filepath, 'r') as f:
                for line_idx, line in enumerate(f):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) == 3: # x,y,sirina
                            try:
                                x = int(parts[0])
                                y = int(parts[1])
                                width = int(parts[2])
                                height = PlatformManager.FIXED_PLATFORM_HEIGHT # Koristi fiksnu visinu
                                loaded_platforms.append(pygame.Rect(x, y, width, height))
                            except ValueError:
                                print(f"Preskačem neispravan redak br. {line_idx+1} u {self.level_filepath}: '{line}' (ValueError)")
                        elif len(parts) == 4: # x,y,sirina,visina (stari format, ignoriraj visinu)
                             try:
                                x = int(parts[0])
                                y = int(parts[1])
                                width = int(parts[2])
                                # height = int(parts[3]) # Ignoriramo učitanu visinu
                                height = PlatformManager.FIXED_PLATFORM_HEIGHT # Koristi fiksnu visinu
                                loaded_platforms.append(pygame.Rect(x, y, width, height))
                                print(f"Upozorenje: Redak br. {line_idx+1} u {self.level_filepath} ima 4 vrijednosti. Koristim fiksnu visinu platforme.")
                             except ValueError:
                                print(f"Preskačem neispravan redak br. {line_idx+1} u {self.level_filepath}: '{line}' (ValueError za 4 dijela)")
                        else:
                            print(f"Preskačem redak br. {line_idx+1} s netočnim brojem vrijednosti u {self.level_filepath}: '{line}'. Očekivano: x,y,sirina")
        except FileNotFoundError:
            print(f"GREŠKA: Datoteka s razinom '{self.level_filepath}' nije pronađena.")
        return loaded_platforms

    def generate_platforms(self):
        self.platforms = []
        
        start_ground_initial_x = -200
        start_ground_visible_width = 300
        start_ground_width = start_ground_visible_width + abs(start_ground_initial_x)
        starting_ground_y = self.screen_height - 50
        starting_ground_height = 50
        starting_ground = pygame.Rect(start_ground_initial_x, starting_ground_y, start_ground_width, starting_ground_height)
        self.platforms.append(starting_ground)

        right_invisible_wall_width = 10
        right_invisible_wall_x = starting_ground.right
        right_invisible_wall = pygame.Rect(right_invisible_wall_x, starting_ground.top, right_invisible_wall_width, starting_ground.height)
        self.platforms.append(right_invisible_wall)

        left_wall_width = 10
        left_wall_x = start_ground_initial_x - left_wall_width
        left_wall = pygame.Rect(left_wall_x, 0, left_wall_width, self.screen_height)
        self.platforms.append(left_wall)

        platforms_from_file = self._load_platforms_from_file()
        self.platforms.extend(platforms_from_file)

        if platforms_from_file:
            target_platform = platforms_from_file[-1]
            goal_width = 160
            goal_height = 160
            goal_x = target_platform.x + (target_platform.width - goal_width) // 2
            goal_y = target_platform.y - goal_height
            self.goal = pygame.Rect(goal_x, goal_y, goal_width, goal_height)
        elif not self.goal:
            print("Nema platformi iz datoteke, cilj nije automatski postavljen.")


    def update_platforms(self, scroll_offset):
        for platform in self.platforms:
            platform.x -= scroll_offset
        if self.goal:
            self.goal.x -= scroll_offset

    def draw_with_offset(self, screen, view_offset_x):
        if len(self.platforms) > 0 and self.ground_image_original:
            ground_platform_rect = self.platforms[0]
            screen_x = ground_platform_rect.x - view_offset_x
            
            if screen_x < self.screen_width and screen_x + ground_platform_rect.width > 0:
                try:
                    scaled_ground_image = pygame.transform.scale(self.ground_image_original, (ground_platform_rect.width, ground_platform_rect.height))
                    screen.blit(scaled_ground_image, (screen_x, ground_platform_rect.y))
                except Exception as e:
                    pygame.draw.rect(screen, (0,150,0), (screen_x, ground_platform_rect.y, ground_platform_rect.width, ground_platform_rect.height))

        if self.platform_image_original:
            for i in range(3, len(self.platforms)):
                platform_rect = self.platforms[i]
                screen_x = platform_rect.x - view_offset_x
                if screen_x < self.screen_width and screen_x + platform_rect.width > 0:
                    try:
                        scaled_platform_image = pygame.transform.scale(self.platform_image_original, (platform_rect.width, platform_rect.height))
                        screen.blit(scaled_platform_image, (screen_x, platform_rect.y))
                    except Exception as e:
                        pygame.draw.rect(screen, (100,100,100), (screen_x, platform_rect.y, platform_rect.width, platform_rect.height))
                
        if self.goal and self.flag_image:
            screen_x_goal = self.goal.x - view_offset_x
            if screen_x_goal < self.screen_width and screen_x_goal + self.goal.width > 0:
                try:
                    screen.blit(self.flag_image, (screen_x_goal, self.goal.y))
                except Exception as e:
                    pygame.draw.rect(screen, (255,200,0), (screen_x_goal, self.goal.y, self.goal.width, self.goal.height))

    def draw(self, screen):
        if not self.platforms:
            return

        if len(self.platforms) > 0 and self.ground_image_original:
            ground_platform_rect = self.platforms[0]
            try:
                scaled_ground_image = pygame.transform.scale(self.ground_image_original, (ground_platform_rect.width, ground_platform_rect.height))
                screen.blit(scaled_ground_image, (ground_platform_rect.x, ground_platform_rect.y))
            except Exception as e:
                 pygame.draw.rect(screen, (0,150,0), ground_platform_rect)


        if self.platform_image_original:
            for i in range(3, len(self.platforms)):
                platform_rect = self.platforms[i]
                try:
                    scaled_platform_image = pygame.transform.scale(self.platform_image_original, (platform_rect.width, platform_rect.height))
                    screen.blit(scaled_platform_image, (platform_rect.x, platform_rect.y))
                except Exception as e:
                    pygame.draw.rect(screen, (100,100,100), platform_rect)

            
        if self.goal and self.flag_image:
            try:
                screen.blit(self.flag_image, (self.goal.x, self.goal.y))
            except Exception as e:
                pygame.draw.rect(screen, (255,200,0), self.goal)