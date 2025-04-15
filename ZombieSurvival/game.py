import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 1000  # Set the window size
FPS = 60
TEAM_SIZE = 50  # Size of the player
SPAWN_SIZE = 150  # Increased size of the spawn points
PLAYER_RADIUS = 15  # Radius of the player circle
GUN_LENGTH = 20  # Length of the gun
BASE_MOVE_SPEED = 5  # Base speed of player movement
SPRINT_MOVE_SPEED = 8  # Speed of player while sprinting
BULLET_SPEED = 10  # Speed of the bullet
EXPLOSION_DURATION = 10  # Duration of the explosion in frames
RECOIL_AMOUNT = 5  # Amount of recoil when shooting

# Stamina settings
MAX_STAMINA = 100  # Maximum stamina
STAMINA_REGEN_RATE = 5  # Stamina regeneration rate (points per second)
SPRINT_DEPLETION_RATE = 20  # Stamina consumption rate while sprinting (points per second)

# Colors
COLORS = {
    "Team 1": (255, 0, 0),  # Red
    "Team 2": (0, 255, 0),  # Green
    "Team 3": (0, 0, 255),  # Blue
    "Team 4": (255, 255, 0)  # Yellow
}

# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

    def update(self):
        self.x += BULLET_SPEED * math.cos(self.angle)
        self.y += BULLET_SPEED * math.sin(self.angle)

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), 5)

# Explosion class
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20  # Size of the explosion
        self.duration = EXPLOSION_DURATION  # How long the explosion lasts

    def update(self):
        self.duration -= 1  # Decrease duration

    def draw(self, screen):
        if self.duration > 0:
            pygame.draw.circle(screen, (255, 165, 0), (int(self.x), int(self.y)), self.size)  # Orange explosion
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.size // 2)  # Red center

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Team Spawn Points with Player Aiming and Shooting")

# Initialize font for displaying health and stamina
font = pygame.font.Font(None, 36)

# Function to draw the map and spawn points
def draw_map():
    # Fill the background
    screen.fill((200, 200, 200))  # Light gray background

    # Draw spawn points for each team
    spawn_points = {
        "Team 1": (0, 0),  # Top-left corner
        "Team 2": (WIDTH - SPAWN_SIZE, 0),  # Top-right corner
        "Team 3": (0, HEIGHT - SPAWN_SIZE),  # Bottom-left corner
        "Team 4": (WIDTH - SPAWN_SIZE, HEIGHT - SPAWN_SIZE)  # Bottom-right corner
    }

    for team, position in spawn_points.items():
        pygame.draw.rect(screen, COLORS[team], (*position, SPAWN_SIZE, SPAWN_SIZE))

# Function to draw the player
def draw_player(x, y, aim_x, aim_y):
    # Draw the player as a circle
    pygame.draw.circle(screen, (0, 0, 0), (x, y), PLAYER_RADIUS)  # Player body

    # Calculate the angle to aim at the mouse
    angle = math.atan2(aim_y - y, aim_x - x)

    # Calculate the end position of the gun
    gun_x = x + (PLAYER_RADIUS + GUN_LENGTH) * math.cos(angle)
    gun_y = y + (PLAYER_RADIUS + GUN_LENGTH) * math.sin(angle)

    # Draw the gun
    pygame.draw.line(screen, (255, 0, 0), (x, y), (gun_x, gun_y), 5)

    return angle  # Return the angle for bullet creation

# Function to display health and stamina in a box at the top
def display_health_stamina(health, stamina):
    # Draw a background box for health and stamina
    box_width = 200
    box_height = 50
    box_x = (WIDTH - box_width) // 2
    box_y = 10
    pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_width, box_height))  # Black box

    # Render health and stamina text
    health_text = font.render(f'Health: {health}', True, (255, 0, 0))
    stamina_text = font.render(f'Stamina: {int(stamina)}', True, (0, 0, 255))  # Display stamina as an integer

    # Blit the text onto the box
    screen.blit(health_text, (box_x + 10, box_y + 10))  # Position for health
    screen.blit(stamina_text, (box_x + 10, box_y + 30))  # Position for stamina

