from .data_model import DopplerPointCloud as DopplerPointCloud, MeanFloatValue as MeanFloatValue
from abc import ABC

class Algorithm(ABC): ...

class SimpleMeanDistance(Algorithm):
    def __init__(self) -> None: ...
    def run(self, input: DopplerPointCloud) -> MeanFloatValue: ...