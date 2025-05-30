import pygame
import sys
import os
from platforms import PlatformManager
from player import Player

LEVEL_FILEPATH = "level.txt" 

def run_game(level_filepath):
    pygame.init()

    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Toni Bros")

    base_path = os.path.dirname(os.path.abspath(__file__))
    background_path = os.path.join(base_path, "../images/Background.jpeg")
    background_image = pygame.image.load(background_path).convert()

    win_image_path = os.path.join(base_path, "../images/Winner's_scene.png")
    win_image = pygame.image.load(win_image_path).convert()
    win_image = pygame.transform.scale(win_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()
    FPS = 60
    gravity = 0.8
    jump_strength = -15
    speed = 5 

    font = pygame.font.SysFont(None, 80)
    timer_font = pygame.font.SysFont(None, 35)

    player = Player(100, SCREEN_HEIGHT - 125, 50, 50) # PROMIJENJENO: Ispravljena početna Y-koordinata
    platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath)
    platform_manager.generate_platforms()

    start_time = pygame.time.get_ticks()

    def reset_game():
        nonlocal player, platform_manager
        player.reset(100, SCREEN_HEIGHT - 125) # PROMIJENJENO: Ispravljena Y-koordinata za reset
        platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath)
        platform_manager.generate_platforms()

    def show_victory_screen(elapsed_time):
        screen.blit(win_image, (0, 0))
        victory_text = font.render("You Win!", True, (0, 0, 0))
        time_text_str = f"Time: {elapsed_time:.2f} seconds"
        time_text = font.render(time_text_str, True, (0, 0, 0))

        screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: 
                    waiting = False 
            if not waiting: 
                break 
    
    running = True
    game_won = False 
    victory_elapsed_time = 0 

    while running:
        clock.tick(FPS)
        
        if not game_won:
            current_ticks = pygame.time.get_ticks()
            elapsed_time = (current_ticks - start_time) / 1000

        for x_bg in range(0, SCREEN_WIDTH, background_image.get_width()):
            for y_bg in range(0, SCREEN_HEIGHT, background_image.get_height()):
                screen.blit(background_image, (x_bg, y_bg))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and player.on_ground:
            player.jump(jump_strength)

        player.apply_gravity(gravity)

        if player.rect.top > SCREEN_HEIGHT: 
            reset_game()

        requested_scroll_offset = 0
        if keys[pygame.K_RIGHT]:
            requested_scroll_offset = speed
            player.facing_left = False
        elif keys[pygame.K_LEFT]:
            requested_scroll_offset = -speed 
            player.facing_left = True

        actual_scroll_offset = requested_scroll_offset

        if requested_scroll_offset < 0: 
            if len(platform_manager.platforms) > 2:
                left_wall = platform_manager.platforms[2]
                if (left_wall.right - requested_scroll_offset) > player.rect.left:
                    actual_scroll_offset = left_wall.right - player.rect.left 
                    actual_scroll_offset = max(actual_scroll_offset, requested_scroll_offset)

        elif requested_scroll_offset > 0: 
            if len(platform_manager.platforms) > 1:
                right_wall = platform_manager.platforms[1]
                if (right_wall.left - requested_scroll_offset) < player.rect.right:
                    actual_scroll_offset = min(actual_scroll_offset, requested_scroll_offset)
        
        platform_manager.update_platforms(actual_scroll_offset)

        player.on_ground = False
        for plat_idx, plat in enumerate(platform_manager.platforms):
            if plat_idx == 2: 
                if player.rect.colliderect(plat): 
                    pass 
                continue 

            if player.collide_with_platform(plat):
                player.on_ground = True 
                break
        
        if not game_won and platform_manager.goal and player.rect.colliderect(platform_manager.goal):
            game_won = True 
            victory_elapsed_time = elapsed_time 
            show_victory_screen(victory_elapsed_time)
            running = False 
            break 

        player.draw(screen)
        platform_manager.draw(screen)

        timer_display_value = victory_elapsed_time if game_won else elapsed_time
        timer_text = timer_font.render(f"Time: {timer_display_value:.2f} s", True, (0, 0, 0))
        screen.blit(timer_text, (10, 10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()