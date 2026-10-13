"""
Welcome to the API Documentation!

You probably want to get started with `API` methods, and have a look at `Result`.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from enum import Enum
from typing import Literal


class API:
    """
    The main access point for your bot. Access this using `self.context` inside your `run` method.

    Each action method returns `Result`, which is `Result.OK` if it succeeded, or another value explaining why it failed.
    """

    def __init__(self) -> None:
        pass

    ### GENERAL GAME METHODS ###

    def get_mode(self) -> GameMode:
        """Returns the current game mode."""
        raise NotImplementedError("GetMode")

    def get_player_count(self) -> int:
        """Returns the amount of players in the player list."""
        raise NotImplementedError("GetPlayerCount")

    def get_current_steps(self) -> int:
        """
        Returns the elapsed time of the game in steps.
        There are 60 steps in every second.
        """
        raise NotImplementedError("GetCurrentSteps")

    def get_current_time(self) -> float:
        """
        Returns the elapsed time of the game in seconds.
        If the time is a precise second, it returns an int instead.
        """
        raise NotImplementedError("GetCurrentTime")

    def get_map(self) -> Maps:
        """Returns the map of the current game."""
        raise NotImplementedError("GetMap")

    def get_track_width(self) -> float:
        """
        Returns the width (in map pixels) of the bloon track.
        A monkey's center must be at least its radius plus half the track width away from the bloon route (and the eco bloon route).
        """
        raise NotImplementedError("GetTrackWidth")

    def get_bloon_route(self) -> list[LineInfo]:
        """Returns the map's bloon route."""
        raise NotImplementedError("GetBloonRoute")

    def get_eco_bloon_route(self) -> list[LineInfo]:
        """Returns the map's eco bloon route."""
        raise NotImplementedError("GetEcoBloonRoute")

    def get_round_times(self) -> list[int]:
        """Returns a list of the round start times in game steps."""
        raise NotImplementedError("GetRoundTimes")

    def get_bloon_spawns(self) -> dict[int, Bloons]:
        """Returns a map from game steps to a bloon that is created in that step."""
        raise NotImplementedError("GetBloonSpawns")

    def get_banned_monkeys(self) -> list[Monkeys]:
        """
        Returns the banned monkeys of the game.
        Bans are decided at the end of the first step, so that no bot knows what the others banned while banning.
        Until then (in `ArazimWarsBot.setup` and in the first call to `ArazimWarsBot.run`), returns an empty list.
        """
        raise NotImplementedError("GetBannedMonkeys")

    ### CURRENT PLAYER METHODS ###

    def get_current_player_index(self) -> int:
        """
        Returns the index of the current player in the player list.

        Every player sees the players in its own random order, fixed for the whole game,
        so player indices passed to and returned from the API are in that order.
        """
        raise NotImplementedError("GetCurrentPlayerIndex")

    def get_money(self) -> int:
        """Returns the current amount of money the player possesses."""
        raise NotImplementedError("GetMoney")

    def get_eco(self) -> float:
        """
        Returns the current eco the player has.
        This is added to the player's money pool every 6 seconds.
        """
        raise NotImplementedError("GetEco")

    def get_eco_queue_size(self) -> int:
        """
        Returns the current filled size of the player's eco queue.
        If this is five, it means you cannot send more eco bloons now.
        """
        raise NotImplementedError("GetEcoQueueSize")

    def get_bloons(self) -> list[BloonInfo]:
        """Returns the current bloons in the player's map."""
        raise NotImplementedError("GetBloons")

    def get_monkey_cooldown(self, monkey_index: int) -> float:
        """
        Returns the current cooldown of the given monkey in seconds.
        During this time, the monkey will not be able to attack!
        If the `monkey_index` is invalid, returns -1.
        """
        raise NotImplementedError("GetMonkeyCooldown")

    def get_monkey_targets(self, monkey_index: int) -> list[BloonInfo]:
        """
        Returns the bloons the specified monkey can see.
        If the `monkey_index` is invalid, returns an empty list.
        """
        raise NotImplementedError("GetMonkeyTargets")

    def place_monkey(self, kind: Monkeys, position: tuple[float, float]) -> Result:
        """
        Places a monkey with the given type in the given (x,y) position on the player's board.
        Returns whether the operation was successful.
        Monkeys can't be placed in the first step (in `ArazimWarsBot.setup` and in the first call to `ArazimWarsBot.run`), before the bans are decided.

        Possible results: `Result.NOT_ENOUGH_MONEY`, `Result.OUT_OF_MAP`, `Result.TOO_CLOSE_TO_BLOON_ROUTE`, `Result.TOO_CLOSE_TO_OTHER_MONKEY`, `Result.INVALID_TIME`, `Result.MONKEY_BANNED`.
        """
        raise NotImplementedError("PlaceMonkey")

    def target_bloon(self, monkey_index: int, bloon_index: int) -> Result:
        """
        Sets the specified bloon as the target for the specified monkey.
        Returns whether the operation was successful.

        Possible results: `Result.INVALID_MONKEY_INDEX`, `Result.INVALID_BLOON_INDEX`, `Result.MONKEY_CANT_SEE`.
        """
        raise NotImplementedError("TargetBloon")

    def upgrade_monkey(self, monkey_index: int, top_row: bool) -> Result:
        """
        Upgrades the specified monkey in the specified row.
        For more information, see the monkeys and upgrades section of the manual.
        Returns whether the operation was successful.

        Possible results: `Result.INVALID_MONKEY_INDEX`, `Result.OTHER_ROW_CHOSEN`, `Result.NOT_ENOUGH_MONEY`, `Result.ALREADY_MAXED_OUT`.
        """
        raise NotImplementedError("UpgradeMonkey")

    def sell_monkey(self, monkey_index: int) -> Result:
        """
        Sells the specified monkey for 70% of its cost (including upgrade costs), rounded down.
        Returns whether the operation was successful.

        Possible results: `Result.INVALID_MONKEY_INDEX`.
        """
        raise NotImplementedError("SellMonkey")

    def send_bloons(
        self,
        player_index: int,
        bloon: EcoBloons,
        is_camo: bool = False,
        is_regen: bool = False,
    ) -> Result:
        """
        Sends the given eco bloons to the specified player.
        Keep in mind that you only have a queue of 5 eco bloons to send out.

        If `is_camo` is specified, the sent bloons will be camo. Note this requires the current round to be at least 8.
        This multiplies the cost by 1.8, rounded down.

        If `is_regen` is specified, the sent bloons will be regen. Note this requires the current round to be at least 12.
        This multiplies the cost by 2.2, rounded down.

        Returns whether the operation was successful.

        Possible results: `Result.ECO_QUEUE_FULL`, `Result.INVALID_BLOON`, `Result.INVALID_MODE`, `Result.INVALID_PLAYER`, `Result.NOT_ENOUGH_MONEY`, `Result.TOO_EARLY`.
        """
        raise NotImplementedError("SendBloons")

    def display_emote(self, emote: Emote) -> Literal[Result.OK]:
        """
        Display the given emote!
        Use `Emote.NONE` to clear the emote.
        """
        raise NotImplementedError("SetEmote")

    def ban_monkey(self, monkey: Monkeys) -> Result:
        """
        Select a monkey to ban for this game.
        You can only call this method **once**, and **only** in the beginning of the game (in `ArazimWarsBot.setup` or in the first call to `ArazimWarsBot.run`).

        In games with 2 players, every monkey a player bans is banned.
        In games with more players, the bans are a vote, and the monkeys with the most votes are banned.

        Possible results: `Result.INVALID_TIME`, `Result.CANT_BAN_TWICE`.
        """
        raise NotImplementedError("BanMonkey")

    def tower_boost(self) -> Result:
        """
        Boost your monkeys' attack speed by 80% for 12 seconds.
        You have three tower boosts for the whole game.

        Possible results: `Result.NOT_ENOUGH_BOOSTS`.
        """
        raise NotImplementedError("TowerBoost")

    def bloon_boost(self) -> Result:
        """
        Speed up sending your eco bloons by 20% for 12 seconds.
        You have three bloon boosts for the whole game.

        Possible results: `Result.NOT_ENOUGH_BOOSTS`.
        """
        raise NotImplementedError("BloonBoost")

    ### OTHER PLAYER INFORMATION ###

    def is_player_active(self, player_index: int) -> bool:
        """
        Returns whether the player is alive (active).
        If the `player_index` is invalid, returns False.
        """
        raise NotImplementedError("IsPlayerActive")

    def get_player_health(self, player_index: int) -> int:
        """
        Returns the current health of the given player.
        If the `player_index` is invalid, returns 0.
        """
        raise NotImplementedError("GetPlayerHealth")

    def get_player_monkeys(self, player_index: int) -> list[MonkeyInfo]:
        """
        Returns the current monkeys in the given player's map.
        If the `player_index` is invalid, returns an empty list.
        """
        raise NotImplementedError("GetPlayerMonkeys")

    def get_player_bloons(self, player_index: int) -> list[BloonInfo]:
        """
        Returns the current bloons in the given player's map.
        If the `player_index` is invalid, returns an empty list.
        """
        raise NotImplementedError("GetPlayerBloons")

    def get_player_remaining_tower_boost_time(self, player_index: int) -> float:
        """
        Returns the remaining time (in seconds) of the tower boost used by the given player.
        If the player doesn't have a tower boost right now, returns 0.
        If the `player_index` is invalid, returns 0.
        """
        raise NotImplementedError("GetPlayerRemainingTowerBoostTime")

    def get_player_remaining_bloon_boost_time(self, player_index: int) -> float:
        """
        Returns the remaining time (in seconds) of the bloon boost used by the given player.
        If the player doesn't have a bloon boost right now, returns 0.
        If the `player_index` is invalid, returns 0.
        """
        raise NotImplementedError("GetPlayerRemainingBloonBoostTime")

    ### GENERAL METHODS ###

    def log_info(self, text: str) -> None:
        """
        Prints the text to the console as an info message.

        **Warning:** Writing to log every time the `run` method is called might slow down the game.
        """
        raise NotImplementedError("Log")

    def log_warning(self, text: str) -> None:
        """
        Prints the text to the console as a warning.

        **Warning:** Writing to log every time the `run` method is called might slow down the game.
        """
        raise NotImplementedError("Log")

    def log_error(self, text: str) -> None:
        """
        Prints the text to the console as an error.

        **Warning:** Writing to log every time the `run` method is called might slow down the game.
        """
        raise NotImplementedError("Log")


