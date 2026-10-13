import random

from api import *

POINT_GRID = [(x, y) for x in range(40, 400) for y in range(50, 550)]
ROUND_INF = 100
EMOTES = [Emote.NONE, Emote.COOL, Emote.LAUGHING, Emote.LOVE]
MONKEY_RADII = {
    Monkeys.DART_MONKEY: 26,
    Monkeys.TACK_SHOOTER: 26,
    Monkeys.NINJA_MONKEY: 27,
    Monkeys.SUPER_MONKEY: 39,
    Monkeys.BOMB_TOWER: 32,
    Monkeys.SNIPER_MONKEY: 26,
}


class GeneralMonkey:
    TARGET_MODE_LAST_BLOON = "last_bloon_targeting"
    TARGET_MODE_FIRST_BLOON = "first_bloon_targeting"
    TARGET_MODE_LEAD_BLOONS = "lead_bloon_targeting"
    TARGET_MODE_CAMO_BLOONS = "camo_bloon_targeting"
    TARGET_MODE_STRONGEST_BLOON = "strongest_bloon_targeting"
    TARGET_MODE_STRONGEST_NON_MOAB_BLOON = "strongest_non_moab_bloon_targeting"

    def __init__(self, monkey_index: int, context: API) -> None:
        """Initializing consts and targetings"""
        self.TARGETS = [
            self.TARGET_MODE_LAST_BLOON,
            self.TARGET_MODE_FIRST_BLOON,
            self.TARGET_MODE_LEAD_BLOONS,
            self.TARGET_MODE_CAMO_BLOONS,
            self.TARGET_MODE_STRONGEST_BLOON,
            self.TARGET_MODE_STRONGEST_NON_MOAB_BLOON,
        ]
        self.TARGETING_ERRORS = [Result.INVALID_BLOON_INDEX, Result.MONKEY_CANT_SEE]
        self.target_modes = [self.TARGET_MODE_FIRST_BLOON]
        self.monkey_index = monkey_index
        self.target = None
        self.context = context

    def max_target_idx(self, bloons: list[BloonInfo]) -> int:
        """get the strongest bloon index from a list of bloons"""
        strongest = max(bloons, key=lambda b: b.kind.value)
        return strongest.index

    def target_next(self) -> Result:
        """target the bloon for this tick, iterates the targeting options until one is valid"""
        if self.target_modes == []:
            self.retarget()
        bloons = self.context.get_monkey_targets(self.monkey_index)
        if not len(bloons):
            return Result.MONKEY_CANT_SEE
        for curr_target in self.target_modes:
            match curr_target:
                case self.TARGET_MODE_LAST_BLOON:
                    if (
                        self.context.target_bloon(self.monkey_index, bloons[-1].index)
                        in self.TARGETING_ERRORS
                    ):
                        continue
                    return Result.OK

                case self.TARGET_MODE_FIRST_BLOON:
                    if (
                        self.context.target_bloon(self.monkey_index, bloons[0].index)
                        in self.TARGETING_ERRORS
                    ):
                        continue
                    return Result.OK

                # strongest bloon
                case self.TARGET_MODE_STRONGEST_BLOON:
                    if not len(bloons):
                        return Result.INVALID_BLOON_INDEX
                    return self.context.target_bloon(
                        self.monkey_index, self.max_target_idx(bloons)
                    )

                case self.TARGET_MODE_STRONGEST_NON_MOAB_BLOON:
                    non_moab_bloons = [
                        bloon
                        for bloon in bloons
                        if bloon.kind.value < Bloons.MOAB.value
                    ]
                    if not len(non_moab_bloons):
                        continue
                    return self.context.target_bloon(
                        self.monkey_index, self.max_target_idx(non_moab_bloons)
                    )

                # filtered targeting section
                case self.TARGET_MODE_LEAD_BLOONS:
                    filtered_bloons = [
                        bloon for bloon in bloons if bloon.kind == Bloons.LEAD
                    ]
                    if not len(filtered_bloons):
                        continue
                    return self.context.target_bloon(
                        self.monkey_index, filtered_bloons[0].index
                    )

                case self.TARGET_MODE_CAMO_BLOONS:
                    filtered_bloons = [bloon for bloon in bloons if bloon.is_camo]
                    if not len(filtered_bloons):
                        continue
                    return self.context.target_bloon(
                        self.monkey_index, filtered_bloons[0].index
                    )

        return Result.INVALID_BLOON

    def retarget(self) -> None:
        """either appends as least priority or resets completley to new targeting list"""
        monkey = self.context.get_player_monkeys(
            self.context.get_current_player_index()
        )[self.monkey_index]
        self.target_modes = Brain.prioritise_bloon(monkey)

    def __str__(self) -> str:
        return f"Monkey number {self.monkey_index} | targets {self.target_modes}"


