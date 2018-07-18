import sqlite3 as lite
#from tld import get_tld

# connect to the output database
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# iterate over all rows
for crawl_id, cmd, args, success, timestamp in cur.execute("SELECT DISTINCT crawl_id, command, arguments, bool_success, dtg"
                                " FROM CrawlHistory"
                                " ORDER BY dtg;"):
	success_res = success
	if success == -1 or success == 0:
		success_res = "FALSE"
	elif success == 1:
		success_res = "TRUE"
	else :
		success_res = success
	
	if "GET" in cmd or "BROWSE" in cmd:
		print "Crawl: ",crawl_id, " ",cmd , " ", args, " ", success_res, " ", timestamp
