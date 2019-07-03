#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-20 23:36:03
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import requests
import fake_useragent

def getHtml(url, newHeader = {}, param = None):
    header = {
    'User-Agent':fake_useragent.UserAgent().random
    }
    header.update(newHeader)
    response = requests.get(url, headers = header, params = param)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text

def main():
    pass

if __name__ == '__main__':
    main()