class ArazimWarsBot:
    """
    Base class for writing your bots.

    **Important:** Your bot must subclass this directly, and be called MyBot!

    **Important:** Your bot must not have a custom __init__ method. Use `setup` for any setup code you may have.

    **Example:**

    ```python
    class MyBot(ArazimWarsBot):
        def setup(self):
            self.message = "Hello!"

        def run(self):
            if self.context.get_current_time() == 2:
                print(self.message)
    ```
    """

    context: API

    def __init__(self, context: API):
        self.context = context
        self.setup()

    def setup(self) -> None:
        """
        This optional method will be called upon construction.

        If you need to define any instance variables like in a constructor, do it here.
        """

    def run(self) -> None:
        """
        This method will be called once every game step.

        Interact with the game using `self.context`.
        """


class Bloons(Enum):
    """An enum representing all bloon types."""

    RED = enum.auto()
    BLUE = enum.auto()
    GREEN = enum.auto()
    YELLOW = enum.auto()
    PINK = enum.auto()
    BLACK = enum.auto()
    WHITE = enum.auto()
    CAMO = enum.auto()
    LEAD = enum.auto()
    ZEBRA = enum.auto()
    RAINBOW = enum.auto()
    CERAMIC = enum.auto()
    MOAB = enum.auto()
    BFB = enum.auto()
    ZOMG = enum.auto()


