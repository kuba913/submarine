import math
import random

# Predefined ship statistics
# 0 - Length, 1 - Width, 2 - Health, 3 - Speed Max, 4 - Speed Min, # 5 - Speed Acceleration, 6 - Speed Deceleration, 7 - Steer Max, 8 - Steer Speed, 9 - Base Visibility
torpedoStat = [5, 1, 100, 25, 1, 5, 1, 15, 15, 500]  # Example stats for torpedo
playerShipStat = [67, 6, 1000, 9, 3, 1, 1, 15, 3, 3000]  # Example stats for player ship
destroyerShipStat = [115, 12, 2500, 10, 6, 1, 1, 10, 2, 8000] # Example stats for destroyer
transportShipStat = [135, 17, 5000, 6, 2, 1, 1, 5, 1, 12000] # Example stats for transport ship
# 0 - Battery Max, 1 - Battery Depletion Rate, 2 - Battery Recharge Rate, 3 - Underwater Speed Multiplier 4 - Torpedo Tube Amount 5 - Torpedo Reload Time
playerSubmarineStat = [1000, 1, 2, 0.5, 4, 60]  # Example stats for player submarine

# Helper functions
def point_in_rect(px: int, py: int, rx: int, ry: int, rw: int, rh: int, rr:int) -> bool:
    """Check if a point (px, py) is inside a rectangle defined by (rx, ry, rw, rh) rotated by rr degrees."""
    # Translate point to rectangle's origin
    translated_x = px - rx
    translated_y = py - ry

    # Rotate point back to axis-aligned coordinates
    angle_rad = math.radians(-rr-90)
    rotated_x = translated_x * math.cos(angle_rad) - translated_y * math.sin(angle_rad)
    rotated_y = translated_x * math.sin(angle_rad) + translated_y * math.cos(angle_rad)

    # Check if the point is within the rectangle bounds
    return -rw/2 <= rotated_x <= rw/2 and -rh/2 <= rotated_y <= rh/2

# Basic entity class
class Entity:
    id: int
    type: str
    name: str

    # Positional attributes (updated every tick)
    x: int
    y: int
    heading: int
    speed: int

    def __init__(self, id: int, type: str, name: str, x: int, y: int, heading: int, speed: int):
        from level import entityList
        self.id = id
        self.type = type
        self.name = name
        self.x = x
        self.y = y
        self.heading = (360 - heading + 90) % 360
        self.speed = speed
        entityList.append(self)

    def tick_update(self):
        # Position
        self.x += self.speed * math.cos(math.radians(self.heading))
        self.y += self.speed * math.sin(math.radians(self.heading))

    def __str__(self):
        return f"{self.type} {self.name} at ({self.x}, {self.y}) heading {(360 - self.heading + 90) % 360}° with speed {self.speed}"

