# -*- coding: utf-8 -*-

import pygame
import random
import sys
import math
import os
import time

# --- Scaling Factor ---
SCALE_FACTOR = 1.5

# --- Constants ---
SCREEN_WIDTH = int(400 * SCALE_FACTOR)
SCREEN_HEIGHT = int(600 * SCALE_FACTOR)
FPS = 60
HIGH_SCORE_FILE = "highscore.txt"

# --- Color Definitions ---
RED = (220, 50, 50); LIGHT_RED = (255, 100, 100); BLUE = (60, 120, 240); LIGHT_BLUE = (100, 160, 255)
GREEN = (50, 200, 50); LIGHT_GREEN = (150, 240, 150); WHITE = (240, 240, 240); BLACK = (0, 0, 0)
NEON_CYAN = (0, 255, 255); NEON_MAGENTA = (255, 0, 255); NEON_LIME = (50, 255, 50)
DARK_BG_NEON = (5, 0, 15); WALL_BASE_NEON = (20, 20, 20)

# --- Theme Definitions ---
light_theme = { "id": "Light", "background_top": (170, 210, 230), "background_bottom": (130, 180, 210), "wall_color": (210, 200, 190), "wall_detail_color": (180, 170, 160), "text_color": (40, 40, 40), "shadow_color": (235, 235, 235), "overlay_color": (240, 240, 240, 180), "game_over_text_color": (40, 40, 40), "game_over_shadow_color": (200, 200, 200), }
dark_theme = { "id": "Dark", "background_top": (20, 20, 40), "background_bottom": (10, 10, 20), "wall_color": (80, 80, 90), "wall_detail_color": (50, 50, 60), "text_color": WHITE, "shadow_color": (10, 10, 20), "overlay_color": (0, 0, 0, 200), "game_over_text_color": WHITE, "game_over_shadow_color": (50, 50, 50), }
neon_theme = { "id": "Neon", "background_top": BLACK, "background_bottom": DARK_BG_NEON, "wall_color": WALL_BASE_NEON, "wall_detail_color": NEON_CYAN, "text_color": NEON_LIME, "shadow_color": BLACK, "overlay_color": (10, 0, 20, 220), "game_over_text_color": NEON_MAGENTA, "game_over_shadow_color": (40, 0, 40), }

# --- Global Theme Variables ---
BACKGROUND_TOP = None; BACKGROUND_BOTTOM = None; WALL_COLOR = None; WALL_DETAIL_COLOR = None
TEXT_COLOR = None; SHADOW_COLOR = None; OVERLAY_COLOR = None
GAME_OVER_TEXT_COLOR = None; GAME_OVER_SHADOW_COLOR = None

# --- Player/Obstacle/Collectible Colors ---
PLAYER_SIZE = int(30 * SCALE_FACTOR); PLAYER_BORDER_WIDTH = int(2 * SCALE_FACTOR)
PLAYER_ROUNDING = int(5 * SCALE_FACTOR); WALL_PADDING = int(15 * SCALE_FACTOR)
PLAYER_Y_POSITION = SCREEN_HEIGHT * 0.8; PLAYER_HORIZONTAL_SPEED = int(18 * SCALE_FACTOR)
SQUASH_STRETCH_DURATION = 0.15; SQUASH_AMOUNT = 0.8; STRETCH_AMOUNT = 1.2
PLAYER_BOB_FREQUENCY = 2.5; PLAYER_BOB_AMPLITUDE = int(2 * SCALE_FACTOR)
PLAYER_COLOR = BLUE; PLAYER_BORDER_COLOR = LIGHT_BLUE

OBSTACLE_MIN_WIDTH = int(30 * SCALE_FACTOR); OBSTACLE_MAX_WIDTH = int(90 * SCALE_FACTOR)
OBSTACLE_MIN_HEIGHT = int(15 * SCALE_FACTOR); OBSTACLE_MAX_HEIGHT = int(35 * SCALE_FACTOR)
OBSTACLE_BORDER_WIDTH = int(2 * SCALE_FACTOR); OBSTACLE_ROUNDING = int(3 * SCALE_FACTOR)
OBSTACLE_COLOR = RED; OBSTACLE_BORDER_COLOR = LIGHT_RED
OBSTACLE_SPEED_START = 4.5 * SCALE_FACTOR; OBSTACLE_SPEED_INCREASE = 0.08 * SCALE_FACTOR
MAX_OBSTACLE_SPEED = 15 * SCALE_FACTOR; OBSTACLE_SPAWN_RATE = 900
OBSTACLE_SPAWN_RATE_DECREASE = 8; MIN_SPAWN_RATE = 280
OBSTACLE_COLOR_VARIATION = 25; BOTH_WALL_SPAWN_CHANCE = 0.55
MIN_OBSTACLE_VERTICAL_GAP = PLAYER_SIZE * 2.2

