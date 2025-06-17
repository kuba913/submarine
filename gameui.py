import pygame
import os
import level
import periscopeui
from settings import SCREEN_SCALING_RATIO
from enum import Enum

class InputType(Enum):
    RADAR = "radar"
    STEER_LEFT = "steer_left"
    STEER_RIGHT = "steer_right"
    TORPEDO1 = "torpedo1"
    TORPEDO2 = "torpedo2"
    PERISCOPE = "periscope"
    THROTTLE_SLOW = "throttle_slow"
    THROTTLE_HALF = "throttle_half"
    THROTTLE_FULL = "throttle_full"
    THROTTLE_STOP = "throttle_stop"
    THROTTLE_REV = "throttle_rev"
    NONE = "none"

class UIScreen(Enum):
    PANEL = "panel"
    TOPDOWN = "topdown"
    PERISCOPE = "periscope"

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

    def to_tuple(self):
        return (self.x, self.y)

class BoundingBox2D:
    def __init__(self, top_left: Vec2, bottom_right: Vec2):
        self.top_left = top_left
        self.bottom_right = bottom_right

    def contains(self, point: Vec2):
        return (self.top_left.x <= point.x <= self.bottom_right.x and
                self.top_left.y <= point.y <= self.bottom_right.y)

class Throttler:
    def __init__(self):
        self.value = 0

    def up(self):
        if self.value >= 3:
            return
        self.value += 1

    def down(self):
        if self.value <= -1:
            return
        self.value -= 1
    def set(self, value):
        if value < -1 or value > 3:
            raise ValueError("Throttle value must be between -1 and 3")
        self.value = value
    
    def reset(self):
        self.value = 0

    def get_value(self):
        return self.value

class Wheel:
    def __init__(self):
        self.value = 0

    def right(self):
        if self.value >= 1:
            return
        self.value += 1

    def left(self):
        if self.value <= -1:
            return
        self.value -= 1
    
    def reset(self):
        self.value = 0

    def get_value(self):
        return self.value

class Button:
    def __init__(self, img, rotation, scale, bounding_box: BoundingBox2D):
        self.image = img
        self.rotation = rotation
        self.scale = scale
        self.bounding_box = bounding_box
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.image = pygame.transform.scale_by(self.image, self.scale)
        self.loc = Vec2(self.bounding_box.top_left.x, self.bounding_box.top_left.y)
        self.rect = self.image.get_rect(center=self.loc.to_tuple())
        self.disabled = False  # Add a disabled attribute

    def draw(self, screen):
        if not self.disabled:
            screen.blit(self.image, self.rect)
    
    def check_clicked(self, mouse_pos):
        if self.disabled:
            return False
        pos = Vec2(mouse_pos[0], mouse_pos[1])
        return self.bounding_box.contains(pos)
    

pygame.font.init()
gameui_font = pygame.font.SysFont('Comic Sans MS', 18)
gameui_font_16 = pygame.font.SysFont('Comic Sans MS', 16)
gameui_font_48 = pygame.font.SysFont('Comic Sans MS', 48)
current_screen = UIScreen.PANEL
img_location_radar = BoundingBox2D(Vec2(820, 1300) * SCREEN_SCALING_RATIO, Vec2(1080, 1550) * SCREEN_SCALING_RATIO)
img_location_steer_left = BoundingBox2D(Vec2(330, 1060) * SCREEN_SCALING_RATIO, Vec2(475, 1300) * SCREEN_SCALING_RATIO)
img_location_steer_right = BoundingBox2D(Vec2(520, 1060) * SCREEN_SCALING_RATIO, Vec2(650, 1300) * SCREEN_SCALING_RATIO)
img_location_torpedo1 = BoundingBox2D(Vec2(160, 880) * SCREEN_SCALING_RATIO, Vec2(300, 1160) * SCREEN_SCALING_RATIO)
img_location_torpedo2 = BoundingBox2D(Vec2(694, 908) * SCREEN_SCALING_RATIO, Vec2(800, 1190) * SCREEN_SCALING_RATIO)
img_location_periscope = BoundingBox2D(Vec2(900, 100) * SCREEN_SCALING_RATIO, Vec2(1040, 586) * SCREEN_SCALING_RATIO)

img_locaton_throttle_full = BoundingBox2D(Vec2(860, 1064) * SCREEN_SCALING_RATIO, Vec2(956, 1084) * SCREEN_SCALING_RATIO)
img_location_throttle_half = BoundingBox2D(Vec2(860, 1086) * SCREEN_SCALING_RATIO, Vec2(956, 1110) * SCREEN_SCALING_RATIO)
img_location_throttle_slow = BoundingBox2D(Vec2(860, 1112) * SCREEN_SCALING_RATIO, Vec2(956, 1140) * SCREEN_SCALING_RATIO)
img_location_throttle_stop = BoundingBox2D(Vec2(860, 1142) * SCREEN_SCALING_RATIO, Vec2(956, 1170) * SCREEN_SCALING_RATIO)
img_location_throttle_rev = BoundingBox2D(Vec2(860, 1172) * SCREEN_SCALING_RATIO, Vec2(956, 1202) * SCREEN_SCALING_RATIO)
img_location_stats = Vec2(1045, 875) * SCREEN_SCALING_RATIO

