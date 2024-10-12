from enum import Enum

from sendingStrategy.basicSend import BasicSend
from sendingStrategy.directSend import DirectSend

class StrategyTypes(Enum):
    BASIC = 0
    DIRECT = 1

    def createStrategy(self) -> bool:
        if self == StrategyTypes.BASIC:
            return BasicSend()
        elif self == StrategyTypes.DIRECT: 
            return DirectSend()

    # StrategyTypes(int(os.getenv(SENDING_STRATEGY))).createStrategy()