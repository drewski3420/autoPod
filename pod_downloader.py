import sqlite3 as sql,urllib3,os,tempfile,subprocess,sys,mimetypes,json,re,pytz,requests, pod_logger
from dateutil import parser
from dateutil.tz import tzutc as tz
from datetime  import datetime
from bs4 import BeautifulSoup as bs

class PodException(Exception):
    pass

def process_mp3(contents,output_file,speed):
    logger.info('Starting File Conversion')
    FFMPEG_BIN = "configs/ffmpeg.exe" #WINDOWS
    with tempfile.NamedTemporaryFile(mode='wb',delete=False) as tf: 
        tf.write(contents) 
        temp_file = tf.name 

    subprocess.call([FFMPEG_BIN 
            ,'-y' 
            ,'-i',temp_file 
            ,'-filter:a','atempo={}'.format(speed) 
            ,'-vn',output_file]) 
    os.remove(temp_file)
    logger.info('Ending File Conversion')

def create_conn():
    global logger
    try:
        db = sql.connect('')
        cur = db.cursor()
        logger.info('Creating Tables')
        cur.execute('''
            create table episodes(pod_name text, episode_name text
            ,episode_title text, episode_description text, url text, published timestamp, playback_speed real)
            ''')
        db.commit()
        logger.info('Created Tables')
        return db
    except Exception as ex:
        logger.warning('error in create_conn: {}'.format(ex))
        raise PodException

def write_last_run(run_complete):
    global logger
    try:
        logger.info('Writing Last Run Date {}'.format(run_complete))
        with open('configs/lastRun','w') as data_file:
            data_file.write(str(run_complete))
        logger.info('Wrote Last Run Date {}'.format(run_complete))
    except Exception as ex:
        logger.warning('error in write_last_run: {}'.format(ex))
        raise PodException

def get_pod_list():
    global logger
    try:
        logger.info('Getting Pod Lsit from JSON file')
        with open('configs/pods.json') as data_file:
            pods = json.load(data_file)
        logger.info('Got Pod List from JSON file')
        return pods
    except Exception as ex:
        logger.warning('error in get_pod_list: {}'.format(ex))
        raise PodException   

def get_last_run():
    global logger
    try:
        logger.info('Getting Last Run Date')
        last_run_path = 'configs/lastRun'
        with open(last_run_path,'r') as f:
            last_date = parser.parse(f.read())
        logger.info('Got Last Run Date {}'.format(last_date))
        return last_date
    except Exception as ex:
        logger.warning('error in print_last_run: {}'.format(ex))
        raise PodException

def get_pod_details(db, pods, last_date):
    global logger
    try:
        logger.info('Getting Pod Details')
        tz = pytz.timezone('US/Eastern')
        cur = db.cursor()
        for a,b in pods.items():
            pod_name = b['pod_name']
            pod_name = pod_name.replace('\r','').replace('\n','')
            link = b['pod_url']
            playback_speed = b['playback_speed']
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
                    logger.error('Published Date not found. Pod {} Episode {}'.format(pod_name,title))
                    break
                if published >= last_date:
                    try:
                        logger.info('Inserting into database. Pod {} Episode {} URL {} '.format(pod_name, title, url))
                        cur.execute('''
                            insert into episodes(pod_name, episode_name,episode_description, url, published, playback_speed)
                            values (?,?,?,?,?,?)''',(pod_name, title, description, url, published,playback_speed))
                        db.commit()
                        logger.info('Inserted into database. Pod {} Episode {} URL {}'.format(pod_name, title, url))
                    except Exception as ex:
                        logger.warning('Error {}: \n Pod Name: {}\n Episode Title: {}'.format(ex, pod_name, title))
        return db
    except Exception as ex:
        logger.warning('error in load_db: {}'.format(ex))
        raise PodException

def strip_for_saving(fn):
    return re.sub(r'[\\/:"*,?<>|\n]+', '', fn)

def download_pods(db):
    global logger
    try:
        logger.info('Getting Episode info from database')
        download_path = 'data'
        cur = db.cursor()
        cur.execute('''
            Select 
                pod_name, episode_name, episode_description, url, published, playback_speed
            from episodes
            order by published desc
            ''')
        logger.info('Got Episode info from database')
        for row in cur.fetchall():
            r_pod = strip_for_saving(row[0])
            r_episode = strip_for_saving(row[1])
            r_description = row[2]
            r_url = row[3]
            r_published = datetime.strftime(parser.parse(row[4]),'%Y%m%d_%H%M%S')
            r_playback = round(row[5],2)
            response = requests.get(r_url, verify = False)
            if is_content_type_ok(response.headers['content-type']):
                pod_path = os.path.join(download_path,r_pod)
                if not os.path.exists(pod_path):
                    os.makedirs(pod_path)
                    logger.info('Created Directory {}'.format(pod_path))
                pod_file_name = r_published + '-' + r_episode + '.mp3'
                episode_path = os.path.join(pod_path,pod_file_name)
                logger.info('Pod Name: {} Episode Name: {} URL: {} Publish Date: {}'.format(r_pod,r_episode,r_url,r_published))
                process_mp3(response.content,episode_path,r_playback)
    except Exception as ex:
        logger.warning('error in download pods: {}'.format(ex))
        raise PodException

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
    logger.info('Got Extension Info')

def get_run_end_date():
    global logger
    try:
        logger.info('Getting Run Complete Date')
        run_complete = datetime.now(pytz.utc)
        logger.info('Got run complete date {}'.format(run_complete))
        return run_complete
        logger.info('Got Run Complete Date')
    except Exception as ex:
        logger.warning('error in get_run_end_date: {}'.format(ex))
        raise PodException

def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    global logger
    logger = pod_logger.setup_custom_logger('pod_downloader')
    try:
        logger.info('Beginning Script')
        db = create_conn()
        pods = get_pod_list()
        last_date = get_last_run()
        db = get_pod_details(db, pods, last_date)
        run_complete = get_run_end_date()
        download_pods(db)
        write_last_run(run_complete)
    except Exception as ex:
        logger.warning('Error: {}'.format(ex))
    finally:
        logger.info('Ending Script')

if __name__ =='__main__':
    main()
