import sqlite3 as lite
from tld import get_tld

# connect to the output database
wpm_db = '/home/tobi/Schreibtisch/Tests/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

visited_tld = ""
total_localStorage_items = 0
errors = 0
third_party_cookies = 0
#print "CHANGE : RAWHOST : HOST : STATUS"
for url in cur.execute("SELECT *"
                            " FROM CrawlHistory;"):
    print url