COLLECTIBLE_SIZE = int(18 * SCALE_FACTOR); COLLECTIBLE_COLOR = GREEN
COLLECTIBLE_BORDER_COLOR = LIGHT_GREEN; COLLECTIBLE_BORDER_WIDTH = int(2 * SCALE_FACTOR)
COLLECTIBLE_ROUNDING = COLLECTIBLE_SIZE // 2; COLLECTIBLE_POINTS = 500
COLLECTIBLE_SPAWN_RATE = 4000; COLLECTIBLE_SPAWN_CHANCE = 0.7
MIN_COLLECTIBLE_SPAWN_RATE = 2000; COLLECTIBLE_SPAWN_RATE_DECREASE = 20

# Particle Settings
PARTICLE_LIFESPAN = 0.5; PARTICLE_SPEED = int(2 * SCALE_FACTOR)
PARTICLE_SIZE = int(3 * SCALE_FACTOR); PARTICLE_SPAWN_RATE_MOVE = 2
PARTICLE_BLUE = NEON_CYAN
PARTICLE_GREEN = NEON_LIME

# Font settings (Using Pygame default font)
# FONT_NAME = 'Gameplay.ttf' # REMOVED
# FONT_PATH = os.path.join('assets', FONT_NAME) # REMOVED
TITLE_FONT_SIZE = int(60 * SCALE_FACTOR); SCORE_FONT_SIZE = int(28 * SCALE_FACTOR)
GAME_OVER_FONT_SIZE = int(55 * SCALE_FACTOR); RESTART_FONT_SIZE = int(26 * SCALE_FACTOR)
INFO_FONT_SIZE = int(22 * SCALE_FACTOR)
MENU_FONT_SIZE = int(20 * SCALE_FACTOR)

# Screen Shake Settings
SHAKE_DURATION = 0.25; SHAKE_INTENSITY = int(5 * SCALE_FACTOR)

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wall Climber Ascent")
clock = pygame.time.Clock()

# --- Load Default Fonts ---
# Use None as the first argument to get the default font
try:
    title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
    font = pygame.font.Font(None, SCORE_FONT_SIZE)
    game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
    restart_font = pygame.font.Font(None, RESTART_FONT_SIZE)
    info_font = pygame.font.Font(None, INFO_FONT_SIZE)
    menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    print("Using Pygame default font.")
except Exception as e:
    print(f"Error loading default font: {e}")
    # Fallback in case even default font fails (highly unlikely)
    # Provide some basic sizes even for the complete fallback
    title_font = pygame.font.Font(None, 60); font = pygame.font.Font(None, 30)
    game_over_font = pygame.font.Font(None, 50); restart_font = pygame.font.Font(None, 25)
    info_font = pygame.font.Font(None, 20); menu_font = pygame.font.Font(None, 18)

# --- High Score Handling (Same) ---
def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f: return int(f.read())
    except (FileNotFoundError, ValueError): return 0
def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f: f.write(str(score))
    except IOError as e: print(f"Error saving high score: {e}")

# --- Theme Handling (Same apply function) ---
def apply_theme(theme_dict):
    global BACKGROUND_TOP, BACKGROUND_BOTTOM, WALL_COLOR, WALL_DETAIL_COLOR
    global TEXT_COLOR, SHADOW_COLOR, OVERLAY_COLOR, GAME_OVER_TEXT_COLOR, GAME_OVER_SHADOW_COLOR
    BACKGROUND_TOP = theme_dict["background_top"]; BACKGROUND_BOTTOM = theme_dict["background_bottom"]
    WALL_COLOR = theme_dict["wall_color"]; WALL_DETAIL_COLOR = theme_dict["wall_detail_color"]
    TEXT_COLOR = theme_dict["text_color"]; SHADOW_COLOR = theme_dict["shadow_color"]
    OVERLAY_COLOR = theme_dict["overlay_color"]; GAME_OVER_TEXT_COLOR = theme_dict["game_over_text_color"]
    GAME_OVER_SHADOW_COLOR = theme_dict["game_over_shadow_color"]
    pygame.display.set_caption(f"Wall Climber ({theme_dict['id']})")

# --- Particle Class (Same) ---
class Particle:
    def __init__(self, x, y, vx, vy, size, color, lifespan):
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.size = size; self.color = color; self.lifespan = lifespan; self.birth_time = time.time()
    def update(self, dt):
        self.x += self.vx * dt * FPS; self.y += self.vy * dt * FPS
        self.size = max(0, self.size - (self.size / (self.lifespan * FPS)) * dt * FPS)
        return time.time() - self.birth_time < self.lifespan
    def draw(self, surface, offset=(0,0)):
        if self.size > 0: pygame.draw.circle(surface, self.color, (int(self.x + offset[0]), int(self.y + offset[1])), int(self.size))

# --- Game State Variables ---
game_state = 'start'; high_score = load_high_score(); current_theme = light_theme; apply_theme(current_theme)
particles = []; player_rect = None; player_on_wall = 'left'; player_target_x = 0; player_is_moving = False
obstacles = []; score = 0; game_over = False; obstacle_speed = OBSTACLE_SPEED_START; last_obstacle_spawn_time = 0
current_spawn_rate = OBSTACLE_SPAWN_RATE; collectibles = []; last_collectible_spawn_time = 0
current_collectible_spawn_rate = COLLECTIBLE_SPAWN_RATE; player_squash_timer = 0.0; player_stretch_timer = 0.0
move_frame_counter = 0; shake_timer = 0.0; score_flash_timer = 0.0

