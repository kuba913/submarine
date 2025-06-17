import pygame
import os
import random as rand
import math
import copy
import level

MAX_OPTION = 3  # Max option number in the main menu (from 0 to 3).
MAX_LVL_SEL_SUBM_OPTION = 1 # Max option in level select submenu (from 0 to 1).
MAX_BUBBLES = 10 # Max amount of bubbles (from bubble animation) on menu screen.

"""
#returns filename of chosen level to load:
def level_select_submenu() -> str:

    submenu_options = [
        "Level 1",
        "Level 2"
    ]

    screen_width, screen_height = screen.get_size()
    submenu_running = True
    while submenu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
"""
#^ probably won't be used



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

    level_select_submenu_options = [
        "Level 1",
        "Level 2"
    ]
    # Idea: Maybe change options to some kind of enums instead (remove this comment later).

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
    # Rendering "Level Select" main header text on the top
    level_select_text_render = font_menu.render("Level Select", True, (255, 255, 255))  # White "Level Select" text
    level_select_text_rect = level_select_text_render.get_rect(center=(screen_width//2, screen_height//6))

    #!Maybe delete reduntant (repeated) code lines later.
    # Rendeing options text logic
    option_count = 0
    option_text_renders = []
    option_text_rects = []
    level_select_option_text_renders = []
    level_select_option_text_rects = []
    for option in options:
        option_text_renders.append(font_option.render(option, True, (255, 255, 255)))
        option_text_rects.append(option_text_renders[option_count].get_rect(center=(screen_width//2, (screen_height//6)*(option_count+2))))
        # Centers of options in 1/2 of window width and spread across 2/6, 3/6, 4/6 and 5/6 of window heights.
        option_count += 1
    option_count = 0
    for option in level_select_submenu_options:
        level_select_option_text_renders.append(font_option.render(option, True, (255, 255, 255)))
        level_select_option_text_rects.append(level_select_option_text_renders[option_count].get_rect(center=(screen_width//2, (screen_height//6)*(option_count+2))))
        # Centers of options in 1/2 of window width and spread across 2/6 and 3/6 of window heights.
        option_count += 1

    selected_option = 0
    
    # Submarine "arrow" select indicator image loading
    base_path = os.path.abspath(os.path.dirname(__file__))
    imgs_path = os.path.join(base_path, "assets", "img")
    ship_img_path = os.path.join(imgs_path, "option_selector_ship.png")
    option_select = pygame.image.load(ship_img_path)
    option_select = pygame.transform.scale(option_select, (100, 57))

    # Bubble image loading
    bubble_img_path = os.path.join(imgs_path, "bubble.png")
    bubble = pygame.image.load(bubble_img_path)
    bubble = pygame.transform.scale(bubble, (29, 29))
    bubbles = {}

    rand.seed()

    menu_running = True
    is_main_menu = True     #is main menu currently active/displayed
    is_level_select = False #is level select submenu currently active/displayed
    while menu_running:
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                return False
            # Key press event
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_option += 1
                    if is_main_menu:
                        selected_option %= (MAX_OPTION+1)
                    elif is_level_select:
                        selected_option %= (MAX_LVL_SEL_SUBM_OPTION+1)
                elif event.key == pygame.K_UP:
                    selected_option -= 1
                    if is_main_menu:
                        if selected_option < 0: selected_option = MAX_OPTION
                    if is_level_select:
                        if selected_option < 0: selected_option = MAX_LVL_SEL_SUBM_OPTION
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0: # Level Select (Start Game, as of yet)
                        if is_main_menu:
                            is_level_select = True
                            is_main_menu = False
                        elif is_level_select:
                            level.loadSave("level1.p") # Load level 1
                            menu_running = False
                            gamestate = "game"
                    elif selected_option == 1: # Load Game
                        if is_main_menu:
                            pass
                        elif is_level_select:
                            level.loadSave("level2.p") # Load level 2
                            menu_running = False
                            gamestate = "game"
                    elif selected_option == 2: # Settings
                        pass
                    elif selected_option == 3: # Quit Game
                        if is_main_menu:
                            return False
                elif event.key == pygame.K_ESCAPE:
                    is_main_menu = True
                    is_level_select = False


        # Fill the screen with black
        screen.fill((0, 0, 0))

        # Bubbles animation and printing logic
        if len(bubbles) < MAX_BUBBLES:
            left_to_max = range(MAX_BUBBLES-len(bubbles)) # How many more bubbles we can add before reaching the MAX_BUBBLES limit.
            for i in left_to_max:
                if rand.randint(1, 200) == 1: # Chance of spawning per frame (0.5% chance).
                    bubbles.update({
                        rand.randint(screen_width//3, (screen_width//3)*2) : screen_height
                    })
        new_bubbles = {}
        for key in bubbles:
            screen.blit(bubble, (key, bubbles[key])) # x and y pair.
            if bubbles[key] > -29:
            # If upper-left corner of bubble still isn't 29 pixels or more above the visible screen surface
                new_bubbles[key + math.sin(bubbles[key] / (screen_height / 11)) * 3] = bubbles[key] - 1
                # Then use the previous bubble coordinates updated by value from dedicated sinus function for the next frame.
            # Otherwise this bubble will be cleared and the new will spawn in its place from the bottom of the menu screen during next frame.
        bubbles.clear()
        bubbles = copy.deepcopy(new_bubbles)

        # Printing Menu text

        # Printing header text
        if is_main_menu:
            # "Main Menu"
            screen.blit(main_menu_text_render, main_menu_text_rect)
        elif is_level_select:
            # "Level Select"
            screen.blit(level_select_text_render, level_select_text_rect)

        # Printing menu option texts
        option_count = 0
        if is_main_menu:
            for option_text_rect in option_text_rects:
                screen.blit(option_text_renders[option_count], option_text_rect)
                option_count += 1
        elif is_level_select:
            for option_text_rect in level_select_option_text_rects:
                screen.blit(level_select_option_text_renders[option_count], option_text_rect)
                option_count += 1

        # Printing select indicator
        screen.blit(option_select, (screen_width * 0.15, ((screen_height//6) * (selected_option+2)) - ((screen_height//13) // (screen_height/480))))
        
        pygame.display.flip()

        clock.tick(fps)
    
    # If everything's fine (menu has been left without wanting to quit the game), return True and chosen gamestate
    return True, gamestate