# Base class for all ships
class Ship(Entity):
    # Control attributes
    throttle: int              # How fast the ship is accelerating or decelerating (-100 to 100)
    steer: int                 # How much the ship is turning
    steer_target: int          # Target steer angle the ship is trying to reach

    # Technical attributes (dont change during gameplay)
    length: int
    width: int
    health_max: int                 # Maximum health of the ship
    speed_max: int                  # Maximum speed of the ship
    speed_min: int                  # Maximum speed of the ship reversing (positive value)
    speed_acceleration: int         # How fast the ship can reach its max speed
    speed_deceleration: int         # How fast the ship can slow down
    steer_max: int
    steer_speed: int                # How fast the ship can change its steer angle
    base_visibility: int            # Base visibility of the ship

    # Status attributes
    alive: bool
    health: int                     # Health of the ship, affects its ability to survive damage
    noise: int                      # Noise level of the ship, affects detection by enemies
    visibility: int

    def __init__(self, id: int, type: str, name: str, x: int, y: int, heading: int, shipStat: list[int]):
        super().__init__(id, type, name, x, y, heading, 0)
        # Control attributes
        self.throttle = 0
        self.steer = 0
        self.steer_target = 0

        # Technical attributes
        self.length = shipStat[0]
        self.width = shipStat[1]
        self.health_max = shipStat[2]
        self.speed_max = shipStat[3]
        self.speed_min = shipStat[4]
        self.speed_acceleration = shipStat[5]
        self.speed_deceleration = shipStat[6]
        self.steer_max = shipStat[7]
        self.steer_speed = shipStat[8]
        self.base_visibility = shipStat[9]

        # Status attributes
        self.alive = True
        self.health = self.health_max
        self.noise = 0
        self.visibility = self.base_visibility

    def tick_update(self):
        # Position and heading
        if self.speed >= 0:
            self.x += (self.speed + (self.length * 1/6 * self.speed/self.speed_max)) * math.cos(math.radians(self.heading))
            self.y += (self.speed + (self.length * 1/6 * self.speed/self.speed_max)) * math.sin(math.radians(self.heading))
        else:
            self.x += (self.speed + (self.length * 1/6 * self.speed/self.speed_min)) * math.cos(math.radians(self.heading))
            self.y += (self.speed + (self.length * 1/6 * self.speed/self.speed_min)) * math.sin(math.radians(self.heading))
        
        self.heading = (360 + self.heading + self.steer) % 360

        if self.speed >= 0:
            self.x += -(self.length * 1/6 * self.speed/self.speed_max) * math.cos(math.radians(self.heading))
            self.y += -(self.length * 1/6 * self.speed/self.speed_max) * math.sin(math.radians(self.heading))
        else:
            self.x -= (self.length * 1/6 * self.speed/self.speed_min) * math.cos(math.radians(self.heading))
            self.y -= (self.length * 1/6 * self.speed/self.speed_min) * math.sin(math.radians(self.heading))
            
        # Throttle and speed
        if self.throttle >= 0 and self.speed >= 0:
            if self.throttle > self.speed/self.speed_max * 100:
                self.speed += self.speed_acceleration * (1.5 - self.speed/self.speed_max)
                self.speed = min(self.speed, self.throttle*self.speed_max/100)
            elif self.throttle < self.speed/self.speed_max * 100:
                self.speed -= self.speed_deceleration * (1.5 - self.speed/self.speed_max)
            self.speed = max(self.speed, 0)
        elif self.throttle < 0 and self.speed < 0:
            if self.throttle < self.speed/self.speed_min * 100:
                self.speed -= self.speed_acceleration * (1.5 - self.speed/-self.speed_min)
                self.speed = max(self.speed, self.throttle*self.speed_min/100)
            elif self.throttle > self.speed/self.speed_min * 100:
                self.speed += self.speed_deceleration * (1.5 - self.speed/-self.speed_min)
            self.speed = min(self.speed, 0)

        # Steer and heading
        if self.alive:
            if self.steer_target > self.steer:
                self.steer += self.steer_speed
                self.steer = min(self.steer, self.steer_target)
            elif self.steer_target < self.steer:
                self.steer -= self.steer_speed
                self.steer = max(self.steer, self.steer_target)

        # Visiblity and noise
        self.visibility = self.base_visibility * ((abs(self.speed) / self.speed_max) / 2 + 0.5)
        self.noise = 10 + abs(self.throttle)

        # Health
        if self.alive and self.health <= 0:
            self.alive = False
        if not self.alive:
            self.throttle = 0
    
    def take_damage(self, damage: int):
        self.health -= damage
        self.health = max(self.health, 0)
        
        if self.health <= 0:
            self.alive = False
            self.throttle = 0