# --- Reset Function (Same) ---
def start_new_game():
    global player_rect, player_on_wall, player_target_x, player_is_moving, obstacles, score, game_over
    global obstacle_speed, last_obstacle_spawn_time, current_spawn_rate, particles, player_squash_timer
    global player_stretch_timer, move_frame_counter, collectibles, last_collectible_spawn_time
    global current_collectible_spawn_rate, shake_timer, score_flash_timer, game_state
    player_on_wall = 'left'; player_x = WALL_PADDING; player_rect = pygame.Rect(player_x, PLAYER_Y_POSITION, PLAYER_SIZE, PLAYER_SIZE)
    player_target_x = player_x; player_is_moving = False; player_squash_timer = 0.0; player_stretch_timer = 0.0; move_frame_counter = 0
    obstacles = []; obstacle_speed = OBSTACLE_SPEED_START; last_obstacle_spawn_time = pygame.time.get_ticks(); current_spawn_rate = OBSTACLE_SPAWN_RATE
    collectibles = []; last_collectible_spawn_time = pygame.time.get_ticks(); current_collectible_spawn_rate = COLLECTIBLE_SPAWN_RATE
    score = 0; game_over = False; particles = []; shake_timer = 0.0; score_flash_timer = 0.0; game_state = 'playing'

