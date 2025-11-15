import random
from typing import List, Optional, Iterator


class RandomSampler:
    def __init__(self, items: List[str], seed: Optional[int] = None, replace: bool = False):
        self.items = items
        self.replace = replace
        self.rng = random.Random(seed)

    def sample(self, n: Optional[int] = None) -> List[str]:
        if n is None or n >= len(self.items):
            if self.replace:
                return [self.rng.choice(self.items) for _ in range(n or len(self.items))]
            items = self.items[:]
            self.rng.shuffle(items)
            return items
        if self.replace:
            return [self.rng.choice(self.items) for _ in range(n)]
        idxs = list(range(len(self.items)))
        self.rng.shuffle(idxs)
        return [self.items[i] for i in idxs[:n]]


class SequentialSampler:
    def __init__(self, items: List[str]):
        self.items = items
        self.ptr = 0

    def sample(self, n: Optional[int] = None) -> List[str]:
        if n is None or n >= len(self.items):
            return self.items[:]
        s = self.items[self.ptr:self.ptr + n]
        self.ptr = min(self.ptr + n, len(self.items))
        return s

    def iterate(self, cycle: bool = False) -> Iterator[str]:
        while True:
            for i in range(self.ptr, len(self.items)):
                yield self.items[i]
            if cycle:
                self.ptr = 0
            else:
                break


class SpecifiedSampler:
    def __init__(self, items: List[str], indices: List[int]):
        self.items = items
        self.indices = indices

    def sample(self, n: Optional[int] = None) -> List[str]:
        picked = [self.items[i] for i in self.indices if 0 <= i < len(self.items)]
        if n is not None:
            return picked[:n]
        return picked