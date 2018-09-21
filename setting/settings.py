import os
import platform

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
OUT_DIR = os.path.join(ROOT, 'out_dir')
TIP_FOLDER = os.path.join(OUT_DIR, 'tips')
CSV_DIR = os.path.join(OUT_DIR, 'data_csv')
INFO_FILE = os.path.join(OUT_DIR, 'info.csv')
CONCEPT_FILE = os.path.join(OUT_DIR, 'concept.csv')
TRADE_DATE_FILE = os.path.join(OUT_DIR, 'trade_date.csv')

BIN_ROOT = os.path.join(ROOT, 'bins')
EXE_CLICKIT = os.path.join(BIN_ROOT, 'bins', 'ClickIt.exe')
EXE_7Z = os.path.join(BIN_ROOT, 'bins', '7z.exe')

SETTING_ROOT = os.path.join(ROOT, 'setting')
T0002_LIST = os.path.join(SETTING_ROOT, 'th0002.list')

MONITOR_ROOT = os.path.join(ROOT, 'monitor')
TDX_IMPORT_LIST = os.path.join(MONITOR_ROOT, 'tdx.txt')
MANUAL_LIST = os.path.join(MONITOR_ROOT, 'manual.txt')

OFFICE_TDX_ROOT = 'e:\\software\\zd_zsone'
HOME_TDX_ROOT= 'o:\\Program Files\\zd_zsone'
TDX_ROOT = OFFICE_TDX_ROOT if platform.node() == 'NeilWang-L10' else HOME_TDX_ROOT

MAX_TASK_NUM = 32
KTYPE = ['D', '60', '30', '15', '5']
PERIORD_TAG = ['day', 'min60', 'min30', 'min15', 'min5']

if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)