# --- Game Functions (spawn_obstacle, etc. same logic) ---
def spawn_obstacle():
    global obstacle_speed, current_spawn_rate # (Logic unchanged)
    first_wall = random.choice(['left', 'right']); obs1_width = random.randint(OBSTACLE_MIN_WIDTH, OBSTACLE_MAX_WIDTH); obs1_height = random.randint(OBSTACLE_MIN_HEIGHT, OBSTACLE_MAX_HEIGHT); obs1_y = -OBSTACLE_MAX_HEIGHT - random.randint(0, OBSTACLE_MAX_HEIGHT // 2); obs1_x = WALL_PADDING if first_wall == 'left' else SCREEN_WIDTH - WALL_PADDING - obs1_width; obs1_rect = pygame.Rect(obs1_x, obs1_y, obs1_width, obs1_height); r1 = max(0, min(255, OBSTACLE_COLOR[0] + random.randint(-OBSTACLE_COLOR_VARIATION, OBSTACLE_COLOR_VARIATION))); g1 = max(0, min(255, OBSTACLE_COLOR[1] + random.randint(-OBSTACLE_COLOR_VARIATION, OBSTACLE_COLOR_VARIATION))); b1 = max(0, min(255, OBSTACLE_COLOR[2] + random.randint(-OBSTACLE_COLOR_VARIATION, OBSTACLE_COLOR_VARIATION))); obs1_color = (r1, g1, b1); obs1_border = (min(255,r1+50), min(255,g1+50), min(255,b1+50)); obstacles.append((obs1_rect, obs1_color, obs1_border))
    if random.random() < BOTH_WALL_SPAWN_CHANCE: second_wall = 'right' if first_wall == 'left' else 'left'; obs2_width = random.randint(OBSTACLE_MIN_WIDTH, OBSTACLE_MAX_WIDTH); obs2_height = random.randint(OBSTACLE_MIN_HEIGHT, OBSTACLE_MAX_HEIGHT); obs1_top_edge = obs1_rect.y; obs1_bottom_edge = obs1_rect.y + obs1_rect.height; safe_y_top_edge_above = obs1_top_edge - obs2_height - MIN_OBSTACLE_VERTICAL_GAP; safe_y_top_edge_below = obs1_bottom_edge + MIN_OBSTACLE_VERTICAL_GAP; obs2_y = safe_y_top_edge_above - random.randint(0, int(OBSTACLE_MAX_HEIGHT * 1.5 * SCALE_FACTOR)) if random.choice([True, False]) else safe_y_top_edge_below + random.randint(0, int(OBSTACLE_MAX_HEIGHT * SCALE_FACTOR)); obs2_x = WALL_PADDING if second_wall == 'left' else SCREEN_WIDTH - WALL_PADDING - obs2_width; obs2_rect = pygame.Rect(obs2_x, obs2_y, obs2_width, obs2_height); r2 = max(0, min(255, OBSTACLE_COLOR[0] + random.randint(-OBSTACLE_COLOR_VARIATION, OBSTACLE_COLOR_VARIATION))); g2 = max(0, min(255, OBSTACLE_COLOR[1] + random.randint(-OBSTACLE_COLOR_VARIATION, OBSTACLE_COLOR_VARIATION))); b2 = max(0, min(255, OBSTACLE_COLOR[2] + random.randint(-OBSTACLE_COLOR_VARIATION, OBSTACLE_COLOR_VARIATION))); obs2_color = (r2, g2, b2); obs2_border = (min(255,r2+50), min(255,g2+50), min(255,b2+50)); obstacles.append((obs2_rect, obs2_color, obs2_border))
    obstacle_speed = min(MAX_OBSTACLE_SPEED, obstacle_speed + OBSTACLE_SPEED_INCREASE); current_spawn_rate = max(MIN_SPAWN_RATE, current_spawn_rate - OBSTACLE_SPAWN_RATE_DECREASE)
def spawn_collectible():
    global current_collectible_spawn_rate # (Logic unchanged)
    collectible_y = -COLLECTIBLE_SIZE; min_x = WALL_PADDING + OBSTACLE_MAX_WIDTH + int(10 * SCALE_FACTOR); max_x = SCREEN_WIDTH - WALL_PADDING - OBSTACLE_MAX_WIDTH - COLLECTIBLE_SIZE - int(10 * SCALE_FACTOR)
    collectible_x = SCREEN_WIDTH // 2 - COLLECTIBLE_SIZE // 2 if min_x >= max_x else random.randint(min_x, max_x); collectible_rect = pygame.Rect(collectible_x, collectible_y, COLLECTIBLE_SIZE, COLLECTIBLE_SIZE); collectibles.append(collectible_rect); current_collectible_spawn_rate = max(MIN_COLLECTIBLE_SPAWN_RATE, current_collectible_spawn_rate - COLLECTIBLE_SPAWN_RATE_DECREASE)
def spawn_effect_particles(center_x, center_y, count, color, speed_multi=1.0):
    # (Logic unchanged)
    for _ in range(count): angle = random.uniform(0, 2 * math.pi); speed = random.uniform(PARTICLE_SPEED * 0.5, PARTICLE_SPEED * 1.5) * speed_multi; vel_x = math.cos(angle) * speed; vel_y = math.sin(angle) * speed; size = random.uniform(PARTICLE_SIZE * 0.8, PARTICLE_SIZE * 1.5); lifespan = random.uniform(PARTICLE_LIFESPAN * 0.5, PARTICLE_LIFESPAN); particles.append(Particle(center_x, center_y, vel_x, vel_y, size, color, lifespan))
def draw_text(text, font_to_use, color, surface, x, y, center=False, shadow=True, shadow_color=None, shadow_offset_base=(1,1), screen_offset=(0,0)):
    # (Logic unchanged)
    if shadow_color is None: shadow_color = SHADOW_COLOR
    shadow_offset = (int(shadow_offset_base[0] * SCALE_FACTOR), int(shadow_offset_base[1] * SCALE_FACTOR))
    x += screen_offset[0]; y += screen_offset[1]; textobj = font_to_use.render(text, True, color); textrect = textobj.get_rect()
    if center: textrect.center = (x, y)
    else: textrect.topleft = (x, y)
    if shadow: actual_shadow_color = shadow_color if shadow_color != color else (color[0]//2, color[1]//2, color[2]//2); shadow_obj = font_to_use.render(text, True, actual_shadow_color); shadow_rect = shadow_obj.get_rect()
    if center: shadow_rect.center = (x + shadow_offset[0], y + shadow_offset[1])
    else: shadow_rect.topleft = (x + shadow_offset[0], y + shadow_offset[1])
    surface.blit(shadow_obj, shadow_rect)
    surface.blit(textobj, textrect)
def draw_gradient_background(surface, top_color=None, bottom_color=None):
    # (Logic unchanged)
    if top_color is None: top_color = BACKGROUND_TOP
    if bottom_color is None: bottom_color = BACKGROUND_BOTTOM
    height = surface.get_height(); rect = pygame.Rect(0, 0, surface.get_width(), 1)
    for y in range(height): ratio = y / height; r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio); g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio); b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio); rect.top = y; pygame.draw.rect(surface, (r, g, b), rect)

