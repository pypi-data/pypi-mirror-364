from dataclasses import dataclass,asdict
from typing import *
import abc

@dataclass
class AbstractData:
    def __dict__(self):
        return asdict(self)
    
    @abc.abstractmethod
    def get_text(self):
        return