class Maps(Enum):
    """
    An enum representing all maps in the game.
    """

    INTERCHANGE = enum.auto()
    SHAPES = enum.auto()
    TEMPLE = enum.auto()
    YELLOW_BRICK = enum.auto()


class Monkeys(Enum):
    """
    An enum representing all available monkeys.

    Keep in mind that not all BTD Battles monkeys are available.
    """

    DART_MONKEY = enum.auto()
    TACK_SHOOTER = enum.auto()
    NINJA_MONKEY = enum.auto()
    SUPER_MONKEY = enum.auto()
    SNIPER_MONKEY = enum.auto()
    BOMB_TOWER = enum.auto()


class EcoBloons(Enum):
    """
    An enum representing available eco bloons, i.e. bloons to send to opponents. See `API.send_bloons`.

    Keep in mind that not all BTD Battles eco bloons are available.
    """

    GROUPED_RED = enum.auto()
    SPACED_BLUE = enum.auto()
    GROUPED_BLUE = enum.auto()
    SPACED_PINK = enum.auto()
    GROUPED_GREEN = enum.auto()
    SPACED_BLACK = enum.auto()
    GROUPED_YELLOW = enum.auto()
    SPACED_WHITE = enum.auto()
    GROUPED_PINK = enum.auto()
    SPACED_LEAD = enum.auto()
    GROUPED_WHITE = enum.auto()
    SPACED_ZEBRA = enum.auto()
    GROUPED_BLACK = enum.auto()
    SPACED_RAINBOW = enum.auto()
    GROUPED_ZEBRA = enum.auto()
    GROUPED_RAINBOW = enum.auto()
    GROUPED_LEAD = enum.auto()
    SPACED_CERAMIC = enum.auto()
    FAST_COOLDOWN_CERAMIC = enum.auto()
    MOAB = enum.auto()
    FAST_COOLDOWN_MOAB = enum.auto()
    BFB = enum.auto()
    FAST_COOLDOWN_BFB = enum.auto()
    ZOMG = enum.auto()
    FAST_COOLDOWN_ZOMG = enum.auto()


