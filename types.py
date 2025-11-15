from dataclasses import dataclass
from typing import Literal, Optional, Callable, List

LengthUnit = Literal['words', 'chars', 'tokens']
SampleMode = Literal['random', 'sequential', 'specified']


@dataclass
class FilterConfig:
    min_len: Optional[int] = None
    max_len: Optional[int] = None
    unit: LengthUnit = 'words'
    # 自定义谓词函数：返回 True 保留，False 丢弃
    predicate: Optional[Callable[[str], bool]] = None


@dataclass
class SampleConfig:
    n: Optional[int] = None
    mode: SampleMode = 'random'
    indices: Optional[List[int]] = None
    replace: bool = False
    seed: Optional[int] = None