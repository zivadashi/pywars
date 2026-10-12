from api import (
    API,
    ArazimWarsBot,
    BloonInfo,
    Bloons,
    Emote,
    MonkeyInfo,
    Monkeys,
    Result,
)

EMOTES = [Emote.NONE, Emote.COOL, Emote.LAUGHING, Emote.LOVE]


class Brain:
    def __init__(self, context: API):
        self.context = context
        self.gen_monkeys: list[GeneralMonkey] = []

    def get_filtered_bloons(self, filter: list[Bloons]) -> list[BloonInfo]:
        """gets a list of bloon types to get, and returns the types it found in the existing map"""
        ret = []
        bloons = self.context.get_bloons()
        for b in bloons:
            if b.kind in filter:
                ret.append(b)
        return ret

    def prioritise_bloon(self, monkey: MonkeyInfo) -> list[str]:
        match monkey.kind, min(monkey.top_level, 3), min(monkey.bottom_level, 3):
            case Monkeys.DART_MONKEY, 3, _:
                return [GeneralMonkey.TARGET_MODE_LAST_BLOON]
            case Monkeys.NINJA_MONKEY, _, _:
                return [
                    GeneralMonkey.TARGET_MODE_CAMO_BLOONS,
                    GeneralMonkey.TARGET_MODE_FIRST_BLOON,
                ]
            case Monkeys.SUPER_MONKEY, _, _:
                return [GeneralMonkey.TARGET_MODE_STRONGEST_BLOON]
            case Monkeys.BOMB_TOWER, _, _:
                return [
                    GeneralMonkey.TARGET_MODE_LEAD_BLOONS,
                    GeneralMonkey.TARGET_MODE_FIRST_BLOON,
                ]
            case Monkeys.SNIPER_MONKEY, _, _:
                return [GeneralMonkey.TARGET_MODE_STRONGEST_BLOON]
            case _:
                return [GeneralMonkey.TARGET_MODE_FIRST_BLOON]

    def get_should_attack(self):
        return self.context.get_money() >= 2750 and self.get_current_round() >= 16

    # def get_possible_attacks(self):
    #     raise NotImplementedError

    # def handle_monkey_placement_and_upgrades():
    #     raise NotImplementedError

    def handle_monkey_targets(self) -> None:
        """
        Basic monkey targeting handling.
        Picks the first visible target for each monkey.
        """
        for monkey in self.gen_monkeys:
            # Target Bloons
            monkey.target_next()

    def handle_emotes(self) -> None:
        """
        Basic emote handling.
        Shows one of the cool emotes every second.
        """
        # if self.context.get_current_time() % 1 == 0:
        #     self.context.display_emote(EMOTES[self.emote_index])
        #     self.emote_index = (self.emote_index + 1) % len(EMOTES)

    def handle_econ(self) -> None:
        """
        Econ handling.
        """


class GeneralMonkey:
    TARGET_MODE_LAST_BLOON = "last_bloon_targeting"
    TARGET_MODE_FIRST_BLOON = "first_bloon_targeting"
    TARGET_MODE_LEAD_BLOONS = "lead_bloon_targeting"
    TARGET_MODE_CAMO_BLOONS = "camo_bloon_targeting"
    TARGET_MODE_STRONGEST_BLOON = "strongest_bloon_targeting"
    TARGET_MODE_STRONGEST_NON_MOAB_BLOON = "strongest_non_moab_bloon_targeting"

    def __init__(self, brain: Brain, monkey_index: int, target_modes: str) -> None:
        """Initializing consts and targetings"""
        self.brain = brain
        self.TARGETS = [
            self.TARGET_MODE_LAST_BLOON,
            self.TARGET_MODE_FIRST_BLOON,
            self.TARGET_MODE_LEAD_BLOONS,
            self.TARGET_MODE_CAMO_BLOONS,
            self.TARGET_MODE_STRONGEST_BLOON,
            self.TARGET_MODE_STRONGEST_NON_MOAB_BLOON,
        ]
        self.TARGETING_ERRORS = [Result.INVALID_BLOON_INDEX, Result.MONKEY_CANT_SEE]
        self.target_modes = [target_modes]
        self.monkey_index = monkey_index
        self.target = None

    def max_target_idx(self, bloons: list[BloonInfo]) -> int:
        """get the strongest bloon index from a list of bloons"""
        strongest_kind = max(bloon.kind.value for bloon in bloons)
        return next(
            idx
            for idx, bloon in enumerate(bloons)
            if bloon.kind.value == strongest_kind
        )

    def target_next(self) -> Result:
        """target the bloon for this tick, iterates the targeting options until one is valid"""
        for curr_target in self.target_modes:
            match curr_target:
                case self.TARGET_MODE_LAST_BLOON:
                    if (
                        self.brain.context.target_bloon(
                            self.monkey_index, len(self.brain.context.get_bloons()) - 1
                        )
                        in self.TARGETING_ERRORS
                    ):
                        continue
                    return Result.OK

                case self.TARGET_MODE_FIRST_BLOON:
                    if (
                        self.brain.context.target_bloon(self.monkey_index, 0)
                        in self.TARGETING_ERRORS
                    ):
                        continue
                    return Result.OK

                # strongest bloon
                case self.TARGET_MODE_STRONGEST_BLOON:
                    bloons = self.brain.context.get_bloons()
                    if not len(bloons):
                        return Result.INVALID_BLOON_INDEX
                    return self.brain.context.target_bloon(
                        self.monkey_index, self.max_target_idx(bloons)
                    )
                case self.TARGET_MODE_STRONGEST_NON_MOAB_BLOON:
                    bloons = [
                        bloon
                        for bloon in self.brain.context.get_bloons()
                        if bloon.kind.value < Bloons.MOAB.value
                    ]
                    if not len(bloons):
                        return Result.INVALID_BLOON_INDEX
                    return self.brain.context.target_bloon(
                        self.monkey_index, self.max_target_idx(bloons)
                    )

                # filtered targeting section
                case self.TARGET_MODE_LEAD_BLOONS:
                    filtered_bloons = self.brain.get_filtered_bloons([Bloons.LEAD])
                case self.TARGET_MODE_CAMO_BLOONS:
                    filtered_bloons = self.brain.get_filtered_bloons([Bloons.CAMO])

            for bloon in filtered_bloons:
                if (
                    self.brain.context.target_bloon(self.monkey_index, bloon.index)
                    in self.TARGETING_ERRORS
                ):
                    continue
                return Result.OK
            return Result.OK
        return Result.INVALID_BLOON

    def retarget(self, new_mode: str, add_next: bool = False) -> bool:
        """either appends as least priority or resets completley to new targeting list"""
        if new_mode in self.TARGETS:
            if add_next:
                self.target_modes.append(new_mode)
            else:
                self.target_modes = [new_mode]
            return True
        return False

    def __str__(self) -> str:
        return f"Monkey number {self.monkey_index} | targets {self.target_modes}"


class MyBot(ArazimWarsBot):
    def setup(self) -> None:
        self.brain = Brain(self.context)
        self.monkey_count = 0
        self.monkey_levels: list[int] = []
        self.monkeys: list[GeneralMonkey] = []
        self.emote_index = 0

    def run(self) -> None:
        # self.brain.handle_monkey_placement_and_upgrades()
        self.brain.handle_monkey_targets()
        # self.brain.handle_emotes()
        # self.brain.handle_econ()
