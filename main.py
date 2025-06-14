import pygame
import level

# Debug settings
debugText = True
debugInstaGame = True
debugBasicDraw = True

# Game loop settings
fps = 12

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1000, 500))
pygame.display.set_caption("Submarine")

tick = 0
tickPerLoop = 12

# Game loop
gamestate = "menu"
running = True

if debugInstaGame:
    gamestate = "game"

while running:
    # Tick management
    tick = (tick + 1) % tickPerLoop
    
    # Game logic
    match gamestate:
        case "menu":
            # Menu logic
            pass
        case "game":
            # Game logic
            if tick == 0:
                level.updateLevel(debugText)  # Update the level and all entities
            pass

    # Event handling
    for event in pygame.event.get():
        match gamestate:
            case "menu":
                # Menu events
                pass
            case "game":
                # Game events
                if event.type == pygame.KEYDOWN:
                    if debugBasicDraw == True:
                        if event.key == pygame.K_w:
                            level.playerShip.throttle = min(level.playerShip.throttle+10, 100)
                        if event.key == pygame.K_s:
                            level.playerShip.throttle = max(level.playerShip.throttle-10, -100)
                        if event.key == pygame.K_a:
                            level.playerShip.steer_target = min(level.playerShip.steer_target+1, level.playerShip.steer_max)
                        if event.key == pygame.K_d:
                            level.playerShip.steer_target = max(level.playerShip.steer_target-1, -level.playerShip.steer_max)
                        if event.key == pygame.K_SPACE:
                            level.playerShip.attack_torpedo(0)
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
            if debugBasicDraw:
                screen.fill((0, 0, 0))
                level.debugDrawLevel(screen)
            pass

    # Display update
    clock.tick(fps)
    pygame.display.update()

# Quit Pygame
pygame.quit()