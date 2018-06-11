import sqlite3 as lite
from tld import get_tld

# connect to the output database
wpm_db = '/home/tobi/Schreibtisch/Tests/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# dummy user email and set of first-party sites on which email is leaked
fp_sites = []

# scans through the database, checking for first parties on which the email is leaked
for url in cur.execute("SELECT location"
                                " FROM links_found;"):
	fp_sites.append(url)
    #if "http" in url:
	#	tld = get_tld(url)
	#	if not "spiegel.de" in tld and not tld in fp_sites:
	#		fp_sites.append(tld)

# outputs the results
#print len(fp_sites)
print fp_sites