# Class for the torpedoes fired by the player
class torpedo(Ship):
    # Technical attributes (dont change during gameplay)
    damage: int                     # Damage dealt by the torpedo when it hits a target

    # Control attributes
    targetAngle: int                # Angle towards which the torpedo is heading
    targetSpeed: int                # Speed at which the torpedo is moving

    # Status attributes
    timeSinceShot: int              # Ticks since the torpedo has been shot

    # Custom init
    def __init__(self, id: int, x: int, y: int, heading: int, targetAngle: int, targetSpeed: int):
        type = "torpedo"
        name = "G7e Torpedo"

        super().__init__(id, type, name, x, y, heading, torpedoStat)

        self.damage = 5000

        self.timeSinceShot = 0

    # init for torpedo fired by the player ship
    def __init__(self, id: int, targetAngle: int, targetSpeed: int, parentShip: Ship):
        type = "torpedo"
        name = "G7e Torpedo"
        heading = (360 - parentShip.heading + 90) % 360
        torpX = parentShip.x + parentShip.length * math.cos(math.radians(parentShip.heading))
        torpY = parentShip.y + parentShip.length * math.sin(math.radians(parentShip.heading))

        super().__init__(id, type, name, torpX, torpY, heading, torpedoStat)

        self.targetAngle = targetAngle
        self.targetSpeed = targetSpeed

        self.speed = parentShip.speed
        self.throttle = (self.targetSpeed/self.speed_max) * 100
        self.damage = 5000

        self.timeSinceShot = 0

    def destroy(self):
        from level import entityList
        entityList.remove(self)

    def check_attack(self):
        from level import entityList
        for entity in entityList:
            if entity != self and math.sqrt((entity.x - self.y)**2 + (entity.y - self.y)**2) < 500:
                for i in range(-round(self.speed)+math.floor(self.length/2),math.ceil(self.length/2)):
                    if(point_in_rect(self.x + i*math.cos(math.radians(self.heading)), self.y + i*math.sin(math.radians(self.heading)), entity.x, entity.y, entity.width, entity.length, entity.heading)):
                        entity.take_damage(self.damage)
                        self.destroy()
                        return

    def tick_update(self):
        self.timeSinceShot += 1
        if self.timeSinceShot >= 180:
            self.destroy()
            return
        if self.targetAngle - self.heading < -180 or self.targetAngle - self.heading > 180:
            if self.targetAngle - self.heading < -180:
                self.steer_target = ((self.targetAngle + 360) - self.heading)
            else:
                self.steer_target = ((self.targetAngle - 360) - self.heading)
        else:
            self.steer_target = (self.targetAngle - self.heading)
        if abs(self.steer_target) <= self.steer_max and self.steer != 0: # Temp fix
            self.steer_target = 0
        if self.steer_target > self.steer_max:
            self.steer_target = self.steer_max
        elif self.steer_target < -self.steer_max:
            self.steer_target = -self.steer_max
        super().tick_update()
        self.check_attack()

