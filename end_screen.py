import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("End Screen - Shadow Protocol")

background = pygame.image.load("assets/background21.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load custom font with error handling
try:
    font_title = pygame.font.Font("assets/font.ttf", 72)
    font_text = pygame.font.Font("assets/font.ttf", 36)
except FileNotFoundError:
    print("Font file not found. Please check the path.")
    pygame.quit()
    sys.exit()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (0, 255, 255)

def draw_text_button(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)
    return rect

def end_screen(score):
    running = True
    while running:
        screen.blit(background, (0, 0))

        title = font_title.render("GAME OVER", True, RED)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        score_text = font_text.render(f"Your Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 200))

        y_start = 300
        gap = 60

        restart_rect = draw_text_button("Restart", font_text, LIGHT_BLUE, WIDTH//2, y_start)
        quit_rect = draw_text_button("Quit", font_text, LIGHT_BLUE, WIDTH//2, y_start + gap)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if restart_rect.collidepoint(mouse_pos):
            draw_text_button("Restart", font_text, WHITE, WIDTH//2, y_start)
            if mouse_click[0]:
                return "restart"

        if quit_rect.collidepoint(mouse_pos):
            draw_text_button("Quit", font_text, WHITE, WIDTH//2, y_start + gap)
            if mouse_click[0]:
                pygame.quit()
                sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

# Menjalankan end screen dengan score contoh
if __name__ == "__main__":
    result = end_screen(100)  # Contoh score 100
    if result == "restart":
        print("Game akan di-restart")

