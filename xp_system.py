import math


class XPSystem:
    """Track XP and derive the player's level from it.

    This is the only place XP and level are stored. Other classes read
    xp_system.level instead of keeping their own copy, which prevents the
    desync bug where a reset did not reach the ship.
    """

    # Level 2 starts at 100 XP. Each later level needs GROWTH times more total XP
    # than the last, so early levels come quickly and later ones take longer.
    BASE_XP = 100
    GROWTH = 1.5

    def __init__(self, xp=0):
        self.xp = xp
        self.level = self.xp_to_level(xp)

    def xp_to_level(self, xp):
        """Convert a total XP amount to a level."""
        if xp < self.BASE_XP:
            return 1
        return int(math.log(xp / self.BASE_XP, self.GROWTH)) + 2

    def add_xp(self, amount):
        """Add XP and update the level."""
        self.xp += amount
        self.level = self.xp_to_level(self.xp)
