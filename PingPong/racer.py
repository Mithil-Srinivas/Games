import pygame
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the sound mixer

# Game settings
WIDTH, HEIGHT = 800, 600  # Window dimensions
FPS = 60  # Frames per second
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PLAYER_SPEED = 7
AI_SPEED = 5  # Adjust this to make the AI easier/harder

# Ball settings
BALL_SIZE = 15
INITIAL_BALL_SPEED = 5

# Load sound effects
paddle_hit_sound = pygame.mixer.Sound("paddle_hit.wav")  # You'll need to create/download this sound file

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong: Player vs. AI")
clock = pygame.time.Clock()

# Initialize positions for player paddle, AI paddle, and ball.
player_x = 20
player_y = HEIGHT // 2 - PADDLE_HEIGHT // 2

ai_x = WIDTH - 20 - PADDLE_WIDTH
ai_y = HEIGHT // 2 - PADDLE_HEIGHT // 2

# Use floating point for more precise ball position
ball_x = float(WIDTH // 2 - BALL_SIZE // 2)
ball_y = float(HEIGHT // 2 - BALL_SIZE // 2)
ball_vel_x = INITIAL_BALL_SPEED
ball_vel_y = INITIAL_BALL_SPEED

# Scores
score_player = 0
score_ai = 0
font = pygame.font.SysFont("Arial", 30)

# Main game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Player paddle movement: controlled by UP and DOWN arrow keys.
    keys = pygame.key.get_pressed()
    if keys[K_UP]:
        player_y -= PLAYER_SPEED
        if player_y < 0:
            player_y = 0
    if keys[K_DOWN]:
        player_y += PLAYER_SPEED
        if player_y > HEIGHT - PADDLE_HEIGHT:
            player_y = HEIGHT - PADDLE_HEIGHT

    # AI paddle movement: simple AI that follows the ball's vertical position.
    # If the AI paddle's center is below the ball, move up; if above, move down.
    if (ai_y + PADDLE_HEIGHT / 2) < (ball_y + BALL_SIZE / 2):
        ai_y += AI_SPEED
    elif (ai_y + PADDLE_HEIGHT / 2) > (ball_y + BALL_SIZE / 2):
        ai_y -= AI_SPEED

    # Ensure the AI paddle stays within the screen bounds.
    if ai_y < 0:
        ai_y = 0
    if ai_y > HEIGHT - PADDLE_HEIGHT:
        ai_y = HEIGHT - PADDLE_HEIGHT

    # Calculate delta time for frame-independent movement
    dt = clock.get_time() / 1000.0  # Convert to seconds

    # Update ball position with delta time
    ball_x += ball_vel_x * dt * 60  # Multiply by 60 to maintain similar speed
    ball_y += ball_vel_y * dt * 60

    # Ball collision with top and bottom boundaries
    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_vel_y *= -1

    # Check collision with the player paddle (left side)
    if ball_x <= player_x + PADDLE_WIDTH:
        if player_y < ball_y + BALL_SIZE and ball_y < player_y + PADDLE_HEIGHT:
            ball_vel_x *= -1
            ball_x = player_x + PADDLE_WIDTH  # reposition ball to avoid sticking
            paddle_hit_sound.play()  # Play the sound effect

    # Check collision with the AI paddle (right side)
    if ball_x + BALL_SIZE >= ai_x:
        if ai_y < ball_y + BALL_SIZE and ball_y < ai_y + PADDLE_HEIGHT:
            ball_vel_x *= -1
            ball_x = ai_x - BALL_SIZE  # reposition ball
            paddle_hit_sound.play()  # Play the sound effect

    # Check if the ball goes out of bounds (score update)
    if ball_x < 0:
        score_ai += 1
        # Reset ball to center and reverse direction
        ball_x = float(WIDTH // 2 - BALL_SIZE // 2)
        ball_y = float(HEIGHT // 2 - BALL_SIZE // 2)
        ball_vel_x = INITIAL_BALL_SPEED
        ball_vel_y = INITIAL_BALL_SPEED

    if ball_x > WIDTH - BALL_SIZE:
        score_player += 1
        # Reset ball to center and reverse direction
        ball_x = float(WIDTH // 2 - BALL_SIZE // 2)
        ball_y = float(HEIGHT // 2 - BALL_SIZE // 2)
        ball_vel_x = -INITIAL_BALL_SPEED
        ball_vel_y = INITIAL_BALL_SPEED

    # Drawing section
    screen.fill(BLACK)

    # Draw the paddles
    pygame.draw.rect(screen, WHITE, (player_x, player_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, WHITE, (ai_x, ai_y, PADDLE_WIDTH, PADDLE_HEIGHT))

    # Draw the ball (convert float positions to int for drawing)
    pygame.draw.rect(screen, WHITE, (int(ball_x), int(ball_y), BALL_SIZE, BALL_SIZE))

    # Display the score at the top center
    score_text = font.render(f"{score_player} : {score_ai}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    # Update the display and tick the clock
    pygame.display.flip()
    clock.tick(FPS)