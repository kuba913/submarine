import pygame
import level
import menu
import gameui
import settings

# Debug settings
debugText = True
debugInstaGame = False
debugBasicDraw = False
debugKeyboardSteering = True

# Game loop settings
fps = 60

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption("Submarine")

tick = 0
tickPerLoop = 60

# Game loop
gamestate = "menu"
running = True

if debugInstaGame:
    gamestate = "game"
    level.loadSave("test.p")

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
    events = pygame.event.get()
    for event in events:
        match gamestate:
            case "game":
                # Game events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        gameui.switch_screen(gameui.UIScreen.PANEL)
                    if debugKeyboardSteering:
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
                        if event.key == pygame.K_p:
                            gamestate = "pause"
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
            else:
                if not gameui.draw_ui(screen, events):
                    gamestate = "menu"
            pass
        case "pause":
            # Draw pause menu
            gameui.draw_pause_screen(screen)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gamestate = "game"

    # Display update
    clock.tick(fps)
    pygame.display.update()

# Quit Pygame
pygame.quit()