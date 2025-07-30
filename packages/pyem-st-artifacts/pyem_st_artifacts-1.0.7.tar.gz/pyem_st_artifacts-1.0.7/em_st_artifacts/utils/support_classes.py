from dataclasses import dataclass

from typing import List


@dataclass
class RawChannels:
    left_bipolar: float
    right_bipolar: float


@dataclass
class MindData:
    rel_attention: float
    rel_relaxation: float
    inst_attention: float
    inst_relaxation: float


@dataclass
class SpectralDataPercents:
    delta: float
    theta: float
    alpha: float
    beta: float
    gamma: float


@dataclass
class RawChannelsArray:
    channels: List[float]


@dataclass
class RawSpectVals:
    alpha: float
    beta: float


@dataclass
class SideType:
    LEFT: int = 0
    RIGHT: int = 1
    NONE: int = 2


@dataclass
class TotalPowValues:
    left: float
    right: float


@dataclass
class QualityValues:
    left: int
    right: int
