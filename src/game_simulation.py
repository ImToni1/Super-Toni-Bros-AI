import pygame
import os
import sys
from .platforms import PlatformManager # Koristimo relativni import unutar src paketa
from .player import Player # Koristimo relativni import unutar src paketa
from .ai_brain import Brain, AIAction

# Konstante igre (neke preuzete iz main.py)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60 # Može se povećati za brže simulacije ako fizika dopušta
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

MAX_ACTION_DURATION_FRAMES = 30 # Max broj frameova za jednu AI akciju (npr. 0.5s pri 60FPS)
MAX_SIMULATION_FRAMES_PER_BRAIN = 3600 # Max trajanje simulacije (npr. 60 sekundi pri 60FPS)


def run_simulation_for_brain(brain, level_filepath, render=False, current_generation=0, brain_idx=0):
    if render:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Super Toni Bros - AI Gen: {current_generation} Brain: {brain_idx}")
        base_path_sim = os.path.dirname(os.path.abspath(__file__))
        background_path_sim = os.path.join(base_path_sim, "../images/Background.jpeg")
        background_image_sim = pygame.image.load(background_path_sim).convert()
        font = pygame.font.SysFont(None, 30)
    else:
        # Pokreni Pygame u headless modu ako je moguće ili s minimalnim inicijalizacijama
        # Za jednostavnost, Pygame se još uvijek inicijalizira, ali bez crtanja na ekran.
        # Pravi headless bi zahtijevao više promjena ili dummy display.
        pygame.display.init() # Inicijalizira display module, ali ne stvara prozor ako se ne zove set_mode
        pygame.font.init() # Potrebno za dummy timer tekst ako se koristi

    clock = pygame.time.Clock()

    player = Player(100, SCREEN_HEIGHT - 150, 50, 50)
    platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath)
    platform_manager.generate_platforms() # Važno za resetiranje platformi

    brain.reset_instructions() # Počni s prvom instrukcijom mozga

    total_scroll_achieved = 0.0
    frames_survived = 0
    game_won_by_ai = False
    max_x_player_world_pos = player.rect.x # Inicijalna pozicija igrača

    current_ai_action = None
    action_frames_remaining = 0
    jump_executed_for_current_action = False

    simulation_running = True
    for frame_num in range(MAX_SIMULATION_FRAMES_PER_BRAIN):
        if not simulation_running:
            break

        if render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit() # Ako renderiramo i korisnik zatvori, prekini sve

        # Upravljanje AI akcijama
        if action_frames_remaining <= 0:
            current_ai_action = brain.get_next_action()
            if current_ai_action is None: # Nema više instrukcija
                simulation_running = False
                break 
            action_frames_remaining = int(current_ai_action.hold_time * MAX_ACTION_DURATION_FRAMES)
            jump_executed_for_current_action = False # Resetiraj za novu akciju

        # Primijeni trenutnu AI akciju
        simulated_keys_pressed = {pygame.K_SPACE: False, pygame.K_LEFT: False, pygame.K_RIGHT: False}
        if current_ai_action:
            if current_ai_action.is_jump and player.on_ground and not jump_executed_for_current_action:
                player.jump(JUMP_STRENGTH)
                jump_executed_for_current_action = True # Skoči samo jednom po akciji skoka

            if current_ai_action.x_direction == -1:
                simulated_keys_pressed[pygame.K_LEFT] = True
            elif current_ai_action.x_direction == 1:
                simulated_keys_pressed[pygame.K_RIGHT] = True
        
        # ---- Logika igre (adaptirano iz main.py) ----
        player.apply_gravity(GRAVITY)

        if player.rect.top > SCREEN_HEIGHT: # Igrač je pao
            simulation_running = False
            break

        requested_scroll_offset = 0
        if simulated_keys_pressed[pygame.K_RIGHT]:
            requested_scroll_offset = PLAYER_SPEED
            player.facing_left = False
        elif simulated_keys_pressed[pygame.K_LEFT]:
            requested_scroll_offset = -PLAYER_SPEED
            player.facing_left = True
        
        # Koristi originalnu logiku za scroll offset ako je moguće
        actual_scroll_offset = requested_scroll_offset
        # Implementacija provjere zidova za scroll (prilagođeno iz main.py)
        if requested_scroll_offset < 0:  # Igrac ide lijevo, platforme desno
            if len(platform_manager.platforms) > 2: # postoji lijevi zid (indeks 2)
                left_wall = platform_manager.platforms[2]
                # Ako bi pomicanje platformi udesno gurnulo desni rub lijevog zida preko lijeve strane igrača
                if (left_wall.rect.right - requested_scroll_offset) > player.rect.left:
                    actual_scroll_offset = left_wall.rect.right - player.rect.left
                    actual_scroll_offset = max(actual_scroll_offset, requested_scroll_offset)
        elif requested_scroll_offset > 0:  # Igrac ide desno, platforme lijevo
             if len(platform_manager.platforms) > 1: # postoji desni zid (indeks 1)
                right_wall = platform_manager.platforms[1]
                 # Ako bi pomicanje platformi ulijevo gurnulo lijevi rub desnog zida preko desne strane igrača
                if (right_wall.rect.left - requested_scroll_offset) < player.rect.right:
                    # Originalna logika je bila samo min(actual, requested) što nije puno radilo.
                    # Ispravnija bi bila:
                    actual_scroll_offset = (right_wall.rect.left - player.rect.right) # Koliko treba scrollati da se poravnaju
                    actual_scroll_offset = min(actual_scroll_offset, requested_scroll_offset) # Ne scrollaj više nego traženo ili unazad


        platform_manager.update_platforms(actual_scroll_offset)
        total_scroll_achieved -= actual_scroll_offset # Akumuliraj scroll (negativan offset znači napredak udesno)
        max_x_player_world_pos = max(max_x_player_world_pos, player.rect.x - total_scroll_achieved)


        player.on_ground = False
        # Provjera kolizije s platformama (prilagođeno iz main.py)
        for plat_idx, plat_obj in enumerate(platform_manager.platforms):
            # Originalno, plat_idx 2 (lijevi zid) je imao poseban tretman
            # `player.collide_with_platform` bi trebao to rješavati interno ako je zid samo prepreka
            # Za sada, koristimo opću koliziju za sve.
            # Ako su zidovi (indeksi 1 i 2) samo vizualni ili ne daju "on_ground",
            # `player.collide_with_platform` bi to trebao reflektirati.
            # U originalu, plat_idx == 2 se preskače za on_ground.
            if plat_idx == 2 and player.rect.colliderect(plat_obj.rect): # Lijevi zid
                # Ovdje se može dogoditi da igrač udari u lijevi zid i bude odgurnut ili zaustavljen.
                # Originalna logika pomicanja igrača se oslanja na scroll platformi,
                # a igrač ostaje fiksiran na X osi osim ako ga platforma ne gurne.
                # Za jednostavnost, `collide_with_platform` će riješiti prizemljenje.
                # Ako zidovi ne bi trebali prizemljiti igrača, logika u `collide_with_platform`
                # ili ovdje bi to trebala osigurati.
                pass # Ne postavljaj on_ground za lijevi zid

            if player.collide_with_platform(plat_obj.rect): # Provjeri koliziju s pravokutnikom platforme
                if plat_idx != 2: # Ne smatraj lijevi zid tlom
                    player.on_ground = True
                # Ako igrač udari u platformu odozdo ili sa strane, `collide_with_platform` bi to trebao riješiti.
                # Na primjer, zaustaviti vertikalno kretanje ako udari glavom.
                # Ili spriječiti prolazak ako udari sa strane.
                # Trenutna `collide_with_platform` primarno rješava slijetanje.
                # Horizontalna kolizija s platformama nije eksplicitno obrađena u `player.py`,
                # osim kroz logiku scrollanja koja sprječava da igrač prođe kroz "zidove" na rubu mape.
                break
        
        if platform_manager.goal and player.rect.colliderect(platform_manager.goal.rect): # Goal je Rect u PlatformManageru
            game_won_by_ai = True
            simulation_running = False
            break
        
        player.update_image_direction() # Za renderiranje

        if render:
            # Crtanje (slično kao u main.py)
            for x_bg in range(0, SCREEN_WIDTH, background_image_sim.get_width()):
                for y_bg in range(0, SCREEN_HEIGHT, background_image_sim.get_height()):
                    screen.blit(background_image_sim, (x_bg, y_bg))
            
            platform_manager.draw(screen)
            player.draw(screen)

            # Info tekst
            info_text_fitness = font.render(f"Fitness (scroll): {total_scroll_achieved:.0f}", True, (0,0,0))
            info_text_frames = font.render(f"Frames: {frames_survived}/{MAX_SIMULATION_FRAMES_PER_BRAIN}", True, (0,0,0))
            info_text_action = font.render(f"Action: {brain.current_instruction_number}/{len(brain.instructions)}", True, (0,0,0))
            screen.blit(info_text_fitness, (10, 10))
            screen.blit(info_text_frames, (10, 40))
            screen.blit(info_text_action, (10, 70))

            pygame.display.update()
            clock.tick(FPS)

        action_frames_remaining -= 1
        frames_survived += 1
    
    # Izračunaj fitness
    # Glavni faktor je koliko je daleko igrač stigao (total_scroll_achieved)
    # Bonus za pobjedu, mali bonus za preživljene frameove
    fitness = total_scroll_achieved
    
    # Udaljenost do cilja (ako nije pobijedio)
    if not game_won_by_ai and platform_manager.goal:
        # Udaljenost se mjeri od trenutne pozicije igrača (koja je fiksna na X=100) do cilja,
        # uzimajući u obzir koliko su platforme scrollane.
        # Goal x je u svjetskim koordinatama. player.rect.x je u koordinatama ekrana.
        # Efektivna X pozicija igrača u svijetu = player.rect.x - total_scroll_achieved (jer je total_scroll_achieved negativan za desno)
        # Udaljenost = platform_manager.goal.rect.centerx - (player.rect.centerx - total_scroll_achieved)
        
        # Jednostavnije: fitness je već baziran na total_scroll_achieved.
        # Ako je cilj na npr. scroll_offset od 2000, a igrač je stigao do 1500, to je već u fitnessu.
        pass # Može se dodati kazna za veliku udaljenost od cilja ako je zapeo daleko

    if game_won_by_ai:
        fitness += 100000.0  # Veliki bonus za pobjedu
        # Nagradi brže pobjede (manje frameova)
        fitness += (MAX_SIMULATION_FRAMES_PER_BRAIN - frames_survived) * 10 
    else:
        # Mali bonus za svaki preživljeni frame ako nije pobijedio
        fitness += frames_survived * 0.1 

    # Kazna ako zapne na početku (mali scroll, puno frameova)
    if total_scroll_achieved < 50 and frames_survived > MAX_SIMULATION_FRAMES_PER_BRAIN * 0.5:
        fitness -= 10000

    # Kazna za pad s platforme (ako nije pobijedio)
    if player.rect.top > SCREEN_HEIGHT and not game_won_by_ai:
        fitness -= 50000 # Značajna kazna za pad

    brain.fitness = fitness
    
    if render: # Očisti pygame ako je korišten samo za ovu simulaciju s renderiranjem
        pygame.quit()

    return fitness