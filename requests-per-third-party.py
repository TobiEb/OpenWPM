import sqlite3 as lite
from tld import get_tld
from collections import OrderedDict

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
        obj = {}
        visited_tld = ""
        for url, visited_url in cur.execute("SELECT DISTINCT h.url, s.site_url"
                                            " FROM http_requests as h JOIN site_visits as s"
                                            " WHERE h.visit_id = s.visit_id AND h.visit_id = ?"
                                            " AND h.crawl_id = s.crawl_id AND h.crawl_id = ?", [int(visits[i][0]), int(crawls[c][0])]):
                # get Top-level-Domain of visited Site
                visited_tld = get_tld(visited_url)
                if "http" in url:
                    # get Top-Level-Domain of each requested site
                    site_tld = get_tld(url)
                    # check if site is third-party
                    if not visited_tld in site_tld:
                        if not str(site_tld) in obj:        
                            obj[str(site_tld)] = 1
                        else:
                            obj[str(site_tld)] += 1
        d_sorted_by_value = OrderedDict(sorted(obj.items(), key=lambda x: x[1], reverse= True))

        if visited_tld != "":
            print "Crawl:",crawls[c][0], "Visit:", visits[i][0], "auf", visited_tld, "Requests per Third-Party:"
            for item in d_sorted_by_value.items():
                print item 
        i = i + 1
    c = c + 1
