import mimetypes
import json
import re
import pytz
from dateutil import parser
from dateutil.tz import tzutc as tz
from datetime  import datetime
import requests
from bs4 import BeautifulSoup as bs
import sqlite3 as sql   
import urllib3
import os
import logging


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)

#todo
'''
- speed up pods
- refactor pods into a real json format
- log/delete listened
- GUI?
'''

def create_conn():
    try:
        db = sql.connect('')
        cur = db.cursor()
        logging.info('Creating Tables')
        cur.execute('''
            create table episodes(pod_name text, episode_name text
            ,episode_title text, episode_description text, url text, published timestamp)
            ''')
        db.commit()
        logging.info('Created Tables')
        return db
    except:
        logging.warning('error in create_conn')
  
def write_last_run(run_complete):
    try:
        logging.info('Writing Last Run Date {}'.format(run_complete))
        with open('configs/lastRun','w') as data_file:
            data_file.write(str(run_complete))
        logging.info('Wrote Last Run Date {}'.format(run_complete))
    except:
        logging.warning('error in write_last_run')

def get_pod_list():
    try:
        logging.info('Getting Pod Lsit from JSON file')
        with open('configs/pods.json') as data_file:
            pods = json.load(data_file)
        logging.info('Got Pod List from JSON file')
        return pods
    except:
        logging.warning('error in get_pod_list')
    

def get_last_run():
    try:
        logging.info('Getting Last Run Date')
        #last_run_path = os.path.join(os.getcwd(),'configs/lastRun')
        last_run_path = 'configs/lastRun'
        with open(last_run_path,'r') as f:
            last_date = parser.parse(f.read())
        logging.info('Got Last Run Date {}'.format(last_date))
        return last_date
    except:
        logging.warning('error in print_last_run')

def get_pod_details(db, pods, last_date):
    try:
        tz = pytz.timezone('US/Eastern')
        cur = db.cursor()
        for a,b in pods.items():
            pod_name = b['pod_name']
            link = b['pod_url']
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
                    logging.info('Pod {} URL not found {}'.format(pod_name,title))
                    break
                try:
                    published = parser.parse(episode.pubDate.text).astimezone(tz)
                except:
                    logging.info('Pod {} Published Date not found {}'.format(pod_name,title))
                    break
                if published >= last_date:
                    try:
                        logging.info('Inserting Pod {} Episode {} URL {} into database'.format(pod_name, title, url))
                        cur.execute('''
                            insert into episodes(pod_name, episode_name,episode_description, url, published)
                            values (?,?,?,?,?)''',(pod_name, title, description, url, published))
                        db.commit()
                        logging.info('Inserted Pod {} Episode {} URL {} into database'.format(pod_name, title, url))
                    except Exception as ex:
                        logging.warning('Error {}: \n Pod Name: {}\n Episode Title: {}'.format(ex, pod_name, title))
        return db
    except Exception as ex:
        logging.warning('Exception: {}'.format(ex))
        logging.warning('error in load_db')

def download_pods(db):
    try:
        logging.info('Getting Episode info from database')
        #download_path = os.path.join(os.getcwd(),'data')
        download_path = 'data'
        cur = db.cursor()
        cur.execute('''
            Select 
                pod_name, episode_name, episode_description, url, published
            from episodes
            order by published desc
            ''')
        logging.info('Got Episode info from database')
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
                    logging.info('Created Directory {}'.format(pod_path))
                pod_file_name = r_published + '-' + r_episode + '.mp3'
                episode_path = os.path.join(pod_path,pod_file_name)
                with open(episode_path, 'wb') as f:
                    f.write(response.content)
                    logging.info('''Pod Name: %s\nEpisode Name: %s\nEpisode Description: %s\nURL: %s\nPublish Date: %s\n*******************''' %(r_pod,r_episode,r_description,r_url,r_published))
    except Exception as ex:
        logging.warning('error in download pods')

def is_content_type_ok(content_type):
    logging.info('Getting Extension Info')
    extension = mimetypes.guess_all_extensions(content_type)
    if not extension:
        logging.info('No Extention')
        return False
    else:
        logging.info('Has Extension')
        return True
                       
def get_run_end_date():
    try:
        logging.info('Getting Run Complete Date')
        run_complete = datetime.now(pytz.utc)
        logging.info('Got run complete date {}'.format(run_complete))
        return run_complete
    except:
        logging.warning('error in get_run_end_date')

def start_logging():
    path = 'configs/autopod.log'
    #path = os.path.join(os.getcwd(),path)
    with open(path,'a') as f:
        f.write('')
    logging.basicConfig(filename=path,level=logging.DEBUG)

def main():
    try:
        start_logging()
        logging.info('Creating Connection')
        db = create_conn()
        logging.info('Created Connection')
        logging.info('Getting Pods')
        pods = get_pod_list()
        logging.info('Got Pods')
        logging.info('Getting Last Date')
        last_date = get_last_run()
        logging.info('Got Last Date')
        logging.info('Getting Pod Details')
        db = get_pod_details(db, pods, last_date)
        logging.info('Got Pod Details')
        logging.info('Getting Run Complete')
        run_complete = get_run_end_date()
        logging.info('Got Run Complete')
        logging.info('Downloading Pods')
        download_pods(db)
        logging.info('Downloaded Pods')
        logging.info('Writing Last Run')
        write_last_run(run_complete)
        logging.info('Wrote Last Run')
    except:
        logging.warning('Error')

main()
