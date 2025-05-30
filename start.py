# start.py - ISPRAVLJENA VERZIJA

import os
import sys
import pygame

# === DODANO: Inicijaliziraj Pygame na početku ===
pygame.init()
# ===============================================

# Postavi varijablu okoline PRIJE uvoza Pygamea.
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Dohvati korijenski direktorij projekta (gdje se nalazi start.py)
project_root = os.path.dirname(os.path.abspath(__file__))

# Dodaj korijenski direktorij projekta u sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- ISPIS ZA DEBUGIRANJE (možete ih ukloniti nakon što proradi) ---
# print(f"sys.path nakon modifikacije: {sys.path}")
# print(f"Pokušavam uvesti iz paketa 'src' u: {project_root}")
# --- KRAJ ISPISA ZA DEBUGIRANJE ---

try:
    import src.main as main_module
    import src.main_ga as main_ga_module

    run_manual_game = main_module.run_game
    run_genetic_algorithm = main_ga_module.run_genetic_algorithm

except ImportError as e:
    print(f"Greška pri importu modula igre (src.main ili src.main_ga): {e}")
    # ... (ostatak error handlinga za import)
    sys.exit(1)
except AttributeError as e:
    print(f"AttributeError: {e}. Provjerite da funkcija 'run_game' postoji u 'src/main.py' i 'run_genetic_algorithm' u 'src/main_ga.py' na top-levelu.")
    # ... (ostatak error handlinga za AttributeError)
    sys.exit(1)
except Exception as e:
    print(f"Neočekivana greška prilikom importa: {e}")
    sys.exit(1)

# Inicijalizacija Pygame font modula (pygame.init() gore bi ovo trebao pokriti, ali ne škodi)
if not pygame.font.get_init():
    pygame.font.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# screen je sada modul-level varijabla, inicijalizirana nakon pygame.init()
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
    return is_hovering # Vrati hover stanje da se može koristiti u event petlji

def main_menu():
    global screen # === VAŽNO: Koristimo globalnu 'screen' varijablu ===

    # Put do level.txt datoteke.
    level_filepath_menu = os.path.join(project_root, "src", "level.txt")

    background_image = None
    try:
        background_path_menu = os.path.join(project_root, "images", "Background.jpeg")
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
        # Dohvati hover stanja na početku svakog okvira
        # (draw_button interno dohvaća mouse_pos, pa ovo nije nužno za samo crtanje, ali jest za logiku klika)
        is_manual_hover = manual_play_button_rect.collidepoint(pygame.mouse.get_pos())
        is_ai_hover = ai_play_button_rect.collidepoint(pygame.mouse.get_pos())
        is_exit_hover = exit_button_rect.collidepoint(pygame.mouse.get_pos())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Lijevi klik
                    if is_manual_hover:
                        print("Pokretanje ručne igre...")
                        run_manual_game(level_filepath_menu)
                        # === ISPRAVAK: Ponovno dodijeli 'screen' ===
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
                        pygame.display.set_caption("Super Toni Bros - Izbornik")
                    elif is_ai_hover:
                        print("Pokretanje genetskog algoritma (AI)...")
                        run_genetic_algorithm()
                        # === ISPRAVAK: Ponovno dodijeli 'screen' ===
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
                        pygame.display.set_caption("Super Toni Bros - Izbornik")
                    elif is_exit_hover:
                        running = False
        
        # Crtanje na ekran
        screen.fill(LIGHT_BLUE) # Sada bi trebalo raditi s ispravnom 'screen' površinom
        if background_image:
            screen.blit(background_image, (0, 0))
        else: # Fallback ako nema pozadinske slike
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,120)) # Poluprozirni crni overlay
            screen.blit(overlay, (0,0))

        draw_text("Super Toni Bros", title_font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        # Funkcija draw_button sama provjerava hover, pa ne moramo prosljeđivati is_..._hover
        draw_button(screen, manual_play_button_rect, "Igraj Ručno", WHITE, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        draw_button(screen, ai_play_button_rect, "Pokreni AI", WHITE, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        draw_button(screen, exit_button_rect, "Izlaz", WHITE, BUTTON_COLOR, BUTTON_HOVER_COLOR)

        pygame.display.update()
        pygame.time.Clock().tick(30)
        
    pygame.quit() # Ugasi Pygame kada se izađe iz glavne petlje (npr. klik na Izlaz)
    sys.exit()

if __name__ == "__main__":
    main_menu()