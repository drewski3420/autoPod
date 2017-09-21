from bs4 import BeautifulSoup as bs

with open('C:\\Users\\andrewj\\Documents\\podcasts_opml.xml') as fn:
    soup = bs(fn,'lxml')
i = 1
o = soup.outline
for pod in o.children:
    if pod.name =='outline':
        print(',\'' + pod.get('text') + '\'' + ' : ' + '\'' + pod.get('xmlurl') + '\'')