# Absolute path to a current file.
base_path = os.path.abspath(os.path.dirname(__file__))
# assets/img/
imgs_path = os.path.join(base_path, "assets", "img")
# Images full paths (with file names now)
bg_img_path = os.path.join(imgs_path, "submarine_main_bg.png")
throttler_img_path = os.path.join(imgs_path, "throttler.png")
wheel_img_path = os.path.join(imgs_path, "wheel.png")
# Images load and scale
# Background image
bg_img = pygame.image.load(bg_img_path)
bg_img = pygame.transform.scale_by(bg_img, SCREEN_SCALING_RATIO)
# Throttler image
throttler_img = pygame.image.load(throttler_img_path)
throttler_img = pygame.transform.scale_by(throttler_img, SCREEN_SCALING_RATIO / 2)
# Wheel image
wheel_img = pygame.image.load(wheel_img_path)
wheel_img = pygame.transform.scale_by(wheel_img, SCREEN_SCALING_RATIO)
arrow_up_img = pygame.image.load(os.path.join("assets", "img", "arrow.png"))
button_img = pygame.image.load(os.path.join("assets", "img", "button.png"))

wheel_size = wheel_img.get_size()
wheel_size = Vec2(wheel_size[0], wheel_size[1])
img_location_wheel = Vec2(494, 1180) * SCREEN_SCALING_RATIO

throttler_size = throttler_img.get_size()
throttler_size = Vec2(throttler_size[0], throttler_size[1])
img_location_throttler = Vec2(970, 1160) * SCREEN_SCALING_RATIO - throttler_size / 2

throttler = Throttler()
wheel = Wheel()

def switch_screen(new_screen):
    """Switch the current UI screen."""
    global current_screen
    current_screen = new_screen

def draw_bg(screen):
    """Draw the background image on the screen."""
    screen.blit(bg_img, (0, 0))

def check_input(mouse_pos):
    """Check if the mouse position is within any clickable UI elements."""
    pos = Vec2(mouse_pos[0], mouse_pos[1])
    if img_location_radar.contains(pos):
        return InputType.RADAR
    elif img_location_steer_left.contains(pos):
        return InputType.STEER_LEFT
    elif img_location_steer_right.contains(pos):
        return InputType.STEER_RIGHT
    elif img_location_torpedo1.contains(pos):
        return InputType.TORPEDO1
    elif img_location_torpedo2.contains(pos):
        return InputType.TORPEDO2
    elif img_location_periscope.contains(pos):
        return InputType.PERISCOPE
    elif img_locaton_throttle_full.contains(pos):
        return InputType.THROTTLE_FULL
    elif img_location_throttle_half.contains(pos):
        return InputType.THROTTLE_HALF
    elif img_location_throttle_slow.contains(pos):
        return InputType.THROTTLE_SLOW
    elif img_location_throttle_stop.contains(pos):
        return InputType.THROTTLE_STOP
    elif img_location_throttle_rev.contains(pos):
        return InputType.THROTTLE_REV
    else:
        return InputType.NONE

def draw_wheel(screen):
    """Draw the steering wheel image on the screen."""
    rotated_wheel_img = pygame.transform.rotate(wheel_img, -wheel.get_value() * 30)  # Rotate based on wheel value
    wheel_rect = rotated_wheel_img.get_rect(center=img_location_wheel.to_tuple())
    screen.blit(rotated_wheel_img, wheel_rect)

def draw_throttler(screen):
    """Draw the throttler image on the screen."""
    offset = throttler.get_value() * 30 * SCREEN_SCALING_RATIO  # Adjust the offset based on throttler value
    location = img_location_throttler + Vec2(0, -offset)
    screen.blit(throttler_img, location.to_tuple())

def adjust_ship_param(ship, param, amount, min_value, max_value, idx):
    """Adjust a parameter value within specified bounds."""
    val = getattr(ship, param)[idx] + amount
    getattr(ship, param)[idx] = max(min(val, max_value), min_value)

torpedo_buttons = []
def launch_torpedo(ship, idx):
    ship.attack_torpedo(idx)
    if ship.torpedo_tube_targetSpeed[idx] > 0:
        torpedo_buttons[idx][4].disabled = True  # Disable the button after launching
    else:
        print(f"Torpedo {idx+1} cannot be launched due to speed being zero.")

