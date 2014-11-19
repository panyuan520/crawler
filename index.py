#encoding:utf-8

import sys
import urllib2
import chardet
import time
import redis
from BeautifulSoup import BeautifulSoup
import driver
import traceback
from gevent.pool import Pool
from configs import FILTER, QUEUE, PROXY, getlogger

logger = getlogger(__name__)




class Crawler(object):

    def __init__(self):
        logger.info("start crawler....")
        
    def fetch(self, url):
        try:
            proxy = driver.zproxy(PROXY)
            print 'proxy url %s, fetch url%s' % (proxy, url)
            if proxy:
                proxy_support = urllib2.ProxyHandler(proxy)  
                opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)  
                urllib2.install_opener(opener) 
            
            request = urllib2.Request(url)
            request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            request.add_header('Referer', self.abs_href)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36')
            return urllib2.urlopen(request).read()
        except Exception as e:
            logger.error("fetch url error %s" %  str(e))
            driver.cpush(QUEUE, url)
            traceback.print_exc()
        
        
    def tagA(self, body):
        soup = BeautifulSoup(''.join(body))
        return soup.findAll('a')
        
    
    def strip(self, title):
        title = title.replace("$nbsp;", " ")
        title = title.replace("&amp;", "&")
        return title.strip()
    
    def find(self, body, tag, attrs=None):
        soup = BeautifulSoup(''.join(body))
        if attrs:
            return soup.find(tag, attrs=attrs)
        else:
            return soup.find(tag)
     
    def findAll(self, body, tag, attrs=None):
        soup = BeautifulSoup(''.join(body))
        if attrs:
            return soup.findAll(tag, attrs=attrs)
        else:
            return soup.findAll(tag)
        

class Zdy(Crawler):
    def __init__(self, url):
        self.url = url
        self.abs_href = "http://ip.zdaye.com/"
        Crawler.__init__(self)
        
    def item(self, body):
        try:
            soup = BeautifulSoup(''.join(body))
            table = soup.find('table', attrs={"id":"ip_list"})
            if table:
                trs = table.findAll("tr")
                for index, tr in enumerate(trs):
                    if index > 0:
                        td = tr.findAll("td")
                        if len(td) == 10:
                            ip, port, head_type = td[2], td[3], td[6]
                            ip, port, head_type = self.strip(ip.text), self.strip(port.text), self.strip(head_type.text).lower()
                            if head_type.find('socks') == -1:
                                print head_type
                                driver.zadd(PROXY, "%s://%s:%s" % (head_type, ip, port))
                                print driver.zlen(PROXY)
        except Exception as e:
            logger.info(str(e))
                        
        
    def proxy(self):
        for i in range(1, 182):
            print "http://www.xici.net.co/nn/%d" % i
            body = self.fetch("http://www.xici.net.co/nn/%d" % i)
            self.item(body)
        for i in range(1, 123):
            body = self.fetch("http://www.xici.net.co/wn/%d" % i)
            self.item(body)
            
    def __call__(self):
        self.proxy()
        
