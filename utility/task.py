from tqdm import tqdm
import ctypes
import numpy as np
import multiprocessing as mp
from functools import reduce
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utility.log import log
from utility.timekit import TimerCount, print_run_time
from setting.settings import MAX_TASK_NUM, CHROME_EXE


class MultiTasks(object):
    def __init__(self, task_num=None):
        with TimerCount('init'):
            self.task_num = MAX_TASK_NUM if task_num == None else task_num
            self.manager = mp.Manager()
            self.lock = self.manager.Lock()
            self.counter = self.manager.Value(ctypes.c_uint32, 0)
            self.finish_flag = self.manager.Queue(self.task_num)
            self.init_counter_queue()
            self.pool = mp.Pool(processes=self.task_num + 1)

    def init_counter_queue(self):
        self.counter.value = 0
        while self.finish_flag.qsize() != self.task_num:
            self.finish_flag.put('f')

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
    def pack_list_func(paras):
        func, var, fix, lock, counter, finish_queue = paras
        is_varg_list = False
        if var is None or len(var) <= 0:
            log.error('Illegal <var> para in <packed_func>')
        if fix is not None and not isinstance(fix, dict):
            assert 0
        if isinstance(var[0], list) or isinstance(var[0], np.ndarray) or isinstance(var[0], tuple):
            is_varg_list = True

        # if 'tips' in fix.keys() and fix['tips']:
        #     opt = Options()
        #     opt.add_argument('--headless')
        #     fix = {'browser':webdriver.Chrome(CHROME_EXE, options=opt)}
        ret_set = []
        for item in var:
            if fix is None:
                if is_varg_list:
                    ret = func(*item)
                else:
                    ret = func(item)
            else:
                if is_varg_list:
                    ret = func(*item, **fix)
                else:
                    ret = func(item, **fix)
            if lock is not None and counter is not None:
                with lock:
                    counter.value += 1
            ret_set.append(ret)
        if lock is not None and finish_queue is not None:
            finish_queue.get()
        return ret_set

    @print_run_time
    def run_list_tasks(self, func, var_args, fix_args=None, en_bar=False, desc=None, tips=False):
        self.init_counter_queue()
        workload = int((len(var_args) + self.task_num) / self.task_num)
        var_sub = [list(var_args[i:i + workload]) for i in range(0, len(var_args), workload)]
        args = [[func, v, fix_args, self.lock, self.counter, self.finish_flag] for v in var_sub]
        bar_max = sum(len(x) for x in var_sub) if en_bar else None
        if en_bar:
            bar_args = (self.counter, self.finish_flag, desc, bar_max)
            self.pool.apply_async(func=self.task_bar, args=bar_args)
        ret_res = self.pool.map(func=self.pack_list_func, iterable=args)
        if isinstance(ret_res[0], dict):
            ret_res = reduce(lambda x, y: {**x, **y}, ret_res)
        elif isinstance(ret_res[0], list):
            ret_res = reduce(lambda x, y: x + y, ret_res)
        return ret_res

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_tasks()
