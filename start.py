import os
import sys
import pygame


src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")


if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from main import run_game as run_manual_game
    from main_ga import run_genetic_algorithm
except ImportError as e:
    print(f"Greška pri importu modula igre (main.py ili main_ga.py): {e}")
    print(f"Provjerite jesu li datoteke 'main.py' i 'main_ga.py' u direktoriju: '{src_path}'.")
    print(f"Također, provjerite jesu li importi unutar tih datoteka prilagođeni (bez vodeće točke).")
    print(f"Trenutni sys.path: {sys.path}")
    sys.exit(1)
except Exception as e:
    print(f"Neočekivana greška prilikom importa: {e}")
    sys.exit(1)

pygame.font.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Toni Bros - Izbornik")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
BUTTON_COLOR = (100, 100, 200)
BUTTON_HOVER_COLOR = (150, 150, 250)

try:
    font = pygame.font.Font(None, 50)
    title_font = pygame.font.Font(None, 70)
except Exception as e:
    print(f"Greška pri učitavanju fonta: {e}. Koristi se SysFont.")
    font = pygame.font.SysFont(None, 50)
    title_font = pygame.font.SysFont(None, 70)

def draw_text(text, text_font, color, surface, x, y, center=True):
    text_obj = text_font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x,y)
    surface.blit(text_obj, text_rect)

def draw_button(surface, rect, text, text_color, button_color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    is_hovering = rect.collidepoint(mouse_pos)
    current_color = hover_color if is_hovering else button_color
    pygame.draw.rect(surface, current_color, rect)
    draw_text(text, font, text_color, surface, rect.centerx, rect.centery)
    return is_hovering

def main_menu():
    level_filepath_menu = os.path.join(src_path, "level.txt") #

    background_image = None
    try:
        project_root_path = os.path.dirname(os.path.abspath(__file__))
        background_path_menu = os.path.join(project_root_path, "images", "Background.jpeg") #
        if os.path.exists(background_path_menu):
            background_image = pygame.image.load(background_path_menu).convert()
            background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Greška pri učitavanju pozadinske slike za izbornik: {e}")

    button_width = 300
    button_height = 70
    spacing = 30
    manual_play_button_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, SCREEN_HEIGHT // 2 - button_height - spacing // 2, button_width, button_height)
    ai_play_button_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, SCREEN_HEIGHT // 2 + spacing // 2, button_width, button_height)
    exit_button_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, SCREEN_HEIGHT // 2 + button_height + spacing * 1.5, button_width, button_height)

    running = True
    while running:
        screen.fill(LIGHT_BLUE)
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,120))
            screen.blit(overlay, (0,0))

        draw_text("Super Toni Bros", title_font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        is_manual_hover = draw_button(screen, manual_play_button_rect, "Igraj Ručno", WHITE, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        is_ai_hover = draw_button(screen, ai_play_button_rect, "Pokreni AI", WHITE, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        is_exit_hover = draw_button(screen, exit_button_rect, "Izlaz", WHITE, BUTTON_COLOR, BUTTON_HOVER_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if is_manual_hover:
                        print("Pokretanje ručne igre...")
                        run_manual_game(level_filepath_menu) #
                        running = False
                    elif is_ai_hover:
                        print("Pokretanje genetskog algoritma (AI)...")
                        run_genetic_algorithm()
                        running = False
                    elif is_exit_hover:
                        running = False
        pygame.display.update()
        pygame.time.Clock().tick(30)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()