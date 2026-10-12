from api import API, BloonInfo, Bloons, Result


class Monkey:
    TARGET_MODE_LAST_BLOON = "last_bloon_targeting"
    TARGET_MODE_FIRST_BLOON = "first_bloon_targeting"
    TARGET_MODE_STRONGEST_BLOON = "strongest_bloon_targeting"
    TARGET_MODE_STRONGEST_NON_MOAB_BLOON = "strongest_non_moab_bloon_targeting"

    def __init__(self, monkey_index: int, target_mode: str) -> None:
        self.TARGETS = [
            self.TARGET_MODE_LAST_BLOON,
            self.TARGET_MODE_FIRST_BLOON,
            self.TARGET_MODE_STRONGEST_BLOON,
            self.TARGET_MODE_STRONGEST_NON_MOAB_BLOON,
        ]
        self.target_mode = target_mode
        self.monkey_index = monkey_index
        self.target = None

    def max_target_idx(self, bloons: list[BloonInfo]) -> int:
        strongest_kind = max(bloon.kind.value for bloon in bloons)
        return next(idx for idx, bloon in enumerate(bloons) if bloon.kind.value == strongest_kind)

    def decide_target(self) -> Result:
        match self.target_mode:
            case self.TARGET_MODE_LAST_BLOON:
                return API().target_bloon(self.monkey_index, len(API().get_bloons()) - 1)
            case self.TARGET_MODE_FIRST_BLOON:
                return API().target_bloon(self.monkey_index, 0)
            case self.TARGET_MODE_STRONGEST_BLOON:
                bloons = API().get_bloons()
                if not len(bloons):
                    return Result.INVALID_BLOON_INDEX
                return API().target_bloon(self.monkey_index, self.max_target_idx(bloons))
            case self.TARGET_MODE_STRONGEST_NON_MOAB_BLOON:
                bloons = [bloon for bloon in API().get_bloons() if bloon.kind.value < Bloons.MOAB.value]
                if not len(bloons):
                    return Result.INVALID_BLOON_INDEX
                return API().target_bloon(self.monkey_index, self.max_target_idx(bloons))
        return Result.INVALID_BLOON

    def retarget(self, new_mode: str) -> bool:
        if new_mode in self.TARGETS:
            self.target_mode = new_mode
            return True
        return False
