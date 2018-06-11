import sqlite3 as lite
from tld import get_tld

# connect to the output database
wpm_db = '/home/tobi/Schreibtisch/Tests/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

visits = []
crawls = []

for visit_id in cur.execute("SELECT DISTINCT visit_id"
                                " FROM site_visits;"):
    # tuple is needed to add in sql query
    visits.append(visit_id)

for crawl_id in cur.execute("SELECT DISTINCT crawl_id"
                                " FROM site_visits;"):
    # tuple is needed to add in sql query
    crawls.append(crawl_id)

c = 0
while(c < len(crawls)):	
    i = 0
    while(i < len(visits)):
        visited_tld = ""
        unique_tp_sites = []
        total_tp_requests = []
        for url, visited_url in cur.execute("SELECT DISTINCT h.url, s.site_url"
                                            " FROM http_requests as h INNER JOIN site_visits as s"
                                            " WHERE h.visit_id = s.visit_id AND h.visit_id = ?"
                                            " AND h.crawl_id = s.crawl_id AND h.crawl_id = ?", [int(visits[i][0]), int(crawls[c][0])]):
            visited_tld = get_tld(visited_url)
            if "http" in url:
                third_tld = get_tld(url)
                if not visited_tld in third_tld:
                    total_tp_requests.append(third_tld)
                    if not third_tld in unique_tp_sites:
                        unique_tp_sites.append(str(third_tld))
        if visited_tld != "":
            print "Crawl:",crawls[c][0], "Visit:", visits[i][0], "auf", visited_tld, ",Anzahl unique third-party TLDs:", len(unique_tp_sites), "Summe third-party-requests:", len(total_tp_requests)
        #Enable this to see the actual name of all unique requested third-parties 
        #print unique_tp_sites
        i = i + 1
    c = c + 1
