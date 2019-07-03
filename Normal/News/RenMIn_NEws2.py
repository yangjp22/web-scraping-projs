# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 20:24:28 2018

@author: dell
"""

def get_number(url):
    num_html = get_html(url)
    num_inter = etree.HTML(num_html)
    
    join_count = num_inter.xpath('/html/body/div[2]/div[3]/div[3]/div[2]/p/span[1]/span[1]/text()')
    if len(join_count) != 0:
        join_count = join_count[0]
        
    count = num_inter.xpath('/html/body/div[2]/div[3]/div[3]/div[2]/p/span[1]/span[2]/text()')
    if len(count) != 0:
        count = count[0]
    
    return join_count,count

 Comment = inter.xpath('//*[@id="rwb_bbstop"]/a/@href')
    if len(Comment) != 0:
        Join ,Com = get_number(Comment[0])
        final_list.append(('评论人数：',Com))
        final_list.append(('参与人数：',Join))