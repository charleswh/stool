from tqdm import tqdm
import ctypes
import multiprocessing as mp
from functools import reduce
from utility.log import log
from utility.timer import TimerCount, print_run_time

MAX_TASK_NUM = mp.cpu_count() * 5

def task_bar(c, q, d=None, bar_max=None):
    if bar_max is None:
        log.error('Wrong <bar max> para when doing <task_bar>')
    with tqdm(total=bar_max, desc=d, ascii=True) as tbar:
        while c.value <= bar_max:
            tbar.update(c.value - tbar.n)
            if q.qsize() == 0:
                tbar.update(bar_max - tbar.n)
                break


def pack_func(paras):
    func, var, fix, lock, counter, finish_queue = paras
    if var is None or len(var) <= 0:
        log.error('Illegal <var> para in <pack_func>')

    OBJ = 0
    LIST = 1
    DICT = 2

    fix_type = None if fix is None else \
        LIST if isinstance(fix, list) else DICT if isinstance(fix, dict) else OBJ
    ret_set = []
    for item in var:
        if fix is None:
            ret = func(item)
        else:
            if fix_type == OBJ:
                ret = func(item, fix)
            elif fix_type == LIST:
                ret = func(item, *fix)
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
def multi_task(func, var_args, fix_args=None, manual_task_num=0, enable_bar=False,
               desc=None, merge_result=True):
    task_num = manual_task_num if manual_task_num > 0 else MAX_TASK_NUM
    task_num = MAX_TASK_NUM if len(var_args) >= task_num else len(var_args)
    progress_num = task_num + 1 if enable_bar else task_num
    if enable_bar:
        m = mp.Manager()
        l = m.Lock()
        c = m.Value(ctypes.c_uint32, 0)
        q = m.Queue(task_num)
        while q.qsize() != task_num:
            q.put('f')
        inner_args = [[func, v, fix_args, l, c, q] for v in var_args]
        total_num = sum(len(x) for x in var_args)
    else:
        l = c = q = total_num = None
        inner_args = (func, list(var_args), fix_args)
    pool = mp.Pool(processes=progress_num)
    if enable_bar:
        pool.apply_async(func=task_bar, args=(c, q, desc, total_num))
        ret_res = pool.map(func=pack_func, iterable=inner_args)
    else:
        t = 'Multi-Task' if desc is None else 'Multi-Task of {}'.format(desc)
        with TimerCount(t):
            ret_res = pool.map(func=pack_func, iterable=inner_args)
    pool.close()
    pool.join()
    if isinstance(ret_res[0], dict):
        ret_res = reduce(lambda x, y: {**x, **y}, ret_res) if merge_result else ret_res
    elif isinstance(ret_res[0], list):
        ret_res = reduce(lambda x, y: x + y, ret_res) if merge_result else ret_res
    return ret_res
