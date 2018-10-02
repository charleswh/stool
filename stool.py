# -*- coding:utf-8 -*-
import sys
import argparse
from datakit.data_local import update_local_database
from crawler.blak import blakfp_entry
from crawler.tips import down_tips, update_tips
from utility.misc import backup_t0002, recover_t0002, make_list_of_t0002


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
parser.add_argument('--make_t0002_list',
                    type=str,
                    dest='t0002_template',
                    help='make th0002 data list based on current template path')
parser.add_argument('--backup_t0002',
                    dest='backup_src_path',
                    help='make backup for t0002')
parser.add_argument('--recover_t0002',
                    dest='recover_dst_path',
                    help='recover for t0002')
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
            if args.down_mode == 'tips':
                down_tips()
            else:
                update_local_database(args.down_mode)
        if args.t0002_template is not None:
            make_list_of_t0002(args.t0002_template)
        if args.backup_src_path is not None:
            backup_t0002(args.backup_src_path)
        if args.recover_dst_path is not None:
            recover_t0002(args.recover_dst_path)
        if args.update_tips is not None:
            update_tips(args.update_tips)
        if args.blakfp is True:
            blakfp_entry()
        if args.test:
            # mail_test()
            dbg = 0
