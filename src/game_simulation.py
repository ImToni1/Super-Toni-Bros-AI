import pygame
import os
import sys
from platforms import PlatformManager
from player import Player
from ai_brain import Brain, AIAction

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

MAX_ACTION_DURATION_FRAMES = 30
MAX_SIMULATION_FRAMES_PER_BRAIN = 3600

def run_simulation_for_brain(brain, level_filepath, render=False, current_generation=0, brain_idx=0):
    pygame.init()

    screen_for_simulation = None
    font = None

    if render:
        screen_for_simulation = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Super Toni Bros - AI Gen: {current_generation} Brain: {brain_idx}")
        base_path_sim = os.path.dirname(os.path.abspath(__file__))
        background_path_sim = os.path.join(base_path_sim, "..", "images", "Background.jpeg")
        try:
            background_image_sim = pygame.image.load(background_path_sim).convert()
        except pygame.error as e:
            print(f"Error loading background image in simulation: {e}")
            print(f"Attempted path: {background_path_sim}")
            background_image_sim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background_image_sim.fill((200, 200, 255))
        font = pygame.font.SysFont(None, 30)
    else:
        try:
            screen_for_simulation = pygame.display.set_mode((1, 1), pygame.NOFRAME)
        except pygame.error as e:
            print(f"Warning: Could not set dummy display in headless mode: {e}. Image operations might fail or be slow.")
        if pygame.font.get_init():
             font = pygame.font.SysFont(None, 30)
        else:
            print("Warning: Font module not initialized in headless mode.")

    clock = pygame.time.Clock()

    player = Player(100, SCREEN_HEIGHT - 150, 50, 50)
    platform_manager = PlatformManager(SCREEN_WIDTH, SCREEN_HEIGHT, level_filepath)
    platform_manager.generate_platforms()

    brain.reset_instructions()

    total_scroll_achieved = 0.0
    frames_survived = 0
    game_won_by_ai = False

    current_ai_action = None
    action_frames_remaining = 0
    jump_executed_for_current_action = False

    simulation_running = True
    last_scroll = 0.0
    stagnation_frames = 0
    MAX_STAGNATION_FRAMES = 60  # npr. 1 sekunda

    for frame_num in range(MAX_SIMULATION_FRAMES_PER_BRAIN):
        if not simulation_running:
            break

        if render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    simulation_running = False
            if not simulation_running:
                break

        if action_frames_remaining <= 0:
            current_ai_action = brain.get_next_action()
            if current_ai_action is None:
                simulation_running = False
                break
            action_frames_remaining = int(current_ai_action.hold_time * MAX_ACTION_DURATION_FRAMES)
            jump_executed_for_current_action = False

        simulated_keys_pressed = {pygame.K_SPACE: False, pygame.K_LEFT: False, pygame.K_RIGHT: False}
        if current_ai_action:
            if current_ai_action.is_jump and player.on_ground and not jump_executed_for_current_action:
                player.jump(JUMP_STRENGTH)
                jump_executed_for_current_action = True

            if current_ai_action.x_direction == -1:
                simulated_keys_pressed[pygame.K_LEFT] = True
            elif current_ai_action.x_direction == 1:
                simulated_keys_pressed[pygame.K_RIGHT] = True

        player.apply_gravity(GRAVITY)

        if player.rect.top > SCREEN_HEIGHT:
            simulation_running = False
            break

        requested_scroll_offset = 0
        if simulated_keys_pressed[pygame.K_RIGHT]:
            requested_scroll_offset = PLAYER_SPEED
            player.facing_left = False
        elif simulated_keys_pressed[pygame.K_LEFT]:
            requested_scroll_offset = -PLAYER_SPEED
            player.facing_left = True

        actual_scroll_offset = requested_scroll_offset

        # Ograniči kretanje tako da igrač ne može izaći iz ekrana desno ili lijevo
        if player.rect.left + actual_scroll_offset < 0:
            actual_scroll_offset = -player.rect.left
        if player.rect.right + actual_scroll_offset > SCREEN_WIDTH:
            actual_scroll_offset = SCREEN_WIDTH - player.rect.right

        platform_manager.update_platforms(actual_scroll_offset)
        total_scroll_achieved -= actual_scroll_offset

        # --- DETEKCIJA ZABIJANJA U ZID ---
        if abs(total_scroll_achieved - last_scroll) < 1.0:
            stagnation_frames += 1
        else:
            stagnation_frames = 0
        last_scroll = total_scroll_achieved

        if stagnation_frames > MAX_STAGNATION_FRAMES:
            # Penaliziraj i prekini simulaciju
            fitness = total_scroll_achieved - 1000
            brain.fitness = fitness
            break

        player.on_ground = False
        for plat_idx, plat_obj in enumerate(platform_manager.platforms):
            if plat_idx == 2 and player.rect.colliderect(plat_obj):
                pass

            if player.collide_with_platform(plat_obj):
                if plat_idx != 2:
                    player.on_ground = True
                break

        if platform_manager.goal and player.rect.colliderect(platform_manager.goal):
            game_won_by_ai = True
            simulation_running = False
            break

        player.update_image_direction()

        if render and screen_for_simulation and font:
            for x_bg in range(0, SCREEN_WIDTH, background_image_sim.get_width()):
                for y_bg in range(0, SCREEN_HEIGHT, background_image_sim.get_height()):
                    screen_for_simulation.blit(background_image_sim, (x_bg, y_bg))

            platform_manager.draw(screen_for_simulation)
            player.draw(screen_for_simulation)

            info_text_fitness = font.render(f"Fitness (scroll): {total_scroll_achieved:.0f}", True, (0,0,0))
            info_text_frames = font.render(f"Frames: {frames_survived}/{MAX_SIMULATION_FRAMES_PER_BRAIN}", True, (0,0,0))
            info_text_action = font.render(f"Action: {brain.current_instruction_number}/{len(brain.instructions)}", True, (0,0,0))
            screen_for_simulation.blit(info_text_fitness, (10, 10))
            screen_for_simulation.blit(info_text_frames, (10, 40))
            screen_for_simulation.blit(info_text_action, (10, 70))

            pygame.display.update()
            clock.tick(FPS)

        action_frames_remaining -= 1
        frames_survived += 1

    fitness = total_scroll_achieved

    if game_won_by_ai:
        fitness += 100000.0
        fitness += (MAX_SIMULATION_FRAMES_PER_BRAIN - frames_survived) * 10
    else:
        fitness += frames_survived * 0.1

    if total_scroll_achieved < 50 and frames_survived > MAX_SIMULATION_FRAMES_PER_BRAIN * 0.5:
        fitness -= 10000

    if player.rect.top > SCREEN_HEIGHT and not game_won_by_ai:
        fitness -= 50000

    brain.fitness = fitness

    if render:
        pygame.display.quit()

    return fitness