class Play:
    """abstraction of 1 play - a purchase&placement, upgrade etc"""

    def __init__(self, round_range: range, minimal_balance: int) -> None:
        self.did_it = False
        self.round_range = round_range
        self.minimal_balance = minimal_balance

    def do_play(
        self,
        curr_round: int,
        curr_balance: int,
        context: API,
        our_monkeys: list[GeneralMonkey],
    ) -> bool:
        """runs the play if needed and allowed"""
        if self.did_it:
            return False
        if curr_round not in self.round_range:
            return False
        if curr_balance < self.minimal_balance:
            return False
        self.did_it = self.run(context, our_monkeys) == Result.OK
        return self.did_it

    def run(self, context: API, our_monkeys: list[GeneralMonkey]) -> Result:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


class PlaceMonkey(Play):
    def __init__(
        self,
        round_range: range,
        minimal_balance: int,
        kind: Monkeys,
        position: tuple[float, float],
    ) -> None:
        """
        Args:
            did_it: did the action
            round_range: range of rounds we want the play to happen in
            minimal_balance: minimal balance needed to do the play
            idx: monkey idx
            wanted_rows: a len 2 array of the wanted upgrades and when to do them
        """
        self.did_it = False
        self.round_range = round_range
        self.minimal_balance = minimal_balance
        self.kind = kind
        self.position = position

    def run(self, context: API, our_monkeys: list[GeneralMonkey]) -> Result:
        if our_monkeys is None:
            return Result.INVALID_MODE
        while (res := context.place_monkey(self.kind, Brain.get_random_points())) in (
            Result.OUT_OF_MAP,
            Result.TOO_CLOSE_TO_OTHER_MONKEY,
            Result.TOO_CLOSE_TO_BLOON_ROUTE,
        ):
            continue

        if res == Result.OK:
            our_monkeys.append(GeneralMonkey(len(our_monkeys), context))
        return res

    def __str__(self) -> str:
        return f"PM, kind: {self.kind}, pos: {self.position}"


class Attack(Play):
    def __init__(
        self,
        round_range: range,
        minimal_balance: int,
        player_index: int,
        bloon: EcoBloons,
        count: int,
        is_camo: bool = False,
        is_regen: bool = False,
    ) -> None:
        self.did_it = False
        self.round_range = round_range
        self.minimal_balance = minimal_balance
        self.player_index = player_index
        self.bloon = bloon
        self.count = count
        self.is_camo = is_camo
        self.is_regen = is_regen

    def run(
        self, context: API, our_monkeys: list[GeneralMonkey] | None = None
    ) -> Result:
        while self.count > 0:
            res = context.send_bloons(
                self.player_index, self.bloon, self.is_camo, self.is_regen
            )
            if (
                res == Result.ECO_QUEUE_FULL
                or res == Result.NOT_ENOUGH_MONEY
                or res == Result.TOO_EARLY
            ):
                return Result.OK
            if res == Result.OK:
                self.count -= 1
        return Result.OK


