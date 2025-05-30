import pygame
from pygame import mixer
import os
import random
import csv
import sys

# Initialize pygame
mixer.init()
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shadow Protocol')

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Game variables
GRAVITY = 0.75
SCROLL_THRESH = 350
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 14
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
score = 0  # Menambahkan variabel skor

# Transition variables
transition_active = False
transition_fade = None
level_complete = False

# Player actions
moving_left = False
moving_right = False
shoot = False

# Load images
# Background
background_img = pygame.image.load('assets/level1/Background.png').convert_alpha()

# Load sound effects
shot_fx = pygame.mixer.Sound('assets/audio/shoot.mp3')
shot_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('assets/audio/jump.mp3')
jump_fx.set_volume(0.5)

# Tiles
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'assets/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# Bullet
bullet_img = pygame.image.load('assets/icon/bullet.png').convert_alpha()

# Items
health_box_img = pygame.image.load('assets/icon/health.png').convert_alpha()
ammo_box_img = pygame.image.load('assets/icon/ammo.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img
}

# Colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)
CYAN = (0, 255, 255)

# Font
font = pygame.font.SysFont('Futura', 30)

# Load custom font for end screen
try:
    font_title = pygame.font.Font("assets/font.ttf", 72)
    font_text = pygame.font.Font("assets/font.ttf", 36)
except FileNotFoundError:
    print("Font file not found. Using system font.")
    font_title = pygame.font.SysFont('Futura', 72)
    font_text = pygame.font.SysFont('Futura', 36)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_score():
    draw_text(f'SCORE: {score}', font, WHITE, SCREEN_WIDTH - 150, 10)

def draw_text_button(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)
    return rect

