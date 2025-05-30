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

    # AŽURIRANE PUTANJE DO SLIKA
    base_path = os.path.dirname(os.path.abspath(__file__)) # src/manual_game
    # Treba ići dva nivoa gore (do Super-Toni-Bros-AI) pa u images
    background_path = os.path.join(base_path, "..", "..", "images", "Background.jpeg")
    try:
        background_image = pygame.image.load(background_path).convert()
    except pygame.error as e:
        print(f"Greška pri učitavanju pozadinske slike: {e}")
        print(f"Pokušana putanja: {background_path}")
        background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background_image.fill((200, 200, 255)) # Plava pozadina kao fallback


    win_image_path = os.path.join(base_path, "..", "..", "images", "Winner's_scene.png")
    try:
        win_image = pygame.image.load(win_image_path).convert()
        win_image = pygame.transform.scale(win_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Greška pri učitavanju slike pobjede: {e}")
        print(f"Pokušana putanja: {win_image_path}")
        win_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        win_image.fill((0,255,0)) # Zelena kao fallback

    clock = pygame.time.Clock()
    FPS = 60
    gravity = 0.8
    jump_strength = -15
    speed = 5

    font = pygame.font.SysFont(None, 80)
    timer_font = pygame.font.SysFont(None, 35)

    # Koristi proslijeđeni level_filepath
    platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath)
    platform_manager.generate_platforms()

    player = Player(100, 0, 50, 50)
    if platform_manager.platforms: # Osiguraj da postoje platforme
        first_platform_rect = platform_manager.platforms[0]
        player_initial_y = first_platform_rect.top - player.rect.height
        player.rect.y = player_initial_y
        player.vel_y = 0
        player.on_ground = True
    else:
        # Fallback ako nema platformi (npr. prazna level datoteka)
        player.rect.y = SCREEN_HEIGHT - player.rect.height - 50 # Postavi na dno ekrana
        player.on_ground = True # Pretpostavi da je na nevidljivom tlu
        print("Upozorenje: Nema platformi, igrač postavljen na dno ekrana.")


    start_time = pygame.time.get_ticks()

    def reset_game():
        nonlocal player, platform_manager, start_time
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
        start_time = pygame.time.get_ticks()

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

    frame_counter = 0

    while running:
        frame_counter += 1
        clock.tick(FPS)

        if not game_won:
            current_ticks = pygame.time.get_ticks()
            elapsed_time = (current_ticks - start_time) / 1000

        # Crtanje pozadine
        # Provjeri da li background_image postoji prije crtanja
        if background_image.get_width() > 0 and background_image.get_height() > 0 : # Osnovna provjera
            for x_bg in range(0, SCREEN_WIDTH, background_image.get_width()):
                for y_bg in range(0, SCREEN_HEIGHT, background_image.get_height()):
                    screen.blit(background_image, (x_bg, y_bg))
        else:
            screen.fill((200,200,255)) # Fallback ako slika nije učitana


        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and player.on_ground:
            player.jump(jump_strength)

        player.apply_gravity(gravity)

        if player.rect.top > SCREEN_HEIGHT + 100:
            print(f"Player fell off screen. Resetting game. (Frame {frame_counter})")
            reset_game()
            frame_counter = 0
            start_time = pygame.time.get_ticks()

        requested_scroll_offset = 0
        if keys[pygame.K_RIGHT]:
            requested_scroll_offset = speed
            player.facing_left = False
        elif keys[pygame.K_LEFT]:
            requested_scroll_offset = -speed
            player.facing_left = True

        actual_scroll_offset = requested_scroll_offset
        
        # Logika za horizontalno pomicanje i koliziju sa zidovima ostaje ista,
        # ali provjeri indekse platformi ako je potrebno
        if requested_scroll_offset < 0: # Kretanje ulijevo
            # Ako postoje barem 3 platforme (tlo, desni zid, lijevi zid)
            if len(platform_manager.platforms) > 2: # Indeks 2 je lijevi zid
                left_wall = platform_manager.platforms[2]
                # Ako bi igračev lijevi rub prešao DESNI rub lijevog zida nakon pomaka platformi
                if (player.rect.left) < (left_wall.right - requested_scroll_offset) :
                     # Zaustavi pomak tako da igračev lijevi rub bude na desnom rubu lijevog zida
                     actual_scroll_offset = (left_wall.right - player.rect.left)
                     # Osiguraj da se ne pomakne u suprotnom smjeru od traženog
                     actual_scroll_offset = min(0, actual_scroll_offset) if requested_scroll_offset < 0 else max(0, actual_scroll_offset)


        elif requested_scroll_offset > 0: # Kretanje udesno
             # Ako postoje barem 2 platforme (tlo, desni zid)
            if len(platform_manager.platforms) > 1: # Indeks 1 je desni zid
                right_wall = platform_manager.platforms[1]
                 # Ako bi igračev desni rub prešao LIJEVI rub desnog zida nakon pomaka platformi
                if (player.rect.right) > (right_wall.left - requested_scroll_offset) :
                    # Zaustavi pomak
                    actual_scroll_offset = (player.rect.right - right_wall.left)
                    actual_scroll_offset = max(0, actual_scroll_offset) if requested_scroll_offset > 0 else min(0, actual_scroll_offset)


        platform_manager.update_platforms(actual_scroll_offset)


        player.on_ground = False
        for plat_idx, plat in enumerate(platform_manager.platforms):
            # Preskoči provjeru kolizije sa zidovima za slijetanje (indeksi 1 i 2)
            # To su nevidljivi zidovi za ograničavanje pomaka, ne za stajanje.
            if plat_idx == 1 or plat_idx == 2:
                continue

            if player.collide_with_platform(plat):
                player.on_ground = True
                break

        if not game_won and platform_manager.goal and player.rect.colliderect(platform_manager.goal):
            game_won = True
            victory_elapsed_time = elapsed_time
            show_victory_screen(victory_elapsed_time)
            # Ne prekidaj petlju ovdje, show_victory_screen ima svoju petlju čekanja
            # running = False # Ovo bi odmah zatvorilo igru nakon pobjede
            # break

        player.draw(screen)
        platform_manager.draw(screen)

        timer_display_value = victory_elapsed_time if game_won else elapsed_time
        timer_text = timer_font.render(f"Time: {timer_display_value:.2f} s", True, (0, 0, 0))
        screen.blit(timer_text, (10, 10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_won and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                 running = False # Izađi iz glavne petlje nakon pobjedničkog ekrana

    # pygame.quit() # Ne zovi quit ovdje jer se vraćaš u start.py izbornik
    # sys.exit()