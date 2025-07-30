import pygame
import sys
import random
import os
from pygame import mixer

pygame.init()
mixer.init()

# Get path relative to this file (installed module)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("LightDash")

clock = pygame.time.Clock()
FPS = 60

# Colors
PLAYER_COLOR = (255, 255, 255)
OBSTACLE_COLOR = (200, 50, 50)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)
PARTICLE_COLOR = (255, 255, 255, 100)

# Load background video frames
bg_frames = []
bg_folder = os.path.join(ASSETS_DIR, "bg_frames")
for fname in sorted(os.listdir(bg_folder)):
    if fname.endswith(".png"):
        img = pygame.image.load(os.path.join(bg_folder, fname)).convert()
        img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_frames.append(img)

bg_frame_index = 0
bg_frame_count = len(bg_frames)

# Load sounds
sound_dir = os.path.join(ASSETS_DIR, "sounds")
mixer.music.load(os.path.join(sound_dir, "bg_music.mp3"))
mixer.music.set_volume(0.5)
mixer.music.play(-1)

jump_sound = mixer.Sound(os.path.join(sound_dir, "jump.wav"))
jump_sound.set_volume(0.5)

# Player setup
player_width = 40
player_height = 40
player_x = 100
player_y = SCREEN_HEIGHT - player_height - 100
player_vel_y = 0
jump_count = 0
GRAVITY = 0.8
JUMP_STRENGTH = -15
GROUND_Y = SCREEN_HEIGHT - 100
player = pygame.Rect(player_x, player_y, player_width, player_height)

# Obstacles
obstacle_width = 30
obstacle_height = 50
obstacle_speed = 6
obstacles = []
spawn_timer = 0

bstacle_width = 30
bstacle_height = 50
bstacle_speed = 4
bstacles = []
spawns_timer = 0

# Font and Score
font = pygame.font.SysFont("Consolas", 30, bold=True)
score = 0
score_timer = 0

# Button
button_font = pygame.font.SysFont("Consolas", 24)
button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 60, 160, 40)

# Game state
running = True
game_over = False

# Particle system
particles = []

def spawn_particles(x, y):
    for _ in range(8):
        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-2, 2),
            "dy": random.uniform(-3, -1),
            "radius": random.randint(2, 4),
            "life": random.randint(20, 40)
        })

def draw_particles():
    for p in particles:
        pygame.draw.circle(screen, PARTICLE_COLOR, (int(p["x"]), int(p["y"])), p["radius"])

def update_particles():
    for p in particles:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["dy"] += 0.1  # gravity
        p["life"] -= 1
    particles[:] = [p for p in particles if p["life"] > 0]

def draw_glow(rect):
    glow_surface = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surface, (0, 255, 255, 50), glow_surface.get_rect())
    screen.blit(glow_surface, (rect.x - 10, rect.y - 10))

def reset_game():
    global player, player_vel_y, jump_count, score, score_timer
    global obstacles, bstacles, spawn_timer, spawns_timer, game_over, particles

    player.x = 100
    player.y = GROUND_Y - player_height
    player_vel_y = 0
    jump_count = 0
    score = 0
    score_timer = 0
    obstacles.clear()
    bstacles.clear()
    particles.clear()
    spawn_timer = 0
    spawns_timer = 0
    game_over = False

# Main loop
def main():
    global running, game_over, player_vel_y, jump_count, score, score_timer
    global spawn_timer, spawns_timer, bg_frame_index

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and jump_count < 2:
                        player_vel_y = JUMP_STRENGTH
                        jump_count += 1
                        jump_sound.play()
                        spawn_particles(player.centerx, player.bottom)
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(pygame.mouse.get_pos()):
                        reset_game()

        if not game_over:
            screen.blit(bg_frames[bg_frame_index], (0, 0))
            bg_frame_index = (bg_frame_index + 1) % bg_frame_count

            player_vel_y += GRAVITY
            player.y += player_vel_y
            if player.y >= GROUND_Y - player_height:
                player.y = GROUND_Y - player_height
                player_vel_y = 0
                jump_count = 0

            score_timer += clock.get_time()
            if score_timer >= 100:
                score += 10 if jump_count == 0 else 5
                score_timer = 0

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            current_time = pygame.time.get_ticks()
            if current_time - spawn_timer > 1500:
                obstacle_x = SCREEN_WIDTH + random.randint(0, 600)
                obstacle = pygame.Rect(obstacle_x, GROUND_Y - obstacle_height, obstacle_width, obstacle_height)
                obstacles.append(obstacle)
                spawn_timer = current_time

            if current_time - spawns_timer > 3000:
                bstacle_x = SCREEN_WIDTH + random.randint(200, 400)
                bstacle = pygame.Rect(bstacle_x, GROUND_Y - bstacle_height - 100, bstacle_width, bstacle_height)
                bstacles.append(bstacle)
                spawns_timer = current_time

            for obstacle in obstacles:
                obstacle.x -= obstacle_speed
                pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle)
                if player.colliderect(obstacle):
                    game_over = True

            for bstacle in bstacles:
                bstacle.x -= bstacle_speed
                pygame.draw.rect(screen, OBSTACLE_COLOR, bstacle)
                if player.colliderect(bstacle):
                    game_over = True

            update_particles()
            draw_particles()
            draw_glow(player)
            pygame.draw.rect(screen, PLAYER_COLOR, player)
            pygame.draw.line(screen, (80, 80, 80), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)

        else:
            screen.fill((10, 10, 30))
            game_over_text = font.render("GAME OVER", True, (255, 255, 255))
            final_score_text = font.render(f"FINAL SCORE : {score}", True, (255, 255, 255))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 60))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20))

            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.rect(screen, BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR, button_rect)
            restart_text = button_font.render("RESTART", True, (255, 255, 255))
            screen.blit(restart_text, (button_rect.x + 30, button_rect.y + 8))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
