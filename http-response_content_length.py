import sqlite3 as lite
from tld import get_tld

# connect to the output database
wpm_db = '/home/tobi/Schreibtisch/Tests/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

crawls = []
visits = []

for crawl_id in cur.execute("SELECT DISTINCT crawl_id"
                                " FROM site_visits;"):
    # tuple is needed to add in sql query
    crawls.append(crawl_id)

for visit_id in cur.execute("SELECT DISTINCT visit_id"
                                " FROM site_visits;"):
	# tuple is needed to add in sql query
	visits.append(visit_id)

c = 0
while(c < len(crawls)):	
	i = 0
	while(i < len(visits)):
		result = 0
		for header in cur.execute("SELECT headers"
									" FROM http_responses"
									" WHERE visit_id = ?"
									" AND crawl_id = ?"
									" ORDER BY visit_id ASC;", [int(visits[i][0]), int(crawls[c][0])]):
			for http_header in header:
				if "Content-Length" in http_header:
					cont_length = http_header.index("Content-Length")
					result = result + cont_length
		if result != 0: 
			print "Crawl:",crawls[c][0], "Visit:", visits[i][0], result, "Byte"		
		i = i + 1
	c = c + 1