# Class for the player-controlled ship
class playerShip(Ship):
    # Control attributes
    periscope_angle: int            # Angle of the periscope, used for visual detection

    # Technical attributes (dont change during gameplay)
    battery_max: int                # Maximum battery level of the player ship
    battery_depletion_rate: int     # Rate at which the battery depletes, affects submerging and speed
    battery_recharge_rate: int      # Rate at which the battery recharges when surfaced
    underwater_speed_mult: float      # Multiplier for speed when underwater, affects how fast the player ship can move when submerged

    # Status attributes
    depth: str                      # Current depth of the player ship, affects visibility, noise and functionality, e.g., "surface", "periscope", "deep"
    battery: int                    # Battery level of the player ship, required for submerging
    periscope_active: bool          # Whether the periscope is currently active, affects visibility

    # Combat attributes
    torpedo_tubes: int              # The number of torpedo tubes to fire at once
    torpedo_time_reload: int        # Time it takes to reload the torpedoes
    torpedo_tube_lastFired: list[int]     # Time since the last torpedo was fired
    torpedo_tube_targetAngle: list[int]   # Angle the torpedo from this tube will be turn towards
    torpedo_tube_targetSpeed: list[int]   # Speed the torpedo from this tube will accelerate towards

    def __init__(self, id: int, x: int, y: int, heading: int):
        type = "playerShip"
        name = "U-Boat Type VII"

        super().__init__(id, type, name, x, y, heading, playerShipStat)

        # Control attributes
        self.periscope_angle = heading # Periscope angle starts at the ship's heading

        # Technical attributes
        self.battery_max = playerSubmarineStat[0]
        self.battery_depletion_rate = playerSubmarineStat[1]
        self.battery_recharge_rate = playerSubmarineStat[2]
        self.underwater_speed_mult = playerSubmarineStat[3]

        # Status attributes
        self.depth = "surface"
        self.battery = self.battery_max
        self.periscope_active = False

        # Torpedo
        self.torpedo_tubes = playerSubmarineStat[4]
        self.torpedo_time_reload = playerSubmarineStat[5]
        self.torpedo_tube_lastFired = [0] * self.torpedo_tubes
        self.torpedo_tube_targetAngle = [0] * self.torpedo_tubes
        self.torpedo_tube_targetSpeed = [torpedoStat[3]] * self.torpedo_tubes

    def tick_update(self):
        # Speed
        temp_speed = self.speed_max
        if self.depth != "surface":
            self.speed_max = self.speed_max * self.underwater_speed_mult

        # Battery
        if self.depth == "periscope" or self.depth == "deep":
            self.battery -= self.battery_depletion_rate
        elif self.depth == "surface":
            self.battery += self.battery_recharge_rate
        self.battery = max(0, min(self.battery, self.battery_max))
        if self.battery <= 0:
            self.depth = "surface"
            self.periscope_active = False

        super().tick_update()

        # Visiblity and noise
        match self.depth:
            case "surface":
                self.visibility = self.base_visibility * ((abs(self.speed) / self.speed_max) / 2 + 0.5)
            case "periscope":
                if self.periscope_active:
                    self.visibility = self.base_visibility * ((abs(self.speed) / self.speed_max) / 2 + 0.5) * 0.2
                else:
                    self.visibility = self.base_visibility * ((abs(self.speed) / self.speed_max) / 2 + 0.5) * 0.01
            case "deep":
                self.visibility = 0
                self.noise = self.noise * 0.5  # Reduced noise when deep

        # Torpedo
        for tube_lastFired in self.torpedo_tube_lastFired:
            if tube_lastFired > 0:
                tube_lastFired -= 1

        # Speed
        self.speed_max = temp_speed
    
    def attack_torpedo(self, tube: int):
        from level import entityList
        if self.torpedo_tube_lastFired[tube] > 0:
            return
        torpedo(len(entityList), self.torpedo_tube_targetAngle[tube], self.torpedo_tube_targetSpeed[tube], self)
        self.torpedo_tube_lastFired[tube] = self.torpedo_time_reload  # Reset the reload time

# Base class for enemy ships
class enemyShip(Ship):
    # AI attributes
    ai_behaviour: str               # e.g., "careless", "safe", "aware", "combat"
    ai_combatMode: str              # e.g., "aggressive", "defensive", "evasive"
    visual_range: int               # Range at which the enemy can visually detect the player ship
    visual_skill: int               # Skill level of the enemy in visually detecting the player ship
    noise_range: int                # Range at which the enemy can detect the player ship based on noise
    noise_skill: int                # Skill level of the enemy in detecting the player ship based on noise

    # Technical attributes (dont change during gameplay)
    radio_range: int                # Range at which the enemy can share information with other enemy ships
    radio_skill: int                # Skill level of the enemy in sharing information with other enemy ships (accuracy and speed of information sharing)

    # Target attributes
        # Default navigation target
    objectivePosition: tuple[int, int]  # Final target position the enemy ship is trying to reach
        # Offensive
    spottedPlayer: bool             # Whether the enemy ship has spotted the player ship
    spottingAccuracy: int           # Accuracy of information about the player
    lastKnownPosition: tuple[int, int]  # Last known position of the player ship
    lastKnownTime: int              # Last time the enemy ship spotted the player ship
    lastKnownHeading: int           # Last known heading of the player ship
    lastKnownSpeed: int             # Last known speed of the player ship
        # Defensive
    spottedTorpedoes: list[torpedo] # List of torpedoes spotted by the enemy ship

