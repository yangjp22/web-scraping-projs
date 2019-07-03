#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-01-08 15:51:47
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from scrapy import cmdline

# cmdline.execute('scrapy crawl bestseller_single_page'.split())
cmdline.execute('scrapy crawl bestseller_multi_page'.split())
# cmdline.execute('scrapy crawl bestseller_auto_pages'.split())
