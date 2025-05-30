import pygame
import os

class PlatformManager:
    FIXED_PLATFORM_HEIGHT = 30 # Sve platforme imaju fiksnu visinu

    def __init__(self, screen_width, screen_height, level_filepath):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.level_filepath = level_filepath # Putanja do datoteke s definicijom levela
        self.platforms = [] # Lista svih platformi (kao pygame.Rect objekti)
        self.goal = None # Ciljni objekt (zastavica)

        base_path = os.path.dirname(os.path.abspath(__file__)) #
        
        try:
            # Učitavanje slika za platforme, tlo i zastavicu
            self.platform_image_original = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Platforms.png")).convert_alpha()
            self.ground_image_original = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Ground.png")).convert_alpha()
            self.flag_image = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Flag.png")).convert_alpha()
            self.flag_image = pygame.transform.scale(self.flag_image, (160, 160)) # Skaliranje slike zastavice
        except pygame.error as e:
            # Ako slike nisu pronađene, koristit će se samo obojani pravokutnici
            self.platform_image_original = None
            self.ground_image_original = None
            self.flag_image = None

    def _load_platforms_from_file(self):
        loaded_platforms = []
        try:
            with open(self.level_filepath, 'r') as f:
                for line_idx, line in enumerate(f):
                    line = line.strip()
                    if line and not line.startswith('#'): # Ignorira prazne linije i komentare
                        parts = line.split(',')
                        if len(parts) == 3: # Format: x,y,širina
                            try:
                                x = int(parts[0])
                                y = int(parts[1])
                                width = int(parts[2])
                                height = PlatformManager.FIXED_PLATFORM_HEIGHT # Visina je fiksna
                                loaded_platforms.append(pygame.Rect(x, y, width, height))
                            except ValueError:
                                pass # Ignorira linije s neispravnim brojevima
                        elif len(parts) == 4: # Stariji format s visinom, visina se ignorira i koristi fiksna
                             try:
                                x = int(parts[0])
                                y = int(parts[1])
                                width = int(parts[2])
                                height = PlatformManager.FIXED_PLATFORM_HEIGHT 
                                loaded_platforms.append(pygame.Rect(x, y, width, height))
                             except ValueError:
                                pass
                        else:
                            pass # Ignorira linije s neispravnim brojem dijelova
        except FileNotFoundError:
            pass # Ako datoteka levela ne postoji, vraća praznu listu
        return loaded_platforms

    def generate_platforms(self):
        self.platforms = []
        
        # Stvaranje početne platforme (tla)
        start_ground_initial_x = -200 # Počinje malo izvan ekrana lijevo
        start_ground_visible_width = 300
        start_ground_width = start_ground_visible_width + abs(start_ground_initial_x)
        starting_ground_y = self.screen_height - 50
        starting_ground_height = 50
        starting_ground = pygame.Rect(start_ground_initial_x, starting_ground_y, start_ground_width, starting_ground_height)
        self.platforms.append(starting_ground) 

        # Stvaranje lijevog "zida" da igrač ne može otići previše ulijevo izvan mape
        left_wall_width = 10
        left_wall_x = start_ground_initial_x - left_wall_width
        left_wall = pygame.Rect(left_wall_x, 0, left_wall_width, self.screen_height)
        self.platforms.append(left_wall) 

        platforms_from_file = self._load_platforms_from_file() # Učitavanje platformi definiranih u datoteci
        self.platforms.extend(platforms_from_file) # Dodavanje učitanih platformi

        if platforms_from_file:
            # Postavljanje cilja (zastavice) na zadnju platformu iz datoteke
            target_platform = platforms_from_file[-1]
            goal_width = 160
            goal_height = 160
            goal_x = target_platform.x + (target_platform.width - goal_width) // 2 # Centriranje zastavice na platformi
            goal_y = target_platform.y - goal_height # Postavljanje zastavice iznad platforme
            self.goal = pygame.Rect(goal_x, goal_y, goal_width, goal_height)
        elif not self.goal:
            # Ako nema platformi iz datoteke, nema ni cilja (osim ako je definiran na drugi način)
            pass


    def update_platforms(self, scroll_offset):
        # Pomicanje svih platformi i cilja za scroll_offset (simulira kretanje kamere)
        for platform in self.platforms:
            platform.x -= scroll_offset
        if self.goal:
            self.goal.x -= scroll_offset

    def draw_with_offset(self, screen, view_offset_x):
        # Iscrtavanje platformi s obzirom na pomak pogleda (view_offset_x) - koristi se u AI simulaciji
        if len(self.platforms) > 0 and self.ground_image_original:
            ground_platform_rect = self.platforms[0] # Pretpostavka da je prva platforma tlo
            screen_x = ground_platform_rect.x - view_offset_x # Izračun pozicije na ekranu
            
            # Iscrtaj samo ako je vidljivo na ekranu
            if screen_x < self.screen_width and screen_x + ground_platform_rect.width > 0:
                try:
                    scaled_ground_image = pygame.transform.scale(self.ground_image_original, (ground_platform_rect.width, ground_platform_rect.height))
                    screen.blit(scaled_ground_image, (screen_x, ground_platform_rect.y))
                except Exception as e: # Fallback ako slika ne radi
                    pygame.draw.rect(screen, (0,150,0), (screen_x, ground_platform_rect.y, ground_platform_rect.width, ground_platform_rect.height))

        if self.platform_image_original:
            # Iscrtavanje ostalih platformi (preskače tlo i lijevi zid)
            for i in range(2, len(self.platforms)): 
                platform_rect = self.platforms[i]
                screen_x = platform_rect.x - view_offset_x
                if screen_x < self.screen_width and screen_x + platform_rect.width > 0:
                    try:
                        scaled_platform_image = pygame.transform.scale(self.platform_image_original, (platform_rect.width, platform_rect.height))
                        screen.blit(scaled_platform_image, (screen_x, platform_rect.y))
                    except Exception as e:
                        pygame.draw.rect(screen, (100,100,100), (screen_x, platform_rect.y, platform_rect.width, platform_rect.height))
                
        if self.goal and self.flag_image: # Iscrtavanje cilja (zastavice)
            screen_x_goal = self.goal.x - view_offset_x
            if screen_x_goal < self.screen_width and screen_x_goal + self.goal.width > 0:
                try:
                    screen.blit(self.flag_image, (screen_x_goal, self.goal.y))
                except Exception as e:
                    pygame.draw.rect(screen, (255,200,0), (screen_x_goal, self.goal.y, self.goal.width, self.goal.height))

    def draw(self, screen):
        # Iscrtavanje platformi bez offseta - koristi se u ručnoj igri gdje se platforme direktno pomiču
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
            for i in range(2, len(self.platforms)): 
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