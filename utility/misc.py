import subprocess
import os
import shutil
from glob import glob
from utility import *
from setting.settings import T0002_LIST, EXE_7Z


def run_cmd(cmd, show_result=True):
    print(cmd)
    sp = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = sp.communicate(input=None)
    if error == '':
        if show_result:
            print(output)
    else:
        print(error)


def make_list_of_th0002(template_path):
    p = template_path + ('*' if template_path[-1] == '\\' else '\\*')
    with open(T0002_LIST, 'w') as f:
        for i in glob(p):
            print(i.split('\\')[-1], file=f)
    log.info('Make th0002 list done.')


def backup_th0002(src_path, en_compress=True):
    dst_folder_name = 'th0002_backup'
    dst_path = os.path.join(os.getcwd(), dst_folder_name)
    log.info('Backup TDX customer data...')
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)
    else:
        shutil.rmtree(dst_path)
        os.mkdir(dst_path)
    if not os.path.exists(T0002_LIST):
        log.error(r'Can not find {}'.format(T0002_LIST))
        exit(0)
    with open(T0002_LIST, 'r') as f:
        list = filter(None, f.read().split('\n'))
    for i in list:
        copy_func = shutil.copy if '.' in i else shutil.copytree
        dst_tmp = dst_path if '.' in i else os.path.join(dst_path, i)
        copy_func(os.path.join(src_path, i), dst_tmp)

    if en_compress:
        cmd = '{} a -t7z {} {}\*'.format(EXE_7Z, dst_folder_name, os.path.join(dst_path, ))
        run_cmd(cmd)
        shutil.rmtree(dst_path)
        zip_full_path = os.path.realpath(dst_folder_name+'.7z')
        subj = 'stool backup' + time_str()
        py_send(subj=subj, atta_files=[zip_full_path])
        os.remove(zip_full_path)


def recover_th0002(dst_path, en_compress=True):
    src_folder_name = 'th0002_backup'
    src_path = os.path.join(src_folder_name, '*.*')
    if en_compress:
        cmd = '{} x -y {}.7z -o{}'.format(EXE_7Z, src_folder_name, dst_path)
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
        c = None
        f = 0
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