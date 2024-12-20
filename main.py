import math
import random
import serial
import time
import pygame
from pygame import mixer

# Initialize pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load('background.png')

# Sound
mixer.music.load("background.ogg")
mixer.music.play(-1)

# Caption and Icon
pygame.display.set_caption("Space Invader")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480
playerX_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(50, 150))
    enemyY_change.append(4)

# Bullet
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 10
bullet_state = "ready"

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
textX = 10
textY = 10

# Game Over Text
over_font = pygame.font.Font('freesansbold.ttf', 64)

# Set up Micro:bit serial connection
microbit = serial.Serial('COM3', 115200, timeout=1)  # Replace 'COM3' with your Micro:bit's port
time.sleep(2)  # Wait for the connection to stabilize


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + math.pow(enemyY - bulletY, 2))
    return distance < 27


def player_collision(enemyX, enemyY, playerX, playerY):
    distance = math.sqrt(math.pow(enemyX - playerX, 2) + math.pow(enemyY - playerY, 2))
    return distance < 27


def read_microbit_command():
    if microbit.in_waiting > 0:  # Check if there's data to read
        command = microbit.readline().decode('utf-8').strip()
        return command
    return None


# Game Loop
running = True
last_bullet_time = time.time()  # Track time of last bullet
bullet_interval = 0.5  # Interval between automatic shots (in seconds)

while running:
    # Background color and image
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read command from Micro:bit
    command = read_microbit_command()
    if command == "left":
        playerX_change = -5
    elif command == "right":
        playerX_change = 5
    elif command == "stop":
        playerX_change = 0

    # Player Movement
    playerX += playerX_change
    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    # Automatic Shooting
    if time.time() - last_bullet_time > bullet_interval:
        bulletX = playerX
        bulletY = playerY
        fire_bullet(bulletX, bulletY)
        last_bullet_time = time.time()

    # Enemy Movement (Vertical)
    for i in range(num_of_enemies):
        # Move enemies vertically
        enemyY[i] += enemyY_change[i]

        # Check for collision with the player
        if player_collision(enemyX[i], enemyY[i], playerX, playerY):
            game_over_text()
            running = False  # End the game if a collision happens
            break

        # If enemy reaches the bottom of the screen, reset it to the top (infinite enemies)
        if enemyY[i] > 600:
            enemyY[i] = random.randint(-100, -40)  # Reset to a random position above the screen
            enemyX[i] = random.randint(0, 736)     # Randomize horizontal position

        # Check for bullet collision with enemies
        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            explosionSound = mixer.Sound("explosion.wav")
            explosionSound.play()
            bulletY = 480
            bullet_state = "ready"
            score_value += 1
            enemyY[i] = random.randint(-100, -40)  # Reset enemy to the top of the screen
            enemyX[i] = random.randint(0, 736)     # Randomize horizontal position

        enemy(enemyX[i], enemyY[i], i)

    # Bullet Movement
    if bulletY <= 0:
        bulletY = 480
        bullet_state = "ready"

    # Update the player and score
    player(playerX, playerY)
    show_score(textX, textY)
    pygame.display.update()

pygame.quit()
