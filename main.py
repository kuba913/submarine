import pygame

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Submarine")

# Game loop
gamestate = "menu"
running = True
while running:

    # Game logic
    match gamestate:
        case "menu":
            # Menu logic
            pass
        case "game":
            # Game logic
            pass

    # Event handling
    for event in pygame.event.get():
        match gamestate:
            case "menu":
                # Menu events
                pass
            case "game":
                # Game events
                pass
        if event.type == pygame.QUIT:
            running = False

    # Drawing
    match gamestate:
        case "menu":
            # Draw menu
            pass
        case "game":
            # Draw game
            pass

    # Display update
    clock.tick(60)
    pygame.display.update()

# Quit Pygame
pygame.quit()