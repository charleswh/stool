# -*- coding:utf-8 -*-
import sys
import argparse
import datakit


parser = argparse.ArgumentParser(description='Integrated share tool for NEIL')
parser.add_argument('-d',
                    help='Download share data by using TuShare and make local database(csv).',
                    action='store_true',
                    dest='is_download')


if __name__ == '__main__':
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
    else:
        if args.is_download:
            datakit.update_local_data()