def get_torpedo_buttons(amount):
    global torpedo_buttons
    if len(torpedo_buttons) > 0:
        return torpedo_buttons
    
    margin = 80
    btn_size = 60
    for idx in range(amount):
        # heading change buttons
        
        button_angle_left = Button(arrow_up_img, 90, 0.5, BoundingBox2D(
            Vec2(1540, 1426 + margin * idx) * SCREEN_SCALING_RATIO, Vec2(1540 + btn_size, (1426 + btn_size) + (margin * idx)) * SCREEN_SCALING_RATIO))
        button_angle_left.on_clicked = lambda target: adjust_ship_param(level.playerShip, 'torpedo_tube_targetAngle', -1, -180, 180, target)
        button_angle_right = Button(arrow_up_img, -90, 0.5, BoundingBox2D(
            Vec2(1680, 1426 + margin * idx) * SCREEN_SCALING_RATIO, Vec2(1680 + btn_size, (1426 + btn_size) + (margin * idx)) * SCREEN_SCALING_RATIO))
        button_angle_right.on_clicked = lambda target: adjust_ship_param(level.playerShip, 'torpedo_tube_targetAngle', 1, -180, 180, target)
        button_speed_up = Button(arrow_up_img, 0, 0.5, BoundingBox2D(
            Vec2(1860, 1426 + margin * idx) * SCREEN_SCALING_RATIO, Vec2(1860 + btn_size, (1426 + btn_size) + (margin * idx)) * SCREEN_SCALING_RATIO))
        button_speed_up.on_clicked = lambda target: adjust_ship_param(level.playerShip, 'torpedo_tube_targetSpeed', 1, 15, 60, target)
        button_speed_down = Button(arrow_up_img, 180, 0.5, BoundingBox2D(
            Vec2(1980, 1440 + margin * idx) * SCREEN_SCALING_RATIO, Vec2(1980 + btn_size, (1426 + btn_size) + (margin * idx)) * SCREEN_SCALING_RATIO))
        button_speed_down.on_clicked = lambda target: adjust_ship_param(level.playerShip, 'torpedo_tube_targetSpeed', -1, 15, 60, target)

        button_fire = Button(button_img, 0, 1, BoundingBox2D(
            Vec2(1750, 1426 + margin * idx) * SCREEN_SCALING_RATIO, Vec2(1750 + btn_size, (1426 + btn_size) + (margin * idx)) * SCREEN_SCALING_RATIO))
        button_fire.on_clicked = lambda target: launch_torpedo(level.playerShip, target)

        torpedo_buttons.append((button_angle_left, button_angle_right, button_speed_up, button_speed_down, button_fire))
        
    return torpedo_buttons

def draw_torpedo_settings(screen, is_mouse_down=False):
    margin = 80
    
    for idx in range(4):
        torpedo_title = gameui_font.render(f'T{idx+1}', False, (25, 25, 25))
        torpedo_current_angle = gameui_font.render(str(level.playerShip.torpedo_tube_targetAngle[idx]), False, (25, 25, 25))
        torpedo_current_speed = gameui_font.render(str(level.playerShip.torpedo_tube_targetSpeed[idx]), False, (25, 25, 25))
        screen.blit(torpedo_title, (Vec2(1464, 1400 + margin * idx) * SCREEN_SCALING_RATIO).to_tuple())
        screen.blit(torpedo_current_angle, (Vec2(1600, 1400 + margin * idx) * SCREEN_SCALING_RATIO).to_tuple())
        screen.blit(torpedo_current_speed, (Vec2(1900, 1400 + margin * idx) * SCREEN_SCALING_RATIO).to_tuple())

    torpedo_buttons = get_torpedo_buttons(4)
    for i, button_set in enumerate(torpedo_buttons):
        for button in button_set:
            button.draw(screen)
            if is_mouse_down and button.check_clicked(pygame.mouse.get_pos()):
                # If the button is clicked, call its on_clicked method
                if hasattr(button, 'on_clicked'):
                    button.on_clicked(i)

def draw_torpedo_screen(screen, is_mouse_down=False):
    text_surface_heading_title = gameui_font.render('Heading', False, (25, 25, 25))
    screen.blit(text_surface_heading_title, (Vec2(1520, 1320) * SCREEN_SCALING_RATIO).to_tuple())
    text_surface_speed_title = gameui_font.render('Speed', False, (25, 25, 25))
    screen.blit(text_surface_speed_title, (Vec2(1860, 1320) * SCREEN_SCALING_RATIO).to_tuple())

    draw_torpedo_settings(screen, is_mouse_down)

def draw_stats(screen):
    """Draw the stats of the player ship on the screen."""
    stats = [
        f"Throttle: {level.playerShip.throttle:.2f}",
        f"Heading: {level.playerShip.heading:.2f}°",
        f"Depth: {level.playerShip.depth}",
    ]
    
    for i, stat in enumerate(stats):
        text_surface = gameui_font_16.render(stat, True, (255, 255, 255))
        screen.blit(text_surface, (img_location_stats.x, img_location_stats.y + i * 15))

