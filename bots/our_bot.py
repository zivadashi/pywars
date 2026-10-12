from api import API, BloonInfo, Bloons, Result


class Brain:
    @staticmethod
    def get_filtered_bloons(filter : list[Bloons]) -> list[BloonInfo]:
        ret = []
        bloons = API().get_bloons()
        for b in bloons:
            if b.kind in filter:
                ret.append(b)
        return ret

class Monkey:
    TARGET_MODE_LAST_BLOON = "last_bloon_targeting"
    TARGET_MODE_FIRST_BLOON = "first_bloon_targeting"
    TARGET_MODE_LEAD_BLOONS = "lead_bloon_targeting"
    TARGET_MODE_CAMO_BLOONS = "camo_bloon_targeting"

    def __init__(self,monkey_index: int, target_modes : str) -> None:
        self.TARGETS = [self.TARGET_MODE_LAST_BLOON,self.TARGET_MODE_FIRST_BLOON,\
                   self.TARGET_MODE_LEAD_BLOONS,self.TARGET_MODE_CAMO_BLOONS]
        self.TARGETING_ERRORS = [Result.INVALID_BLOON_INDEX, Result.MONKEY_CANT_SEE]
        self.target_modes = [target_modes]
        self.monkey_index = monkey_index
        self.target = None
    
    def target_next(self) -> Result:
        for curr_target in self.target_modes:
            match curr_target:
                case self.TARGET_MODE_LAST_BLOON:
                    if API().target_bloon(self.monkey_index,len(API().get_bloons())-1) in self.TARGETING_ERRORS:
                        continue
                    return Result.OK

                case self.TARGET_MODE_FIRST_BLOON:
                    if API().target_bloon(self.monkey_index,0) in self.TARGETING_ERRORS:
                        continue
                    return Result.OK
                
                #filtered targeting section
                case self.TARGET_MODE_LEAD_BLOONS:
                    filtered_bloons = Brain.get_filtered_bloons([Bloons.LEAD])
                case self.TARGET_MODE_CAMO_BLOONS:
                    filtered_bloons = Brain.get_filtered_bloons([Bloons.CAMO])
            
            for bloon in filtered_bloons:
                if API().target_bloon(self.monkey_index,bloon.index) in self.TARGETING_ERRORS:
                    continue
                return Result.OK              
            return Result.OK
        return Result.INVALID_BLOON

    
    def retarget(self,new_mode : str,add_next:bool = False) -> bool:
        if new_mode in self.TARGETS:
            if add_next:
                self.target_modes.append(new_mode)
            else:
                self.target_modes = [new_mode]
            return True
        return False
    
    def __str__(self)->str:
        return(f"Monkey number {self.monkey_index} | targets {self.target_modes}")

