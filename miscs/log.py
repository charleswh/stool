# -*- coding: utf-8 -*-
import logging
import sys

log = logging.getLogger('STOOL')
formatter = logging.Formatter('%(asctime)s %(levelname)-8s : %(message)s')

file_handler = logging.FileHandler('stool.log')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter

log.addHandler(file_handler)
log.addHandler(console_handler)

log.setLevel(logging.INFO)
