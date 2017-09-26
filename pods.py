import sys
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

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#todo
'''
- speed up pods
- log/delete listened
- GUI?
'''

def create_conn():
    global logger
    try:
        db = sql.connect('')
        cur = db.cursor()
        logger.info('Creating Tables')
        cur.execute('''
            create table episodes(pod_name text, episode_name text
            ,episode_title text, episode_description text, url text, published timestamp)
            ''')
        db.commit()
        logger.info('Created Tables')
        return db
    except:
        logger.warning('error in create_conn')
  
def write_last_run(run_complete):
    global logger
    try:
        logger.info('Writing Last Run Date {}'.format(run_complete))
        with open('configs/lastRun','w') as data_file:
            data_file.write(str(run_complete))
        logger.info('Wrote Last Run Date {}'.format(run_complete))
    except:
        logger.warning('error in write_last_run')

def get_pod_list():
    global logger
    try:
        logger.info('Getting Pod Lsit from JSON file')
        with open('configs/pods.json') as data_file:
            pods = json.load(data_file)
        logger.info('Got Pod List from JSON file')
        return pods
    except:
        logger.warning('error in get_pod_list')
    

def get_last_run():
    global logger
    try:
        logger.info('Getting Last Run Date')
        last_run_path = 'configs/lastRun'
        with open(last_run_path,'r') as f:
            last_date = parser.parse(f.read())
        logger.info('Got Last Run Date {}'.format(last_date))
        return last_date
    except:
        logger.warning('error in print_last_run')

def get_pod_details(db, pods, last_date):
    global logger
    try:
        tz = pytz.timezone('US/Eastern')
        cur = db.cursor()
        for a,b in pods.items():
            pod_name = b['pod_name']
            pod_name = pod_name.replace('\r','').replace('\n','')
            link = b['pod_url']
            r = requests.get(link, verify = False)
            soup = bs(r.text, features = 'xml')
            for episode in soup.find_all('item'):
                try:
                    title = episode.title.text
                    title = title.replace('\r','').replace('\n','')
                except:
                    title = 'No Title Found'
                try:
                    description = episode.description.text
                except:
                    description = 'No Description Found'
                try:
                    url = episode.enclosure.get('url')
                except:
                    logger.error('Pod {} URL not found {}'.format(pod_name,title))
                    break
                try:
                    published = parser.parse(episode.pubDate.text).astimezone(tz)
                except:
                    logger.error('Pod {} Published Date not found {}'.format(pod_name,title))
                    break
                if published >= last_date:
                    try:
                        logger.info('Inserting Pod {} Episode {} URL {} into database'.format(pod_name, title, url))
                        cur.execute('''
                            insert into episodes(pod_name, episode_name,episode_description, url, published)
                            values (?,?,?,?,?)''',(pod_name, title, description, url, published))
                        db.commit()
                        logger.info('Inserted Pod {} Episode {} URL {} into database'.format(pod_name, title, url))
                    except Exception as ex:
                        logger.warning('Error {}: \n Pod Name: {}\n Episode Title: {}'.format(ex, pod_name, title))
        return db
    except Exception as ex:
        logger.warning('Exception: {}'.format(ex))
        logger.warning('error in load_db')

def download_pods(db):
    global logger
    try:
        logger.info('Getting Episode info from database')
        download_path = 'data'
        cur = db.cursor()
        cur.execute('''
            Select 
                pod_name, episode_name, episode_description, url, published
            from episodes
            order by published desc
            ''')
        logger.info('Got Episode info from database')
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
                    logger.info('Created Directory {}'.format(pod_path))
                pod_file_name = r_published + '-' + r_episode + '.mp3'
                episode_path = os.path.join(pod_path,pod_file_name)
                with open(episode_path, 'wb') as f:
                    f.write(response.content)
                    logger.info('''Pod Name: %s\nEpisode Name: %s\nEpisode Description: %s\nURL: %s\nPublish Date: %s\n*******************''' %(r_pod,r_episode,r_description,r_url,r_published))
    except Exception as ex:
        logger.warning('error in download pods')

def is_content_type_ok(content_type):
    global logger
    logger.info('Getting Extension Info')
    extension = mimetypes.guess_all_extensions(content_type)
    if not extension:
        logger.info('No Extention')
        return False
    else:
        logger.info('Has Extension')
        return True
                       
def get_run_end_date():
    global logger
    try:
        logger.info('Getting Run Complete Date')
        run_complete = datetime.now(pytz.utc)
        logger.info('Got run complete date {}'.format(run_complete))
        return run_complete
    except:
        logger.warning('error in get_run_end_date')

def setup_custom_logger(name):
    path = 'configs/autopod.log'
    formatter = logging.Formatter(fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(path, mode='a')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

def main():
    global logger
    logger = setup_custom_logger('autopod')
    try:
        logger.info('Beginning Script')
        logger.info('Creating Connection')
        db = create_conn()
        logger.info('Created Connection')
        logger.info('Getting Pods')
        pods = get_pod_list()
        logger.info('Got Pods')
        logger.info('Getting Last Date')
        last_date = get_last_run()
        logger.info('Got Last Date')
        logger.info('Getting Pod Details')
        db = get_pod_details(db, pods, last_date)
        logger.info('Got Pod Details')
        logger.info('Getting Run Complete')
        run_complete = get_run_end_date()
        logger.info('Got Run Complete')
        logger.info('Downloading Pods')
        download_pods(db)
        logger.info('Downloaded Pods')
        logger.info('Writing Last Run')
        write_last_run(run_complete)
        logger.info('Wrote Last Run')
    except:
        logger.warning('Error')
    logger.info('Ending Script')


main()