class UpgradeMonkey(Play):
    """
    upgrade monkey play
    """

    def __init__(
        self, round_range: range, minimal_balance: int, idx: int, wanted_rows: list[int]
    ) -> None:
        """
        Args:
            did_it: did the action
            round_range: range of rounds we want the play to happen in
            minimal_balance: minimal balance needed to do the play
            idx: monkey idx
            wanted_rows: a len 2 array of the wanted upgrades and when to do them
        """
        self.did_it = False
        self.round_range = round_range
        self.minimal_balance = minimal_balance
        self.idx = idx
        self.wanted_rows = wanted_rows

    def run(self, context: API, our_monkeys: list[GeneralMonkey]) -> Result:
        for i in range(2):
            if self.wanted_rows[i] != 0:
                res = context.upgrade_monkey(self.idx, i == 0)
                if res == Result.ALREADY_MAXED_OUT:
                    return Result.OK  # edge case cause by bans
                elif res != Result.OK:
                    continue
                our_monkeys[self.idx].target_modes = []
                self.wanted_rows[i] -= 1
        return Result.OK if self.wanted_rows == [0, 0] else Result.NOT_ENOUGH_MONEY

    def __str__(self) -> str:
        return f"UM, idx: {self.idx}, wanted_rows: {self.wanted_rows}"


class Brain:
    def __init__(self, context: API):
        self.monkey_priorities = [
            (Monkeys.DART_MONKEY, [2, 3]),
            (Monkeys.TACK_SHOOTER, [2, 1]),
            (Monkeys.NINJA_MONKEY, [3, 0]),
            (Monkeys.BOMB_TOWER, [1, 1]),
            (Monkeys.SNIPER_MONKEY, [1, 2]),
        ]
        self.round_num = 0
        self.attacks = None
        self.our_monkeys: list[GeneralMonkey] = []
        self.context = context
        self.round_times = self.context.get_round_times()
        self.sequence = self.get_sequence()

    @staticmethod
    def get_random_points() -> tuple[int, int]:
        return random.choice(POINT_GRID)

    def get_current_round(self) -> int:
        curr = self.context.get_current_steps()
        self.round_num = len(
            [round_time for round_time in self.round_times if round_time < curr]
        )
        return self.round_num

    def sequential_play(self, plays: list[Play]) -> None:
        """sequentially tries to run all plays"""
        if plays is None:
            return
        self.get_current_round()
        play = plays[0]
        res = play.do_play(
            self.round_num,
            self.context.get_money(),
            self.context,
            our_monkeys=self.our_monkeys,
        )
        if res:
            plays.pop(0)
        return

    @staticmethod
    def get_filtered_bloons(filtered: list[Bloons], api: API) -> list[BloonInfo]:
        """gets a list of bloon types to get, and returns the types it found in the existing map"""
        ret = []
        bloons = api.get_bloons()
        for b in bloons:
            if b.kind in filtered:
                ret.append(b)
        return ret

    @staticmethod
    def prioritise_bloon(monkey: MonkeyInfo) -> list[str]:
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

    def get_minimal_money(self, round_num: int) -> int:
        self.get_current_round()
        if round_num < 3:
            return 0
        if round_num < 4:
            return 300
        if round_num < 5:
            return 600
        if round_num < 6:
            return 500
        if round_num < 8:
            return 1000
        if round_num < 12:
            return 300
        return 1000

    def handle_econ(self) -> None:
        """
        Econ handling.
        """
        BLOON_TYPE_BY_ROUND = {
            2: EcoBloons.GROUPED_RED,
            3: EcoBloons.GROUPED_RED,
            4: EcoBloons.SPACED_PINK,
            5: EcoBloons.SPACED_PINK,
            6: EcoBloons.SPACED_PINK,
            7: EcoBloons.SPACED_PINK,
            8: EcoBloons.SPACED_WHITE,
            9: EcoBloons.SPACED_WHITE,
            10: EcoBloons.SPACED_LEAD,
            11: EcoBloons.SPACED_LEAD,
            12: EcoBloons.SPACED_ZEBRA,
            13: EcoBloons.SPACED_ZEBRA,
        }
        self.get_current_round()
        if self.attacks is None or (
            not self.context.is_player_active(self.attacks[0].player_index)
        ):
            player_index = 0
            for player_index in range(8):
                if (
                    self.context.is_player_active(player_index)
                    and player_index != self.context.get_current_player_index()
                ):
                    break
            if player_index >= 8:
                return
            attacks = [
                Attack(
                    range(round_num, round_num + 1),
                    self.get_minimal_money(round_num),
                    player_index,
                    BLOON_TYPE_BY_ROUND[round_num],
                    5,
                    round_num >= 10,
                )
                for round_num in range(2, 14)
            ]
        if self.get_should_attack(
            self.context.get_money(), self.round_num, self.context.get_player_count()
        ):
            self.sequential_play(
                [
                    Attack(
                        range(self.round_num, self.round_num),
                        self.get_minimal_money(self.round_num),
                        player_index,
                        EcoBloons.GROUPED_RAINBOW,
                        5,
                        False,
                        True,
                    )
                ]
            )
        if self.round_num < 2:
            pass
        if 2 <= self.round_num < 14:
            if self.context.get_current_steps() % 100 == 0:
                self.context.log_info(
                    f"round {self.round_num} | attack: {self.context.get_money()}"
                )
            for p in attacks:
                p.do_play(self.round_num, self.context.get_money(), self.context, None)

    def get_should_attack(self, money: int, round_num: int, player_count: int) -> bool:
        return money >= 2750 and round_num >= 16 and player_count == 2

    # def get_possible_attacks(self):
    #     raise NotImplementedError

    # def handle_monkey_placement_and_upgrades():
    #     raise NotImplementedError

    def minimal_defend(self) -> None:
        self.sequential_play(self.sequence)

    def handle_monkey_targets(self) -> None:
        """
        Basic monkey targeting handling.
        Picks the first visible target for each monkey.
        """
        # self.context.log_info(self.our_monkeys)
        for monkey in self.our_monkeys:
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

    def get_sequence(self) -> list[Play]:
        banned_monkeys = self.context.get_banned_monkeys()
        sequence = RAND_PLAY
        index = -1
        banned_indexes = []
        replacement = next(
            priority
            for priority in self.monkey_priorities
            if priority[0] not in banned_monkeys
        )
        for i, m in enumerate(sequence):
            if isinstance(m, PlaceMonkey):
                index += 1
            if isinstance(m, PlaceMonkey) and m.kind in banned_monkeys:
                banned_indexes.append(index)
                sequence[i] = PlaceMonkey(
                    m.round_range, m.minimal_balance, replacement[0], m.position
                )
        for m in sequence:
            if isinstance(m, UpgradeMonkey) and m.idx in banned_indexes:
                m.wanted_rows = replacement[1].copy()
        return sequence

    def handle_monkey_placement_and_upgrades(self) -> None:
        self.minimal_defend()


