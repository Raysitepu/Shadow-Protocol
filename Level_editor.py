import pygame
import csv
import os
import button

pygame.init()

clock = pygame.time.Clock()
FPS = 60


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')


ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 14 
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1


pine1_img = pygame.image.load('assets/level1/Background.png').convert_alpha()
pine1_img = pygame.transform.scale(pine1_img, (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))


img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'assets/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)
dark_blue = (0, 0, 128)

# Font
font = pygame.font.SysFont('Futura', 30)


world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)


for tile in range(0, MAX_COLS):
    world_data[ROWS - 1][tile] = 0


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(dark_blue)
    width = pine1_img.get_width()
    for x in range(4):
        screen.blit(pine1_img, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height()))


def draw_grid():
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))

def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))


def save_level(level):
    with open(f'level{level}_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in world_data:
            writer.writerow(row)
    print(f'Level {level} saved.')


def load_level(level):
    try:
        with open(f'level{level}_data.csv', newline='') as file:
            reader = csv.reader(file)
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    world_data[y][x] = int(tile)
        print(f'Level {level} loaded.')
    except FileNotFoundError:
        print(f'Level {level} not found. Starting empty.')
        for y in range(ROWS):
            for x in range(MAX_COLS):
                world_data[y][x] = -1


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        # Get mouse position
        pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

# Main loop
run = True
while run:
    clock.tick(FPS)
    draw_bg()
    draw_world()
    draw_grid()

    pygame.draw.rect(screen, dark_blue, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))
    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)
    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP/DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
    draw_text('S: Save  |  L: Load', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 30)

    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_s:
                save_level(level)
            if event.key == pygame.K_l:
                load_level(level)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1


    pygame.display.update()


    pygame.display.update()

pygame.quit()
