import math


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
        self.id = id
        self.type = type
        self.name = name
        self.x = x
        self.y = y
        self.heading = (360 - heading + 90) % 360
        self.speed = speed

    def tick_update(self):
        # Position
        self.x += self.speed * math.cos(math.radians(self.heading))
        self.y += self.speed * math.sin(math.radians(self.heading))

    def __str__(self):
        return f"{self.type} {self.name} at ({self.x}, {self.y}) heading {self.heading - 90}° with speed {self.speed}"

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
    speed_max: int
    speed_min: int
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

    def tick_update(self):
        # Position and heading
        if self.speed >= 0:
            self.x += (self.speed + (self.length * 1/6 * self.speed/self.speed_max)) * math.cos(math.radians(self.heading))
            self.y += (self.speed + (self.length * 1/6 * self.speed/self.speed_max)) * math.sin(math.radians(self.heading))
        else:
            self.x += (self.speed - (self.length * 1/6 * self.speed/self.speed_min)) * math.cos(math.radians(self.heading))
            self.y += (self.speed - (self.length * 1/6 * self.speed/self.speed_min)) * math.sin(math.radians(self.heading))
        
        self.heading = (360 + self.heading + self.steer) % 360

        if self.speed >= 0:
            self.x += -(self.length * 1/6 * self.speed/self.speed_max) * math.cos(math.radians(self.heading))
            self.y += -(self.length * 1/6 * self.speed/self.speed_max) * math.sin(math.radians(self.heading))
        else:
            self.x += (self.length * 1/6 * self.speed/self.speed_min) * math.cos(math.radians(self.heading))
            self.y += (self.length * 1/6 * self.speed/self.speed_min) * math.sin(math.radians(self.heading))
            
        # Throttle and speed
        if self.throttle > 0:
            if self.throttle > self.speed/self.speed_max * 100:
                self.speed += self.speed_acceleration * (1.5 - self.speed/self.speed_max)
            elif self.throttle < self.speed/self.speed_min * 100:
                self.speed += self.speed_deceleration * (1.5 - self.speed/self.speed_min)
        elif self.throttle < 0:
            if self.throttle < self.speed/self.speed_min * 100:
                self.speed -= self.speed_deceleration * (1.5 - self.speed/self.speed_min)
            elif self.throttle > self.speed/self.speed_max * 100:
                self.speed -= self.speed_acceleration * (1.5 - self.speed/self.speed_max)

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

        super().tick_update(self)

        # Periscope# Visiblity and noise
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

        # Speed
        self.speed_max = temp_speed

# Class for the torpedoes fired by the player
class torpedo(Ship):
    # Technical attributes (dont change during gameplay)
    damage: int                     # Damage dealt by the torpedo when it hits a target

    # Control attributes
    targetAngle: int                # Angle towards which the torpedo is heading
    targetSpeed: int                # Speed at which the torpedo is moving

    def tick_update(self):
        if self.targetAngle - self.heading < -180 or self.targetAngle - self.heading > 180:
            if self.targetAngle - self.heading < -180:
                self.steer_target = ((self.targetAngle + 360) - self.heading)
            else:
                self.steer_target = ((self.targetAngle - 360) - self.heading)
        else:
            self.steer_target = (self.targetAngle - self.heading)
        if self.steer_target > self.steer_max:
            self.steer_target = self.steer_max
        elif self.steer_target < -self.steer_max:
            self.steer_target = -self.steer_max
        super().tick_update(self)

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

# Enemy ship capable of combat
class destroyer(enemyShip):
    # Combat attributes
        # Gun
    has_gun: bool                   # Whether the destroyer has a gun
    weapon_range: int               # Range of the destroyer's weapons
    weapon_damage: int              # Damage dealt by the destroyer's weapons
    weapon_reload_time: int         # Time it takes to reload the destroyer's weapons
    weapon_accuracy: int            # Accuracy of the destroyer's weapons
        # Depth charge
    has_depthCharge: bool          # Whether the destroyer has depth charges
    depthCharge_splash_radius: int # Splash radius of the destroyer's depth charges
    depthCharge_damage: int        # Damage dealt by the destroyer's depth charges
    depthCharge_reload_time: int   # Time it takes to reload the destroyer's depth charges
    depthCharge_burst_amount: int  # Number of depth charges in a burst
    depthCharge_burst_interval: int # Time between depth charges in a burst
    depthCharge_pattern: str       # Pattern of the depth charge attack, e.g., "behind", "sides", "all"
    depthCharge_pattern_size: int  # Distance from ship the charges are dropped
    depthCharge_explosion_time: int # Time it takes for the depth charge to explode after being dropped
        # Hedgehog
    has_hedgehog: bool              # Whether the destroyer has a hedgehog weapon
    hedgehog_range: int             # Range of the hedgehog weapon
    hedgehog_damage: int            # Damage dealt by the hedgehog weapon
    hedgehog_reload_time: int       # Time it takes to reload the hedgehog weapon
    hedgehog_burst_amount: int      # Number of hedgehog projectiles in a burst
    hedgehog_burst_interval: int    # Time between hedgehog projectiles in a burst
    hedgehog_pattern_size: int      # Diameter of the attack pattern

# Enemy ship incapable of combat, objective for player to destroy
class transport(enemyShip):
    # Cargo attributes (???)
    cargo_type: str                 # Type of cargo the transport is carrying
    cargo_amount: int               # Amount of cargo the transport is carrying
    cargo_value: int                # Value of the cargo, affects score when destroyed