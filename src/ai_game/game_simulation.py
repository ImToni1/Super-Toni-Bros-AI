# src/ai_game/game_simulation.py

import pygame
import os
import sys
# AŽURIRANI IMPORTI
from src.core.platforms import PlatformManager
from src.core.player import Player
# Može i relativni import ako je unutar istog paketa
from .ai_brain import Brain, AIAction # AIAction je potreban
# from src.ai_game.ai_brain import Brain, AIAction


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

MAX_ACTION_DURATION_FRAMES = 30 # Koliko dugo AI drži jednu akciju (u frameovima)

def run_simulation_for_brain(brain, level_filepath, render=False, current_generation=0, brain_idx=0):
    # Pygame se inicijalizira u start.py, ali ako se ova funkcija poziva samostalno,
    # možda je potrebno osigurati da je inicijaliziran.
    # pygame.init() # Može biti ovdje ako se simulacija pokreće neovisno

    screen_for_simulation = None
    font = None
    background_image_sim = None

    if render:
        # Osiguraj da je display modul inicijaliziran
        if not pygame.display.get_init():
            pygame.display.init()
            
        screen_for_simulation = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Super Toni Bros - AI Gen: {current_generation} Brain: {brain_idx}")
        
        # AŽURIRANA PUTANJA DO SLIKE
        base_path_sim = os.path.dirname(os.path.abspath(__file__)) # src/ai_game
        # Treba ići dva nivoa gore (do Super-Toni-Bros-AI) pa u images
        background_path_sim = os.path.join(base_path_sim, "..", "..", "images", "Background.jpeg")
        try:
            background_image_sim = pygame.image.load(background_path_sim).convert()
        except pygame.error as e:
            print(f"Error loading background image in simulation: {e}")
            print(f"Attempted path: {background_path_sim}")
            background_image_sim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background_image_sim.fill((200, 200, 255))
        
        if not pygame.font.get_init():
            pygame.font.init()
        if pygame.font.get_init():
            try:
                font = pygame.font.SysFont(None, 30)
            except Exception as e_font:
                print(f"Greška pri učitavanju SysFont: {e_font}. Koristim defaultni font.")
                try:
                    font = pygame.font.Font(None, 30) # Default Pygame font
                except Exception as e_font_default:
                    print(f"Greška pri učitavanju defaultnog fonta: {e_font_default}. Font neće biti dostupan.")
                    font = None
        else:
            print("Upozorenje: Pygame font modul nije inicijaliziran.")
            font = None
    else:
        # Za headless mod, pokušaj postaviti dummy display ako već nije postavljen
        if not pygame.display.get_init():
            try:
                # Pokušaj inicijalizirati display s minimalnim postavkama
                # Ovo može biti problematično na nekim sustavima bez X servera
                # os.environ["SDL_VIDEODRIVER"] = "dummy" # Pokušaj s dummy driverom
                pygame.display.init()
                screen_for_simulation = pygame.display.set_mode((1, 1), pygame.NOFRAME)
            except pygame.error as e:
                print(f"Upozorenje: Ne mogu postaviti dummy display u headless modu: {e}.")
                # Ako ni ovo ne uspije, Pygame funkcije koje ovise o displayu mogu zakazati.


    try:
        # Koristi proslijeđeni level_filepath
        platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath)
        platform_manager.generate_platforms()
    except pygame.error as e: # Hvatanje Pygame grešaka specifično
        print(f"KRITIČNA GREŠKA: Pygame greška tijekom inicijalizacije PlatformManager-a: {e}")
        brain.fitness = -float('inf') # Teška kazna
        # Ne pokušavaj ugasiti display ako nije ni inicijaliziran kako treba
        if render and screen_for_simulation and pygame.display.get_init():
            pygame.display.quit()
        return brain.fitness
    except Exception as e: # Hvatanje ostalih neočekivanih grešaka
        print(f"KRITIČNA GREŠKA: Neočekivana greška tijekom inicijalizacije PlatformManager-a: {e}")
        brain.fitness = -float('inf')
        if render and screen_for_simulation and pygame.display.get_init():
            pygame.display.quit()
        return brain.fitness


    player_start_x_on_screen = 100
    player_world_x = 0.0

    player_visual_height = 50 * 1.5 # Iz Player klase
    
    # Postavljanje igrača na prvu platformu, ako postoji
    player_initial_y = SCREEN_HEIGHT - player_visual_height - 70 # Fallback
    if platform_manager.platforms:
        first_platform_rect = platform_manager.platforms[0] # Pretpostavka da je prva platforma tlo
        player_initial_y = first_platform_rect.top - player_visual_height
    
    player = Player(player_start_x_on_screen, player_initial_y, 50, 50)
    if platform_manager.platforms : player.on_ground = True # Ako kreće s platforme


    brain.reset_instructions()

    max_world_x_achieved = 0.0
    total_left_movement_world = 0.0
    
    frames_survived = 0
    game_won_by_ai = False

    current_ai_action = None
    action_frames_remaining = 0
    jump_executed_for_current_action = False

    simulation_running = True
    
    stagnation_frames = 0
    STAGNATION_LIMIT_MAX_X = 240 # Ako se max_X ne poveća X frameova, prekini
    last_check_world_x = player_world_x

    view_offset_x = 0.0 # Koliko je svijet pomaknut ulijevo (kamera)

    clock = pygame.time.Clock() if render else None # Koristi sat samo ako renderiraš

    while simulation_running:
        if render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    simulation_running = False
                    brain.fitness = -float('inf') # Kazna za ručni prekid
                    # pygame.quit() # Ne gasi cijeli pygame ovdje
                    if pygame.display.get_init(): pygame.display.quit()
                    return brain.fitness # Odmah izađi
            if not simulation_running: break


        if action_frames_remaining <= 0:
            current_ai_action = brain.get_next_action()
            if current_ai_action is None: # Nema više instrukcija
                if render and font: print(f"Brain {brain_idx} potrošio instrukcije.")
                simulation_running = False; break
            action_frames_remaining = int(current_ai_action.hold_time * MAX_ACTION_DURATION_FRAMES)
            jump_executed_for_current_action = False # Resetiraj za novu akciju

        current_x_direction = 0 # Default je da stoji
        if current_ai_action:
            if current_ai_action.is_jump and player.on_ground and not jump_executed_for_current_action:
                player.jump(JUMP_STRENGTH)
                jump_executed_for_current_action = True
            current_x_direction = current_ai_action.x_direction

        player.apply_gravity(GRAVITY)

        # Provjera pada s ekrana
        if player.rect.top > SCREEN_HEIGHT + 200: # Pao daleko ispod vidljivog dijela
            if render and font: print(f"Brain {brain_idx} PAO S EKRANA!")
            brain.fitness = -300000.0; simulation_running = False; break # Velika kazna

        # Horizontalno kretanje svijeta
        world_movement_this_frame = 0
        if current_x_direction == 1: # Desno
            world_movement_this_frame = PLAYER_SPEED
            player.facing_left = False
        elif current_x_direction == -1: # Lijevo
            world_movement_this_frame = -PLAYER_SPEED
            player.facing_left = True
        
        player_world_x += world_movement_this_frame # Ažuriraj svjetsku poziciju igrača

        if world_movement_this_frame < 0: # Ako se kretao ulijevo
            total_left_movement_world += abs(world_movement_this_frame)

        view_offset_x = player_world_x # Kamera prati svjetsku X poziciju igrača

        # Provjera stagnacije
        if player_world_x > max_world_x_achieved:
            max_world_x_achieved = player_world_x
            stagnation_frames = 0 # Resetiraj brojač stagnacije
        else:
            # Povećaj stagnaciju samo ako nema značajnog pomaka u X smjeru
             if abs(player_world_x - last_check_world_x) < 1.0 : # Ako je pomak manji od 1 piksela
                 stagnation_frames +=1
        # Ažuriraj last_check_world_x bez obzira na pomak za sljedeću provjeru
        if abs(player_world_x - last_check_world_x) >= 1.0: # Resetiraj ako ima hor. kretanja
             stagnation_frames = 0 
        last_check_world_x = player_world_x


        if stagnation_frames > STAGNATION_LIMIT_MAX_X :
            if render and font: print(f"Brain {brain_idx} STAGNIRA (max X)! Prekid.")
            simulation_running = False; break
        
        # Kolizija s platformama
        player.on_ground = False # Resetiraj prije provjere
        for plat_obj_original in platform_manager.platforms:
            # Za koliziju, X koordinata platforme treba biti relativna na ekran,
            # view_offset_x je pomak svijeta ulijevo.
            # Igrač je na fiksnoj ekranskoj poziciji (player_start_x_on_screen).
            # Efektivna ekranska X pozicija platforme je njen svjetski X minus pomak kamere.
            temp_plat_rect = pygame.Rect(plat_obj_original.x - view_offset_x + player_start_x_on_screen, # Dodaj player_start_x_on_screen
                                         plat_obj_original.y,
                                         plat_obj_original.width,
                                         plat_obj_original.height)
            
            # Ispravka: igračev rect je već na ekranskim koordinatama (uvijek na player_start_x_on_screen)
            # Dakle, platforme se pomiču u odnosu na svijet, a igrač ostaje na istom mjestu na ekranu
            # Ekranska pozicija platforme = Svjetska pozicija platforme - Svjetska pozicija igrača (view_offset_x) + Fiksna ekranska pozicija igrača
            
            # Jednostavnije: Igračev rect je na player_start_x_on_screen.
            # Platforme se crtaju na plat_obj_original.x - view_offset_x.
            # Za koliziju, trebamo usporediti player.rect s pomaknutim platformama.
            
            collision_plat_rect = pygame.Rect(plat_obj_original.x - view_offset_x, # Ovo je ekranski X platforme
                                              plat_obj_original.y,
                                              plat_obj_original.width,
                                              plat_obj_original.height)

            # Igračev rect je već na (player_start_x_on_screen, player.rect.y)
            # Ne treba pomicati player.rect za koliziju, on je referenca.
            if player.collide_with_platform(collision_plat_rect): # Koristi player.rect kakav jest
                player.on_ground = True; break
        
        # Kolizija s ciljem
        if platform_manager.goal:
            goal_original = platform_manager.goal
            # Slično kao za platforme, izračunaj ekransku poziciju cilja
            temp_goal_rect = pygame.Rect(goal_original.x - view_offset_x, # Ekranski X cilja
                                         goal_original.y,
                                         goal_original.width,
                                         goal_original.height)
            if player.rect.colliderect(temp_goal_rect): # Koristi player.rect kakav jest
                game_won_by_ai = True; simulation_running = False; break

        player.update_image_direction() # Ažuriraj sliku igrača

        if render and screen_for_simulation: # Crtaj samo ako je render True i screen postoji
            if background_image_sim: # Provjeri da li je slika učitana
                bg_width = background_image_sim.get_width()
                render_x_bg = (-view_offset_x) % bg_width
                screen_for_simulation.blit(background_image_sim, (render_x_bg - bg_width, 0))
                screen_for_simulation.blit(background_image_sim, (render_x_bg, 0))
            else: # Fallback ako slika nije učitana
                 screen_for_simulation.fill((200,200,255))

            platform_manager.draw_with_offset(screen_for_simulation, view_offset_x)
            player.draw(screen_for_simulation) # Igrač se crta na svojoj fiksnoj ekranskoj poziciji

            if font: # Crtaj tekst samo ako je font uspješno učitan
                font_color = (0,0,0) # Crna boja za tekst
                texts = [
                    f"Max X (Svijet): {max_world_x_achieved:.0f}",
                    f"Lijevo (Svijet): {total_left_movement_world:.0f}",
                    f"Player Svijet X: {player_world_x:.0f}",
                    f"View Offset X: {view_offset_x:.0f}",
                    f"Okviri: {frames_survived}",
                    f"Akcija: {brain.current_instruction_number}/{len(brain.instructions)} (Smjer: {current_x_direction if current_ai_action else 'N/A'})",
                    f"Stagnacija: {stagnation_frames}/{STAGNATION_LIMIT_MAX_X}"
                ]
                for i, text_content in enumerate(texts):
                    try: # Dodatna provjera za renderiranje teksta
                        text_surface = font.render(text_content, True, font_color)
                        screen_for_simulation.blit(text_surface, (10, 10 + i * 30))
                    except Exception as e_render_font: # Ako dođe do greške pri renderiranju
                        # print(f"Greška pri renderiranju teksta: {e_render_font}")
                        pass # Ignoriraj grešku i nastavi bez tog teksta

            pygame.display.update()
            if clock: clock.tick(FPS)

        action_frames_remaining -= 1
        frames_survived += 1
    # Kraj while petlje

    # Izračun fitnessa
    fitness = max_world_x_achieved * 1.5 # Nagradi udaljenost
    penalty_factor_left_movement = 5.0 # Kazna za kretanje ulijevo
    fitness -= total_left_movement_world * penalty_factor_left_movement
    
    if player_world_x < -100: # Ako je otišao predaleko ulijevo
        fitness -= 20000 # Dodatna kazna

    if game_won_by_ai:
        fitness += 2000000.0 # Veliki bonus za pobjedu
        # Nagradi AI ako je pobijedio s manje instrukcija (brže)
        fitness += (len(brain.instructions) - brain.current_instruction_number) * 200 # Bonus za preostale instrukcije
        if render and font: print(f"Brain {brain_idx} POBJEDIO! Fitness: {fitness:.2f}")
    else:
        # Ako nije pobijedio, a nije ni pao s ekrana (što ima svoju kaznu)
        if max_world_x_achieved < 50: # Ako se jedva pomaknuo
            fitness -= 50000 # Kazna za mali napredak
        elif brain.fitness != -300000.0 : # Ako nije već dobio kaznu za pad
            fitness += frames_survived * 0.01 # Mali bonus za preživljavanje

    # Ako je fitness postavljen zbog pada (-300000), ne mijenjaj ga osim ako je pobijedio
    if brain.fitness == -300000.0 and not game_won_by_ai:
        pass # Zadrži kaznu za pad
    else:
        brain.fitness = fitness

    # Zatvori display samo ako je bio otvoren za renderiranje i ako je inicijaliziran
    if render and screen_for_simulation and pygame.display.get_init():
        pygame.display.quit() # Ugasi samo display prozor ove simulacije

    return brain.fitness