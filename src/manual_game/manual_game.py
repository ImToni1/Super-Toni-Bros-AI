# src/manual_game/main_manual.py

import pygame
import sys
import os
# AŽURIRANI IMPORTI
from src.core.platforms import PlatformManager
from src.core.player import Player

# LEVEL_FILEPATH se sada prosljeđuje funkciji run_game iz start.py

def run_game(level_filepath): # level_filepath je sada argument
    pygame.init()

    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Toni Bros - Ručna Igra")

    base_path = os.path.dirname(os.path.abspath(__file__)) 
    background_path = os.path.join(base_path, "..", "..", "images", "Background.jpeg")
    try:
        background_image = pygame.image.load(background_path).convert()
    except pygame.error as e:
        print(f"Greška pri učitavanju pozadinske slike: {e}")
        print(f"Pokušana putanja: {background_path}")
        background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background_image.fill((200, 200, 255)) 


    win_image_path = os.path.join(base_path, "..", "..", "images", "Winner's_scene.png")
    try:
        win_image = pygame.image.load(win_image_path).convert()
        win_image = pygame.transform.scale(win_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Greška pri učitavanju slike pobjede: {e}")
        print(f"Pokušana putanja: {win_image_path}")
        win_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        win_image.fill((0,255,0)) 

    clock = pygame.time.Clock()
    FPS = 60
    gravity = 0.8
    jump_strength = -15
    speed = 5

    font = pygame.font.SysFont(None, 80)
    timer_font = pygame.font.SysFont(None, 35)

    platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath)
    platform_manager.generate_platforms()

    player = Player(100, 0, 50, 50)
    if platform_manager.platforms: 
        first_platform_rect = platform_manager.platforms[0] 
        player_initial_y = first_platform_rect.top - player.rect.height
        player.rect.y = player_initial_y
        player.vel_y = 0
        player.on_ground = True
    else:
        player.rect.y = SCREEN_HEIGHT - player.rect.height - 50 
        player.on_ground = True 
        print("Upozorenje: Nema platformi, igrač postavljen na dno ekrana.")

    start_time = pygame.time.get_ticks()

    def reset_game():
        nonlocal player, platform_manager 
        platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath)
        platform_manager.generate_platforms()
        if platform_manager.platforms:
            first_platform_rect_reset = platform_manager.platforms[0]
            player_initial_y_reset = first_platform_rect_reset.top - player.rect.height
            player.reset(100, player_initial_y_reset)
            player.vel_y = 0
            player.on_ground = True
        else:
            player.reset(100, SCREEN_HEIGHT - player.rect.height - 50)
            player.on_ground = True
        
    def show_victory_screen(elapsed_time):
        screen.blit(win_image, (0, 0))
        victory_text = font.render("You Win!", True, (0, 0, 0))
        time_text_str = f"Time: {elapsed_time:.2f} seconds"
        time_text = font.render(time_text_str, True, (0, 0, 0))

        screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.update()

        waiting = True
        user_chose_to_exit = False # Nova varijabla
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    user_chose_to_exit = True # Korisnik je kliknuo/pritisnuo tipku
            # Nema potrebe za `if not waiting: break` jer while petlja to rješava
        return user_chose_to_exit # Vrati da li je korisnik izašao

    running = True
    game_won = False
    victory_elapsed_time = 0
    frame_counter = 0

    while running:
        frame_counter += 1
        clock.tick(FPS)

        if not game_won:
            current_ticks = pygame.time.get_ticks()
            elapsed_time = (current_ticks - start_time) / 1000

        if background_image.get_width() > 0 and background_image.get_height() > 0 : 
            for x_bg in range(0, SCREEN_WIDTH, background_image.get_width()):
                for y_bg in range(0, SCREEN_HEIGHT, background_image.get_height()):
                    screen.blit(background_image, (x_bg, y_bg))
        else:
            screen.fill((200,200,255)) 


        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and player.on_ground:
            player.jump(jump_strength)

        player.apply_gravity(gravity)

        if player.rect.top > SCREEN_HEIGHT + 100: 
            print(f"Player fell off screen. Resetting game. (Frame {frame_counter})") 
            reset_game() 
            frame_counter = 0 
            
        requested_scroll_offset = 0
        if keys[pygame.K_RIGHT]:
            requested_scroll_offset = speed
            player.facing_left = False
        elif keys[pygame.K_LEFT]:
            requested_scroll_offset = -speed
            player.facing_left = True

        actual_scroll_offset = requested_scroll_offset
        
        if requested_scroll_offset < 0: 
            if len(platform_manager.platforms) > 1: 
                left_wall = platform_manager.platforms[1] 
                if (player.rect.left) < (left_wall.right - requested_scroll_offset) :
                     actual_scroll_offset = (left_wall.right - player.rect.left)
                     actual_scroll_offset = min(0, actual_scroll_offset) if requested_scroll_offset < 0 else max(0, actual_scroll_offset)

        platform_manager.update_platforms(actual_scroll_offset)

        player.on_ground = False
        for plat_idx, plat in enumerate(platform_manager.platforms):
            if plat_idx == 1: 
                continue

            if player.collide_with_platform(plat):
                player.on_ground = True
                break

        # Provjera pobjede i poziv ekrana pobjede
        if not game_won and platform_manager.goal and player.rect.colliderect(platform_manager.goal):
            game_won = True
            victory_elapsed_time = elapsed_time
            # Ako je korisnik kliknuo na ekranu pobjede, postavi running na False
            if show_victory_screen(victory_elapsed_time):
                running = False # ODMAH postavi running na False
        
        # Ako running postane False zbog pobjede, ne crtaj više i ne obrađuj događaje u ovoj iteraciji
        if not running:
            break # Izađi iz while petlje odmah

        player.draw(screen)
        platform_manager.draw(screen)

        timer_display_value = victory_elapsed_time if game_won else elapsed_time
        timer_text = timer_font.render(f"Time: {timer_display_value:.2f} s", True, (0, 0, 0))
        screen.blit(timer_text, (10, 10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Ovaj dio više nije nužno potreban ako gornji `if show_victory_screen...` postavi `running = False`
            # Ali ostavljamo ga za slučaj da korisnik klikne nakon što je `game_won` već true, a `show_victory_screen`
            # nije pozvan u toj iteraciji (manje vjerojatno s novom logikom).
            # Ili, ako se `show_victory_screen` ne bi odmah prekinuo petlju.
            if game_won and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                 if not running: # Ako je running već False zbog show_victory_screen, ne radi ništa
                     pass
                 else: # Inače, ovo je drugi klik nakon što je ekran pobjede već prošao
                     # Ovo se sada ne bi trebalo događati ako je gornja logika ispravna.
                     # Za svaki slučaj, ako bi se ipak desilo, osiguraj izlazak.
                     print("Dodatni klik nakon pobjede detektiran za izlaz.") # Za debug
                     running = False