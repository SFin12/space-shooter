import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Continuous Background Scrolling")

# Load your background image
background_image = pygame.image.load("./assets/background-black-wide.png")  # Replace with your image path

# Get the height of the background image
background_height = background_image.get_height()

# Initialize the y-coordinates for the two background images
background_y1 = 0
background_y2 = -background_height  # Initially off the screen

# Set the speed of the scrolling
scroll_speed = 2

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the background images
    background_y1 += scroll_speed
    background_y2 += scroll_speed

    # If the first background image goes off the screen, reset its position
    if background_y1 >= HEIGHT:
        background_y1 = -background_height

    # If the second background image goes off the screen, reset its position
    if background_y2 >= HEIGHT:
        background_y2 = -background_height

    # Fill the screen with white (or any other background color)
    screen.fill(WHITE)

    # Draw the two background images
    screen.blit(background_image, (0, background_y1))
    screen.blit(background_image, (0, background_y2))

    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()