from api import ArazimWarsBot, Emote, Exceptions, Monkeys

# Only pick the cool emotes of course
EMOTES = [Emote.NONE, Emote.COOL, Emote.LAUGHING, Emote.LOVE]


class MyBot(ArazimWarsBot):
    def setup(self) -> None:
        self.monkey_count = 0
        self.monkey_levels: list[int] = []
        self.attempted_position = 0
        self.emote_index = 0

    def run(self) -> None:
        self.handle_monkey_placement_and_upgrades()
        self.handle_monkey_targets()
        self.handle_emotes()

    def handle_monkey_placement_and_upgrades(self) -> None:
        """
        Basic monkey placement and upgrades handling.
        Tries to place monkeys in a straight line once every 5 seconds.
        After 20 seconds, tries to upgrade each monkey's top row.
        """

        if self.context.get_current_time() % 5 == 0:
            self.context.log_info("Placing Monkeys!")

            # Place Monkeys
            result = self.context.place_monkey(
                Monkeys.DART_MONKEY, (24 * self.attempted_position + 24, 400)
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

        for monkey_index in range(self.monkey_count):
            # Upgrade Monkeys
            if (
                self.context.get_current_time() > 20
                and self.monkey_levels[monkey_index] < 4
                and self.context.upgrade_monkey(monkey_index, True)
            ):
                self.monkey_levels[monkey_index] += 1

    def handle_monkey_targets(self) -> None:
        """
        Basic monkey targeting handling.
        Picks the first visible target for each monkey.
        """

        for monkey_index in range(self.monkey_count):
            # Target Bloons
            targets = self.context.get_monkey_targets(monkey_index)
            if len(targets) > 0:
                self.context.target_bloon(monkey_index, targets[0].index)

    def handle_emotes(self) -> None:
        """
        Basic emote handling.
        Shwos one of the cool emotes every second.
        """

        if self.context.get_current_time() % 1 == 0:
            self.context.display_emote(EMOTES[self.emote_index])
            self.emote_index = (self.emote_index + 1) % len(EMOTES)