# Main game loop
def main():
    clock = pygame.time.Clock()
    player_x, player_y = WIDTH // 2, HEIGHT // 2  # Start player in the center
    bullets = []  # List to hold bullets
    explosions = []  # List to hold explosions

    # Player stats
    health = 100  # Starting health
    stamina = MAX_STAMINA  # Starting stamina
    sprint_cooldown = 0  # Cooldown timer for sprinting

    # Recoil variables
    recoil_timer = 0  # Timer for recoil effect
    recoil_duration = 10  # Duration of recoil in frames
    is_recoiling = False  # Flag to check if the player is recoiling

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Shoot bullet on mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    aim_x, aim_y = pygame.mouse.get_pos()
                    angle = math.atan2(aim_y - player_y, aim_x - player_x)
                    bullets.append(Bullet(player_x, player_y, angle))

                    # Start recoil effect
                    is_recoiling = True
                    recoil_timer = recoil_duration  # Reset the recoil timer

        # Get the mouse position
        aim_x, aim_y = pygame.mouse.get_pos()

        # Determine movement speed
        move_speed = BASE_MOVE_SPEED
        can_sprint = stamina > 0 and sprint_cooldown <= 0  # Allow sprinting if stamina is above 0 and cooldown is over

        # Get the keys pressed for movement
        keys = pygame.key.get_pressed()
        moving = False  # Flag to check if the player is moving

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= move_speed
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += move_speed
            moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_y -= move_speed
            moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_y += move_speed
            moving = True

        # Update stamina only if moving and sprinting
        if moving and keys[pygame.K_SPACE] and can_sprint:
            stamina -= (SPRINT_DEPLETION_RATE / FPS)  # Decrease stamina while sprinting
            if stamina < 0:
                stamina = 0
                sprint_cooldown = 6 * FPS  # Start cooldown for 6 seconds
        else:
            # Regenerate stamina when not moving
            if stamina < MAX_STAMINA:
                stamina += (STAMINA_REGEN_RATE / FPS)
                if stamina > MAX_STAMINA:
                    stamina = MAX_STAMINA

        # Update cooldown timer
        if sprint_cooldown > 0:
            sprint_cooldown -= 1  # Decrease cooldown timer

        # Update player position during recoil
        if is_recoiling:
            recoil_factor = (recoil_duration - recoil_timer) / recoil_duration  # Calculate easing factor
            player_x -= RECOIL_AMOUNT * math.cos(angle) * (1 - recoil_factor)  # Smoothly adjust position
            player_y -= RECOIL_AMOUNT * math.sin(angle) * (1 - recoil_factor)

            recoil_timer -= 1  # Decrease the timer
            if recoil_timer <= 0:
                is_recoiling = False  # End recoil effect

        # Keep the player within the screen bounds
        player_x = max(PLAYER_RADIUS, min(WIDTH - PLAYER_RADIUS, player_x))
        player_y = max(PLAYER_RADIUS, min(HEIGHT - PLAYER_RADIUS, player_y))

        # Update and draw bullets
        for bullet in bullets[:]:  # Iterate over a copy of the list
            bullet.update()
            # Check for bullet collisions with walls
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                explosions.append(Explosion(bullet.x, bullet.y))  # Create an explosion
                bullets.remove(bullet)  # Remove the bullet

        # Update explosions
        for explosion in explosions[:]:  # Iterate over a copy of the list
            explosion.update()
            if explosion.duration <= 0:
                explosions.remove(explosion)  # Remove the explosion if its duration is over

        draw_map()
        draw_player(player_x, player_y, aim_x, aim_y)

        # Draw all bullets
        for bullet in bullets:
            bullet.draw(screen)

        # Draw all explosions
        for explosion in explosions:
            explosion.draw(screen)

        # Display health and stamina in a box at the top
        display_health_stamina(health, stamina)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()