class Dianping(Crawler):

    def __init__(self, url):
        self.url = url
        self.abs_href = "http://www.dianping.com"
        Crawler.__init__(self)
        
    def citylist(self, url):
        try:
            body = self.fetch(url)
            for are in self.find(body, "ul", {"id":"divArea"}).findAll("li"):
                positin  = are.find("strong", attrs={"class":"vocabulary"}).text
                province = are.find("dt")
                if province:
                    province =  province.text
                citys = are.findAll("a")
                for city in citys:
                    href = self.abs_href + city.get('href') + "/sports"
                    city = city.text
                    #if city in [u'上海', u'天津', u'石家庄', u'鄂州']:
                        print city, province, href
                    driver.push_url(href, 1, {'province':province, 'city':city, 'href':href})
        except Exception as e:
            logger.info("citylist error:%s" % str(e))
                
        
    def sport(self, url):
        try:
            description = driver.pop_url(1, url)
            body = self.fetch(url)
            lis = self.findAll(body, "li", {"class":"term-list-item"})
            if len(lis) > 2:
                ali = lis[1].findAll("a")
                for al in ali:
                    href, text =  self.abs_href + al.get('href'), al.text
                    if text.find(u'更多') == -1:
                        #logger.info("sport:%s" %  {"href":href, "text":text, "description":description})
                        driver.push_url(href, 2, {'category':text, 'href':href, 'city_id':description.get('_id')})
            else:
                logger.info("sport no sport:%s" % url)
        except Exception as e:
            print traceback.print_exc()
            logger.error("sport error:%s" % str(e))
            
        
    def search(self, url):
        try:
            description = driver.pop_url(2, url)
            print "description", description
            if True:
                body = self.fetch(url)
                for titles in self.findAll(body, "div", {"class":"tit"}):
                    title = titles.find("a")
                    logger.info("search title:%s" % titles.text)
                    if title:
                        thref = title.get("href")
                        if thref:
                            thref = self.abs_href + thref
                            print "description", description
                            logger.info("search 1:%s" % {"thref":thref, "description":description})
                            driver.push_url(thref, 3, {'href':thref, 'title':title.text, 'city_id':description.get('city_id'), 'sport_id':description.get('_id')})
                            
                pages = self.findAll(body, "a", {"class":"PageLink"})
                if len(pages) > 0:
                    page = pages[-1]
                    href = self.abs_href + page.get('href')
                    #driver.push_url(href)
                    print "page", page, page.text
                    for i in range(2, int(page.text)+1):
                        aid, sport_href = None, None
                        if href.find("aid=") > -1:
                            aid = href[href.rindex("?aid"):]
                            href2 = href[:href.rindex("?aid")]
                        else:
                            href2 = href
                        sport_href = href2[0:href2.rindex("p")+1] + str(i)
                        if aid: sport_href = sport_href + aid 
                        logger.info('sport_list:%s' % sport_href)
                        driver.push_url(sport_href, 2, {'category':description.get('category'), 'href':sport_href, 'city_id':description.get('city_id')})
            else:
                logger.info("search driver.pop_url 2 url:%s" % url)
        except Exception as e:
            print traceback.print_exc()
            logger.info("search error:%s" % str(e))
               
               
    def shop(self, url):
        try:
            result  = driver.pop_url(3, url)
            logger.info("shop result:%s" % result)
            body = self.fetch(url)
            soup = BeautifulSoup(''.join(body))
            title = soup.find("h1", attrs={"class":"shop-name"})
            if title:
                result['title'] = title.text
            
            region = soup.find("span", attrs={"itemprop":"locality region"})
            if region: result['region'] = region.text
            
            address = soup.find("span", attrs={"itemprop":"street-address"})
            if address: result['address'] = address.text
            
            tel = soup.find("span", attrs={"itemprop":"tel"})
            if tel: result['tel']  = tel.text
              
            others = {}
            other = soup.find("div", attrs={"class":"other J-other Hide"})
            if other:
                other_items = other.findAll("p")
                for other_item in other_items:
                    info_name = other_item.find("span", attrs={"class":"info-name"})
                    if info_name:
                        info_name = info_name.text
                        if info_name.find(u"别") > -1 or info_name.find(u"营业") > -1:
                            info_item = other_item.find("span", attrs={"class":"item"})
                            if info_item:
                                others.update({info_name:info_item.text})
                        elif info_name.find(u"分类标签") > -1:
                            other_tags = []
                            tags = other_item.findAll("span", attrs={"class":"item"})
                            for tag in tags:
                                tag_a = tag.find("a")
                                if tag_a:
                                    other_tags.append(tag_a.text)
                            others.update({info_name:other_tags})
                            
            
            photos = soup.find("img", attrs={"itemprop":"photo"})
            if photos: result['photos']  = photos.src
            if len(others) > 0:  result['others']  = others
            logger.info("shop:%s" % result)
            driver.save_sport(result)
        except Exception as e:
            logger.info("shop error:%s" % str(e))
        
        
    def handel(self, url): 
        if url.find("citylist") > -1:
            self.citylist(url)
        elif url.find("sports") > -1:
            self.sport(url)
        elif url.find("search") > -1:
            self.search(url)
        elif url.find("shop") > -1:
            self.shop(url)
        else:
            logger.info("this url no handel:%s" % url)
            
        
    def __call__(self):
        print "starting ......"
        driver.cpush(QUEUE, self.url)
        while driver.clen(QUEUE) > 0:
            url = driver.cpop(QUEUE)
            print 'start handel url:%s' % url
            self.handel(url)
        #pool.join()    
        

class Pga(Crawler):
    def __init__(self, url):
        Crawler.__init__(self)
        self.url = url
    
    def tagAddress(self, body):
        soup = BeautifulSoup(''.join(body))
        title = soup.find("div", attrs={"class":"views-field-title"}).span.text
        address = soup.find("div", attrs={"class":"views-field-address"}).span.text
        zip = soup.find("div", attrs={"class":"views-field-city-state-zip"}).span.text
        return title, address, zip
        
    def courses(self):
        body = self.fetch(self.url)
        for i in self.tagA(body):
            href =  i.get('href')
            print href
            if href and href.find("/golf-courses/details/") > -1 and href.find("?") == -1:
                province, href = i.text, "http://www.pga.com" + href
                if province and href:
                    print href
                    body = self.fetch(href)
                    for i2 in self.tagA(body):
                        href = i2.get('href')
                        if href and href.find("/golf-courses/details/") > -1 and href.find("?") == -1:
                            city, href = i2.text, "http://www.pga.com" + href
                            if not DB.list.find_one({'href':href}):
                                body = self.fetch(href)
                                title, address, zip = self.tagAddress(body)
                                print province, city, title, address, zip
                                DB.list.save({
                                              'province':self.strip(province),
                                              'city':self.strip(city),
                                              'title':self.strip(title), 
                                              'address':self.strip(address), 
                                              'zip':self.strip(zip),
                                              'href':href
                                              })
                   
                
                
    def __call__(self):
        print "starting........"
        self.courses()
    


        
        
        
        
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    
    #pga   = Pga("http://www.pga.com/golf-courses")
    #pga()
    
    #get proxy ip
    Zdy("http://www.xici.net.co/")()
   
    
    dianpin = Dianping("http://www.dianping.com/citylist")
    #dianpin = Dianping("http://www.dianping.com/search/category/1/45/g152p2?aid=7a931f2bc0bc79efdccd32d06dff9b91")
    dianpin()
    
    