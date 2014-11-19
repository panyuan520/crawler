#!/usr/bin/python
#-*- coding:utf-8 -*-


'''
Created on 2013-8-13
通过python实现自动抓取网上的代理ip和端口

@author: 136354553
'''
import urllib,time,re,logging




URL = 'http://ip.zdaye.com/'


class getProxyIP:
    def format_log(self):
        logging.basicConfig(level=logging.INFO,
                format='%(asctime)s  %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='proxy.log',
                filemode='w+')


        logging.info("ip:        " + "port")
    
    
#   从网页抓去代理 ip ，并整理格式
    def getProxyHtml(self):
#        抓去代理 ip页面的代码
        page = urllib.urlopen(URL)
        html = page.read()
        #print html
        return html
   
    def ipPortRe(self):
#       从页面代码中取出代理 ip和端口
        html = self.getProxyHtml()
        #ip_re = re.compile(r'(((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?))')
        ip_re = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).+\n.+>(\d{1,5})<')
        ip_port = re.findall(ip_re,html)
        print ip_port
        return ip_port
       
       
    def proxyIP(self):
#       格式化输出代理 ip和端口
        ip_port = self.ipPortRe()
#       将代理 ip整理成['221.238.28.158:8081', '183.62.62.188:9999']格式       
        proxyIP = []
        for i in range( 0,len(ip_port)):
            proxyIP.append( ':'.join(ip_port[i]))  
            logging.info(proxyIP[i])
#       将代理 ip整理成[{'http': 'http://221.238.28.158:8081'}, {'http': 'http://183.62.62.188:9999'}]格式       
        proxy_list = []
        for i in range( 0,len(proxyIP)):
            a0 = 'http://%s'%proxyIP[i]
            a1 = { 'http ':'%s'%a0}
            proxy_list.append(a1)
        print proxy_list
        return proxy_list


if __name__ == '__main__':
    time_start = time.time()
    t = getProxyIP()
    t.format_log()
    t.proxyIP()
    time_end = time.time()
    time = time_end - time_start
    print time