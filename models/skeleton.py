import numpy as np
import random


class RandomRec:
    def __init__(self):
        pass

    def forward(self, batch):
        return np.array([random.randint(0, 10000) for _ in range(len(batch))])
