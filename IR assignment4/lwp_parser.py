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

def similarity(root,url):
    pass

def get_non_local(root):
    r = request.urlopen(root)
    for l,text in get_links(root,r.read()):
        slashpos = root.find('//')
        a = root[slashpos+2:]
        singslashpos = a.find('/')
        b = a[:singslashpos]
        

        if l != root and l.find(b) == -1:
            if 'http' in l:
                print(l)






if __name__ == '__main__':

    address = sys.argv[1]
    if address.find('http') == -1:
        print("Error: Invalid address, please start with \'http://\' or \'https://\'")

    get_non_local(address)