class Result(Enum):
    """
    An enum representing result of API methods.
    See each method for a list of possible results.
    If a method was successful, it always returns `OK`.
    """

    OK = 0
    NOT_ENOUGH_MONEY = enum.auto()
    OUT_OF_MAP = enum.auto()
    """The monkey would not fully fit inside the map borders at the specified position."""
    TOO_CLOSE_TO_BLOON_ROUTE = enum.auto()
    """The monkey would overlap the bloon track (see `API.get_track_width`)."""
    TOO_CLOSE_TO_OTHER_MONKEY = enum.auto()
    INVALID_MONKEY_INDEX = enum.auto()
    """The specified monkey index argument is not a valid index of the player's monkeys."""
    INVALID_BLOON_INDEX = enum.auto()
    """The specified bloon index argument is not a valid index of the player's bloons."""
    MONKEY_CANT_SEE = enum.auto()
    """The monkey cannot target the specified bloon because it is outside of its range or it is camouflage and the monkey can't see camouflage."""
    OTHER_ROW_CHOSEN = enum.auto()
    """The upgrade cannot be completed because the monkey was already upgraded on the other row beyond Level 2."""
    INVALID_PLAYER = enum.auto()
    """The specified player is either yourself, an inactive player or an invalid player index."""
    ECO_QUEUE_FULL = enum.auto()
    """You sent too many eco bloons which have not been sent yet. Your queue of size 5 is filled."""
    TOO_EARLY = enum.auto()
    """The specified eco bloons are only available in the future."""
    ALREADY_MAXED_OUT = enum.auto()
    """The monkey is already upgraded to the highest available level in the selected path."""
    INVALID_TIME = enum.auto()
    """The specified method was called at an inappropriate time."""
    INVALID_MODE = enum.auto()
    """The given action is invalid for this game mode."""
    INVALID_BLOON = enum.auto()
    """The requested bloon can't be camo or regen because it is a MOAB/BFB/ZOMG."""
    NOT_ENOUGH_BOOSTS = enum.auto()
    """You are out of this type of boost."""
    MONKEY_BANNED = enum.auto()
    """The monkey that was requested is banned."""
    CANT_BAN_TWICE = enum.auto()
    """You tried to ban more than one monkey."""

    def __bool__(self) -> bool:
        return self == Result.OK


