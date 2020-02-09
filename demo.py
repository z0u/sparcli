#!/usr/bin/env python
from itertools import count
import math
import random
import time

import numpy as np
import sparcli


def run():
    try:
        demo()
    except KeyboardInterrupt:
        print("Exiting demo")


def demo():
    with sparcli.sparcli() as s:
        randoms = take(random.random)
        sine = sinewave()
        for x1, x2 in zip(randoms, sine):
            s.record(random=x1, sine=x2)
            time.sleep(0.1)


def sinewave():
    for x in count():
        yield np.sin(x / 10)


def take(callable):
    while True:
        yield callable()


if __name__ == "__main__":
    run()
