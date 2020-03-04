#!/usr/bin/env python
from itertools import count
import math
import random
import sys
from threading import Thread
import time

import numpy as np
import sparcli


running = True


def demo():
    jobs = start_producers()
    try:
        time.sleep(100)
    finally:
        stop_producers(jobs)


def start_producers():
    global running
    running = True
    jobs = []
    for producer in (context_manager, generator, text):
        job = Thread(target=producer, daemon=True)
        job.start()
        jobs.append(job)
    return jobs


def stop_producers(jobs):
    global running
    running = False
    for job in jobs:
        job.join()


def context_manager():
    with sparcli.ctx() as context:
        while running:
            context.record(random=random.random())
            time.sleep(0.1)


def generator():
    time.sleep(0.5)
    for y in sparcli.gen(sinewave(), "sine"):
        if not running:
            break
        time.sleep(0.2)


def sinewave():
    x = 0
    while True:
        yield np.sin(x / 10)
        x += 1


def text():
    time.sleep(1)
    while running:
        print("Print to stdout")
        print("Print to stderr", file=sys.stderr)
        time.sleep(1)


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        pass
