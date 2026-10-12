from api import API
from common_utilities.consts import ConstsMonkey
class Monkey:
    def __init__(self,target_mode : str) -> None:
        self.target_mode = target_mode
    def decide_target(self):
        if self.target_mode == ConstsMonkey.TARGET_MODE_LAST_BLOON:
            print("hi")