import pygame
import os

class PlatformManager:
    FIXED_PLATFORM_HEIGHT = 30

    def __init__(self, screen_width, screen_height, level_filepath):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.level_filepath = level_filepath 
        self.platforms = []
        self.goal = None

        base_path = os.path.dirname(os.path.abspath(__file__)) 
        
        try:
            self.platform_image_original = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Platforms.png")).convert_alpha()
            self.ground_image_original = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Ground.png")).convert_alpha()
            self.flag_image = pygame.image.load(os.path.join(base_path, "..", "..", "images", "Flag.png")).convert_alpha()
            self.flag_image = pygame.transform.scale(self.flag_image, (160, 160))
        except pygame.error as e:
            self.platform_image_original = None
            self.ground_image_original = None
            self.flag_image = None

    def _load_platforms_from_file(self):
        loaded_platforms = []
        try:
            with open(self.level_filepath, 'r') as f:
                for line_idx, line in enumerate(f):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) == 3: 
                            try:
                                x = int(parts[0])
                                y = int(parts[1])
                                width = int(parts[2])
                                height = PlatformManager.FIXED_PLATFORM_HEIGHT 
                                loaded_platforms.append(pygame.Rect(x, y, width, height))
                            except ValueError:
                                pass
                        elif len(parts) == 4: 
                             try:
                                x = int(parts[0])
                                y = int(parts[1])
                                width = int(parts[2])
                                height = PlatformManager.FIXED_PLATFORM_HEIGHT 
                                loaded_platforms.append(pygame.Rect(x, y, width, height))
                             except ValueError:
                                pass
                        else:
                            pass
        except FileNotFoundError:
            pass
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
            pass


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
            for i in range(2, len(self.platforms)): 
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