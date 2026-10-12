from api import API,Result,Bloons

class Brain:
    def get_filtered_bloons(filter : list) -> list:
        ret = []
        bloons = API.get_bloons()
        for b in bloons:
            if b in filter:
                ret.append(b)
        return ret

class Monkey:
    TARGET_MODE_LAST_BLOON = "last_bloon_targeting"
    TARGET_MODE_FIRST_BLOON = "first_bloon_targeting"
    TARGET_MODE_LEAD_BLOONS = "lead_bloon_targeting"
    TARGET_MODE_CAMO_BLOONS = "camo_bloon_targeting"
    TARGETS = [TARGET_MODE_LAST_BLOON,TARGET_MODE_FIRST_BLOON,TARGET_MODE_LEAD_BLOONS,TARGET_MODE_CAMO_BLOONS]
    TARGETING_ERRORS = [Result.INVALID_BLOON_INDEX, Result.MONKEY_CANT_SEE]
    def __init__(self,monkey_index: int, target_mode : str) -> None:
        self.target_mode = target_mode
        self.monkey_index = monkey_index
        self.target = None
    
    def target_next(self) -> Result:
        for curr_target in self.target_modes:
            match curr_target:
                case self.TARGET_MODE_LAST_BLOON:
                    if API.target_bloon(self.monkey_index,len(API.get_bloons())-1) in self.TARGETING_ERRORS:
                        continue
                    return Result.OK

                case self.TARGET_MODE_FIRST_BLOON:
                    if API.target_bloon(self.monkey_index,0) in self.TARGETING_ERRORS:
                        continue
                    return Result.OK
                
                #filtered targeting section
                case self.TARGET_MODE_LEAD_BLOONS:
                    filtered_bloons = Brain.get_filtered_bloons([Bloons.LEAD])
                case self.TARGET_MODE_CAMO_BLOONS:
                    filtered_bloons = Brain.get_filtered_bloons([Bloons.CAMO])
            
            for bloon in filtered_bloons:
                if API.target_bloon(self.monkey_index,bloon.index) in self.TARGETING_ERRORS:
                    continue
                return Result.OK              
            return Result.OK
        return Result.INVALID_BLOON

    
    def retarget(self,new_mode : str) -> bool:
        if new_mode in self.TARGETS:
            self.target_mode = new_mode
            return True
        return False
    
    def __str__(self):
        print(f"Monkey number {self.monkey_index} | targets {self.targeting_modes}")

