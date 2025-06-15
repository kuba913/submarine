import pygame
import os

MAX_OPTION = 3  # Max option number in the main menu (from 0 to 3).

# Return values: First value returns False when whole game is meant to stop running (sets running = False (in "main.py" game loop)).
#                Second value returns "gamestate" chosen by player in menu.
def menu(screen: pygame.Surface, clock: pygame.time.Clock, fps: int) -> tuple[bool, str]:

    gamestate = "menu"

    options = [
        "Level Select",
        "Load Game",
        "Settings",
        "Quit Game"
    ]
    # Maybe change options to some kind of enums instead (remove this comment later).

    screen_width, screen_height = screen.get_size()

    # Font loading logic
    # Fonts and option texts primarly optimized for 480x640 window:
    font_option = pygame.font.Font(None, 36 * (screen_height//480))
    font_menu = pygame.font.Font(None, 60 * (screen_height//480))
    
    # Rendering menu screen logic

    # Rendering "Main Menu" main header text on the top
    main_menu_text_render = font_menu.render("Main Menu", True, (255, 255, 255))  # White "Main Menu" text
    main_menu_text_rect = main_menu_text_render.get_rect(center=(screen_width//2, screen_height//6))
    # Center in 1/2 of width and 1/6 of window height.

    # Rendeing options text logic
    option_count = 0
    option_text_renders = []
    option_text_rects = []
    for option in options:
        option_text_renders.append(font_option.render(option, True, (255, 255, 255)))
        option_text_rects.append(option_text_renders[option_count].get_rect(center=(screen_width//2, (screen_height//6)*(option_count+2))))
        # Centers of options in 1/2 of window width and spread across 2/6, 3/6, 4/6 and 5/6 of window heights.
        option_count += 1

    selected_option = 0
    
    # Submarine "arrow" select indicator image loading
    base_path = os.path.abspath(os.path.dirname(__file__))
    img_path = os.path.join(base_path, "assets", "img", "option_selector_ship.png")
    #option_select = pygame.image.load("/os.path.dirname(__file__) + assets/img/option_selector_ship.png")
    option_select = pygame.image.load(img_path)
    option_select = pygame.transform.scale(option_select, (100, 57))

    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                return False
            # Key press event
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_option += 1
                    selected_option %= (MAX_OPTION+1)
                elif event.key == pygame.K_UP:
                    selected_option -= 1
                    if selected_option < 0: selected_option = MAX_OPTION
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0: # Level Select (Start Game, as of yet)
                        menu_running = False
                        gamestate = "game"
                    elif selected_option == 1: # Load Game
                        pass
                    elif selected_option == 2: # Settings
                        pass
                    elif selected_option == 3: # Quit Game
                        return False

        # Fill the screen with black
        screen.fill((0, 0, 0))

        #Printing Main Menu
        screen.blit(main_menu_text_render, main_menu_text_rect)

        option_count = 0
        for option in option_text_rects:
            screen.blit(option_text_renders[option_count], option_text_rects[option_count])
            option_count += 1

        #Printing select indicator
        screen.blit(option_select, (screen_width * 0.15, ((screen_height//6) * (selected_option+2)) - ((screen_height//13) // (screen_height/480))))
        
        pygame.display.flip()

        clock.tick(fps)
    
    # If everything's fine (menu has been left without wanting to quit the game), return True and chosen gamestate
    return True, gamestate
