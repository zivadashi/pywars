import api



ROUND_INF = 100
EMOTES = [Emote.NONE, Emote.COOL, Emote.LAUGHING, Emote.LOVE]


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
                        self.context.target_bloon(
                            self.monkey_index, len(self.context.get_bloons()) - 1
                        )
                        in self.TARGETING_ERRORS
                    ):
                        continue
                    return Result.OK

                case self.TARGET_MODE_FIRST_BLOON:
                    if (
                        self.context.target_bloon(self.monkey_index, 0)
                        in self.TARGETING_ERRORS
                    ):
                        continue
                    return Result.OK

                # strongest bloon
                case self.TARGET_MODE_STRONGEST_BLOON:
                    bloons = self.context.get_bloons()
                    if not len(bloons):
                        return Result.INVALID_BLOON_INDEX
                    return self.context.target_bloon(
                        self.monkey_index, self.max_target_idx(bloons)
                    )
                case self.TARGET_MODE_STRONGEST_NON_MOAB_BLOON:
                    bloons = [
                        bloon
                        for bloon in self.context.get_bloons()
                        if bloon.kind.value < EcoBloons.MOAB.value
                        if bloon.kind.value < EcoBloons.MOAB.value
                    ]
                    if not len(bloons):
                        return Result.INVALID_BLOON_INDEX
                    return self.context.target_bloon(
                        self.monkey_index, self.max_target_idx(bloons)
                    )

                # filtered targeting section
                case self.TARGET_MODE_LEAD_BLOONS:
                    filtered_bloons = Brain.get_filtered_bloons(
                        [Bloons.LEAD], self.context
                    )
                case self.TARGET_MODE_CAMO_BLOONS:
                    filtered_bloons = Brain.get_filtered_bloons(
                        [Bloons.CAMO], self.context
                    )

            for bloon in filtered_bloons:
                if (
                    self.context.target_bloon(self.monkey_index, bloon.index)
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


class Play:
    """abstraction of 1 play - a purchase&placement, upgrade etc"""

    def __init__(self, round_range: range, minimal_balance: int) -> None:
        self.did_it = False
        self.round_range = round_range
        self.minimal_balance = minimal_balance

    def do_play(self, curr_round: int, curr_balance: int, context: API) -> bool:
        """runs the play if needed and allowed"""
        if self.did_it:
            return False
        if curr_round not in self.round_range:
            return False
        if curr_balance < self.minimal_balance:
            return False
        self.did_it = self.run(context) == Result.OK
        return self.did_it

    def run(self, context: API) -> Result:
        raise NotImplementedError

class Attack(Play):
    def __init__(self,
        round_range:range,
        minimal_balance:int,                       
        player_index: int,
        bloon: EcoBloons,
        count: int,
        is_camo: bool = False,
        is_regen: bool = False,) -> None:
        self.did_it = False
        self.round_range = round_range
        self.minimal_balance = minimal_balance
        self.player_index = player_index
        self.bloon = bloon
        self.count = count
        self.is_camo = is_camo
        self.is_regen = is_regen
    def run(self, context: API,our_monkeys: list[GeneralMonkey] | None = None) -> bool:
        while self.count>0:
            res = context.send_bloons(self.player_index,self.bloon,self.is_camo,self.is_regen)
            if res == Result.ECO_QUEUE_FULL or res == Result.NOT_ENOUGH_MONEY or res == Result.TOO_EARLY:
                return True
            if res == Result.OK:
                self.count-=1
        return True

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

    def run(
        self, context: API, our_monkeys: list[GeneralMonkey] | None = None
    ) -> Result:
        if our_monkeys is None:
            return Result.INVALID_MODE
        if (res := context.place_monkey(self.kind, self.position)) == Result.OK:
            our_monkeys.append(GeneralMonkey(len(our_monkeys), context))
        return res


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

    def run(self, context: API) -> Result:
        done = Result.OK
        for i in range(2):
            if self.wanted_rows[i] != 0:
                if not (res := context.upgrade_monkey(self.idx, i == 0)):
                    self.wanted_rows[i] -= 1
                done = Result(max(done.value, res.value))
        return done


class Brain:
    def __init__(self, context: API):
        self.round_num = 0
        self.our_monkeys: list[GeneralMonkey] = []
        self.context = context
        self.round_times = self.context.get_round_times()
        self.attacks = None
        self.sequence = PLAYS[self.context.get_map()]

    def get_current_round(self) -> int:
        curr = self.context.get_current_steps()
        times = self.context.get_round_times()
        self.round_num = len([round_time for round_time in times if round_time < curr])
        return self.round_num

    def sequential_play(self, plays: list[Play]) -> None:
        """sequentially tries to run all plays"""
        self.get_current_round()
        for p in plays:
            res = p.do_play(self.round_num, self.context.get_money(), self.context)
            # self.context.log_info(f"res: {res}, is place: {isinstance(p, PlaceMonkey)}")
            if res and isinstance(p, PlaceMonkey):
                self.our_monkeys.append(
                    GeneralMonkey(len(self.our_monkeys), self.context)
                )
                return

    def place_monkey(self, kind: Monkeys, position: tuple[float, float]) -> Result:
        if (res := self.context.place_monkey(kind, position)) == Result.OK:
            self.our_monkeys.append(GeneralMonkey(len(self.our_monkeys), self.context))
        return res

    @staticmethod
    def get_filtered_bloons(filter: list[Bloons], api: API) -> list[BloonInfo]:
        """gets a list of bloon types to get, and returns the types it found in the existing map"""
        ret = []
        bloons = api.get_bloons()
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

    def get_should_attack(self) -> bool:
        return self.context.get_money() >= 2750 and self.get_current_round() >= 16

    # def get_possible_attacks(self):
    #     raise NotImplementedError

    # def handle_monkey_placement_and_upgrades():
    #     raise NotImplementedError

    def minimal_defend(self) -> None:
        self.sequential_play(PLAYS[self.context.get_map()])

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

    def get_minimal_money(self,round_num) -> int:
        self.get_current_round()
        if round_num <3:
            return 0
        if round_num <5:
            return 1000
        if round_num <6:
            return 1000
        if round_num <8:
            return 1000
        if  round_num <12:
            return 1000
        return 1000


    def handle_econ(self) -> None:
        """
        Econ handling.
        """
        BLOON_TYPE_BY_ROUND = {
            2: EcoBloons.GROUPED_RED, 3:  EcoBloons.GROUPED_RED, 4:  EcoBloons.SPACED_PINK,
        5:  EcoBloons.SPACED_PINK, 6:  EcoBloons.SPACED_PINK, 7:  EcoBloons.SPACED_PINK,
        8:  EcoBloons.SPACED_WHITE, 9:  EcoBloons.SPACED_WHITE, 10:  EcoBloons.SPACED_LEAD,
        11:  EcoBloons.SPACED_LEAD, 12:  EcoBloons.SPACED_ZEBRA, 13:  EcoBloons.SPACED_ZEBRA
        }
        self.get_current_round()
        if self.attacks is None or (not self.context.is_player_active(self.attacks[0].player_index)):
            player_index = 0
            for player_index in range(8):
                if self.context.is_player_active(player_index) and player_index != self.context.get_current_player_index():
                    break
            if player_index>=8:
                return
            attacks = [Attack(range(round_num,round_num+1),
                                self.get_minimal_money(round_num),
                                                player_index, 
                                BLOON_TYPE_BY_ROUND[round_num], 5,round_num>=10) for round_num in range(2,14)]
        if self.get_should_attack(self.context.get_money(),self.round_num,self.context.get_player_count()):
            self.sequential_play([Attack(range(self.round_num,self.round_num),self.get_minimal_money(), player_index, EcoBloons.GROUPED_RAINBOW,5,False, True)])
        if self.round_num<2:
            pass
        if 2<=self.round_num<14:
            for p in attacks:
                p.do_play(self.round_num,self.context.get_money(),self.context)

    
    def get_should_attack(self,money: int, round_num: int, player_count: int)->bool: 
        return (money >= 2750 and round_num >= 16 and player_count==2)
    
    def handle_monkey_placement_and_upgrades(self) -> None:
        self.minimal_defend()


class MyBot(ArazimWarsBot):
    def setup(self) -> None:
        self.brain = Brain(self.context)
        self.monkey_count = 0
        self.monkey_levels: list[int] = []
        self.monkeys: list[GeneralMonkey] = []
        self.emote_index = 0

    def run(self) -> None:
        self.context.log_info(f"round nums: {self.brain.get_current_round()}")
        self.brain.handle_monkey_placement_and_upgrades()
        self.brain.handle_monkey_targets()
        # self.brain.handle_emotes()
        self.brain.handle_econ()


# idxs: Tack 0, Tack 1, Sniper 2
# Ninja 3, Super 4, Ninja 5, Super 6, Sniper 7, Sniper 8, Sniper 9
BANANZA_INTERCHANGE_PLAYS = [
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.TACK_SHOOTER, (234, 164)),
    UpgradeMonkey(range(ROUND_INF), 0, 0, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.TACK_SHOOTER, (271, 202)),
    UpgradeMonkey(range(ROUND_INF), 0, 1, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (455, 26)),
    UpgradeMonkey(range(ROUND_INF), 0, 2, [1, 2]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.NINJA_MONKEY, (248, 361)),
    UpgradeMonkey(range(ROUND_INF), 0, 3, [4, 0]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SUPER_MONKEY, (358, 301)),
    UpgradeMonkey(range(ROUND_INF), 0, 4, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.NINJA_MONKEY, (249, 420)),
    UpgradeMonkey(range(ROUND_INF), 0, 5, [4, 0]),
    UpgradeMonkey(range(ROUND_INF), 0, 2, [2, 0]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SUPER_MONKEY, (167, 258)),
    UpgradeMonkey(range(ROUND_INF), 0, 6, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (455, 79)),
    UpgradeMonkey(range(ROUND_INF), 0, 7, [3, 2]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (455, 140)),
    UpgradeMonkey(range(ROUND_INF), 0, 8, [3, 2]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (455, 200)),
    UpgradeMonkey(range(ROUND_INF), 0, 9, [3, 2]),
]
BANANZA_YELLOWBRICK_PLAYS = [
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.TACK_SHOOTER, (151, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 0, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.TACK_SHOOTER, (347, 199)),
    UpgradeMonkey(range(ROUND_INF), 0, 1, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (454, 613)),
    UpgradeMonkey(range(ROUND_INF), 0, 2, [1, 2]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.NINJA_MONKEY, (202, 280)),
    UpgradeMonkey(range(ROUND_INF), 0, 3, [4, 0]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SUPER_MONKEY, (314, 262)),
    UpgradeMonkey(range(ROUND_INF), 0, 4, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.NINJA_MONKEY, (259, 304)),
    UpgradeMonkey(range(ROUND_INF), 0, 5, [4, 0]),
    UpgradeMonkey(range(ROUND_INF), 0, 2, [2, 0]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SUPER_MONKEY, (128, 284)),
    UpgradeMonkey(range(ROUND_INF), 0, 6, [2, 1]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (400, 613)),
    UpgradeMonkey(range(ROUND_INF), 0, 7, [3, 2]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (397, 557)),
    UpgradeMonkey(range(ROUND_INF), 0, 8, [3, 2]),
    PlaceMonkey(range(ROUND_INF), 0, Monkeys.SNIPER_MONKEY, (453, 553)),
    UpgradeMonkey(range(ROUND_INF), 0, 9, [3, 2]),
]
PLAYS = {
    Maps.INTERCHANGE: BANANZA_INTERCHANGE_PLAYS,
    Maps.YELLOW_BRICK: BANANZA_YELLOWBRICK_PLAYS,
}
