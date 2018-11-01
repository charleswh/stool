# -*- coding:utf-8 -*-
import sys
import argparse
from datakit.datakit import down_k_data_local
from crawler.blak import blakfp_entry
from crawler.tips import down_tips, copy_tips_files, modify_tips, check_valid_proxy_ip
from crawler.proxy import down_proxy_ip
from utility.misc import backup_t0002, recover_t0002, make_list_of_t0002


parser = argparse.ArgumentParser(description='Integrated share tool for NEIL',
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
parser.add_argument('--down_proxy',
                    action='store_true',
                    help='down proxy IPs')
parser.add_argument('--check_proxy',
                    action='store_true',
                    help='check proxy IPs')
parser.add_argument('--test',
                    action='store_true',
                    help='test function entry')


if __name__ == '__main__':
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
    else:
        if args.down_all is True:
            down_k_data_local()
            down_proxy_ip()
            check_valid_proxy_ip()
            down_tips()
            copy_tips_files()
        if args.local_data is True:
            down_k_data_local()
        if args.t0002_template is not None:
            make_list_of_t0002(args.t0002_template)
        if args.backup_src_path is not None:
            backup_t0002(args.backup_src_path)
        if args.recover_dst_path is not None:
            recover_t0002(args.recover_dst_path)
        if args.blakfp is True:
            blakfp_entry()
        if args.down_tips is True:
            down_tips()
        if args.copy_tips is True:
            copy_tips_files()
        if args.modify_tips is not None:
            modify_tips(args.modify_tips)
        if args.down_proxy is True:
            down_proxy_ip()
        if args.check_proxy is True:
            check_valid_proxy_ip()
        if args.test:
            # mail_test()
            dbg = 0

# TODO: 分割tips的下载，否则失败率太高
# TODO: 选股部分，板块生成
# TODO: 定时系统