class MyBot(ArazimWarsBot):
    def setup(self) -> None:
        self.init_seq = True
        self.brain = Brain(self.context)
        self.monkey_count = 0
        self.monkey_levels: list[int] = []
        self.monkeys: list[GeneralMonkey] = []
        self.emote_index = 0
        if self.context.get_current_time() == 0:
            self.context.ban_monkey(Monkeys.SNIPER_MONKEY)

    def run(self) -> None:
        if self.init_seq:
            if self.context.get_current_time() < 1:
                return
            self.brain.sequence = self.brain.get_sequence()
            self.init_seq = False
        self.brain.handle_monkey_placement_and_upgrades()
        self.brain.handle_monkey_targets()
        self.brain.handle_econ()
        # self.brain.handle_emotes()


RAND_PLAY = [
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 0, [2, 3]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.TACK_SHOOTER, (347, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 1, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.TACK_SHOOTER, (454, 613)),
    UpgradeMonkey(range(ROUND_INF), 0, 2, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (202, 280)),
    UpgradeMonkey(range(ROUND_INF), 0, 3, [1, 2]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.BOMB_TOWER, (314, 262)),
    UpgradeMonkey(range(ROUND_INF), 0, 4, [0, 0]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.BOMB_TOWER, (259, 304)),
    UpgradeMonkey(range(ROUND_INF), 0, 5, [0, 0]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.TACK_SHOOTER, (128, 284)),
    UpgradeMonkey(range(ROUND_INF), 0, 6, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 7, [2, 3]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 8, [2, 3]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 9, [2, 3]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 10, [2, 3]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 11, [2, 3]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 12, [2, 3]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 13, [2, 3]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.DART_MONKEY, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 14, [2, 3]),
]