# Class for depth charges used by enemy ships
class preDepthCharge:
    x: int                          # X offset of the depth charge from the ship
    y: int                          # Y offset of the depth charge from the ship
    target: Ship                    # Target ship the depth charge is aimed at
    time: int                       # Time until the depth charge is dropped

    def __init__(self, x: int, y: int, target: Ship, time: int):
        self.x = x
        self.y = y
        self.target = target
        self.time = time

    def tick_update(self):
        if self.time > 0:
            self.time -= 1

# Class for depth charges used by enemy ships
class depthCharge:
    x: int                          # X position of the depth charge
    y: int                          # Y position of the depth charge
    target: Ship                    # Target ship the depth charge is aimed at
    explosion_time: int             # Time until the depth charge explodes
    damage: int                     # Damage dealt by the depth charge
    splash_radius: int              # Splash radius of the depth charge explosion

    def __init__(self, x: int = 0, y: int = 0, target: Ship = None, explosion_time: int = 0, damage: int = 0, splash_radius: int = 0):
        self.x = x
        self.y = y
        self.target = target
        self.explosion_time = explosion_time
        self.damage = damage
        self.splash_radius = splash_radius

    def tick_update(self):
        if self.explosion_time > 0:
            self.explosion_time -= 1
        else:
            # Explode and deal damage to the target ship
            if self.target:
                distance = math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2)
                if distance <= self.splash_radius:
                    self.target.take_damage(self.damage)

