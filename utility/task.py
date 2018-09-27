from tqdm import tqdm
import ctypes
import numpy as np
import multiprocessing as mp
from functools import reduce
from utility.log import log
from setting.settings import MAX_TASK_NUM
from utility.timekit import TimerCount, print_run_time


OBJ = 0
LIST = 1


class MultiTasks(object):
    def __init__(self, tn=None):
        with TimerCount('init'):
            self.task_num = MAX_TASK_NUM if tn == None else tn
            self.manager = mp.Manager()
            self.lock = self.manager.Lock()
            self.counter = self.manager.Value(ctypes.c_uint32, 0)
            self.queue = self.manager.Queue(self.task_num)
            self.init_counter_queue()
            self.pool = mp.Pool(processes=self.task_num + 1)

    def init_counter_queue(self):
        self.counter.value = 0
        while self.queue.qsize() != self.task_num:
            self.queue.put('f')

    def close_tasks(self):
        self.pool.close()
        self.pool.join()

    @staticmethod
    def task_bar(c, q, d=None, bar_max=None):
        if bar_max is None:
            log.error('Wrong <bar max> para when doing <task_bar>')
        with tqdm(total=bar_max, desc=d, ascii=True) as tbar:
            while c.value <= bar_max:
                tbar.update(c.value - tbar.n)
                if q.qsize() == 0 or c.value == bar_max:
                    tbar.update(bar_max - tbar.n)
                    break

    @staticmethod
    def pack_func(paras):
        func, var, fix, lock, counter, finish_queue = paras
        if var is None or len(var) <= 0:
            log.error('Illegal <var> para in <packed_func>')
        fix_type = None if fix is None else \
            LIST if isinstance(fix, list) else OBJ
        var_type = None if var[0] is None else \
            LIST if isinstance(var[0], list) or isinstance(var[0], np.ndarray) \
                    or isinstance(var[0], tuple) else OBJ
        ret_set = []
        for item in var:
            if fix is None:
                if var_type == OBJ:
                    ret = func(item)
                elif var_type == LIST:
                    ret = func(*item)
                else:
                    ret = None
            else:
                if fix_type == OBJ:
                    if var_type == OBJ:
                        ret = func(item, fix)
                    elif var_type == LIST:
                        ret = func(fix, *item)
                    else:
                        ret = None
                elif fix_type == LIST:
                    if var_type == OBJ:
                        ret = func(item, *fix)
                    elif var_type == LIST:
                        ret = func(*item, *fix)
                    else:
                        ret = None
                else:
                    ret = None
            if lock is not None and counter is not None:
                with lock:
                    counter.value += 1
            ret_set.append(ret)
        if lock is not None and finish_queue is not None:
            finish_queue.get()
        return ret_set

    @print_run_time
    def run_tasks(self, func, var_args, fix_args=None, en_bar=False, desc=None, merge_result=True):
        self.init_counter_queue()
        args = [[func, v, fix_args, self.lock, self.counter, self.queue] for v in var_args]
        bar_max = sum(len(x) for x in var_args) if en_bar else None
        if en_bar:
            bar_args = (self.counter, self.queue, desc, bar_max)
            self.pool.apply_async(func=self.task_bar, args=bar_args)
        ret_res = self.pool.map(func=self.pack_func, iterable=args)
        if isinstance(ret_res[0], dict):
            ret_res = reduce(lambda x, y: {**x, **y}, ret_res) if merge_result else ret_res
        elif isinstance(ret_res[0], list):
            ret_res = reduce(lambda x, y: x + y, ret_res) if merge_result else ret_res
        return ret_res