class Emote(Enum):
    """
    An enum representing all emotes. This is only intended for fun purposes.
    """

    NONE = ""
    ANGRY = "angry"
    COOL = "cool"
    CRYING = "crying"
    FACEPALM = "facepalm"
    IDEA_THOUGHT = "idea-thought"
    LAUGHING = "laughing"
    LOVE = "love"
    POINTING = "pointing"
    SHOCKED = "shocked"
    SMILE = "smile"
    THUMBS_DOWN = "thumbs-down"
    THUMBS_UP = "thumbs-up"


class GameMode(Enum):
    """An enum representing all game modes."""

    STANDARD = "Standard"
    DEFENSE = "Defense"
    BANANZA = "Bananza"


@dataclass
class BloonInfo:
    kind: Bloons
    """The type (usually color) of the bloon."""

    is_camo: bool
    """Whether this bloon is camouflaged."""

    is_regen: bool
    """Whether this bloon is regen."""

    is_eco: bool
    """Whether this bloon was sent by another player."""

    eco_from: int | None
    """If this bloon was sent by another player, that player's index."""

    position: tuple[float, float]
    """The position of the bloon, as a tuple of (x, y)."""

    index: int
    """
    The index of the bloon.
    
    **Important:** This may change between repeated calls to `ArazimWarsBot.run`!
    """

    uid: int
    """
    The unique id of the bloon.
    This is guaranteed to be unique and persistent, but it is for your usage only.
    When targeting a bloon, you must use its **current** index.
    """


@dataclass
class MonkeyInfo:
    kind: Monkeys
    position: tuple[float, float]
    """The position of the monkey, as a tuple of (x, y)."""
    top_level: int
    bottom_level: int
    direction: float
    """The direction the monkey is facing: 0 for up, `math.pi / 2` for right etc."""


@dataclass
class LineInfo:
    start: tuple[float, float]
    """The start position (x,y) of the line, in pixels."""
    end: tuple[float, float]
    """The end position (x,y) of the line, in pixels."""
    hidden: bool
    """Whether this line is hidden (e.g. under a bridge)."""


@dataclass
class EcoBloonsInfo:
    """Information regarding eco bloons to send."""

    kind: Bloons
    """The type of bloons to send."""
    count: int
    """The amount of bloons to send."""
    cooldown: float
    """The time (in seconds) to wait before sending is complete."""
    cost: int
    """The cost of these bloons."""
    eco: float
    """The eco change as a result of sending these bloons (in the Standard game mode)."""
    availability_round: int
    """The round in which these eco bloons are first available (in the Standard game mode)."""


@dataclass
class BloonKindInfo:
    """Information about a specific `Bloons` kind, for instance red bloons."""

    size: int
    """The total health of bloons in this bloon (including itself)."""
    health: int
    """The initial health of the bloon itself (not including the bloons inside)."""
    speed: float
    """The speed of the bloon, relative to red bloons (see `RED_BLOON_SPEED`)."""
    inside: list[Bloons]
    """The types of the bloons inside."""


