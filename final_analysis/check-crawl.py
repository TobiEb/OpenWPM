import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3 as lite
from datetime import datetime

# connect to the output database
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/facebook.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# CONFIG
selected_crawl = 2
fmt = '%Y-%m-%d %H:%M:%S'

# RESULT VARIABLES
total_percentage_result = 0
get_percentage_result = 0
first_timestamp = ""
last_timestamp = ""

# OPERATIONAL VARIABLES
cmds = []
argss = []
successes = []
timestamps = []
total_errors = 0
get_errors = 0

# iterate over all rows
for crawl_id, cmd, args, success, timestamp in cur.execute("SELECT DISTINCT crawl_id, command, arguments, bool_success, dtg"
                                " FROM CrawlHistory"
                                " WHERE crawl_id = ?"
                                " ORDER BY dtg;", (selected_crawl,)):
    success_res = success
    if success == -1 or success == 0:
        success_res = "FALSE"
        total_errors += 1
        get_errors += 1
    elif success == 1:
        success_res = "TRUE"
    else :
        success_res = success
    
    if "GET" in cmd:
        cmds.append(cmd)
        argss.append(args)
        successes.append(success_res)
        timestamps.append(timestamp)

if len(cmds) == len(argss) and len(cmds) == len(successes) and len(cmds) == len(timestamps):
    total = len(cmds)
    total_percentage_result = (float(total_errors)/float(total)) * 100
    get_percentage_result = (float(get_errors)/float(total)) * 100
else:
    print "Es gibt unterschiedlich lange Ergebnis-Summen"

df = pd.DataFrame({'Command':list(cmds), 'Site':list(argss), 'Success':list(successes), 'Timestamp':list(timestamps)})
print(df)
df.to_csv('test.csv', sep='\t', encoding='utf-8', index=False)

first_timestamp = df.loc[df.index[0], 'Timestamp']
last_timestamp = df.loc[df.index[-1], 'Timestamp']

# calculate timestamp difference -> duration
tstamp1 = datetime.strptime(first_timestamp, fmt)
tstamp2 = datetime.strptime(last_timestamp, fmt)
td = tstamp2 - tstamp1

print 'Ergebnis:'
print "Crawled Sites: ",len(cmds), "# Failures: ", total_errors, "Failures in %: ", total_percentage_result, "Dauer des Crawls: ", first_timestamp, "-", last_timestamp, "thus: ", td 