# --- Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    now = pygame.time.get_ticks()
    current_time = time.time()

    # --- Shared Updates ---
    screen_offset = (0, 0)
    if shake_timer > 0: shake_timer -= dt; screen_offset = (int(random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY)), int(random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY))); shake_timer = max(0, shake_timer)
    if score_flash_timer > 0: score_flash_timer -= dt; score_flash_timer = max(0, score_flash_timer)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if game_state == 'start':
                if event.key == pygame.K_SPACE: start_new_game()
                if event.key == pygame.K_t: # Theme Cycling
                    if current_theme['id'] == 'Light': current_theme = dark_theme
                    elif current_theme['id'] == 'Dark': current_theme = neon_theme
                    else: current_theme = light_theme # Neon goes back to Light
                    apply_theme(current_theme)
            elif game_state == 'playing':
                if event.key == pygame.K_SPACE:
                    if not player_is_moving: player_is_moving = True; player_squash_timer = SQUASH_STRETCH_DURATION; player_stretch_timer = 0.0; player_target_x = SCREEN_WIDTH - WALL_PADDING - PLAYER_SIZE if player_on_wall == 'left' else WALL_PADDING; player_on_wall = 'right' if player_on_wall == 'left' else 'left'
            elif game_state == 'game_over':
                if event.key == pygame.K_SPACE: start_new_game()
                if event.key == pygame.K_m: game_state = 'start'

    # --- Game Logic & Drawing by State ---
    if game_state == 'start':
        # --- Start Screen Drawing ---
        draw_gradient_background(screen)
        draw_text("Wall Climber", title_font, TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2, center=True)
        draw_text("Press SPACE to Start", restart_font, TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.5, center=True)
        draw_text(f"Press T for Theme: {current_theme['id']}", info_font, TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.6, center=True)
        draw_text(f"High Score: {high_score}", font, TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.75, center=True)


    elif game_state == 'playing':

        # --- Playing Logic ---

        game_over_internal = False  # Use a local flag for this frame's collision check

        # Calculate Player Visual Rect for Collision

        current_player_width = PLAYER_SIZE;
        current_player_height = PLAYER_SIZE

        player_center = player_rect.center

        if player_squash_timer > 0:

            scale = 1.0 - ((SQUASH_STRETCH_DURATION - player_squash_timer) / SQUASH_STRETCH_DURATION)

            current_player_height = PLAYER_SIZE * (1.0 - (1.0 - SQUASH_AMOUNT) * math.sin(scale * math.pi));
            current_player_width = PLAYER_SIZE * (1.0 + (STRETCH_AMOUNT - 1.0) * math.sin(scale * math.pi))

        elif player_stretch_timer > 0:

            scale = 1.0 - ((SQUASH_STRETCH_DURATION - player_stretch_timer) / SQUASH_STRETCH_DURATION)

            current_player_height = PLAYER_SIZE * (1.0 + (STRETCH_AMOUNT - 1.0) * math.sin(scale * math.pi));
            current_player_width = PLAYER_SIZE * (1.0 - (1.0 - SQUASH_AMOUNT) * math.sin(scale * math.pi))

        collision_rect = pygame.Rect(0, 0, current_player_width, current_player_height);
        collision_rect.center = player_center

        # Player Movement & Collectible Collision

        if player_is_moving:

            move_frame_counter += 1;
            move_direction = 0

            move_amount = PLAYER_HORIZONTAL_SPEED * dt * FPS  # Calculate potential move amount once

            if player_rect.x < player_target_x:

                move_direction = 1

                actual_move = min(move_amount, player_target_x - player_rect.x)  # Prevent overshooting

                player_rect.x += actual_move

            elif player_rect.x > player_target_x:

                move_direction = -1

                actual_move = min(move_amount, player_rect.x - player_target_x)  # Prevent overshooting

                player_rect.x -= actual_move

            # Snap to target if very close (optional refinement)

            if abs(player_rect.x - player_target_x) < move_amount * 0.5:  # Use move_amount for comparison

                player_rect.x = player_target_x

            # Spawn trail particles

            if move_frame_counter % PARTICLE_SPAWN_RATE_MOVE == 0:
                spawn_effect_particles(collision_rect.centerx, collision_rect.centery, 1, PARTICLE_BLUE, 0.5)

            # --- Collectible Collision Check ---

            for i in range(len(collectibles) - 1, -1, -1):

                collectible_rect = collectibles[i]  # Define rect for this iteration

                # Check collision with the CURRENT collectible_rect

                if collision_rect.colliderect(collectible_rect):
                    score += COLLECTIBLE_POINTS

                    score_flash_timer = 0.2

                    spawn_effect_particles(collectible_rect.centerx, collectible_rect.centery, 15, PARTICLE_GREEN, 1.2)

                    collectibles.pop(i)  # Remove the collected item

                    break  # Exit the collectible loop for this frame

            # Check if movement is complete

            if player_rect.x == player_target_x:
                player_is_moving = False

                move_frame_counter = 0

                player_stretch_timer = SQUASH_STRETCH_DURATION

                player_squash_timer = 0.0

        # Update Squash/Stretch Timers

        player_squash_timer = max(0.0, player_squash_timer - dt)

        player_stretch_timer = max(0.0, player_stretch_timer - dt)

        # Obstacle Spawning & Movement

        if now - last_obstacle_spawn_time > current_spawn_rate:
            spawn_obstacle()

            last_obstacle_spawn_time = now

        current_obstacle_speed = obstacle_speed * dt * FPS

        for i in range(len(obstacles) - 1, -1, -1):

            obstacle_rect, obs_color, border_color = obstacles[i]

            obstacle_rect.y += current_obstacle_speed

            if obstacle_rect.top > SCREEN_HEIGHT:

                obstacles.pop(i)

            else:

                obstacles[i] = (obstacle_rect, obs_color, border_color)

        # Collectible Spawning & Movement

        if now - last_collectible_spawn_time > current_collectible_spawn_rate:

            if random.random() < COLLECTIBLE_SPAWN_CHANCE:
                spawn_collectible()

            last_collectible_spawn_time = now

        collectible_speed_factor = 0.9

        current_collectible_speed = obstacle_speed * collectible_speed_factor * dt * FPS

        # ===== Crucial Indentation Area for Collectibles ======

        for i in range(len(collectibles) - 1, -1, -1):  # Level 2 Indent

            # Level 3 Indent: Assign the variable INSIDE the loop

            collectible_rect_move = collectibles[i]

            # Level 3 Indent: Now use the assigned variable

            collectible_rect_move.y += current_collectible_speed

            if collectible_rect_move.top > SCREEN_HEIGHT:
                collectibles.pop(i)

        # ===== End Crucial Indentation Area =====

        # Obstacle Collision Detection

        for obstacle_data in obstacles:

            obstacle_rect_collision, _, _ = obstacle_data

            if collision_rect.colliderect(obstacle_rect_collision):
                game_over_internal = True

                shake_timer = SHAKE_DURATION

                spawn_effect_particles(collision_rect.centerx, collision_rect.centery, 25, LIGHT_RED, 1.5)

                break  # Exit obstacle collision loop

        # Update Score (Time-based)

        score += 1

        # Update Particles

        particles = [p for p in particles if p.update(dt)]

        # --- Playing Drawing ---

        draw_gradient_background(screen)

        wall_thickness = WALL_PADDING;
        pygame.draw.rect(screen, WALL_COLOR, (screen_offset[0], screen_offset[1], wall_thickness, SCREEN_HEIGHT));
        pygame.draw.rect(screen, WALL_COLOR, (
        SCREEN_WIDTH - wall_thickness + screen_offset[0], screen_offset[1], wall_thickness, SCREEN_HEIGHT))

        if current_theme['id'] == 'Neon':  # Neon wall details

            line_thickness = int(1 * SCALE_FACTOR);
            pygame.draw.line(screen, WALL_DETAIL_COLOR, (screen_offset[0], screen_offset[1]),
                             (wall_thickness - 1 + screen_offset[0], screen_offset[1]), line_thickness);
            pygame.draw.line(screen, WALL_DETAIL_COLOR, (screen_offset[0], SCREEN_HEIGHT + screen_offset[1]),
                             (wall_thickness - 1 + screen_offset[0], SCREEN_HEIGHT + screen_offset[1]), line_thickness);
            pygame.draw.line(screen, WALL_DETAIL_COLOR, (screen_offset[0], screen_offset[1]),
                             (screen_offset[0], SCREEN_HEIGHT + screen_offset[1]), line_thickness);
            pygame.draw.line(screen, WALL_DETAIL_COLOR,
                             (wall_thickness - line_thickness + screen_offset[0], screen_offset[1]),
                             (wall_thickness - line_thickness + screen_offset[0], SCREEN_HEIGHT + screen_offset[1]),
                             line_thickness);
            pygame.draw.line(screen, WALL_DETAIL_COLOR,
                             (SCREEN_WIDTH - wall_thickness + 1 + screen_offset[0], screen_offset[1]),
                             (SCREEN_WIDTH + screen_offset[0], screen_offset[1]), line_thickness);
            pygame.draw.line(screen, WALL_DETAIL_COLOR,
                             (SCREEN_WIDTH - wall_thickness + 1 + screen_offset[0], SCREEN_HEIGHT + screen_offset[1]),
                             (SCREEN_WIDTH + screen_offset[0], SCREEN_HEIGHT + screen_offset[1]), line_thickness);
            pygame.draw.line(screen, WALL_DETAIL_COLOR,
                             (SCREEN_WIDTH - wall_thickness + screen_offset[0], screen_offset[1]),
                             (SCREEN_WIDTH - wall_thickness + screen_offset[0], SCREEN_HEIGHT + screen_offset[1]),
                             line_thickness);
            pygame.draw.line(screen, WALL_DETAIL_COLOR,
                             (SCREEN_WIDTH - line_thickness + screen_offset[0], screen_offset[1]),
                             (SCREEN_WIDTH - line_thickness + screen_offset[0], SCREEN_HEIGHT + screen_offset[1]),
                             line_thickness)

        else:  # Original texture for light/dark

            for y_base in range(0, SCREEN_HEIGHT, int(10 * SCALE_FACTOR)): y = y_base + screen_offset[
                1]; noise_l = random.randint(-8, 8); noise_r = random.randint(-8, 8); noisy_detail_color_l = (
            max(0, min(255, WALL_DETAIL_COLOR[0] + noise_l)), max(0, min(255, WALL_DETAIL_COLOR[1] + noise_l)),
            max(0, min(255, WALL_DETAIL_COLOR[2] + noise_l))); noisy_detail_color_r = (
            max(0, min(255, WALL_DETAIL_COLOR[0] + noise_r)), max(0, min(255, WALL_DETAIL_COLOR[1] + noise_r)),
            max(0, min(255, WALL_DETAIL_COLOR[2] + noise_r))); pygame.draw.line(screen, noisy_detail_color_l,
                                                                                (screen_offset[0], y), (
                                                                                wall_thickness - 1 + screen_offset[0],
                                                                                y), 1); pygame.draw.line(screen,
                                                                                                         noisy_detail_color_r,
                                                                                                         (
                                                                                                         SCREEN_WIDTH - wall_thickness + 1 +
                                                                                                         screen_offset[
                                                                                                             0], y), (
                                                                                                         SCREEN_WIDTH +
                                                                                                         screen_offset[
                                                                                                             0], y), 1)

            inner_edge_thickness = int(3 * SCALE_FACTOR);
            pygame.draw.rect(screen, WALL_DETAIL_COLOR, (
            wall_thickness - inner_edge_thickness + screen_offset[0], screen_offset[1], inner_edge_thickness,
            SCREEN_HEIGHT));
            pygame.draw.rect(screen, WALL_DETAIL_COLOR, (
            SCREEN_WIDTH - wall_thickness + screen_offset[0], screen_offset[1], inner_edge_thickness, SCREEN_HEIGHT))

        for particle in particles: particle.draw(screen, screen_offset)

        for obstacle_rect_draw, obs_color, border_color in obstacles: obs_draw_rect = obstacle_rect_draw.move(
            screen_offset); current_obs_rounding = min(OBSTACLE_ROUNDING, obs_draw_rect.width // 2,
                                                       obs_draw_rect.height // 2); border_rect = obs_draw_rect.inflate(
            OBSTACLE_BORDER_WIDTH * 2, OBSTACLE_BORDER_WIDTH * 2); pygame.draw.rect(screen, border_color, border_rect,
                                                                                    border_radius=current_obs_rounding + 1); pygame.draw.rect(
            screen, obs_color, obs_draw_rect, border_radius=current_obs_rounding)

        for collectible_rect_draw in collectibles: coll_draw_rect = collectible_rect_draw.move(
            screen_offset); border_rect = coll_draw_rect.inflate(COLLECTIBLE_BORDER_WIDTH * 2,
                                                                 COLLECTIBLE_BORDER_WIDTH * 2); pygame.draw.rect(screen,
                                                                                                                 COLLECTIBLE_BORDER_COLOR,
                                                                                                                 border_rect,
                                                                                                                 border_radius=COLLECTIBLE_ROUNDING + 1); pygame.draw.rect(
            screen, COLLECTIBLE_COLOR, coll_draw_rect, border_radius=COLLECTIBLE_ROUNDING)

        bob_offset = 0;

        if not player_is_moving: bob_offset = math.sin(current_time * PLAYER_BOB_FREQUENCY) * PLAYER_BOB_AMPLITUDE

        visual_player_rect = pygame.Rect(0, 0, int(collision_rect.width), int(collision_rect.height));
        visual_player_rect.center = (
        collision_rect.centerx + screen_offset[0], collision_rect.centery + bob_offset + screen_offset[1]);
        current_rounding = int(
            PLAYER_ROUNDING * min(visual_player_rect.width / PLAYER_SIZE, visual_player_rect.height / PLAYER_SIZE));
        player_border_rect = visual_player_rect.inflate(PLAYER_BORDER_WIDTH * 2, PLAYER_BORDER_WIDTH * 2);
        pygame.draw.rect(screen, PLAYER_BORDER_COLOR, player_border_rect, border_radius=current_rounding + 1);
        pygame.draw.rect(screen, PLAYER_COLOR, visual_player_rect, border_radius=current_rounding)

        score_color = LIGHT_GREEN if score_flash_timer > 0 else TEXT_COLOR;
        draw_text(f"Score: {score}", font, score_color, screen, SCREEN_WIDTH // 2, int(20 * SCALE_FACTOR), center=True,
                  shadow=True, screen_offset=screen_offset)

        # --- Transition to Game Over ---

        if game_over_internal:

            if score > high_score:
                high_score = score

                save_high_score(high_score)

            game_state = 'game_over'  # Change state

    elif game_state == 'game_over':
        # --- Game Over Drawing (Static background, shaking text) ---
        draw_gradient_background(screen)
        wall_thickness = WALL_PADDING; pygame.draw.rect(screen, WALL_COLOR, (0, 0, wall_thickness, SCREEN_HEIGHT)); pygame.draw.rect(screen, WALL_COLOR, (SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT))
        if current_theme['id'] == 'Neon': line_thickness = int(1 * SCALE_FACTOR); pygame.draw.line(screen, WALL_DETAIL_COLOR, (0, 0), (wall_thickness -1 , 0), line_thickness); pygame.draw.line(screen, WALL_DETAIL_COLOR, (0, SCREEN_HEIGHT), (wall_thickness -1, SCREEN_HEIGHT), line_thickness); pygame.draw.line(screen, WALL_DETAIL_COLOR, (0, 0), (0, SCREEN_HEIGHT), line_thickness); pygame.draw.line(screen, WALL_DETAIL_COLOR, (wall_thickness - line_thickness, 0), (wall_thickness - line_thickness, SCREEN_HEIGHT), line_thickness); pygame.draw.line(screen, WALL_DETAIL_COLOR, (SCREEN_WIDTH - wall_thickness + 1, 0), (SCREEN_WIDTH, 0), line_thickness); pygame.draw.line(screen, WALL_DETAIL_COLOR, (SCREEN_WIDTH - wall_thickness + 1, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), line_thickness); pygame.draw.line(screen, WALL_DETAIL_COLOR, (SCREEN_WIDTH - wall_thickness, 0), (SCREEN_WIDTH - wall_thickness, SCREEN_HEIGHT), line_thickness); pygame.draw.line(screen, WALL_DETAIL_COLOR, (SCREEN_WIDTH - line_thickness, 0), (SCREEN_WIDTH - line_thickness, SCREEN_HEIGHT), line_thickness)
        else:
             for y_base in range(0, SCREEN_HEIGHT, int(10 * SCALE_FACTOR)): y = y_base; noise_l = random.randint(-8, 8); noise_r = random.randint(-8, 8); noisy_detail_color_l = (max(0, min(255, WALL_DETAIL_COLOR[0]+noise_l)), max(0, min(255,WALL_DETAIL_COLOR[1]+noise_l)), max(0, min(255,WALL_DETAIL_COLOR[2]+noise_l))); noisy_detail_color_r = (max(0, min(255,WALL_DETAIL_COLOR[0]+noise_r)), max(0, min(255,WALL_DETAIL_COLOR[1]+noise_r)), max(0, min(255,WALL_DETAIL_COLOR[2]+noise_r))); pygame.draw.line(screen, noisy_detail_color_l, (0, y), (wall_thickness -1 , y), 1); pygame.draw.line(screen, noisy_detail_color_r, (SCREEN_WIDTH - wall_thickness + 1, y), (SCREEN_WIDTH, y), 1)
             inner_edge_thickness = int(3 * SCALE_FACTOR); pygame.draw.rect(screen, WALL_DETAIL_COLOR, (wall_thickness - inner_edge_thickness, 0, inner_edge_thickness, SCREEN_HEIGHT)); pygame.draw.rect(screen, WALL_DETAIL_COLOR, (SCREEN_WIDTH - wall_thickness, 0, inner_edge_thickness, SCREEN_HEIGHT))
        for particle in particles: particle.draw(screen)
        for obstacle_rect, obs_color, border_color in obstacles: current_obs_rounding = min(OBSTACLE_ROUNDING, obstacle_rect.width // 2, obstacle_rect.height // 2); border_rect = obstacle_rect.inflate(OBSTACLE_BORDER_WIDTH * 2, OBSTACLE_BORDER_WIDTH * 2); pygame.draw.rect(screen, border_color, border_rect, border_radius=current_obs_rounding + 1); pygame.draw.rect(screen, obs_color, obstacle_rect, border_radius=current_obs_rounding)
        for collectible_rect in collectibles: border_rect = collectible_rect.inflate(COLLECTIBLE_BORDER_WIDTH * 2, COLLECTIBLE_BORDER_WIDTH * 2); pygame.draw.rect(screen, COLLECTIBLE_BORDER_COLOR, border_rect, border_radius=COLLECTIBLE_ROUNDING + 1); pygame.draw.rect(screen, COLLECTIBLE_COLOR, collectible_rect, border_radius=COLLECTIBLE_ROUNDING)
        visual_player_rect = pygame.Rect(0, 0, int(PLAYER_SIZE), int(PLAYER_SIZE)); visual_player_rect.center = player_rect.center; current_rounding = PLAYER_ROUNDING; player_border_rect = visual_player_rect.inflate(PLAYER_BORDER_WIDTH * 2, PLAYER_BORDER_WIDTH * 2); pygame.draw.rect(screen, PLAYER_BORDER_COLOR, player_border_rect, border_radius=current_rounding + 1); pygame.draw.rect(screen, PLAYER_COLOR, visual_player_rect, border_radius=current_rounding)

        # --- Draw overlay and Game Over text (Added Menu Text) ---
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill(OVERLAY_COLOR); screen.blit(overlay, (0, 0))
        text_y_spacing = SCREEN_HEIGHT * 0.1 # Adjust spacing as needed
        draw_text("GAME OVER", game_over_font, GAME_OVER_TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.3, center=True, shadow=True, shadow_color=GAME_OVER_SHADOW_COLOR, screen_offset=screen_offset)
        draw_text("Press SPACE to Restart", restart_font, GAME_OVER_TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.5, center=True, shadow=True, shadow_color=GAME_OVER_SHADOW_COLOR, screen_offset=screen_offset)
        draw_text(f"Final Score: {score}", font, GAME_OVER_TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.6, center=True, shadow=True, shadow_color=GAME_OVER_SHADOW_COLOR, screen_offset=screen_offset)
        draw_text(f"High Score: {high_score}", font, GAME_OVER_TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.7, center=True, shadow=True, shadow_color=GAME_OVER_SHADOW_COLOR, screen_offset=screen_offset)
        draw_text("Press M for Menu", menu_font, GAME_OVER_TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.85, center=True, shadow=True, shadow_color=GAME_OVER_SHADOW_COLOR, screen_offset=screen_offset)


    # --- Update Display ---
    pygame.display.flip()

# --- Quit Pygame ---
pygame.quit()
sys.exit()