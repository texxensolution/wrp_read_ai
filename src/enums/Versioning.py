from enum import Enum

class Versioning(Enum):
    ONE_ZERO_ONE="1.0.1"
    ONE_ZERO_TWO="1.0.2"

    def __str__(self):
        return str(self.value)
    