def end_screen(score):
    running = True
    # Load dan scale background
    try:
        background = pygame.image.load("assets/background21.jpg")
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(BLACK)
    
    while running:
        # Draw background
        screen.blit(background, (0, 0))
        
        title = font_title.render("GAME OVER", True, RED)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        score_text = font_text.render(f"Your Score: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 200))

        y_start = 300
        gap = 60

        restart_rect = draw_text_button("Restart", font_text, CYAN, SCREEN_WIDTH//2, y_start)
        quit_rect = draw_text_button("Quit", font_text, CYAN, SCREEN_WIDTH//2, y_start + gap)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if restart_rect.collidepoint(mouse_pos):
            draw_text_button("Restart", font_text, WHITE, SCREEN_WIDTH//2, y_start)
            if mouse_click[0]:
                return "restart"

        if quit_rect.collidepoint(mouse_pos):
            draw_text_button("Quit", font_text, WHITE, SCREEN_WIDTH//2, y_start + gap)
            if mouse_click[0]:
                pygame.quit()
                sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

def draw_bg():
    screen.fill(BG)
    width = background_img.get_width()
    for x in range(5):
        screen.blit(background_img, ((x * width) - bg_scroll * 0.5, 0))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, damage=20):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        self.damage = damage  # Damage inflicted by this soldier's bullets or attacks
        
        # AI specific
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # Load all images
        animation_types = ['idle', 'walk', 'jump', 'death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'assets/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'assets/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check collision with tiles
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Check collision with moving platforms
        for platform in world.moving_platforms:
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = platform.rect.bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = platform.rect.top - self.rect.bottom
                    # Jika player berdiri di platform, ikut bergerak dengan platform
                    if self.char_type == 'zeero':
                        self.rect.x += platform.speed * platform.move_direction
                        dx += platform.speed * platform.move_direction

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == 'zeero':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.char_type == 'zeero':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.damage)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if not self.idling:
                    ai_moving_right = self.direction == 1
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range):
        pygame.sprite.Sprite.__init__(self)
        self.image = img_list[4]  # Menggunakan tile 4
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_range = move_range
        self.move_counter = 0
        self.move_direction = 1
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.move_direction
        self.move_counter += 1
        if self.move_counter >= self.move_range:
            self.move_direction *= -1
            self.move_counter = 0

class World:
    def __init__(self):
        self.obstacle_list = []
        self.moving_platforms = pygame.sprite.Group()

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 6:
                        if tile == 4:  # Moving platform
                            platform = MovingPlatform(x * TILE_SIZE, y * TILE_SIZE, 100)
                            self.moving_platforms.add(platform)
                        else:
                            self.obstacle_list.append(tile_data)
                    elif tile == 7:  # Player
                        global player, health_bar
                        player = Soldier('zeero', 
                            x * TILE_SIZE, 
                            y * TILE_SIZE + 15,0.8,3,20, damage=25)
                        player.health = 200
                        player.max_health = 200
                        health_bar = HealthBar(10, 10, player.health, player.max_health)    
                    elif tile == 8:  # Enemy1
                        enemy = Soldier('enemy1', x * TILE_SIZE, y * TILE_SIZE, 1.0, 2, 20, damage=10)
                        enemy.health= 100
                        enemy.max_health = 100
                        enemy_group.add(enemy)
                    elif tile == 9:  # Enemy2
                        enemy = Soldier('enemy2', x * TILE_SIZE, y * TILE_SIZE, 1.0, 2, 20, damage=15)
                        enemy.health= 100
                        enemy.max_health = 100
                        enemy_group.add(enemy)
                    elif tile == 10:  # Enemy3
                        enemy = Soldier('enemy3', x * TILE_SIZE, y * TILE_SIZE, 1.0, 2, 20, damage=20)
                        enemy.health= 100
                        enemy.max_health = 100
                        enemy_group.add(enemy)
                    elif tile == 12:  # Ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 11:  # Health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 13:  # Exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
        for platform in self.moving_platforms:
            platform.rect.x += screen_scroll
            screen.blit(platform.image, platform.rect)

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 30
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            self.kill()

class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 8
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.damage = damage  # damage this bullet will cause

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # Bullet hitting player
        if pygame.sprite.collide_rect(player, self) and self.direction != player.direction:
            # Check if bullet is from enemy (direction opposite player)
            if player.alive:
                player.health -= self.damage
                if player.health <= 0:
                    player.health = 0
                    player.alive = False
                self.kill()

        # Bullet hitting enemies
        for enemy in enemy_group:
            # Bullet should be from player to damage enemies
            if pygame.sprite.collide_rect(enemy, self) and self.direction == player.direction:
                if enemy.alive:
                    enemy.health -= self.damage
                    if enemy.health <= 0:
                        enemy.health = 0
                        enemy.alive = False
                        global score
                        if enemy.char_type == 'enemy1':
                            score += 10
                        elif enemy.char_type == 'enemy2':
                            score += 15
                        elif enemy.char_type == 'enemy3':
                            score += 20
                    self.kill()

class ScreenFade:
    def __init__(self, direction, color, speed):
        self.direction = direction  # 1 = horizontal, 2 = vertical
        self.color = color
        self.speed = speed
        self.fade_counter = 0
        self.fade_complete = False
        
    def reset(self):
        self.fade_counter = 0
        self.fade_complete = False
        
    def fade(self):
        if not self.fade_complete:
            self.fade_counter += self.speed
            
            if self.direction == 1:  # Horizontal fade
                pygame.draw.rect(screen, self.color, (0, 0, self.fade_counter, SCREEN_HEIGHT))
                pygame.draw.rect(screen, self.color, (SCREEN_WIDTH - self.fade_counter, 0, self.speed, SCREEN_HEIGHT))
            elif self.direction == 2:  # Vertical fade
                pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, self.fade_counter))
            
            if self.fade_counter >= SCREEN_HEIGHT:
                self.fade_complete = True
                
        return self.fade_complete

def show_main_menu():
    try:
        background = pygame.image.load('assets/background21.jpg')
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        font_title = pygame.font.Font('assets/font.ttf', 53)
        font_menu = pygame.font.Font('assets/font.ttf', 25)
    except:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill((0, 0, 50))
        font_title = pygame.font.SysFont('arial', 53, bold=True)
        font_menu = pygame.font.SysFont('arial', 25)

    menu_options = ["START", "EXIT"]
    selected = 0
    menu_active = True

    while menu_active:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if menu_options[selected] == "START":
                        return True
                    elif menu_options[selected] == "EXIT":
                        pygame.quit()
                        sys.exit()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, option in enumerate(menu_options):
                    text_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 300 + idx*60, 200, 40)
                    if text_rect.collidepoint(mouse_pos):
                        if option == "START":
                            return True
                        elif option == "EXIT":
                            pygame.quit()
                            sys.exit()

        screen.blit(background, (0, 0))
        
        # Title
        title1 = font_title.render("SHADOW", True, CYAN)
        title2 = font_title.render("PROTOCOL", True, CYAN)
        screen.blit(title1, (SCREEN_WIDTH//2 - title1.get_width()//2, 120))
        screen.blit(title2, (SCREEN_WIDTH//2 - title2.get_width()//2, 180))
        
        # Menu options
        for idx, option in enumerate(menu_options):
            color = RED if idx == selected else CYAN
            text = font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 320 + idx*60))
            
            if text_rect.collidepoint(mouse_pos):
                selected = idx
                pygame.draw.rect(screen, (50, 50, 50), (text_rect.x-10, text_rect.y-5, text_rect.width+20, text_rect.height+10), 2)
                
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    return False

def handle_level_transition():
    global level, bg_scroll, screen_scroll, world_data, world, player, health_bar, transition_active, transition_fade, level_complete
    
    if not transition_fade:
        # Start fade out
        transition_fade = ScreenFade(2, BLACK, 8)
    else:
        if transition_fade.fade():
            # Fade out complete, load new level
            level += 1
            if level <= MAX_LEVELS:
                try:
                    # Reset game variables
                    bg_scroll = 0
                    screen_scroll = 0
                    world_data = reset_level()
                    
                    # Load new level
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    
                    world = World()
                    player, health_bar = world.process_data(world_data)
                    
                    # Reset enemy and item groups
                    enemy_group.empty()
                    bullet_group.empty()
                    item_box_group.empty()
                    decoration_group.empty()
                    exit_group.empty()
                    
                    # Prepare for fade in
                    transition_fade.reset()
                    transition_fade.fade_counter = SCREEN_HEIGHT
                    transition_fade.fade_complete = False
                    transition_fade.speed = -8
                    
                    level_complete = False
                except FileNotFoundError:
                    print(f"Level {level} file not found!")
                    draw_text('LEVEL LOAD ERROR!', font, RED, SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2-50)
                    pygame.display.update()
                    pygame.time.delay(2000)
                    return False
            else:
                # Game completed - show end screen
                result = end_screen(score)
                if result == "restart":
                    # Reset ke level 1
                    level = 1
                    score = 0
                    bg_scroll = 0
                    screen_scroll = 0
                    world_data = reset_level()
                    try:
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
                        transition_fade = None
                        transition_active = False
                        return True
                    except FileNotFoundError:
                        print("Level 1 file not found!")
                        return False
                return False
        elif transition_fade.speed < 0 and transition_fade.fade_counter <= 0:
            # Fade in complete
            transition_fade = None
            transition_active = False
    
    return True

# Create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# Load level data
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

# Create screen fades
death_fade = ScreenFade(2, PINK, 4)
intro_fade = ScreenFade(1, BLACK, 4)

# Show menu first
start_game = show_main_menu()
start_intro = True

# Main game loop
while start_game:
    clock.tick(FPS)
    
    if start_intro:
        if intro_fade.fade():
            start_intro = False
            intro_fade.fade_counter = 0
    
    if not transition_active:
        draw_bg()
        world.draw()
        world.moving_platforms.update()  # Update moving platforms
        health_bar.draw(player.health)
        
        # Show ammo
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
            
        # Show score
        draw_score()

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        bullet_group.update()
        item_box_group.update()
        decoration_group.update()
        exit_group.update()
        
        bullet_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        exit_group.draw(screen)

        if player.alive:
            if shoot:
                player.shoot()
                
            if player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)
                
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            
            if level_complete:
                transition_active = True
                
        else:
            screen_scroll = 0
            if death_fade.fade():
                pygame.time.delay(500)
                # Show end screen when player dies
                result = end_screen(score)
                if result == "restart":
                    # Reset ke level 1
                    level = 1
                    score = 0
                    bg_scroll = 0
                    screen_scroll = 0
                    world_data = reset_level()
                    try:
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
                        death_fade.fade_counter = 0
                        start_intro = True
                    except FileNotFoundError:
                        print("Level 1 file not found!")
                        start_game = False
                else:
                    start_game = False
    
    # Handle level transition
    if transition_active:
        if not handle_level_transition():
            start_game = False
    
    # Draw transition effect on top of everything
    if transition_fade and not transition_fade.fade_complete:
        transition_fade.fade()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start_game = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if show_main_menu():
                    start_game = True
                    start_intro = True
                else:
                    start_game = False
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
sys.exit()

