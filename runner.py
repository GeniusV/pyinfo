#!/usr/local/bin/python3
# -*-encoding: utf-8-*-

# Created by GeniusV on 5/11/18.
from pyinfo.custom_queryer import GenchQueryer

from pyinfo.info import init, start

if __name__ == '__main__':
    init(conf = '/Users/GeniusV/Documents/pythonProject/pyinfo/config.yaml')
    start([GenchQueryer()])
