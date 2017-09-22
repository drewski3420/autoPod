from datetime import datetime as d
import pytz

today_date = d.now(pytz.utc)


with open('data/lastRun','w') as data_file:
    data_file.write(str(today_date))
    data_file.close()
