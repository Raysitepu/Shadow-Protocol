import pygame
import sys

# Inisialisasi pygame
pygame.init()
screen_width, screen_height = 512, 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Shadow Protocol - Title Screen")

# Load assets
background = pygame.image.load('assets/background21.jpg')
background = pygame.transform.scale(background, (screen_width, screen_height))
font_title = pygame.font.Font('assets/font.ttf', 53)
font_menu = pygame.font.Font('assets/font.ttf', 25)

# Warna
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
selected_color = (255, 0, 0)  

# Menu options
menu_options = ["CONTINUE", "START", "OPTIONS", "EXIT"]
selected = 0

# Fungsi untuk render menu
def draw_menu():
    global selected 
    screen.blit(background, (0, 0))  

    title_text1 = "SHADOW"
    title_text2 = "PROTOCOL"

    title_surface1 = font_title.render(title_text1, True, CYAN) 
    title_surface2 = font_title.render(title_text2, True,  CYAN)  

    # Adjust title position to center both parts
    title_rect1 = title_surface1.get_rect(center=(screen_width // 2, 120))  
    title_rect2 = title_surface2.get_rect(center=(screen_width // 2, 170))  

    screen.blit(title_surface1, title_rect1)
    screen.blit(title_surface2, title_rect2)

    spacing = 60  
    start_y = 300 

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for idx, text in enumerate(menu_options):
        color = selected_color if idx == selected else CYAN 
        label = font_menu.render(text, True, color)
        label_rect = label.get_rect(center=(screen_width // 2, start_y + idx * spacing))  

        if label_rect.collidepoint(mouse_x, mouse_y):
            selected = idx

        screen.blit(label, label_rect)

# Main loop
clock = pygame.time.Clock()
running = True
while running:
    screen.fill((0, 0, 0))
    draw_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(menu_options)  # Move down in menu
            elif event.key == pygame.K_UP:
                selected = (selected - 1) % len(menu_options)  # Move up in menu
            elif event.key == pygame.K_RETURN:
                print(f"Selected: {menu_options[selected]}")
                if menu_options[selected] == "EXIT":
                    running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()