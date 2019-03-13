import os
import shutil
from glob import glob
from utility.misc import run_cmd
from utility.log import log
from utility.mail import py_send
from utility.timekit import time_str
from setting.settings import sets


def make_list_of_t0002(template_path):
    p = template_path + ('*' if template_path[-1] == '\\' else '\\*')
    os.rename(sets.T0002_LIST, sets.T0002_LIST + '.bak')
    with open(sets.T0002_LIST, 'w') as f:
        for i in glob(p):
            print(i.split('\\')[-1], file=f)
    log.info('Make th0002 list done.')


def backup_t0002(src_path, en_compress=True):
    dst_folder_name = 't0002_backup'
    dst_path = os.path.join(os.getcwd(), dst_folder_name)
    log.info('Backup TDX customer data...')
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)
    else:
        shutil.rmtree(dst_path)
        os.mkdir(dst_path)
    if not os.path.exists(sets.T0002_LIST):
        log.error(r'Can not find {}'.format(sets.T0002_LIST))
        exit(0)

    src_list = glob(os.path.join(src_path, '*'))
    with open(sets.T0002_LIST, 'r') as f:
        t0002_list = filter(None, f.read().split('\n'))
    for i in t0002_list:
        if '*' in i:
            key = i.split('.')[-1]
            key_list = list(filter(lambda x: key in x, src_list))
            for k in key_list:
                shutil.copy(os.path.join(src_path, k), dst_path)
        else:
            copy_func = shutil.copy if '.' in i else shutil.copytree
            dst_tmp = dst_path if '.' in i else os.path.join(dst_path, i)
            copy_func(os.path.join(src_path, i), dst_tmp)

    if en_compress:
        cmd = '{} a -t7z {} {}\*'.format(sets.EXE_7Z, dst_folder_name, os.path.join(dst_path, ))
        run_cmd(cmd)
        shutil.rmtree(dst_path)
        zip_full_path = os.path.realpath(dst_folder_name+'.7z')
        subj = 'stool backup' + time_str()
        py_send(subj=subj, atta_files=[zip_full_path])
        os.remove(zip_full_path)


def recover_t0002(dst_path, en_compress=True):
    src_folder_name = 't0002_backup'
    src_path = os.path.join(src_folder_name, '*.*')
    if os.path.exists(os.path.join(dst_path, 'pad')):
        shutil.rmtree(os.path.join(dst_path, 'pad'))

    if en_compress:
        cmd = '{} x -y {}.7z -o{}'.format(sets.EXE_7Z, src_folder_name, dst_path)
        run_cmd(cmd)
        os.remove('{}.7z'.format(src_folder_name))
    else:
        cmd = 'xcopy {} {} /S /E /Y /Q'.format(src_path, dst_path)
        run_cmd(cmd)
        shutil.rmtree(src_folder_name)

    from glob import glob
    pad_dir = os.path.join(dst_path, 'pad')
    tip_dir = os.path.join(dst_path, 'tips')
    pad_files = glob(os.path.join(pad_dir, '*.sp'))
    for file in pad_files:
        u = 0
        l = []
        with open(file, 'r') as f:
            for line in f:
                if 'UnitStr=通用浏览器' in line:
                    f = 1
                if f == 1 and 'Url=' in line and 'com' not in line:
                    l.append('Url={}'.format(os.path.join(tip_dir, 'xxxxxx.html\n')))
                    u = 1
                    f = 0
                else:
                    l.append(line)
        if u == 1:
            with open(file, 'w') as f:
                f.write(''.join(l))