#import magic
import requests
import mimetypes
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def get_extension(url):
    response = requests.get(url,verify=False)
    content_type = response.headers['content-type']
    extension = mimetypes.guess_all_extensions(content_type)
    if not extension:
        print('Is HTML')
    else:
        print('Is MP3')


url = "https://dts.podtrac.com/redirect.mp3/media.blubrry.com/99percentinvisible/dovetail.prxu.org/99pi/f944c58d-cba3-4911-ba7a-1305ae37551a/276-The-Finnish-Experiment.mp3"
get_extension(url)
url = "https://dts.podtrac.com/redirect.mp3/dovetail.prxu.org/criminal/1d9ff31d-9116-4754-b3fa-fa0fc11a91d1/Episode_75__The_Gatekeeper.mp3"
get_extension(url)


