import numpy as np
from typing import List

class ProbabilityHelper:
    @staticmethod
    def normalise(arr: List[float]) -> List[float]:
        arr = np.clip(arr, 0.0, None)
        s = float(sum(arr))
        return [x / s for x in arr] if s else [1 / len(arr)] * len(arr)

    @staticmethod
    def sample(categories: List[str], probs: List[float]) -> str:
        probs = ProbabilityHelper.normalise(probs)
        return str(np.random.choice(categories, p=probs))

    @staticmethod
    def shift(probs: List[float], src: int, dst: int, delta: float) -> None:
        take = min(delta, probs[src])
        probs[src] -= take
        probs[dst] += take

    @staticmethod
    def cap(probs: List[float], idx: int, cap_val: float) -> None:
        if probs[idx] <= cap_val:
            return
        excess = probs[idx] - cap_val
        probs[idx] = cap_val
        redistribute_idxs = [i for i in range(len(probs)) if i != idx]
        total = sum(probs[i] for i in redistribute_idxs)
        for i in redistribute_idxs:
            probs[i] += excess * (probs[i] / total)

    @staticmethod
    def shift_equal(probs: List[float], dst: int, srcs: List[int], delta: float) -> None:
        share = delta / len(srcs)
        for s in srcs:
            taken = min(share, probs[s])
            probs[s] -= taken
            probs[dst] += taken

    @staticmethod
    def shift_from_to(probs: List[float], src_idxs: List[int], dst_idx: int, delta: float) -> None:
        share = delta / len(src_idxs)
        for s in src_idxs:
            taken = min(share, probs[s])
            probs[s] -= taken
            probs[dst_idx] += taken

    @staticmethod
    def multiply(probs: List[float], idxs: List[int], factor: float) -> None:
        for i in idxs:
            probs[i] *= factor
