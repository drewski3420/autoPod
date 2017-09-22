from bs4 import BeautifulSoup as bs
path_to_file = 'file/name/here.opml'
with open(path_to_file) as fn:
    soup = bs(fn,'lxml')
o = soup.outline
for pod in o.children:
    if pod.name =='outline':
        print(',\'' + pod.get('text') + '\'' + ' : ' + '\'' + pod.get('xmlurl') + '\'')