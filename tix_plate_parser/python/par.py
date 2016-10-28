import multiprocessing as mp
import random

import numpy
import time

lock, pool = None, None


class TaskRunner:
    def __init__(self, task):
        self._task = task

    def do(self):
        global lock
        global pool
        lock = mp.Lock()
        pool = mp.Pool(mp.cpu_count())
        l = list(range(100))
        #random.shuffle(l)
        for i in l:
            pool.apply_async(func=self._do, args=(i,))
        pool.close()
        pool.join()

    def _do(self, plate):
        self._task.do(plate)


class Task:
    def do(self, a):
        global lock
        try:
            # lock.acquire()
            k = numpy.full(shape=(100, 100), fill_value=10, dtype="float64")
            numpy.dot(k, k)
            time.sleep(10)
            print(a)
        finally:
            # lock.release()
            a += 1


if __name__ == "__main__":
    task = Task()
    test = TaskRunner(task)
    test.do()
