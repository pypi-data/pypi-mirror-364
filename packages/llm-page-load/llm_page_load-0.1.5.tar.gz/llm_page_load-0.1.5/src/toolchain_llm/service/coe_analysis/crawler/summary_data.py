from service.coe_analysis.crawler.abstract_data import AbstractData
from dataclasses import dataclass,asdict
from typing import *

@dataclass
class SummaryData(AbstractData):
    summary:str
    answer:str
    coe_id:int
    
    def get_text(self):
        return f'[线上问题-{self.coe_id}]总结如下:\n{self.summary}\n'