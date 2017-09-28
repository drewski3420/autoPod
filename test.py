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
#ffmpeg -i input.mp4 -filter:a "atempo=0.5,atempo=0.5" -vn output.aac
FFMPEG_BIN = "configs/ffmpeg.exe" # on Windows
input_file = "data/Radiolab/20170926_175546-Driverless Dilemma.mp3"
output_file = "data/Radiolab/output_test.mp3"
subprocess.call([FFMPEG_BIN
                     ,'-i',input_file
                     ,'-filter:a','atempo=1.5'
                     ,'-vn',output_file])
