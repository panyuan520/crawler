#encoding:utf-8

import os
import logging  
import pymongo
import redis


DB_NAME = 'crawler'

DB_HOST         = 'localhost'
REDIS_HOST      = 'localhost'

  

DB              = getattr(pymongo.MongoClient(host=DB_HOST),DB_NAME)
REDIS           = redis.Redis(host=REDIS_HOST)

FILTER              = "filter"
QUEUE               = "queue"
PROXY               = "proxy"

               
# 创建一个logger  
def getlogger(name):
    logger = logging.getLogger(name)  
    logger.setLevel(logging.DEBUG)  
      
    # 创建一个handler，用于写入日志文件  
    fh = logging.FileHandler('chart.log')  
    fh.setLevel(logging.DEBUG)  
      
    # 再创建一个handler，用于输出到控制台  
    ch = logging.StreamHandler()  
    ch.setLevel(logging.DEBUG)  
      
    # 定义handler的输出格式  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter)  
      
    # 给logger添加handler  
    logger.addHandler(fh)  
    logger.addHandler(ch)  
    
    return logger
  
