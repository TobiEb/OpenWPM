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
for l in cur.execute("SELECT *"
                            " FROM localStorage;"):
    print l