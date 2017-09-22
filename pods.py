import mimetypes
import json
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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#todo
'''
- implement logging
- speed up pods
- refactor pods into a real json format
- log/delete listened
- GUI?
'''

def create_conn():
    try:
        db = sql.connect('')
        cur = db.cursor()
        cur.execute('''
            create table episodes(pod_name text, episode_name text
            ,episode_title text, episode_description text, url text, published timestamp)
            ''')
        db.commit()
        return db
    except:
        print('error in create_conn')
  
def write_last_run(run_complete):
    try:
        with open('configs/lastRun','w') as data_file:
            data_file.write(str(run_complete))
    except:
        print('error in write_last_run')

def get_pod_list():
    try:
        with open('configs/pods.json') as data_file:
            pods = json.load(data_file)
        return pods
    except:
        print('error in get_pod_list')
    

def get_last_run():
    try:
        last_run_path = os.path.join(os.getcwd(),'configs/lastRun')
        with open(last_run_path,'r') as f:
            last_date = parser.parse(f.read())
        return last_date
    except:
        print('error in print_last_run')

def get_pod_details(db, pods, last_date):
    try:
        tz = pytz.timezone('US/Eastern')
        cur = db.cursor()
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
                    break
                if published >= last_date:
                    try:
                        cur.execute('''
                            insert into episodes(pod_name, episode_name,episode_description, url, published)
                            values (?,?,?,?,?)''',(pod, title, description, url, published))
                        db.commit()
                    except:
                        print('Error: \n Pod Name: %s\n Episode Title: %s' %(pod, episode.title.text))
        return db
    except:
        print('error in load_db')

def download_pods(db):
    try:
        download_path = os.path.join(os.getcwd(),'data')
        cur = db.cursor()
        cur.execute('''
            Select 
                pod_name, episode_name, episode_description, url, published
            from episodes
            order by published desc
            ''')
        for row in cur.fetchall():
            r_pod = re.sub(r'[\\/:"*,?<>|\n]+', '', row[0])
            r_episode = re.sub(r'[\\/:"*,?<>|\n]+', '', row[1])
            r_description = row[2]
            r_url = row[3]
            r_published = datetime.strftime(parser.parse(row[4]),'%Y%m%d_%H%M%S')
            response = requests.get(r_url, verify = False)
            if is_content_type_ok(response.headers['content-type']):
                pod_path = os.path.join(download_path,r_pod)
                if not os.path.exists(pod_path):
                    os.makedirs(pod_path)
                pod_file_name = r_published + '-' + r_episode + '.mp3'
                episode_path = os.path.join(pod_path,pod_file_name)
                with open(episode_path, 'wb') as f:
                    f.write(response.content)
                    print('''Pod Name: %s\nEpisode Name: %s\nEpisode Description: %s\nURL: %s\nPublish Date: %s\n*******************''' %(r_pod,r_episode,r_description,r_url,r_published))
    except Exception as ex:
        print('error in download pods')

def is_content_type_ok(content_type):
    extension = mimetypes.guess_all_extensions(content_type)
    if not extension:
        return False
    else:
        return True
                       
def get_run_end_date():
    try:
        run_complete = datetime.now(pytz.utc)
        return run_complete
    except:
        print('error in get_run_end_date')

def main():
    try:
        db = create_conn()
        pods = get_pod_list()
        last_date = get_last_run()
        db = get_pod_details(db, pods, last_date)
        run_complete = get_run_end_date()
        download_pods(db)
        write_last_run(run_complete)
    except:
        print ('Error')

main()
