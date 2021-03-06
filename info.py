#!/usr/local/bin/python3
# -*-encoding: utf-8-*-

# Created by GeniusV on 5/8/18.
import base64
import json
import logging
import os
import time
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from logging import Logger
from smtplib import SMTP

import requests
import yaml
from lxml import html
from pyinfo import log

content = ''
logger = log.get_logger(to_file = False)  # type: Logger
config = {}
base_header = {
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
}
data = {}


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


def __load_config(file: str):
    global config
    try:
        config = yaml.load(open(file, 'r'))
    except FileNotFoundError:
        logger.error('config file "{}" not found'.format(file))
    return config


def __save_config(file: str):
    yaml.dump(config, stream = open(file, 'w'), default_flow_style = False)


def __load_data(file: str):
    global data
    if not os.path.exists(file):
        __save_data(file)
    with open(file, 'r') as f:
        try:
            raw = json.loads(f.read())  # type: dict
            data = {key: __b64_to_str(raw[key]) for key in raw.keys()}
        except json.decoder.JSONDecodeError as e:
            logger.error('The data file "{}" is broken. We will create a new one instead.'.format(file))
            __save_data(file)


def __save_data(file: str):
    with open(file, 'w') as f:
        f.write(json.dumps({key: __str_to_b64(data[key]) for key in data.keys()},
                           ensure_ascii = False, indent = 2))


def __str_to_b64(string: str):
    return base64.b64encode(string.encode()).decode()


def __b64_to_str(b64: str):
    return base64.b64decode(b64.encode()).decode()


class Info():
    def __init__(self, text: str, href: str, datetime: str = '0000-00-00 00:00'):
        """

        :param text:
        :param href:
        :param datetime: format: yyyy-mm-dd hh:mm
        """
        self.text = text
        self.href = href
        self.datetime = datetime

    def __str__(self):
        return '<p>{}  -  <a href="{}">{}</a></p>'.format(self.datetime, self.href, self.text)

    def __eq__(self, other):
        if isinstance(other, Info) and self.text == other.text and self.href == other.href:
            return True
        else:
            return False

    def __repr__(self):
        return str(self.text)


class Queryer():
    def __init__(self, domain_name: str, url: str, init_page_num: int, init_mode = False):
        """
        :param domain_name:
        :param url:
        :param init_page_num: the num of pages to query when in init mode. And if query page num (in normal mode) is
         bigger than init_page_num, it will get into init mode and retry.
        :param init_mode:
        """
        self.name = domain_name
        self.url = url
        self.init_page_num = init_page_num
        self.infos = []
        self.init_mode = init_mode
        if domain_name not in data or data[domain_name] == "":
            self.init_mode = True

    def get_one_page_infos(self, url):
        """
        Add infos in this page and return the lxml.html of the page.
        :return: the lxml.html tree
        :rtype: html.HtmlElement
        """
        pass

    def next_page_url(self, page):
        """
        return the next page url in html
        :param html:
        :return:
        :rtype: str
        """
        pass

    @staticmethod
    def format_datetime(date, datetime_format):
        return datetime.strptime(date, datetime_format).strftime("%Y-%m-%d %H:%M")

    def formated_infos(self):
        return '<h1>{}</h1>\n'.format(self.name) + '\n'.join([str(info) for info in self.infos])

    def get_new_infos(self):
        """
        :rtype: Info
        :param html:
        :return:
        """
        url = self.url
        if self.init_mode:
            logger.debug('"{}" is in init mode.'.format(self.name))
            for i in range(self.init_page_num):
                html = self.get_one_page_infos(url)
                url = self.next_page_url(html)
        else:
            ct = 0
            while data[self.name] not in [info.text for info in self.infos] and ct < self.init_page_num:
                html = self.get_one_page_infos(url)
                url = self.next_page_url(html)
                ct +=1
            # If query num is bigger tha init page num, use set this queryer to init mode and retry
            if ct >= self.init_page_num:
                self.init_mode = True
                logger.warning('Query "{}" num is bigger than init_page_num = {}.'.format(self.name, self.init_page_num))
                logger.warning('Cannot find the last record.')
                logger.warning('Enable init mode for "{}" and retry.'.format(self.name))
                return self.get_new_infos()
            self.infos = self.infos[:[info.text for info in self.infos].index(data[self.name])]
        if len(self.infos) > 0:
            data[self.name] = self.infos[0].text
        if len(self.infos) == 0:
            return ""
        return self.formated_infos()


def retry_on_network_problem(num = 20, sleep = 60):
    def decorate(f):
        def wrapper(*args, **kwargs):
            ct = num
            while ct:
                logger.debug("Trying query {} {} times remaining..".format(args, ct))
                try:
                    return f(*args, **kwargs)
                except requests.ConnectionError as e:
                    ct -= 1
                    logger.warning("Encount the connection error on {}. Sleeping {} seconds...".format(args, sleep))
                    time.sleep(sleep)
                    logger.warning("Retry query {}, {} times remaining.".format(args, num))
            logger.warning("the network connection is poor.")
            raise e

        return wrapper

    return decorate


def start(runner_list):
    logger.debug("pyinfo in starting...")
    if not config:
        logger.critical("pyinfo has not been init yet, please call init() first.")
    if config['init-mode']:
        for queryer in runner_list:
            queryer.init_mode = True
    infos = []
    if len(runner_list) == 0:
        logger.error("There is no queryer in runner_list")
        exit()
    logger.info('Runner list: {}'.format([runner.name for runner in runner_list]))
    with ThreadPoolExecutor(max_workers = len(runner_list)) as executor:
        futures = {executor.submit(item.get_new_infos): item for item in runner_list}
        for future in as_completed(futures):  # type: Future
            data_set = futures[future]  # type: Queryer
            try:
                infos.append(future.result())
            except Exception as e:
                logger.error("{} generate an error: {}".format(data_set['name'], e))
            else:
                logger.debug("{} done".format(data_set.name))
    logger.info('query complete')
    __save_data(config['data-file'])

    body = '<br><br>'.join(infos)
    logger.info('Sending mail..')
    try:
        mail_config = config['mail']  # type: dict
        send_email(mail_config['smpt'], mail_config['from-address'], mail_config['password'], mail_config['receiver'],
                   mail_config['subject'], body)
    except Exception as e:
        logger.error("Send mail error!!")
        raise e
    else:
        logger.info('Mail sending complete.')


def init(conf = "config.yaml"):
    global logger
    logger.debug("pyinfo is initializing...")
    __load_config(conf)
    logger = log.get_logger(filepath = config['log']['path'], name = "Main_Logger")
    __load_data(config['data-file'])
    logger.setLevel(logging.DEBUG) if config['log']['level'] == "debug" else logger.setLevel(logging.INFO)
