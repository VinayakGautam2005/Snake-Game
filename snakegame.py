import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game By Vinayak')

# Clock and FPS
clock = pygame.time.Clock()
FPS = 10

# Block size
snake_block = 20

# Colors for button animations
green_anim_colors = [(50,180,50), (120,200,60), (80,240,140), (50,180,50)]
red_anim_colors = [(200,50,50), (220,80,80), (180,0,0), (200,50,50)]

# Load images
background_image = pygame.image.load('background.jpg')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

food_img_orig = pygame.image.load('food.png').convert_alpha()

# Scale food image larger than snake block
food_size = int(snake_block * 1.5)  # e.g., 30 if snake_block = 20
food_img = pygame.transform.scale(food_img_orig, (food_size, food_size))

# Fonts
title_font = pygame.font.SysFont("bahnschrift", 50, bold=True)
button_font = pygame.font.SysFont("bahnschrift", 30, bold=True)
score_font = pygame.font.SysFont("comicsansms", 35)
msg_font = pygame.font.SysFont("bahnschrift", 25)

# Button class with animation
class AnimatedButton:
    def __init__(self, rect, text, font, anim_colors, anim_speed=10):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.anim_colors = anim_colors
        self.anim_speed = anim_speed
        self.anim_index = 0
        self.hover = False

    def update(self):
        self.anim_index = (self.anim_index + 1) % (len(self.anim_colors) * self.anim_speed)

    def draw(self, surface):
        color_index = (self.anim_index // self.anim_speed) % len(self.anim_colors)
        color = tuple(min(255, c + 40) for c in self.anim_colors[color_index]) if self.hover else self.anim_colors[color_index]
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_render = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_render.get_rect(center=self.rect.center)
        surface.blit(text_render, text_rect)

    def check_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        return self.hover

# Draw the snake with rounded head and tail, rotating face on the head
def draw_snake(snake_body, x_change, y_change):
    if len(snake_body) >= 2:
        # Tail with rounded corners
        tail_pos = snake_body[0]
        pygame.draw.rect(screen, (0, 150, 0), [tail_pos[0], tail_pos[1], snake_block, snake_block], border_radius=8)

        # Body segments (rectangles without rounding)
        for segment in snake_body[1:-1]:
            pygame.draw.rect(screen, (0, 200, 0), [segment[0], segment[1], snake_block, snake_block])

    if len(snake_body) > 0:
        head_pos = snake_body[-1]
        # Head with rounded corners
        pygame.draw.rect(screen, (0, 255, 0), [head_pos[0], head_pos[1], snake_block, snake_block], border_radius=8)

        # Draw rotating face on head based on direction
        eye_radius = snake_block // 8
        mouth_thickness = 2
        cx, cy = head_pos[0], head_pos[1]

        if x_change == snake_block:  # Moving right
            left_eye = (cx + 3*snake_block//4, cy + snake_block//3)
            right_eye = (cx + 3*snake_block//4, cy + 2*snake_block//3)
            mouth_start = (cx + snake_block//2, cy + 3*snake_block//4)
            mouth_end = (cx + 3*snake_block//4, cy + 3*snake_block//4)
        elif x_change == -snake_block:  # Moving left
            left_eye = (cx + snake_block//4, cy + snake_block//3)
            right_eye = (cx + snake_block//4, cy + 2*snake_block//3)
            mouth_start = (cx + snake_block//4, cy + 3*snake_block//4)
            mouth_end = (cx + snake_block//2, cy + 3*snake_block//4)
        elif y_change == snake_block:  # Moving down
            left_eye = (cx + snake_block//3, cy + 3*snake_block//4)
            right_eye = (cx + 2*snake_block//3, cy + 3*snake_block//4)
            mouth_start = (cx + snake_block//4, cy + snake_block//2)
            mouth_end = (cx + 3*snake_block//4, cy + snake_block//2)
        elif y_change == -snake_block or (x_change == 0 and y_change == 0):  # Moving up or initial state
            left_eye = (cx + snake_block//3, cy + snake_block//4)
            right_eye = (cx + 2*snake_block//3, cy + snake_block//4)
            mouth_start = (cx + snake_block//4, cy + snake_block//2)
            mouth_end = (cx + 3*snake_block//4, cy + snake_block//2)
        else:
            # default face position
            left_eye = (cx + snake_block//3, cy + snake_block//4)
            right_eye = (cx + 2*snake_block//3, cy + snake_block//4)
            mouth_start = (cx + snake_block//4, cy + snake_block//2)
            mouth_end = (cx + 3*snake_block//4, cy + snake_block//2)

        # Draw eyes
        pygame.draw.circle(screen, (0, 0, 0), left_eye, eye_radius)
        pygame.draw.circle(screen, (0, 0, 0), right_eye, eye_radius)
        # Draw smile
        pygame.draw.line(screen, (0, 0, 0), mouth_start, mouth_end, mouth_thickness)

# Show the current score
def show_score(score):
    value = score_font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(value, [0, 0])

# Render messages
def message(msg, color):
    mesg = msg_font.render(msg, True, color)
    screen.blit(mesg, [WIDTH / 6, HEIGHT / 3])

# Intro screen with animated title and buttons
def intro_screen():
    play_button = AnimatedButton(((WIDTH - 200) // 2, 220, 200, 60), "PLAY", button_font, green_anim_colors)
    exit_button = AnimatedButton(((WIDTH - 200) // 2, 300, 200, 60), "EXIT", button_font, red_anim_colors)

    title_phase = 0

    while True:
        screen.blit(background_image, (0, 0))

        pulse = 100 + int(55 * abs(math.sin(title_phase / 20.0)))
        title_color = (pulse, 255 - pulse // 2, pulse // 2)
        title_surf = title_font.render("SNAKE GAME", True, title_color)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 140))
        screen.blit(title_surf, title_rect)

        title_phase += 1

        mouse_pos = pygame.mouse.get_pos()
        for btn in (play_button, exit_button):
            btn.check_hover(mouse_pos)
            btn.update()
            btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.check_hover(mouse_pos):
                    return
                if exit_button.check_hover(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(30)

# Game over screen with animated retry and quit buttons
def game_over_screen(score):
    retry_button = AnimatedButton(((WIDTH - 200) // 2, 220, 200, 60), "RETRY", button_font, green_anim_colors)
    quit_button = AnimatedButton(((WIDTH - 200) // 2, 300, 200, 60), "QUIT", button_font, red_anim_colors)

    while True:
        screen.blit(background_image, (0, 0))
        message_surf = title_font.render("Game Over!", True, (220, 40, 40))
        message_rect = message_surf.get_rect(center=(WIDTH // 2, 140))
        screen.blit(message_surf, message_rect)

        score_surf = score_font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(WIDTH // 2, 180))
        screen.blit(score_surf, score_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        for btn in (retry_button, quit_button):
            btn.check_hover(mouse_pos)
            btn.update()
            btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_button.check_hover(mouse_pos):
                    return True  # retry
                if quit_button.check_hover(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(30)

# Main game loop
def game_loop():
    x = WIDTH // 2
    y = HEIGHT // 2
    x_change = 0
    y_change = 0
    snake_length = 4
    snake_body = []
    score = 0
    started = False
    game_over = False
    game_close = False

    for i in range(snake_length):
        snake_body.append([x - i * snake_block, y])

    while not game_over:

        while game_close:
            retry = game_over_screen(score)
            if retry:
                game_loop()
            else:
                game_over = True
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -snake_block
                    y_change = 0
                    started = True
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = snake_block
                    y_change = 0
                    started = True
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -snake_block
                    x_change = 0
                    started = True
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = snake_block
                    x_change = 0
                    started = True

        if started:
            x += x_change
            y += y_change

            if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
                game_close = True

            snake_head = [x, y]
            snake_body.append(snake_head)

            if len(snake_body) > snake_length:
                del snake_body[0]

            for segment in snake_body[:-1]:
                if segment == snake_head:
                    game_close = True

        # Generate or maintain food position aligned to grid
        if not hasattr(game_loop, "food_pos"):
            food_x = round(random.randrange(0, WIDTH - snake_block) / snake_block) * snake_block
            food_y = round(random.randrange(0, HEIGHT - snake_block) / snake_block) * snake_block
            game_loop.food_pos = (food_x, food_y)
        else:
            food_x, food_y = game_loop.food_pos

        # Center food image on grid cell because food is larger
        food_draw_x = food_x - (food_size - snake_block)//2
        food_draw_y = food_y - (food_size - snake_block)//2

        # Draw everything
        screen.blit(background_image, (0, 0))
        screen.blit(food_img, (food_draw_x, food_draw_y))
        draw_snake(snake_body, x_change, y_change)
        show_score(score)

        pygame.display.update()

        # Check if snake ate food
        if started and x == food_x and y == food_y:
            food_x = round(random.randrange(0, WIDTH - snake_block) / snake_block) * snake_block
            food_y = round(random.randrange(0, HEIGHT - snake_block) / snake_block) * snake_block
            game_loop.food_pos = (food_x, food_y)
            snake_length += 1
            score += 1

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# Run the game
intro_screen()
game_loop()
