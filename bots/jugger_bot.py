from api import ArazimWarsBot, BloonInfo, Bloons, EcoBloons, Emote, Exceptions, Maps, Monkeys

# Only pick the cool emotes of course
EMOTES = [Emote.NONE, Emote.COOL, Emote.LAUGHING, Emote.LOVE]

UPGRADE_PATHS = {
    Monkeys.DART_MONKEY: [True, True, True, False, False, True],
    Monkeys.SNIPER_MONKEY: [True, False, True, False, False],
}
MAX_PATH_LEN = {
    Monkeys.DART_MONKEY: len(UPGRADE_PATHS[Monkeys.DART_MONKEY]),
    Monkeys.SNIPER_MONKEY: len(UPGRADE_PATHS[Monkeys.SNIPER_MONKEY]),
}


class MyBot(ArazimWarsBot):
    def setup(self) -> None:
        self.map = self.context.get_map()
        self.ind = self.context.get_current_player_index()
        for player in range(7):
            if player != self.ind:
                self.enemy_ind = player
                break
        self.get_money = False
        self.monkey_count = 0
        self.monkey_levels: list[int] = []
        self.attempted_position = 0
        self.emote_index = 0
        if self.map == Maps.TEMPLE:
            self.poses = [
                (57, 506),
                (455, 568),
                (410, 259),
                (44, 255),
                (301, 382),
                (187, 493),
                (103, 150),
                (454, 118),
                (53, 116),
                (154, 349),
                (53, 454),
                (101, 599),
            ]
            self.monkeys = [
                Monkeys.DART_MONKEY,
                Monkeys.DART_MONKEY,
                Monkeys.DART_MONKEY,
                Monkeys.SNIPER_MONKEY,
                Monkeys.DART_MONKEY,
                Monkeys.DART_MONKEY,
                # Monkeys.DART_MONKEY,
                # Monkeys.DART_MONKEY,
                # Monkeys.DART_MONKEY,
                # Monkeys.DART_MONKEY,
                # Monkeys.DART_MONKEY,
                # Monkeys.DART_MONKEY
            ]
        else:
            self.poses = [(456, 185), (223, 461), (449, 33), (181, 108), (27, 386)]
            self.monkeys = [
                Monkeys.DART_MONKEY,
                Monkeys.DART_MONKEY,
                Monkeys.SNIPER_MONKEY,
                Monkeys.DART_MONKEY,
                Monkeys.DART_MONKEY,
            ]

    def run(self) -> None:
        self.handle_monkey_placement_and_upgrades()
        self.handle_monkey_targets()
        self.handle_eco()
        self.handle_emotes()

    def handle_monkey_placement_and_upgrades(self) -> None:
        """
        Basic monkey placement and upgrades handling.
        Tries to place monkeys in a straight line once every 5 seconds.
        After 20 seconds, tries to upgrade each monkey's top row.
        """
        for monkey_index in range(self.monkey_count):
            # Upgrade Monkeys
            self.upgrade_monkey(monkey_index)

        if self.context.get_current_time() % 5 == 0 and self.monkey_count < len(
            self.monkeys
        ):
            self.context.log_info("Placing Monkeys!")
            # Place Monkeys

            result = self.context.place_monkey(
                self.monkeys[self.monkey_count], self.poses[self.monkey_count]
            )
            if result == Exceptions.OK:
                self.monkey_count += 1
                self.monkey_levels.append(0)
            elif (
                result == Exceptions.OUT_OF_MAP
                or result == Exceptions.TOO_CLOSE_TO_BLOON_ROUTE
                or result == Exceptions.TOO_CLOSE_TO_OTHER_MONKEY
            ):
                self.context.log_warning(f"Couldn't place monkey because of: {result}")
                self.attempted_position += 1

    def handle_monkey_targets(self) -> None:
        """
        Basic monkey targeting handling.
        Picks the first visible target for each monkey.
        """
        for monkey_index in range(self.monkey_count):
            # Target Bloons
            targets = self.context.get_monkey_targets(monkey_index)
            if len(targets) > 0:
                bloon = self.prioritise_bloon(self.monkeys[monkey_index], targets)
                self.context.target_bloon(monkey_index, bloon)

    def handle_emotes(self) -> None:
        """
        Basic emote handling.
        Shows one of the cool emotes every second.
        """

        if self.context.get_current_time() % 1 == 0:
            self.context.display_emote(EMOTES[self.emote_index])
            self.emote_index = (self.emote_index + 1) % len(EMOTES)

    def prioritise_bloon(self, monkey: Monkeys, targets: list[BloonInfo]) -> int:
        match monkey:
            case Monkeys.DART_MONKEY:
                return targets[-1].index
            case Monkeys.SNIPER_MONKEY:
                for i in range(len(targets)):
                    if targets[i].kind == Bloons.LEAD:
                        return targets[i].index
                return targets[0].index
            case _:
                return targets[0].index

    def handle_eco(self) -> None:
        curr_time = self.context.get_current_time()
        if (curr_time) >= 140:
            return
        if (curr_time) < 40:
            bloon = EcoBloons.GROUPED_RED
        else:
            bloon = EcoBloons.SPACED_PINK
        if curr_time % 2 == 0 and self.get_money:
            self.context.send_bloons(self.enemy_ind, bloon)
            self.get_money = False
        elif curr_time % 2 == 1:
            self.get_money = True

    def upgrade_monkey(self, monkey_index: int) -> None:
        """upgrade the monkey at the given index"""
        if (self.monkey_levels[monkey_index] < MAX_PATH_LEN[self.monkeys[monkey_index]] and
            self.context.upgrade_monkey(monkey_index, True)):
            self.context.log_info(f"monkey_levels: {self.monkey_levels}!")
            self.monkey_levels[monkey_index] += 1
