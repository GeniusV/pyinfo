#!/usr/bin/env python3
# -*-encoding: utf-8-*-

# Created by GeniusV on 5/8/18.

from smtplib import SMTP
from email.mime.text import MIMEText
from email.header import Header

import logging
from scripts import log

fromAddress = 'apple310100@163.com'
password = '55895285599'
subject = 'Daily Info Check'
content = ''
logger = log.get_logger()


def send_email(SMTP_host, from_addr, password, to_addrs, subject, content):
    email_client = SMTP(SMTP_host)
    email_client.login(from_addr, password)
    # create msg
    msg = MIMEText(content, 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')  # subject
    msg['From'] = from_addr
    msg['To'] = to_addrs
    email_client.sendmail(from_addr, to_addrs, msg.as_string())
    email_client.quit()

class Info():
    def __init__(self, text, href):
        self.text = text
        self.href = href

    def __str__(self):
        return '<a href="{}">{}<\\a>'.format(self.href, self.text)

    def __eq__(self, other):
        if isinstance(other, Info) and self.text == other.text and self.href == other.href:
            return True
        else:
            return False

class Queryer():
    def __init__(self, data: dict, domain_name: str, url: str, init_page_num: int):
        self.data = data
        self.name = domain_name
        self.url = url
        self.init_page_num = init_page_num
        self.infos = []


    def get_one_page_infos(self, url):
        """
        Add infos in this page and return the lxml.html of the page.
        :return: the lxml.html tree
        """
        pass

    def next_page_url(self, html):
        """
        return the next page url in html
        :param html:
        :return:
        :rtype: str
        """
        pass

    def get_new_infos(self):
        """
        :rtype: Info
        :param html:
        :return:
        """
        url = self.url
        while self.data[self.name] not in self.infos:
            html = self.get_one_page_infos(url)
            url = self.next_page_url(html)

        self.infos = self.infos[:self.infos.index(self.data[self.name])]
        self.data[self.name] = self.infos[0]
        return self.infos



def run(debug = False):
    logger.setLevel(logging.DEBUG) if debug else logger.setLevel(logging.DEBUG)
    logger.debug("this is the debug log")
    # send_email("smtp.163.com", fromAddress, password, fromAddress, subject  ,'<p><a href="http://www.runoob.com">这是一个链接</a></p>')


if __name__ == "__main__":
    run(debug = True)

