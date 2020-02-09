#!/usr/bin/env python
from itertools import count
import math
import random
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
    for producer in (using_context_manager, using_generator):
        job = Thread(target=producer, daemon=True)
        job.start()
        jobs.append(job)
    return jobs


def stop_producers(jobs):
    global running
    running = False
    for job in jobs:
        job.join()


def using_context_manager():
    with sparcli.context() as ctx:
        while running:
            ctx.record(random=random.random())
            time.sleep(0.1)


def using_generator():
    for y in sparcli.gen(sinewave(), "sine"):
        if not running:
            break
        time.sleep(0.2)


def sinewave():
    x = 0
    while True:
        yield np.sin(x / 10)
        x += 1


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        pass
