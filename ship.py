from pathlib import Path

import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """Manage the player's ship: movement, drawing, and damage."""

    def __init__(self, ai_game):
        """Initialize the ship and place it at the bottom center of the screen."""
        super().__init__()
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Path(__file__) makes the image load work no matter which folder the game runs from.
        image_path = Path(__file__).parent / "images" / "ship.bmp"
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom

        # Store a float for exact position. Rect stores integers and would drop fractions.
        self.x = float(self.rect.x)

        self.moving_right = False
        self.moving_left = False

    @property
    def damage(self):
        """Damage per bullet. Computed from the player's level, so it can't drift out of sync."""
        # Each level above 1 adds 0.5 damage.
        return self.settings.base_damage + 0.5 * (self.ai_game.stats.xp_system.level - 1)

    def center_ship(self):
        """Move the ship back to the bottom center of the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        """Move the ship based on the movement flags."""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # Sync the integer rect from the float position after moving.
        self.rect.x = self.x

    def blitme(self):
        """Draw the ship at its current position."""
        self.screen.blit(self.image, self.rect)
