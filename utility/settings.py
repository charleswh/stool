import os
import platform

OFFICE_TDX_ROOT = 'e:\\software\\zd_zsone'
HOME_TDX_ROOT= 'o:\\Program Files\\zd_zsone'
TDX_ROOT = OFFICE_TDX_ROOT if platform.node() == 'NeilWang-L10' else HOME_TDX_ROOT
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
OUT_DIR = os.path.join(ROOT, 'out_dir')

MAX_TASK_NUM = 32
KTYPE = ['D', '60', '30', '15', '5']
PERIORD_TAG = ['day', 'min60', 'min30', 'min15', 'min5']

if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)
