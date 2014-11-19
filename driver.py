#encoding:utf-8

import time
import pickle
import hashlib
import traceback
import gevent
from datetime import datetime as dt
from configs import DB, REDIS as R, FILTER, QUEUE, getlogger
from bson.objectid import ObjectId as _id

logger = getlogger(__name__)




def push_url(href, head_type, kmap={}): 
    if not chexists(FILTER, href):
        print 'kmap', kmap
        cpush(QUEUE, href)
        chset(FILTER, href, 1)
        kmap.update({'head_type':head_type})
        if head_type == 1:
            DB.city.save(kmap)
        elif head_type == 2:
            DB.sport.save(kmap)
        elif head_type == 3:
            DB.sport_list.save(kmap)
            
        
def pop_url(head_type, href):
    result = {}
    if chexists(FILTER, href):
        if head_type == 1:
            return DB.city.find_one({'head_type':head_type, 'href':href})
        elif head_type == 2:
            return DB.sport.find_one({'head_type':head_type, 'href':href})
        elif head_type == 3:
            return DB.sport_list.find_one({'head_type':head_type, 'href':href})
    return result
    
    
def save_sport(item):
    if item.get('title'):
        if item.get('_id'):
            del item['_id']
        DB.sport_detals.save(item)
        
        
def cpop(key):
    return R.lpop(key)
    
def cpush(key, value):
    R.rpush(key, value)
    
def clen(key):
    return R.llen(key)
    
def chget(pointer, key):
    return R.hget(pointer, key)
    
def chset(pointer, key, val):
    R.hset(pointer, key, val)
    
def chlen(pointer):
    return R.hlen(pointer)
 
def chexists(pointer, key):
    return R.hexists(pointer, key)
    
def chkeys(pointer):
    return R.hkeys(pointer)
    
def chdel(pointer, key):
    R.hdel(pointer, key)
    
   
def zadd(pointer, key):
    R.sadd(pointer, key)

def zrandom(pointer):
    return R.srandmember(pointer)
    
def zlen(pointer):
    return R.scard(pointer)
    
def zproxy(pointer):
    ip =  zrandom(pointer)
    if ip:
        ips = ip.split("://")
        if len(ips) == 2:
            return {ips[0]:ip}
    
