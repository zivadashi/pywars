from api import API, BloonInfo, Bloons, Result,Maps,Monkeys

class Play:
    """abstraction of 1 play - a purchase&placement, upgrade etc"""
    def __init__(self,round_range: range,minimal_balance: int)->None:
        self.did_it = False
        self.round_range = round_range
        self.minimal_price = minimal_balance
    
    def do_play(self,curr_round:int,curr_balance: int,brain:Brain) -> bool:
        """runs the play if needed and allowed"""
        if self.did_it:
            return False
        if curr_round not in self.round_range:
            return False
        if curr_balance< self.minimal_price:
            return False
        self.did_it = self.run()
        return True
    
    def run(self,brain:Brain)->None:
        return False

class PlaceMonkey(Play):
    def __init__(self,round_range: range,minimal_balance: int,kind:Monkeys, position: tuple[float, float])->None:
        self.did_it = False
        self.round_range = round_range
        self.minimal_balance = minimal_balance
        self.kind = kind
        self.position = position
    
    def run(self,brain:Brain):
        return brain.place_monkey(self.kind,self.position)

class UpgradeMonkey(Play):
    def __init__(self,round_range: range,minimal_balance: int,idx:int,wanted_rows:list[int])->None:
        self.did_it = False
        self.round_range = round_range
        self.minimal_balance = minimal_balance
        self.idx = idx
        self.wanted_rows = wanted_rows

    def run(self,brain:Brain)->bool:
        done = True
        for i in range(2):
            if self.wanted_rows[i]!=0:
                if brain.context.upgrade_monkey(self.idx,i==0):
                    self.wanted_rows[i]-=1
                done=False
        return done

class Brain:
    def __init__(self,context:API):
        self.round_num = 0
        self.our_monkeys = []
        self.context = context
        self.round_times = self.context.get_round_times()
    
    def get_current_round(self) -> int:
        for i in range(len(self.round_times)-self.round_num):
            if self.round_times[self.round_num+i] <= self.context.get_current_time():
                self.round_num = i
                return i
        return i
    
    def sequential_play(self,plays:list[Play]):
        """sequentially tries to run all plays"""
        self.get_current_round()
        for p in plays:
            if p.do_play(self.round_num,self.context.get_money(),self):
                return

    
    def minimal_defend(self)->None:
        self.get_current_round()
        if round >= 14:
            return
        if self.context.get_map() == Maps.INTERCHANGE:
            self.sequential_play([PlaceMonkey(range(3),0,Monkeys.DART_MONKEY,(197,286)),UpgradeMonkey(range(3),0,0,[3,0])])
        elif self.context.get_map == Maps.SHAPES:
            self.sequential_play()
        
    def place_monkey(self, kind: Monkeys, position: tuple[float, float]) -> bool:
        if self.context.place_monkey(kind,position) == Result.OK:
            self.our_monkeys.append(GeneralMonkey(len(self.our_monkeys),self.context))
            return True
        return False

    @staticmethod
    def get_filtered_bloons(filter: list[Bloons],api) -> list[BloonInfo]:
        """gets a list of bloon types to get, and returns the types it found in the existing map"""
        ret = []
        bloons = api.get_bloons()
        for b in bloons:
            if b.kind in filter:
                ret.append(b)
        return ret
    


class GeneralMonkey:
    TARGET_MODE_LAST_BLOON = "last_bloon_targeting"
    TARGET_MODE_FIRST_BLOON = "first_bloon_targeting"
    TARGET_MODE_LEAD_BLOONS = "lead_bloon_targeting"
    TARGET_MODE_CAMO_BLOONS = "camo_bloon_targeting"
    TARGET_MODE_STRONGEST_BLOON = "strongest_bloon_targeting"
    TARGET_MODE_STRONGEST_NON_MOAB_BLOON = "strongest_non_moab_bloon_targeting"

    def __init__(self, monkey_index: int,context: API) -> None:
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
                        if bloon.kind.value < Bloons.MOAB.value
                    ]
                    if not len(bloons):
                        return Result.INVALID_BLOON_INDEX
                    return self.context.target_bloon(
                        self.monkey_index, self.max_target_idx(bloons)
                    )

                # filtered targeting section
                case self.TARGET_MODE_LEAD_BLOONS:
                    filtered_bloons = Brain.get_filtered_bloons([Bloons.LEAD],self.context)
                case self.TARGET_MODE_CAMO_BLOONS:
                    filtered_bloons = Brain.get_filtered_bloons([Bloons.CAMO],self.context)

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
