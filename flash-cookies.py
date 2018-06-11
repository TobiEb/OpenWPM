import sqlite3 as lite

# connect to the output database
wpm_db = '/home/tobi/Schreibtisch/Tests/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

visits = []

for visit_id in cur.execute("SELECT visit_id"
                                " FROM site_visits;"):
    # tuple is needed to add in sql query
    visits.append(visit_id)

i = 0
while(i < len(visits)):
    for domain, filename in cur.execute("SELECT domain, filename"
                                " FROM flash_cookies"
                                " WHERE visit_id = ?", visits[i]):
	    print domain, filename
    i = i + 1