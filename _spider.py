#import requests
import os
import re
import time
from itertools import repeat
from urllib.parse import urlparse
from multiprocessing import Process
from bs4 import BeautifulSoup as bs
from html2text import html2text as h2t
from urllib.request import Request, urlopen

#Defining allowed urls to crawl and the starting page
database = {}
base_url = "https://en.wikipedia.org"
start_url = "https://en.wikipedia.org/wiki/Ontology"

def info(name):
	print(name)
	print('Parent process: ', os.getppid())
	print('Process id: ', os.getpid())


#Download HTML document
def download_page(url):
    try:
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = Request(url, headers = headers)
        resp = urlopen(req)
        respData = str(resp.read())
        return respData
    except Exception as e:
        print(str(e))

def clean(page):
	page = page.replace('\\t', '')
	page = page.replace('\\n', '')
	return page

#Extract the title tag
def get_page_title(page):
    tag_open = page.find("<span dir")
    tag_close = page.find(">",tag_open+1)
    title_close = page.find("</span>", tag_close + 1)
    title = page[tag_close + 1 : title_close]
    return title

	
#Extract the see also section elements
def get_see_also(page):
    if 'id="See_also">' in page:
        start_see_also = page.find('id="See_also">')
        start_list_items = page.find('<li>', start_see_also + 1)
        end_see_also = page.find('<h2>', start_list_items + 1)
        see_also_section = page[start_list_items: end_see_also]
        raw_item = (re.sub(r'<.+?>', '', see_also_section)).replace('\n', ',')
        raw_item2 = raw_item.replace(',,', ',')
        item = raw_item2.replace(',,', ',')
        flag = False
    else:
        item = "No Related Links"
        flag = True
    return item, flag


#Extract just the "Introduction" part of the page
def get_intro(page):
    tag_open = page.find("<p>")
    tag_close = page.find('<div id="toctitle">', tag_open + 1)
    
    #If the page only has introduction
    if '<div id="toctitle">' not in page:
        tag_close = page.find('</p>', tag_open + 1)
    else:
        pass
    intro = page[tag_open : tag_close]
    return intro



#Finding 'Next Link' on a given web page
def get_next_link(s):
    start_link = s.find("<a href")
    if start_link == -1:    #If no links are found then give an error!
        end_quote = 0
        link = "NONE"
        return link, end_quote
    else:
        start_quote = s.find('"', start_link)
        end_quote = s.find('"', start_quote + 1)
        link = str(s[start_quote + 1: end_quote])
        return link, end_quote
          

#Get all links in page
def get_all_links(page):
    links = []
    while True:
        link, end_link = get_next_link(page)
        if link == "NONE":
            break
        else:
            links.append(link)
            page = page[end_link:]
    return links 



#Remove HTML tags
def parse_intro(page):
    parsed_intro = (re.sub(r'<.+?>', '', page))
    return parsed_intro



#Ignore image and text files
def extension_scan(url):
    ext_list = ['.png', '.jpg', '.jpeg', '.gif', '.tif', '.txt', '.ogg']
    for ext in ext_list:
        if ext in url:
            found = True
            break
        else:
            found = False
    return found


#URL parsing for incomplete or duplicate URLs
def url_parse(url):
    url = url
    s = urlparse(url)
    base_url_n = base_url
    i = 0
    in_domain = False
    while i<=9:
        if url == "/":
            url = base_url_n
            in_domain = False  
        elif not s.scheme:
            url = "http://" + url
            in_domain = False
        elif "#" in url:
            url = url[:url.find("#")]
            in_domain = False
        elif "?" in url:
            url = url[:url.find("?")]
            in_domain = False
        elif s.netloc == "":
            url = base_url + s.path
            in_domain = False
        elif url[len(url)-1] == "/":
            url = url[:-1]
            in_domain = False
        else:
            url = url
            in_domain = False
            break
        
        i = i+1
        s = urlparse(url)   #Parse after every loop to update the values of url parameters
    return(url, in_domain)

def save_page(url, title, intro):
	try:
		w = '/wiki/'
		name = url[url.find(w) + len(w):]
		file = open(name + '.txt', 'a', encoding='utf-8')
		file.write(url + "\n")
		file.write(clean(h2t(title)) + ": " + "\n")
		file.write(clean(h2t(intro)))
		file.close()
	except Exception as e:
		print(str(e))
		return "Error"		
	return name

def save_db():
	file = open('database.txt', 'a', encoding='utf-8')
	file.write(str(database))
	file.close()



#Crawler
def spider_crawl(start_url, id):
    info("Crawler " + str(id)) 
    to_crawl = [start_url]
    crawled = []
    try:
        while to_crawl:
            url_ = to_crawl.pop(0)      #Get next link
            url_, in_domain = url_parse(url_)
            found = extension_scan(url_)
            if in_domain or found:
                pass
            else:       
                if url_ in crawled:     #Check if the URL is already crawled
                    pass
                else:       #Crawl page(s)
                    print("Link:\n" + url_)
                    page = download_page(url_)
                    title = str(get_page_title(page)).lower()
                    print("Title:\n" + bs(title, 'html.parser').prettify())
                    see_also, found = get_see_also(page)
                    print("Related Links:\n" + see_also)     
                    intro = get_intro(page)                    
                    to_crawl = to_crawl + get_all_links(intro)
                    crawled.append(url_)                   
                    parsed_intro = parse_intro(intro)
                    print("Introduction:\n" + parsed_intro.replace('   ',' '))
                    #Bind link to document
                    database[url_.lower()] = save_page(url_, title, parsed_intro).lower()
                    #Remove duplicated from to_crawl
                    site_ = 0
                    site_count = 1					
                    while site_ < (len(to_crawl)- site_count):
                        if to_crawl[site_] in to_crawl[site_ + 1:(len(to_crawl) - 1)]:
                            to_crawl.pop(site_)
                            site_count = site_count + 1
                        else:
                            pass
                        site_ = site_+1
    except Exception as e:
        save_db()
        print(str(e))					
        return "Finished crawling"
    save_db()
    return "Finished crawling"

if __name__ == '__main__':
	i = 0
	p1 = Process(target=spider_crawl, args=("https://en.wikipedia.org/wiki/Strife", i))
	p1.start()
	i += 1
	p2 = Process(target=spider_crawl, args=("https://en.wikipedia.org/wiki/Water", i))
	p2.start()
	i += 1
	p3 = Process(target=spider_crawl, args=("https://en.wikipedia.org/wiki/Cold", i))
	p3.start()
	i += 1
	p1.join()
	p2.join()
	p3.join()