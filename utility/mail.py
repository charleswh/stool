# -*- coding:utf-8 -*-
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.utils import parseaddr, formataddr
import smtplib
import os
from utility import *
import win32com.client as win32c


EXE_CLICKIT = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'bins', 'ClickIt.exe')

ADDR = {'o': 'charles_wh@outlook.com',
        'n': 'noodleormeat@163.com',
        'c': 'neilwang@zhaoxin.com'}

SRV = {'163': 'smtp.163.com',
       'c': 'email.zhaoxin.com',
       'o': 'eas.outlook.com'}


def outlook_send(body, subj):
    outlook_handler = win32c.Dispatch('outlook.application')
    mail_handler = outlook_handler.CreateItem(0)
    mail_handler.To = ADDR['o']
    mail_handler.Subject = subj
    mail_handler.Body = body
    cmd = 'start /MIN {}'.format(EXE_CLICKIT)
    os.system(cmd)
    mail_handler.Send()
    cmd = 'taskkill /f /im ClickIt.exe'
    run_cmd(cmd)


def mail_test():
    py_send('aa', 'tsets', ['c:\\Users\\Charl\\Desktop\\th0002_backup.7z'])


def py_attach(file:str):
    file_name = file.split('\\')[-1]
    with open(file, 'rb') as f:
        contype = 'application/octet-stream'
        maintype, subtype = contype.split('/', 1)
        atta = MIMEBase(maintype, subtype, filename=file_name)
        atta.add_header('Content-Disposition', 'attachment', filename=file_name)
        atta.add_header('Content-ID', '<0>')
        atta.add_header('X-Attachment-Id', '0')
        atta.set_payload(f.read())
        encoders.encode_base64(atta)
    return atta


def py_send(subj, body=None, atta_files:list=None):
    mail = MIMEMultipart()
    mail['from'] = 'neilwang'
    mail['to'] = ADDR['o']
    mail['subject'] = subj
    mail.attach(MIMEText(body if body is not None else '', 'plain', 'utf-8'))

    if atta_files is not None:
        for file in atta_files:
            atta = py_attach(file)
            mail.attach(atta)
    try:
        server = smtplib.SMTP(SRV['o'], 25)
        server.ehlo()
        server.starttls()
        server.login(ADDR['o'], '0q164b13')
        log.info('Login email server with user {}'.format(ADDR['o']))
        server.sendmail(ADDR['o'], ADDR['o'], mail.as_string())
        log.info('Sending mail...')
        server.quit()
        log.info('Success!')
    except smtplib.SMTPException as err:
        print(err)
#
#
# def send(cont, atta, subj, srv=SSREVER, saddr=SADDR, taddr=RADDR, pw=SPW):
#     cmd = r'blat -subject "{}" -body "{}" -to {} -f {} -u {} -server {}'.format(
#         subj, cont, taddr, saddr, saddr.split('@')[0], srv)
#     run_cmd(cmd)


if __name__ == '__main__':
    # send(cont='aa', atta=None, subj='aa')
    pass
