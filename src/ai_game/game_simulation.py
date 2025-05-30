import pygame
import os
import sys

from src.core.platforms import PlatformManager
from src.core.player import Player
from .ai_brain import Brain, AIAction


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

MAX_ACTION_DURATION_FRAMES = 30 # Koliko maksimalno frameova traje jedna AI akcija

def run_simulation_for_brain(brain, level_filepath, render=False, current_generation=0, brain_idx=0):
    screen_for_simulation = None
    font = None
    background_image_sim = None

    if render: # Inicijalizacija Pygamea samo ako je potrebno iscrtavanje
        if not pygame.display.get_init():
            pygame.display.init()

        screen_for_simulation = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Super Toni Bros - AI Gen: {current_generation} Brain: {brain_idx}")

        base_path_sim = os.path.dirname(os.path.abspath(__file__))
        background_path_sim = os.path.join(base_path_sim, "..", "..", "images", "Background.jpeg")
        try:
            background_image_sim = pygame.image.load(background_path_sim).convert()
        except pygame.error as e:
            background_image_sim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background_image_sim.fill((200, 200, 255))

        if not pygame.font.get_init():
            pygame.font.init()
        if pygame.font.get_init():
            try:
                font = pygame.font.SysFont(None, 30)
            except Exception as e_font:
                try:
                    font = pygame.font.Font(None, 30)
                except Exception as e_font_default:
                    font = None
        else:
            font = None
    else: # Ako nema renderiranja, koristi dummy display da Pygame radi u pozadini
        if not pygame.display.get_init():
            try:
                pygame.display.init()
                screen_for_simulation = pygame.display.set_mode((1, 1), pygame.NOFRAME)
            except pygame.error as e:
                pass


    try:
        platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath) #
        platform_manager.generate_platforms() 
    except pygame.error as e:
        brain.fitness = -float('inf') # Kazna ako level nije uspješno učitan
        if render and screen_for_simulation and pygame.display.get_init():
            pygame.display.quit()
        return brain.fitness
    except Exception as e:
        brain.fitness = -float('inf')
        if render and screen_for_simulation and pygame.display.get_init():
            pygame.display.quit()
        return brain.fitness


    player_start_x_on_screen = 100
    player_world_x = 0.0 # Pozicija igrača u svijetu igre (neovisno o ekranu)

    player_visual_height = 50 * 1.5

    player_initial_y = SCREEN_HEIGHT - player_visual_height - 70
    if platform_manager.platforms:
        first_platform_rect = platform_manager.platforms[0]
        player_initial_y = first_platform_rect.top - player_visual_height

    player = Player(player_start_x_on_screen, player_initial_y, 50, 50) #
    if platform_manager.platforms : player.on_ground = True


    brain.reset_instructions() 

    max_world_x_achieved = 0.0 # Najdalja dosegnuta x koordinata
    total_left_movement_world = 0.0 # Ukupno kretanje ulijevo, koristi se za penalizaciju

    frames_survived = 0 # Brojač frameova preživljavanja, koristi se u fitnessu
    game_won_by_ai = False

    current_ai_action = None
    action_frames_remaining = 0
    jump_executed_for_current_action = False # Sprječava višestruke skokove unutar jedne "jump" akcije

    simulation_running = True

    stagnation_frames = 0 # Brojač frameova bez značajnog napretka
    STAGNATION_LIMIT_MAX_X = 240 # Limit frameova stagnacije prije prekida simulacije
    last_check_world_x = player_world_x

    view_offset_x = 0.0 # Pomak kamere (view)

    clock = pygame.time.Clock() if render else None

    while simulation_running:
        if render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    simulation_running = False
                    brain.fitness = -float('inf') # Kazna ako se prozor zatvori tijekom simulacije
                    if pygame.display.get_init(): pygame.display.quit()
                    return brain.fitness
            if not simulation_running: break


        if action_frames_remaining <= 0: # Vrijeme je za sljedeću AI akciju
            current_ai_action = brain.get_next_action() 
            if current_ai_action is None: # Nema više akcija u mozgu
                simulation_running = False; break
            action_frames_remaining = int(current_ai_action.hold_time * MAX_ACTION_DURATION_FRAMES) #
            jump_executed_for_current_action = False

        current_x_direction = 0
        if current_ai_action:
            if current_ai_action.is_jump and player.on_ground and not jump_executed_for_current_action: #
                player.jump(JUMP_STRENGTH) 
                jump_executed_for_current_action = True
            current_x_direction = current_ai_action.x_direction #

        player.apply_gravity(GRAVITY) 

        if player.rect.top > SCREEN_HEIGHT + 200: # Igrač je pao s ekrana
            brain.fitness = -300000.0; simulation_running = False; break # Velika kazna za pad

        world_movement_this_frame = 0
        if current_x_direction == 1:
            world_movement_this_frame = PLAYER_SPEED
            player.facing_left = False
        elif current_x_direction == -1:
            world_movement_this_frame = -PLAYER_SPEED
            player.facing_left = True

        player_world_x += world_movement_this_frame

        if world_movement_this_frame < 0:
            total_left_movement_world += abs(world_movement_this_frame)

        view_offset_x = player_world_x # Kamera prati igrača

        if player_world_x > max_world_x_achieved:
            max_world_x_achieved = player_world_x
            stagnation_frames = 0 # Resetira brojač stagnacije ako postoji napredak
        else:
             if abs(player_world_x - last_check_world_x) < 1.0 : # Ako se igrač jedva pomaknuo
                 stagnation_frames +=1
        if abs(player_world_x - last_check_world_x) >= 1.0: # Ako je pomak bio značajan
             stagnation_frames = 0
        last_check_world_x = player_world_x


        if stagnation_frames > STAGNATION_LIMIT_MAX_X : # Prekid ako je AI zapeo
            simulation_running = False; break

        player.on_ground = False
        for plat_obj_original in platform_manager.platforms:
            # Preračunavanje pozicije platforme s obzirom na pomak kamere
            temp_plat_rect = pygame.Rect(plat_obj_original.x - view_offset_x + player_start_x_on_screen,
                                         plat_obj_original.y,
                                         plat_obj_original.width,
                                         plat_obj_original.height)

            collision_plat_rect = pygame.Rect(plat_obj_original.x - view_offset_x, # Stvarna pozicija platforme za koliziju
                                              plat_obj_original.y,
                                              plat_obj_original.width,
                                              plat_obj_original.height)

            if player.collide_with_platform(collision_plat_rect): 
                player.on_ground = True; break

        if platform_manager.goal:
            goal_original = platform_manager.goal
            temp_goal_rect = pygame.Rect(goal_original.x - view_offset_x,
                                         goal_original.y,
                                         goal_original.width,
                                         goal_original.height)
            if player.rect.colliderect(temp_goal_rect): # Provjera je li AI dosegao cilj
                game_won_by_ai = True; simulation_running = False; break

        player.update_image_direction() 

        if render and screen_for_simulation:
            if background_image_sim:
                bg_width = background_image_sim.get_width()
                render_x_bg = (-view_offset_x) % bg_width # Scrolling pozadine
                screen_for_simulation.blit(background_image_sim, (render_x_bg - bg_width, 0))
                screen_for_simulation.blit(background_image_sim, (render_x_bg, 0))
            else:
                 screen_for_simulation.fill((200,200,255))

            platform_manager.draw_with_offset(screen_for_simulation, view_offset_x) 
            player.draw(screen_for_simulation) 

            if font:
                font_color = (0,0,0)
                texts = [
                    f"Generacija: {current_generation}", 
                    f"Potez AI: {brain.current_instruction_number}", 
                    f"Vrijeme: {frames_survived / FPS:.2f} s" 
                ]
                for i, text_content in enumerate(texts):
                    try:
                        text_surface = font.render(text_content, True, font_color)
                        screen_for_simulation.blit(text_surface, (10, 10 + i * 30))
                    except Exception as e_render_font:
                        pass # Greška pri renderiranju teksta se ignorira

            pygame.display.update()
            if clock: clock.tick(FPS) # Održavanje konstantnog FPS-a

        action_frames_remaining -= 1
        frames_survived += 1 

    # Izračun fitnessa na kraju simulacije
    fitness = max_world_x_achieved * 1.5 # Nagrada za udaljenost
    penalty_factor_left_movement = 5.0
    fitness -= total_left_movement_world * penalty_factor_left_movement # Kazna za kretanje ulijevo

    if player_world_x < -100: # Dodatna kazna ako završi daleko lijevo od početka
        fitness -= 20000

    if game_won_by_ai:
        fitness += 2000000.0 # Velika nagrada za pobjedu
        fitness += (len(brain.instructions) - brain.current_instruction_number) * 200 # Bonus za preostale neiskorištene instrukcije (brzina)
    else:
        if max_world_x_achieved < 50: # Kazna ako nije prešao ni početak
            fitness -= 50000
        elif brain.fitness != -300000.0 : # Izbjegava dodavanje fitnessa ako je već pao
            fitness += frames_survived * 0.01 # Mala nagrada za preživljavanje

    if brain.fitness == -300000.0 and not game_won_by_ai: # Ako je pao, zadržava se kazna za pad
        pass
    else:
        brain.fitness = fitness

    if render and screen_for_simulation and pygame.display.get_init():
        pygame.display.quit() # Zatvara Pygame display ako je bio korišten za renderiranje

    return brain.fitness