def handle_panel_ui(screen, events):
    draw_bg(screen)
    is_mouse_down = pygame.mouse.get_pressed()[0]  # Check if the left mouse button is pressed
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            input_type = check_input(mouse_pos)
            if input_type == InputType.STEER_LEFT:
                wheel.left()
                level.playerShip.steer_target = min(level.playerShip.steer_target+2, level.playerShip.steer_max)
            elif input_type == InputType.STEER_RIGHT:
                wheel.right()
                level.playerShip.steer_target = max(level.playerShip.steer_target-2, -level.playerShip.steer_max)
            elif input_type == InputType.RADAR:
                switch_screen(UIScreen.TOPDOWN)
            elif input_type == InputType.PERISCOPE:
                switch_screen(UIScreen.PERISCOPE)
            elif input_type == InputType.PERISCOPE:
                print("Periscope clicked")
            elif input_type == InputType.THROTTLE_FULL:
                throttler.set(3)
            elif input_type == InputType.THROTTLE_HALF:
                throttler.set(2)
            elif input_type == InputType.THROTTLE_SLOW:
                throttler.set(1)
            elif input_type == InputType.THROTTLE_STOP:
                throttler.set(0)
            elif input_type == InputType.THROTTLE_REV:
                throttler.set(-1)

    draw_wheel(screen)
    draw_throttler(screen)
    draw_torpedo_screen(screen, is_mouse_down)
    draw_stats(screen)

# TODO move these to ship.py or similar
throttle_per_sec = 6  # Base throttle change per second
# How fast the ship throttles up/down when the lever is up/down
def update_ship_throttle(coefficient, target_max_throttle, target_min_throttle=-20):
    # ! Hardcoded 60 FPS, may need to change to delta time.
    currentThrottle = level.playerShip.throttle
    if coefficient > 0:
        # Accelerate towards target_max_throttle, or slow down if above it
        if currentThrottle < target_max_throttle:
            level.playerShip.throttle += coefficient * throttle_per_sec * 1/60
            if level.playerShip.throttle > target_max_throttle:
                level.playerShip.throttle = target_max_throttle
        elif currentThrottle > target_max_throttle:
            # Slow down if above target_max_throttle
            level.playerShip.throttle -= throttle_per_sec * 1.5 * 1/60
            if level.playerShip.throttle < target_max_throttle:
                level.playerShip.throttle = target_max_throttle
        else:
            level.playerShip.throttle = target_max_throttle
    elif coefficient < 0:
        # Decelerate towards target_min_throttle
        if currentThrottle > target_min_throttle:
            level.playerShip.throttle += coefficient * throttle_per_sec * 1/60
            if level.playerShip.throttle < target_min_throttle:
                level.playerShip.throttle = target_min_throttle
        else:
            level.playerShip.throttle = target_min_throttle
    else:
        # Slow down to 0
        if abs(currentThrottle) <= 0.16:
            level.playerShip.throttle = 0
        elif currentThrottle < 0:
            level.playerShip.throttle += throttle_per_sec * 1.5 * 1/60
            if level.playerShip.throttle > 0:
                level.playerShip.throttle = 0
        else:
            level.playerShip.throttle -= throttle_per_sec * 1.5 * 1/60
            if level.playerShip.throttle < 0:
                level.playerShip.throttle = 0

def reset_buttons():
    global torpedo_buttons
    torpedo_buttons = []

def draw_pause_screen(screen):
    screen.fill((0,0,0))
    pause_text = gameui_font_48.render("Game Paused", True, (255, 255, 255))
    pause_rect = pause_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    save_info_text = gameui_font_48.render("Press 's' to save the game", True, (255, 255, 255))
    save_info_rect = save_info_text.get_rect(center=(screen.get_width() // 2, screen.get_height()*2 // 3))
    screen.blit(pause_text, pause_rect)
    screen.blit(save_info_text, save_info_rect)

def draw_ui(screen, events):
    screen.fill((0,0,0))
    global current_screen
    update_ship_throttle(throttler.get_value(), 40 * throttler.get_value())
    #update_ship_steering(wheel.get_value())
    match current_screen:
        case UIScreen.PANEL:
            handle_panel_ui(screen, events)
        case UIScreen.TOPDOWN:
            level.debugDrawLevel(screen)
        case UIScreen.PERISCOPE:
            periscopeui.draw_periscope(screen, events, level.playerShip.periscope_angle, 40, level.playerShip)
    if level.playerShip.alive == False:
        game_over_text = gameui_font_48.render("Your ship has been shot down!", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(game_over_text, game_over_rect)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
    return True
        
        

