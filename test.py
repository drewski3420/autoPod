from dateutil import parser
from dateutil.tz import *
from datetime import *

print(datetime.now(tzutc()).tzname())
print(datetime.now(tzlocal()).tzname())
