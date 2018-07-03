# -*- coding:utf-8 -*-

from .log import log
import subprocess


SADDR = r'noodleormeat@163.com'
SPW = r'pqur888'
SSREVER = r'smtp.163.com'
RADDR = r'noodleormeat@163.com'


def set_blat(srv=SSREVER, saddr=SADDR):
    cmd = r'blat -install {} {} 3 25'.format(srv, saddr)
    print(cmd)


def send(cont, atta, subj, saddr=SADDR, taddr=RADDR, pw=SPW):
    cmd = r'blat -body "{}" -to {} -u {} -pw {} -subject "{}"'.format(
        cont, taddr, saddr.split('@')[0], pw, subj
        )
    # cmd = ['blat', '-body', cont, '-to', taddr, '-u', saddr.split('@')[0], '-pw', pw, '-subjext', subj]
    aa = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    so, se = aa.communicate(input=None)
    if se == '':
        print(so)
        print('Send mail successfully!')
    else:
        print(se)


