from api import API,Result
class Monkey:
    TARGET_MODE_LAST_BLOON = "last_bloon_targeting"
    TARGET_MODE_FIRST_BLOON = "first_bloon_targeting"
    TARGETS = [TARGET_MODE_LAST_BLOON,TARGET_MODE_FIRST_BLOON]
    def __init__(self,monkey_index: int, target_mode : str) -> None:
        self.target_mode = target_mode
        self.monkey_index = monkey_index
        self.target = None
    
    def decide_target(self) -> Result:
        match self.target_mode:
            case self.TARGET_MODE_LAST_BLOON:
                return API.target_bloon(self.monkey_index,len(API.get_bloons())-1)
            case self.TARGET_MODE_FIRST_BLOON:
                return API.target_bloon(self.monkey_index,0)
    
    def retarget(self,new_mode : str) -> bool:
        if new_mode in self.TARGETS:
            self.target_mode = new_mode
            return True
        return False

            