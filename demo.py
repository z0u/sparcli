#!/usr/bin/env python
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
        for x in take(random.random):
            s.record(random=x)
            time.sleep(0.1)


def take(callable):
    while True:
        yield callable()


if __name__ == "__main__":
    run()
