# -*- coding:utf-8 -*-
import sys
import argparse
from utility import *
from datakit import *
from crawler.blak import blakfp_entry


parser = argparse.ArgumentParser(description='Integrated share tool for NEIL',
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-d',
                    type=str,
                    help='download share data by using TuShare and make local database(csv)\n'
                         'all   : down basic data and info data\n'
                         'basic : down basic data only\n'
                         'info  : down info data only\n'
                         'tips  : down tips',
                    dest='down_mode')
parser.add_argument('-s',
                    action='store_true',
                    dest='statistics_after_close',
                    help='do after close statistics')
parser.add_argument('-m',
                    action='store_true',
                    dest='start_monitor',
                    help='start realtime monitor')
parser.add_argument('-x',
                    action='store_true',
                    dest='after_filtering',
                    help='filter and choose stocks after close')
parser.add_argument('--make_th0002_list',
                    type=str,
                    dest='th0002_template',
                    help='make th0002 data list based on current template path')
parser.add_argument('--backup_th0002',
                    dest='backup_src_path',
                    help='make backup for th0002')
parser.add_argument('--recover_th0002',
                    dest='recover_dst_path',
                    help='recover for th0002')
parser.add_argument('--update_tips',
                    nargs=4,
                    help='test function entry')
parser.add_argument('--blakfp',
                    action='store_true',
                    help='download blakfp papers')
parser.add_argument('--test',
                    action='store_true',
                    help='test function entry')


if __name__ == '__main__':
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
    else:
        if args.down_mode is not None:
            update_local_database(args.down_mode)
        if args.th0002_template is not None:
            make_list_of_th0002(args.th0002_template)
        if args.backup_src_path is not None:
            backup_th0002(args.backup_src_path)
        if args.recover_dst_path is not None:
            recover_th0002(args.recover_dst_path)
        if args.update_tips is not None:
            update_tips(args.update_tips)
        if args.blakfp is True:
            blakfp_entry()
        if args.test:
            mail_test()
