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

last_date = parser.parse('2017-09-01 11:00:00-04:00')
download_path = os.path.join(os.getcwd(),'data')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
tz = pytz.timezone('US/Eastern')

pods = {
    'Reply All' : 'HTTP://Feeds.gimletmedia.com/hearreplyall'
    ,'Benjamen Walker\'s Theory of Everything' : 'http://feeds.prx.org/toe'
    ,'Constitutional' : 'http://podcast.posttv.com/itunes-5951e18ce4b056ae8fa8e4b2.xml'
    ,'Kurt Vonneguys' : 'http://feeds.soundcloud.com/users/soundcloud:users:263797969/sounds.rss'
    ,'LeVar Burton Reads' : 'https://rss.art19.com/levar-burton-reads'
    ,'KCRW\'s Here Be Monsters' : 'http://feeds.feedburner.com/herebemonsterspodcast/'
    ,'Worldly' : 'http://feeds.feedburner.com/voxworldly'
    ,'Longform' : 'http://longform.libsyn.com/rss'
    ,'This American Life' : 'http://feed.thisamericanlife.org/talpodcast'
    ,'The Daily 202\'s Big Idea' : 'https://podcast.posttv.com/itunes/daily-202-big-idea.xml'
    ,'Uncivil' : 'https://feeds.megaphone.fm/uncivil'
    ,'Larry Wilmore: Black on the Air' : 'http://feeds.feedburner.com/larrywilmoreblackontheair'
    ,'The United States of Anxiety' : 'http://feeds.wnyc.org/unitedstatesofanxiety'
    ,'Science Solved It' : 'http://rss.acast.com/sciencesolvedit'
    ,'Invisibilia' : 'https://www.npr.org/rss/podcast.php?id=510307'
    ,'Homecoming' : 'http://feeds.gimletmedia.com/homecomingshow'
    ,'What Trump Can Teach Us About Con Law' : 'http://feeds.TrumpConLaw.com/TrumpConLaw'
    ,'Outside/In' : 'http://feeds.megaphone.fm/PPY5156495451'
    ,'Every Little Thing' : 'http://feeds.gimletmedia.com/eltshow'
    ,'Flash Forward' : 'http://www.flashforwardpod.com/feed/podcast/'
    ,'Radiolab' : 'http://feeds.wnyc.org/radiolab'
    ,'Only A Game' : 'https://www.npr.org/rss/podcast.php?id=510052'
    ,'The Allusionist' : 'http://feeds.theallusionist.org/Allusionist'
    ,'Lovett or Leave It' : 'http://feeds.feedburner.com/lovett-or-leave-it'
    ,'the memory palace' : 'http://feeds.thememorypalace.us/thememorypalace'
    ,'You Are Not So Smart' : 'http://feeds.soundcloud.com/users/soundcloud:users:16745745/sounds.rss'
    ,'Story of the Day : NPR' : 'https://www.npr.org/templates/rss/podlayer.php?id=1090'
    ,'Sidedoor' : 'http://feeds.si.edu/SmithsonianSidedoor'
    ,'Strangers' : 'http://feeds.kcrw.com/kcrw/sg'
    ,'Linux Action News' : 'http://linuxactionnews.com/rss'
    ,'Freakonomics Radio' : 'http://feeds.feedburner.com/freakonomicsradio'
    ,'On the Media' : 'http://feeds.wnyc.org/onthemedia'
    ,'Radio Diaries' : 'http://feed.radiodiaries.org/radio-diaries?id=510288'
    ,'FanGraphs Baseball' : 'http://www.fangraphs.com/blogs/feed/podcast'
    ,'The Ezra Klein Show' : 'http://feeds.feedburner.com/TheEzraKleinShow'
    ,'Pod Save America' : 'http://feeds.feedburner.com/pod-save-america'
    ,'Embedded' : 'https://www.npr.org/rss/podcast.php?id=510311'
    ,'Vox\'s The Weeds' : 'http://feeds.feedburner.com/voxtheweeds'
    ,'Fictional' : 'http://fictional.libsyn.com/rss'
    ,'pluspluspodcast' : 'http://rss.acast.com/pluspluspodcast'
    ,'The Ringer MLB Show' : 'https://rss.art19.com/the-ringer-mlb-show'
    ,'Love + Radio' : 'http://feeds.feedburner.com/loveplusradio'
    ,'30 For 30 Podcasts' : 'http://www.espn.com/espnradio/podcast/feeds/itunes/podCast?id=19472136'
    ,'Can He Do That?' : 'http://podcast.posttv.com/itunes-58861635e4b039a652877de6.xml'
    ,'Imaginary Worlds' : 'http://feeds.feedburner.com/imaginaryworldspodcast'
    ,'The Uncertain Hour' : 'https://feeds.publicradio.org/public_feeds/the-uncertain-hour/itunes/rss'
    ,'Dooley Noted' : 'http://www.omnycontent.com/d/playlist/a858b0a5-e5e6-4a14-9717-a70b010facc1/2e8d881b-21cf-4683-a9b4-a77600a8078c/2bbfdb41-040e-4002-8880-a77600a8079a/podcast.rss'
    ,'terrestrial' : 'https://kuow.drupal.publicbroadcasting.net/podcasts/102329/rss.xml'
    ,'Planet Money' : 'http://www.npr.org/rss/podcast.php?id=510289'
    ,'Ear Hustle' : 'http://feeds.earhustlesq.com/earhustlesq'
    ,'Pod Save the World' : 'http://feeds.feedburner.com/pod-save-the-world'
    ,'Up First' : 'https://www.npr.org/rss/podcast.php?id=510318'
    ,'FiveThirtyEight Politics' : 'http://www.espn.com/espnradio/podcast/feeds/itunes/podCast?id=14554755'
    ,'Crimetown' : 'http://feeds.gimletmedia.com/crimetownshow'
    ,'Something True' : 'https://www.idlethumbs.net/feeds/somethingtrue'
    ,'Myths and Legends' : 'http://mythpodcast.libsyn.com/rss'
    ,'The Lawfare Podcast' : 'http://lawfare.libsyn.com/rss'
    ,'Cosmic Vertigo - ABC RN' : 'http://www.abc.net.au/radionational/feed/8294152/podcast.xml'
    ,'S-Town' : 'http://feeds.stownpodcast.org/stownpodcast'
    ,'The Next Picture Show' : 'http://feeds.megaphone.fm/FLM2375047009'
    ,'Undone' : 'http://feeds.gimletmedia.com/undoneshow'
    ,'Very Bad Words' : 'https://audioboom.com/channels/4686307.rss'
    ,'99% Invisible' : 'http://feeds.99percentinvisible.org/99percentinvisible?'
    ,'The Nerdist' : 'http://nerdist.libsyn.com/rss'
    ,'Beginner' : 'https://rss.simplecast.com/podcasts/3485/rss'
    ,'Radiolab Presents: More Perfect' : 'http://feeds.wnyc.org/moreperfect'
    ,'Note to Self' : 'http://feeds.wnyc.org/notetoself-podcast'
    ,'Slate\'s Amicus with Dahlia Lithwick' : 'http://feeds.feedburner.com/SlateAmicusWithDahliaLithwick'
    ,'I Tell My Husband The News' : 'http://feeds.soundcloud.com/users/soundcloud:users:188712331/sounds.rss'
    ,'The Turnaround with Jesse Thorn' : 'http://maximumfun.org/feeds/tt.xml'
    ,'The Truth' : 'http://feeds.feedburner.com/thetruthapm'
    ,'TLDR' : 'http://feeds.wnyc.org/otm_tldr'
    ,'Criminal' : 'http://feeds.thisiscriminal.com/CriminalShow'
    ,'The World in Words' : 'http://feeds.feedburner.com/pri/world-words'
}

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
