import re
import sys
import time

from bs4 import BeautifulSoup
from urllib import parse, request

from queue import PriorityQueue



def get_links(address, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string or ''
            text = re.sub('\s+', ' ', text).strip()
            yield parse.urljoin(address, href), text


def content_extract(address, content, writer=sys.stdout):
    for phonenum in re.findall('\d{3}-\d{3}-\d{4}',str(content)):
        info = '{}; PHONE; {}\n'.format(address, phonenum.strip())
        writer.write(info)

    for email_info in re.findall('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',str(content)):
        if 'png' not in email_info:
            info = '{}; EMAIL; {}\n'.format(address, email_info.strip())
            writer.write(info)

    for address_info in re.findall('[a-zA-Z\s]+,\s*[a-zA-Z]+,?\s*\d{5}',str(content)):
        info = '{}; CITY; {}\n'.format(address, re.sub('\s+', ' ', address_info).strip())
        writer.write(info)




def crawl(content,log,root,content_extract = lambda a,h:None):
    visited = set()
    results = []
    
    def shouldvisit(adr):
        return "cs.jhu.edu" in adr and adr not in visited

    queue = PriorityQueue()
    queue.put((1,root))

    while not queue.empty():
        priority,address = queue.get()
        try:           
            r=request.urlopen(address)
            if r.status == 200:
                content_type = r.getheader('Content-Type')
                if 'text/html' in content_type:
                    log.write(address+'\n')
                    html = r.read()
                    content_extract(address,html.decode('utf-8'),content)

                    for url, text in get_links(address, html):
                        if shouldvisit(url) and url != address and url not in visited:
                            rel = priority + 1
                            queue.put((rel, url))
                            visited.add(url)
                else:
                    continue
        except Exception as e:
            print(e, address)                   
    



if __name__ == '__main__':
    log_file = sys.argv[1]
    address = sys.argv[3]
    cont_file = sys.argv[2]

    cont = open(cont_file, 'w')
    log = open(log_file, 'w')
    
    crawl(cont,log,address,content_extract)

