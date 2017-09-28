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
import subprocess
import tempfile as t
import shutil

'''
def process_mp3(file,speed):
    FFMPEG_BIN = "configs/ffmpeg.exe" # on Windows
    with open(input_file,'rb') as f:
        data = f.read()
        with t.NamedTemporaryFile(mode='wb',delete=False) as tf:
            tf.write(data)
            temp_file = tf.name
    
    subprocess.call([FFMPEG_BIN
                     ,'-y'
                     ,'-i',temp_file
                     ,'-filter:a','atempo={}'.format(speed)
                     ,'-vn',input_file])
    os.remove(temp_file)
    

input_file = "data/Note to Self/20170927_000000-Ghosting Simmering and Icing with Esther Perel.mp3"
speed = '.75'
process_mp3(input_file,speed)



with open('configs/pods.json') as data_file:
    pods = json.load(data_file)
'''
with open('configs/pods.json') as data_file:
    pods = json.load(data_file)