ECO_BLOONS_INFO = {
    EcoBloons.GROUPED_RED: EcoBloonsInfo(Bloons.RED, 8, 0.8, 25, 1, 2),
    EcoBloons.SPACED_BLUE: EcoBloonsInfo(Bloons.BLUE, 6, 1, 25, 1, 2),
    EcoBloons.GROUPED_BLUE: EcoBloonsInfo(Bloons.BLUE, 6, 0.6, 42, 1.7, 4),
    EcoBloons.SPACED_PINK: EcoBloonsInfo(Bloons.PINK, 3, 1, 42, 1.7, 4),
    EcoBloons.GROUPED_GREEN: EcoBloonsInfo(Bloons.GREEN, 5, 0.5, 60, 2.4, 6),
    EcoBloons.SPACED_BLACK: EcoBloonsInfo(Bloons.BLACK, 3, 1, 60, 2.4, 6),
    EcoBloons.GROUPED_YELLOW: EcoBloonsInfo(Bloons.YELLOW, 5, 0.25, 75, 3, 8),
    EcoBloons.SPACED_WHITE: EcoBloonsInfo(Bloons.WHITE, 4, 1, 90, 3, 8),
    EcoBloons.GROUPED_PINK: EcoBloonsInfo(Bloons.PINK, 3, 0.2, 90, 3.6, 10),
    EcoBloons.SPACED_LEAD: EcoBloonsInfo(Bloons.LEAD, 2, 1, 90, 3.6, 10),
    EcoBloons.GROUPED_WHITE: EcoBloonsInfo(Bloons.WHITE, 3, 0.5, 125, 5, 12),
    EcoBloons.SPACED_ZEBRA: EcoBloonsInfo(Bloons.ZEBRA, 3, 1, 125, 5, 12),
    EcoBloons.GROUPED_BLACK: EcoBloonsInfo(Bloons.BLACK, 3, 0.5, 150, 6, 14),
    EcoBloons.SPACED_RAINBOW: EcoBloonsInfo(Bloons.RAINBOW, 1, 1, 150, 6, 14),
    EcoBloons.GROUPED_ZEBRA: EcoBloonsInfo(Bloons.ZEBRA, 3, 0.6, 220, 6, 16),
    EcoBloons.GROUPED_RAINBOW: EcoBloonsInfo(Bloons.RAINBOW, 3, 1, 550, 3, 16),
    EcoBloons.GROUPED_LEAD: EcoBloonsInfo(Bloons.LEAD, 4, 1, 200, 6, 18),
    EcoBloons.SPACED_CERAMIC: EcoBloonsInfo(Bloons.CERAMIC, 1, 3, 300, 0, 18),
    EcoBloons.FAST_COOLDOWN_CERAMIC: EcoBloonsInfo(Bloons.CERAMIC, 1, 1, 450, -5, 20),
    EcoBloons.MOAB: EcoBloonsInfo(Bloons.MOAB, 1, 11, 1500, -24, 20),
    EcoBloons.FAST_COOLDOWN_MOAB: EcoBloonsInfo(Bloons.MOAB, 1, 1, 1500, -56, 22),
    EcoBloons.BFB: EcoBloonsInfo(Bloons.BFB, 1, 11, 2500, -140, 22),
    EcoBloons.FAST_COOLDOWN_BFB: EcoBloonsInfo(Bloons.BFB, 1, 1, 2500, -140, 24),
    EcoBloons.ZOMG: EcoBloonsInfo(Bloons.ZOMG, 1, 11, 9000, -600, 24),
    EcoBloons.FAST_COOLDOWN_ZOMG: EcoBloonsInfo(Bloons.ZOMG, 1, 1, 10000, -900, 24),
}
"""Information about every possible eco bloon to send."""

