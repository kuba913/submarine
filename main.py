import pygame
import level
import menu

# Idea: Maybe make separate .py file for settings...
# (among others: passing values to menu function wouldn't be needed)...
# Screen settings
SCREEN_HEIGHT = 480
SCREEN_WIDTH = 640

# Debug settings
debugText = True
debugInstaGame = False
debugBasicDraw = True

# Game loop settings
fps = 60

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Submarine")

tick = 0
tickPerLoop = 60

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
            running, gamestate = menu.menu(screen, clock, fps)
        case "game":
            # Game logic
            if tick == 0:
                level.updateLevel(debugText)  # Update the level and all entities
            pass

    # Event handling
    for event in pygame.event.get():
        match gamestate:
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