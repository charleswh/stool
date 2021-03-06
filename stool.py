# -*- coding:utf-8 -*-
import sys
import argparse
from datakit.datakit import data_kit
from crawler import *
from analysis import *
from utility import *

parser = argparse.ArgumentParser(description='Integrated stock tool for NEIL',
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-d',
                    action='store_true',
                    dest='down_all',
                    help='down all data: k data, info data, tips data')
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
parser.add_argument('--local_data',
                    action='store_true',
                    help='download share data by using TuShare and make local database(csv)\n')
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
parser.add_argument('--blakfp',
                    action='store_true',
                    help='download blakfp papers')
parser.add_argument('--down_tips',
                    action='store_true',
                    help='download tips infomation\n')
parser.add_argument('--copy_tips',
                    action='store_true',
                    help='copy tips files to tdx dir\n')
parser.add_argument('--modify_tips',
                    nargs=4,
                    help='modify tips files\'s font, color and size')
parser.add_argument('--connectable_ip',
                    action='store_true',
                    help='get connectalbe ips from local manual collect raw ips')
parser.add_argument('--refresh_ip_lib',
                    action='store_true',
                    help='sort all local valid ips')
parser.add_argument('--check_proxy',
                    action='store_true',
                    help='check valid ips for tip use')
parser.add_argument('--blk_process',
                    action='store_true',
                    help='do stock collection')
parser.add_argument('--url2wiz',
                    action='store_true',
                    help='save url web to wiznote\n')
parser.add_argument('--test',
                    action='store_true',
                    help='test function entry')

if __name__ == '__main__':
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
    else:
        if args.down_all is True:
            data_kit.down_k()
            post.blk_process()
            tips.down_tips()
            tips.copy_tips_files()

        if args.local_data is True:
            data_kit.down_k()

        if args.t0002_template is not None:
            backup.make_list_of_t0002(args.t0002_template)

        if args.backup_src_path is not None:
            backup.backup_t0002(args.backup_src_path)

        if args.recover_dst_path is not None:
            backup.recover_t0002(args.recover_dst_path)

        if args.blakfp is True:
            blak.blakfp_entry()

        if args.connectable_ip is True:
            proxy.connectable_ip()

        if args.refresh_ip_lib is True:
            proxy.refresh_ip_lib()

        if args.down_tips is True:
            tips.down_tips()

        if args.copy_tips is True:
            tips.copy_tips_files()

        if args.modify_tips is not None:
            tips.modify_tips(args.modify_tips)

        if args.check_proxy is True:
            tips.check_valid_tips_ip()

        if args.blk_process is True:
            post.blk_process()

        if args.url2wiz is True:
            wx_crawler.save2wiz()

        if args.test:
            # mail_test()
            dbga = 0
