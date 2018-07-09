# -*- coding:utf-8 -*-
import sys
import argparse
from datakit.data import update_local_database


parser = argparse.ArgumentParser(description='Integrated share tool for NEIL',
                    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-d',
                    type=int,
                    help='download share data by using TuShare and make local database(csv)\n'
                         '0 : down basic data and info data\n'
                         '1 : down basic data only\n'
                         '2 : down info data only',
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

if __name__ == '__main__':
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
    else:
        if args.down_mode is not None:
            update_local_database(args.down_mode)
        elif args.statistics_after_close:
            print('1')
        elif args.start_monitor:
            print('1')
        elif args.after_filtering:
            print('1')