BLOON_KIND_INFO: dict[Bloons, BloonKindInfo] = {
    Bloons.RED: BloonKindInfo(1, 1, 1, []),
    Bloons.BLUE: BloonKindInfo(2, 1, 1.4, [Bloons.RED]),
    Bloons.GREEN: BloonKindInfo(3, 1, 1.8, [Bloons.BLUE]),
    Bloons.YELLOW: BloonKindInfo(4, 1, 3.2, [Bloons.GREEN]),
    Bloons.PINK: BloonKindInfo(5, 1, 3.5, [Bloons.YELLOW]),
    Bloons.BLACK: BloonKindInfo(11, 1, 1.8, [Bloons.PINK, Bloons.PINK]),
    Bloons.WHITE: BloonKindInfo(11, 1, 2, [Bloons.PINK, Bloons.PINK]),
    Bloons.CAMO: BloonKindInfo(11, 1, 1.4, [Bloons.PINK, Bloons.PINK]),
    Bloons.LEAD: BloonKindInfo(23, 1, 1, [Bloons.BLACK, Bloons.BLACK]),
    Bloons.ZEBRA: BloonKindInfo(23, 1, 1.8, [Bloons.BLACK, Bloons.WHITE]),
    Bloons.RAINBOW: BloonKindInfo(47, 1, 2.2, [Bloons.ZEBRA, Bloons.ZEBRA]),
    Bloons.CERAMIC: BloonKindInfo(104, 10, 2.5, [Bloons.RAINBOW, Bloons.RAINBOW]),
    Bloons.MOAB: BloonKindInfo(
        616, 200, 1, [Bloons.CERAMIC, Bloons.CERAMIC, Bloons.CERAMIC, Bloons.CERAMIC]
    ),
    Bloons.BFB: BloonKindInfo(
        3164, 700, 0.25, [Bloons.MOAB, Bloons.MOAB, Bloons.MOAB, Bloons.MOAB]
    ),
    Bloons.ZOMG: BloonKindInfo(
        16656, 4000, 0.18, [Bloons.BFB, Bloons.BFB, Bloons.BFB, Bloons.BFB]
    ),
}
"""Information about every `Bloons` kind."""

RED_BLOON_SPEED = 93
"""
The speed of a red bloon along the route, in map pixels per second (measured from a recorded BTD Battles game).
A bloon's speed in map pixels per second is its `BloonKindInfo.speed` multiplied by this.
"""

BLOON_RADII: dict[Bloons, float] = {
    Bloons.RED: 8,
    Bloons.BLUE: 8,
    Bloons.GREEN: 8,
    Bloons.YELLOW: 8,
    Bloons.PINK: 8,
    Bloons.BLACK: 8,
    Bloons.WHITE: 8,
    Bloons.CAMO: 8,
    Bloons.LEAD: 8,
    Bloons.ZEBRA: 8,
    Bloons.RAINBOW: 8,
    Bloons.CERAMIC: 8,
    Bloons.MOAB: 50,
    Bloons.BFB: 75,
    Bloons.ZOMG: 87.5,
}
"""
The hit radius (in map pixels) of each `Bloons` kind.
A projectile hits a bloon when the distance between their centers is less than the sum of their radii.
"""


MONKEY_COSTS: dict[Monkeys, int] = {
    Monkeys.DART_MONKEY: 200,
    Monkeys.TACK_SHOOTER: 360,
    Monkeys.NINJA_MONKEY: 500,
    Monkeys.BOMB_TOWER: 650,
    Monkeys.SNIPER_MONKEY: 350,
    Monkeys.SUPER_MONKEY: 3000,
}
"""The cost of each monkey."""

UPGRADE_COSTS: dict[
    Monkeys, tuple[tuple[int, int, int, int], tuple[int, int, int, int]]
] = {
    Monkeys.DART_MONKEY: ((90, 160, 500, 1900), (140, 170, 475, 8000)),
    Monkeys.TACK_SHOOTER: ((210, 300, 500, 2500), (75, 175, 600, 2800)),
    Monkeys.NINJA_MONKEY: ((300, 250, 700, 3000), (250, 400, 2750, 5000)),
    Monkeys.BOMB_TOWER: ((200, 300, 700, 3600), (400, 400, 900, 3200)),
    Monkeys.SNIPER_MONKEY: ((300, 1800, 3500, 5500), (350, 300, 2400, 7000)),
    Monkeys.SUPER_MONKEY: ((3000, 4000, 13500, 100000), (800, 1200, 9000, 25000)),
}
"""The cost of all of the upgrades, as a tuple of the four top-row upgrades and then the four bottom-row upgrades."""

PROJECTILE_RADII: dict[str, int] = {
    "dart": 6,
    "spike": 13,
    "juggernaut_spike": 31,
    "tack": 7,
    "shuriken": 8,
    "laser": 8,
    "plasma": 10,
    "bomb": 20,
}
"""
The radius (in pixels) of each projectile, by its skin name.
A projectile hits a bloon when the distance between their centers is less than the sum of their radii.
"""

# Backwards compatibility.
Context = API
Exceptions = Result