# Enemy ship capable of combat
class destroyer(enemyShip):
    # Combat attributes
        # Gun
    has_gun: bool                   # Whether the destroyer has a gun
    gun_range: int               # Range of the destroyer's weapons
    gun_damage: int              # Damage dealt by the destroyer's weapons
    gun_time_reload: int         # Time it takes to reload the destroyer's weapons
    gun_accuracy: int            # Accuracy of the destroyer's weapons
        # Depth charge
    has_depthCharge: bool          # Whether the destroyer has depth charges
    depthCharge_splash_radius: int # Splash radius of the destroyer's depth charges
    depthCharge_damage: int        # Damage dealt by the destroyer's depth charges
    depthCharge_time_reload: int   # Time it takes to reload the destroyer's depth charges
    depthCharge_burst_amount: int  # Number of depth charges in a burst
    depthCharge_burst_interval: int # Time between depth charges in a burst
    depthCharge_pattern: str       # Pattern of the depth charge attack, e.g., "behind", "sides", "all"
    depthCharge_pattern_size: int  # Distance from ship the charges are dropped
    depthCharge_explosion_time: int # Time it takes for the depth charge to explode after being dropped
        # Hedgehog
    has_hedgehog: bool              # Whether the destroyer has a hedgehog weapon
    hedgehog_range: int             # Range of the hedgehog weapon
    hedgehog_damage: int            # Damage dealt by the hedgehog weapon
    hedgehog_time_reload: int       # Time it takes to reload the hedgehog weapon
    hedgehog_burst_amount: int      # Number of hedgehog projectiles in a burst
    hedgehog_pattern_size: int      # Diameter of the attack pattern

    # Status attributes
    gun_time_lastFired: int      # Time when the last shot was fired
    depthCharge_time_lastDropped: int # Time when the last depth charge was dropped
    depthCharge_stack_dropping: list[preDepthCharge]  # List of depth charges left to drop
    depthCharge_stack_dropped: list[depthCharge]  # List of depth charges that have been dropped
    hedgehog_time_lastFired: int    # Time when the last hedgehog was fired

    def __init__(self, id: int, x: int, y: int, heading: int, destroyerWeaponStat: list[list[int]]):
        type = "destroyer"
        name = "Fletcher-class"

        super().__init__(id, type, name, x, y, heading, destroyerShipStat)

        # Predefined attributes
        self.gun_time_lastFired = 0
        self.depthCharge_time_lastDropped = 0
        self.hedgehog_time_lastFired = 0

        self.depthCharge_stack_dropping = []
        self.depthCharge_stack_dropped = []

        # Imported attributes
            # Gun
        self.has_gun = len(destroyerWeaponStat[0]) == 4
        self.gun_range = destroyerWeaponStat[0][0]
        self.gun_damage = destroyerWeaponStat[0][1]
        self.gun_time_reload = destroyerWeaponStat[0][2]
        self.gun_accuracy = destroyerWeaponStat[0][3]
            # Depth charge
        self.has_depthCharge =len(destroyerWeaponStat[1]) == 8
        self.depthCharge_splash_radius = destroyerWeaponStat[1][0]
        self.depthCharge_damage = destroyerWeaponStat[1][1]
        self.depthCharge_time_reload = destroyerWeaponStat[1][2]
        self.depthCharge_burst_amount = destroyerWeaponStat[1][3]
        self.depthCharge_burst_interval = destroyerWeaponStat[1][4]
        self.depthCharge_pattern = destroyerWeaponStat[1][5]
        self.depthCharge_pattern_size = destroyerWeaponStat[1][6]
        self.depthCharge_explosion_time = destroyerWeaponStat[1][7]
            # Hedgehog
        self.has_hedgehog = len(destroyerWeaponStat[2]) == 5
        self.hedgehog_range = destroyerWeaponStat[2][0]
        self.hedgehog_damage = destroyerWeaponStat[2][1]
        self.hedgehog_time_reload = destroyerWeaponStat[2][2]
        self.hedgehog_burst_amount = destroyerWeaponStat[2][3]
        self.hedgehog_pattern_size = destroyerWeaponStat[2][4]

    def tick_update(self):
        from level import get_player 
        super().tick_update()

        # Gun
        if self.has_gun and self.gun_time_lastFired > 0:
            self.gun_time_lastFired -= 1

        # Depth charge
        if self.has_depthCharge and self.depthCharge_time_lastDropped > 0:
            self.depthCharge_time_lastDropped -= 1
        
        if len(self.depthCharge_stack_dropping) > 0:
            for preCharge in self.depthCharge_stack_dropping:
                preCharge.tick_update()
                if preCharge.time <= 0:
                    self.stack_drop_depthCharge(preCharge)
                    self.depthCharge_stack_dropping.remove(preCharge)

        if len(self.depthCharge_stack_dropped) > 0:
            for charge in self.depthCharge_stack_dropped:
                charge.tick_update()
                if charge.explosion_time <= 0:
                    self.depthCharge_stack_dropped.remove(charge)

        # Hedgehog
        if self.has_hedgehog and self.hedgehog_time_lastFired > 0:
            self.hedgehog_time_lastFired -= 1

        # Player check needed for ai_combat_behavior method.
        player = get_player()
        if player and player.alive:
            self.ai_combat_behavior(player)    

    def ai_combat_behavior(self, player: Ship):
        # Step 1: Calculate direction to player
        dx = player.x - self.x
        dy = player.y - self.y
        target_angle = math.degrees(math.atan2(dy, dx)) % 360  # [0, 360)
        # Step 2: Adjust heading
        angle_diff = (target_angle - self.heading + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360  # Normalize to [-180, 180]
        if abs(angle_diff) > self.steer_speed:
            self.steer_target = max(-self.steer_max, min(self.steer_max, angle_diff))
        # Step 3: Move forward
        self.throttle = 100  # Max throttle to charge
        # Step 4: Attack if in range and ready
        if self.has_gun and self.gun_time_lastFired <= 0:
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance <= self.gun_range:
                self.attack_gun(player)

    # Gun functions
    def attack_gun(self, target: Ship):
        if not self.has_gun:
            return
        # Calculate distance to target
        distance = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        if distance <= self.gun_range:
            # Calculate hit chance based on accuracy and distance
            if ((2 - distance / self.gun_range) * self.gun_accuracy) > random.randint(0, 100):
                # Hit the target
                target.take_damage(self.gun_damage)
            '''play sound?'''
        self.gun_time_lastFired = self.gun_time_reload  # Reset the reload time

    # Depth charge functions
    def attack_depth_charge(self, target: Ship):
        if not self.has_depthCharge:
            return
        match self.depthCharge_pattern:
            case "behind": # Drop depth charges behind the ships
                for i in range(self.depthCharge_burst_amount):
                    self.stack_add_depthCharge(0, -self.length/2 - self.depthCharge_pattern_size, i * self.depthCharge_burst_interval, target)
            case "sides": # Drop depth charges on both sides of the ship
                for i in range(self.depthCharge_burst_amount):
                    self.stack_add_depthCharge(-self.width/2 - self.depthCharge_pattern_size, 0, i * self.depthCharge_burst_interval, target)
                    self.stack_add_depthCharge(self.width/2 + self.depthCharge_pattern_size, 0, i * self.depthCharge_burst_interval, target)
            case "all": # Drop depth charges behind and both sides of the ship
                for i in range(self.depthCharge_burst_amount):
                    self.stack_add_depthCharge(0, -self.length/2 - self.depthCharge_pattern_size, i * self.depthCharge_burst_interval, target)
                    self.stack_add_depthCharge(-self.width/2 - self.depthCharge_pattern_size, 0, i * self.depthCharge_burst_interval, target)
                    self.stack_add_depthCharge(self.width/2 + self.depthCharge_pattern_size, 0, i * self.depthCharge_burst_interval, target)
        self.depthCharge_time_lastDropped = self.depthCharge_time_reload  # Reset the reload time

    def stack_add_depthCharge(self, xOff, yOff, delay, target: Ship):
        new_charge = preDepthCharge(x=xOff, y=yOff, target=target, time=delay)
        self.depthCharge_stack_dropping.append(new_charge)

    def stack_drop_depthCharge(self, preDepthCharge: preDepthCharge):
        offDis = math.sqrt(preDepthCharge.x ** 2 + preDepthCharge.y ** 2)
        offAngle = math.degrees(math.atan2(preDepthCharge.y, preDepthCharge.x))
        xOffset = self.x + offDis * math.cos(math.radians(self.heading) + offAngle)
        yOffset = self.y + offDis * math.sin(math.radians(self.heading) + offAngle)
        new_charge = depthCharge(xOffset, yOffset, preDepthCharge.target, self.depthCharge_explosion_time, self.depthCharge_damage, self.depthCharge_splash_radius)
        self.depthCharge_stack_dropped.append(new_charge)

    # Hedgehog functions
    def attack_hedgehog(self, target: Ship):
        if not self.has_hedgehog:
            return
        offMainDis = math.sqrt(0 ** 2 + (self.length/2) ** 2) + self.hedgehog_range
        xOffset = self.x + offMainDis * math.cos(math.radians(self.heading))
        yOffset = self.y + offMainDis * math.sin(math.radians(self.heading))
        offAngle = 360 / self.hedgehog_burst_amount
        for i in range(self.hedgehog_burst_amount):
            offSecDis = self.hedgehog_pattern_size/2
            xOffsetSec = xOffset + offSecDis * math.cos(math.radians(self.heading + offAngle * i))
            yOffsetSec = yOffset + offSecDis * math.sin(math.radians(self.heading + offAngle * i))
            if point_in_rect(xOffsetSec, yOffsetSec, target.x, target.y, target.width, target.length, target.heading):
                target.take_damage(self.hedgehog_damage)
        self.hedgehog_time_lastFired = self.hedgehog_time_reload  # Reset the reload time
        

# Enemy ship incapable of combat, objective for player to destroy
class transport(enemyShip):
    # Cargo attributes (???)
    cargo_type: str                 # Type of cargo the transport is carrying
    cargo_amount: int               # Amount of cargo the transport is carrying
    cargo_value: int                # Value of the cargo, affects score when destroyed

    def __init__(self, id: int, x: int, y: int, heading: int, cargoType: str, cargoAmount: int, cargoValue: int):
        type = "transport"
        name = "Liberty ship"

        super().__init__(id, type, name, x, y, heading, transportShipStat)

        # Cargo attributes
        self.cargo_type = cargoType
        self.cargo_amount = cargoAmount
        self.cargo_value = cargoValue