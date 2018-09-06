# -*- coding: utf-8 -*-
import logging
import sys
import os

log = logging.getLogger('STOOL')
formatter = logging.Formatter('%(asctime)s %(levelname)-8s : %(message)s')

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
path = os.path.join(path, 'stool.log')
file_handler = logging.FileHandler(path)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter

log.addHandler(file_handler)
log.addHandler(console_handler)

log.setLevel(logging.INFO)
