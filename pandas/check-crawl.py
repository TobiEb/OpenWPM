import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3 as lite

# connect to the output database
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# RESULT VARIABLES
total_percentage_result = 0
get_percentage_result = 0
browse_percentage_result = 0

# OPERATIONAL VARIABLES
cmds = []
argss = []
successes = []
timestamps = []
total_errors = 0
get_errors = 0
browse_errors = 0

# iterate over all rows
for crawl_id, cmd, args, success, timestamp in cur.execute("SELECT DISTINCT crawl_id, command, arguments, bool_success, dtg"
                                " FROM CrawlHistory"
                                " WHERE crawl_id = 1"
                                " ORDER BY dtg;"):
    success_res = success
    if success == -1 or success == 0:
        success_res = "FALSE"
        total_errors += 1
        if "GET" in cmd:
            get_errors += 1
        elif "BROWSE" in cmd:
            browse_errors += 1
    elif success == 1:
        success_res = "TRUE"
    else :
        success_res = success
    
    if "GET" in cmd or "BROWSE" in cmd:
        cmds.append(cmd)
        argss.append(args)
        successes.append(success_res)
        timestamps.append(timestamp)

if len(cmds) == len(argss) and len(cmds) == len(successes) and len(cmds) == len(timestamps):
    total = len(cmds)
    total_percentage_result = (float(total_errors)/float(total)) * 100
    get_percentage_result = (float(get_errors)/float(total)) * 100
    browse_percentage_result = (float(browse_errors)/float(total)) * 100
else:
    print "Es gibt unterschiedlich lange Ergebnis-Summen"

# conn = sqlite3.connect("/media/tobi/Daten/Workspace/OpenWPM/Output/crawl-data.sqlite")
# df = pd.read_sql_query("SELECT DISTINCT command, arguments, bool_success, dtg"
#                                 " FROM CrawlHistory"
#                                 " WHERE crawl_id = 1"
#                                 " ORDER BY dtg;", conn)

df = pd.DataFrame({'Command':list(cmds), 'Site':list(argss), 'Success':list(successes), 'Timestamp':list(timestamps)})

df = df.set_index(('Timestamp'))
#df = df.sort_values(by='B')
#print(df['command'])
#print(df)
print total_percentage_result,"Prozent aller Befehle waren fehlerhaft"
print "davon sind ", get_percentage_result,"Prozent GET Befehle fehlerhaft"
print "davon sind ", browse_percentage_result,"Prozent BROWSE Befehle fehlerhaft"