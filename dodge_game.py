import pygame
import sys
import random
import math
import os

# -----------------------------
# LOAD / SAVE HIGH SCORE
# -----------------------------
def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            txt = f.read().strip()
            if txt.isdigit():
                return int(txt)
    return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# -----------------------------
# LOAD / SAVE LEADERBOARD
# -----------------------------
def load_leaderboard():
    leaderboard = []
    if os.path.exists("leaderboard.txt"):
        with open("leaderboard.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",", 1)
                if len(parts) == 2:
                    name, score_str = parts
                    if score_str.isdigit():
                        leaderboard.append((name, int(score_str)))
    return leaderboard

def save_leaderboard(leaderboard):
    with open("leaderboard.txt", "w") as f:
        for name, score in leaderboard:
            f.write(f"{name},{score}\n")

# -----------------------------
# INITIAL VARIABLES
# -----------------------------
player_width = 100
player_height = 100
player_x = 500
player_y = 850

block_width = 100
block_height = 100
block_x = random.randint(0, 900)
block_y = 0
block_speed = 20

score = 0
high_score = load_high_score()
leaderboard = load_leaderboard()

game_over = False
title_screen = True

particles = []
death_timer = 0
shake_timer = 0

title_anim = 0
bg_anim = 0

entering_name = False
current_name = ""
name_saved = False

# -----------------------------
# SETUP
# -----------------------------
pygame.init()
window = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption("Dodge Game")

font_big = pygame.font.Font(None, 150)
font_small = pygame.font.Font(None, 80)
font_tiny = pygame.font.Font(None, 50)
clock = pygame.time.Clock()

# -----------------------------
# SCREEN SHAKE
# -----------------------------
def get_shake_offset():
    if shake_timer > 0:
        return random.randint(-20, 20), random.randint(-20, 20)
    return 0, 0

# -----------------------------
# ANIMATED BACKGROUND
# -----------------------------
def draw_animated_background():
    global bg_anim
    bg_anim += 0.01
    r = int(100 + 50 * math.sin(bg_anim))
    g = int(100 + 50 * math.sin(bg_anim + 2))
    b = int(100 + 50 * math.sin(bg_anim + 4))
    window.fill((r, g, b))

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if entering_name and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if current_name.strip() == "":
                    current_name = "Player"
                leaderboard.append((current_name, score))
                leaderboard.sort(key=lambda x: x[1], reverse=True)
                leaderboard = leaderboard[:5]
                save_leaderboard(leaderboard)
                current_name = ""
                entering_name = False
                name_saved = True
            elif event.key == pygame.K_BACKSPACE:
                current_name = current_name[:-1]
            else:
                if len(current_name) < 12 and event.unicode.isprintable():
                    current_name += event.unicode

    keys = pygame.key.get_pressed()

    # -----------------------------
    # TITLE SCREEN
    # -----------------------------
    if title_screen:
        draw_animated_background()

        title_anim += 0.05
        pulse = (math.sin(title_anim) + 1) / 2
        title_alpha = int(255 * pulse)

        title_text = font_big.render("DODGE GAME", True, (255, 255, 255))
        title_surface = title_text.copy()
        title_surface.set_alpha(title_alpha)

        bounce_y = 500 + int(math.sin(title_anim * 2) * 20)

        start_text = font_small.render("Press SPACE to Start", True, (230, 230, 230))
        high_score_text = font_small.render(f"High Score: {high_score}", True, (255, 255, 0))

        window.blit(title_surface, title_surface.get_rect(center=(500, 250)))
        window.blit(start_text, start_text.get_rect(center=(500, bounce_y)))
        window.blit(high_score_text, high_score_text.get_rect(center=(500, 700)))

        # Show leaderboard on title
        y_pos = 780
        title_lb = font_tiny.render("Leaderboard:", True, (255, 255, 255))
        window.blit(title_lb, title_lb.get_rect(center=(500, y_pos)))
        y_pos += 40
        if leaderboard:
            for name, s in leaderboard:
                line = font_tiny.render(f"{name}: {s}", True, (255, 255, 255))
                window.blit(line, line.get_rect(center=(500, y_pos)))
                y_pos += 35
        else:
            no_lb = font_tiny.render("No scores yet", True, (200, 200, 200))
            window.blit(no_lb, no_lb.get_rect(center=(500, y_pos)))

        if keys[pygame.K_SPACE]:
            score = 0
            block_speed = 20
            block_x = random.randint(0, 900)
            block_y = 0
            player_x = 500
            title_screen = False
            game_over = False
            entering_name = False
            name_saved = False

        pygame.display.flip()
        clock.tick(60)
        continue

    # -----------------------------
    # GAMEPLAY
    # -----------------------------
    if not game_over:

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= 25
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += 25

        if player_x < 0:
            player_x = 0
        if player_x > 900:
            player_x = 900

        block_y += block_speed

        if block_y > 1000:
            block_x = random.randint(0, 900)
            block_y = 0
            score += 1
            block_speed += 0.5

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        block_rect = pygame.Rect(block_x, block_y, block_width, block_height)

        if player_rect.colliderect(block_rect):
            game_over = True
            death_timer = 60
            shake_timer = 20
            particles = []
            entering_name = True
            name_saved = False
            current_name = ""

            for i in range(40):
                particles.append([
                    player_x + player_width // 2,
                    player_y + player_height // 2,
                    random.randint(-15, 15),
                    random.randint(-20, -5),
                    random.randint(8, 15)
                ])

            if score > high_score:
                high_score = score
                save_high_score(high_score)

        draw_animated_background()

        shake_x, shake_y = get_shake_offset()
        pygame.draw.rect(window, (255, 0, 0), (block_x + shake_x, block_y + shake_y, block_width, block_height))
        pygame.draw.rect(window, (255, 255, 255), (player_x + shake_x, player_y + shake_y, player_width, player_height))

        score_text = font_small.render(str(score), True, (255, 255, 255))
        window.blit(score_text, (20, 20))

    # -----------------------------
    # GAME OVER + NAME ENTRY + LEADERBOARD
    # -----------------------------
    else:
        draw_animated_background()

        # Screen shake during early death frames
        global_shake_x, global_shake_y = get_shake_offset()

        # Particles
        for p in particles:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 1
            pygame.draw.rect(window, (255, 255, 0), (p[0] + global_shake_x, p[1] + global_shake_y, p[4], p[4]))

        if shake_timer > 0:
            shake_timer -= 1

        if death_timer > 0:
            death_timer -= 1

        if entering_name:
            prompt = font_small.render("New Score! Enter Name:", True, (255, 255, 255))
            name_text = font_small.render(current_name + "|", True, (255, 255, 0))
            window.blit(prompt, prompt.get_rect(center=(500 + global_shake_x, 400 + global_shake_y)))
            window.blit(name_text, name_text.get_rect(center=(500 + global_shake_x, 500 + global_shake_y)))
        else:
            game_over_text = font_big.render("GAME OVER", True, (255, 0, 0))
            score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))
            high_score_text = font_small.render(f"High Score: {high_score}", True, (255, 255, 0))
            restart_text = font_small.render("Press R to Restart", True, (100, 200, 100))
            quit_text = font_small.render("Press Q to Quit", True, (100, 200, 100))

            window.blit(game_over_text, game_over_text.get_rect(center=(500 + global_shake_x, 200 + global_shake_y)))
            window.blit(score_text, score_text.get_rect(center=(500 + global_shake_x, 320 + global_shake_y)))
            window.blit(high_score_text, high_score_text.get_rect(center=(500 + global_shake_x, 400 + global_shake_y)))
            window.blit(restart_text, restart_text.get_rect(center=(500 + global_shake_x, 650 + global_shake_y)))
            window.blit(quit_text, quit_text.get_rect(center=(500 + global_shake_x, 730 + global_shake_y)))

            # Show leaderboard under game over
            y_pos = 800 + global_shake_y
            lb_title = font_tiny.render("Leaderboard:", True, (255, 255, 255))
            window.blit(lb_title, lb_title.get_rect(center=(500 + global_shake_x, y_pos)))
            y_pos += 35
            if leaderboard:
                for name, s in leaderboard:
                    line = font_tiny.render(f"{name}: {s}", True, (255, 255, 255))
                    window.blit(line, line.get_rect(center=(500 + global_shake_x, y_pos)))
                    y_pos += 30

            if keys[pygame.K_r]:
                title_screen = True
                game_over = False

            if keys[pygame.K_q]:
                pygame.quit()
                sys.exit()

    pygame.display.flip()
    clock.tick(60)