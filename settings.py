class Settings:
    """Store all static and dynamic settings for Alien Invasion.

    Static values are set once here. Values that change during play live in
    initialize_dynamic_settings() so a new game can reset them in one call.
    """

    def __init__(self):
        # Screen
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Ship. Damage is derived from player level in Ship.damage, so only the base is stored.
        self.ship_limit = 3
        self.base_damage = 1

        # Bullets
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3

        # Aliens. Health and XP reward scale with player level, so the game
        # gets harder and more rewarding at the same rate.
        self.fleet_drop_speed = 10
        self.base_alien_health = 1
        self.alien_health_scale = 1.3
        self.base_xp_drop = 10
        self.xp_scale = 1.5

        # Difficulty growth applied each time a fleet is cleared
        self.speedup_scale = 1.1
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Reset settings that change during a game. Called at the start of each game."""
        self.ship_speed = 1.5
        self.bullet_speed = 2.5
        self.alien_speed = 1.0

        # fleet_direction of 1 is right, -1 is left.
        self.fleet_direction = 1

        self.alien_points = 50

    def increase_speed(self):
        """Speed up movement and raise point values after each cleared fleet."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
