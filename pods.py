import re
import pytz
from dateutil import parser
from dateutil.tz import tzutc as tz
from datetime  import tzinfo,datetime
import requests
from bs4 import BeautifulSoup as bs
import sqlite3 as sql   
import urllib3
import os

path = os.path.join(os.getcwd(),'data\lastRun')
with open(path,'r') as f:
    last_date = f.read()
#last_date = parser.parse('2017-09-01 11:00:00-04:00')
download_path = os.path.join(os.getcwd(),'data')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
tz = pytz.timezone('US/Eastern')

with open('data/pods.json') as data_file:
    pods = json.load(data_file)

db = sql.connect('')
cur = db.cursor()
cur.execute('''
    create table episodes(pod_name text, episode_name text
    ,episode_title text, episode_description text, url text, published timestamp)
    ''')
db.commit()
for pod,link in pods.items():
    r = requests.get(link, verify = False)
    soup = bs(r.text, features = 'xml')
    for episode in soup.find_all('item'):
        try:
            title = episode.title.text
        except:
            title = 'No Title Found'
        try:
            description = episode.description.text
        except:
            description = 'No Description Found'
        try:
            url = episode.enclosure.get('url')
        except:
            break
        try:
            published = parser.parse(episode.pubDate.text).astimezone(tz)
        except:
            published = parser.parse('1900-01-01')
        if published >= last_date:
            try:
                cur.execute('''
                    insert into episodes(pod_name, episode_name,episode_description, url, published)
                    values (?,?,?,?,?)''',(pod, title, description, url, published))
                db.commit()
            except:
                print('Error: \n Pod Name: %s\n Episode Title: %s' %(pod, episode.title.text))
        
cur.execute('''
    Select 
    pod_name, episode_name, episode_description, url, published
    from episodes
    order by published desc
    limit 10
    ''')

for row in cur.fetchall():
    r_pod = re.sub(r'[\\/:"*?<>|\n]+', '', row[0])
    r_episode = re.sub(r'[\\/:"*?<>|\n]+', '', row[1])
    r_description = row[2]
    r_url = row[3]
    r_published = datetime.strftime(parser.parse(row[4]),'%Y-%m-%d %H:%M:%S')
    response = requests.get(url)
    pod_path = os.path.join(download_path,r_pod)
    if not os.path.exists(pod_path):
        os.makedirs(pod_path)
    episode_path = os.path.join(pod_path,r_episode + '.mp3')
    with open(episode_path, 'wb') as f:
        f.write(response.content)
        f.close()
    print('''Pod Name: %s\nEpisode Name: %s\nEpisode Description: %s\nURL: %s\nPublish Date: %s\n*******************''' %(r_pod,r_episode,r_description,r_url,r_published))

db.close()
