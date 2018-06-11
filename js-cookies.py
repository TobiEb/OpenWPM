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

for visit_id in cur.execute("SELECT visit_id"
                                " FROM site_visits;"):
    # tuple is needed to add in sql query
    visits.append(visit_id)

c = 0
while(c < len(crawls)):	
    v = 0
    while(v < len(visits)):
        visited_tld = ""
        sessionCookies = 0
        cookie_hosts = []
        unique_cookie_names = []
        cookie_values = []
        third_party_cookie_hosts = []
        unique_third_party_cookie_names = []
        third_party_cookie_values = []
        for name, value, host, is_session, visited_site in cur.execute("SELECT c.name, c.value, c.host, c.is_session, s.site_url"
                                    " FROM javascript_cookies as c JOIN site_visits as s"
                                    " WHERE c.visit_id = s.visit_id AND c.visit_id = ?"
                                    " AND c.crawl_id = s.crawl_id AND c.crawl_id = ?", [int(visits[v][0]), int(crawls[c][0])]):
            visited_tld = get_tld(visited_site)
            if name is not None:
                if not name in unique_cookie_names:
                    cookie_hosts.append(str(host))
                    unique_cookie_names.append(str(name))
                    cookie_values.append(str(value))
                    if not visited_tld in host:
                        third_party_cookie_hosts.append(str(host))
                        unique_third_party_cookie_names.append(str(name))
                        third_party_cookie_values.append(str(value))
                        if is_session == 1:
                            sessionCookies = sessionCookies + 1

        if visited_tld != "":
            print "Crawl:",crawls[c][0], "Visit:", visits[v][0], "auf", visited_tld, ". Insgesamt:", len(unique_cookie_names), "Unique Cookies. Davon sind", sessionCookies, "SessionStorage und", len(unique_third_party_cookie_names), "third-party cookies"    

        #print "HOST : NAME : VALUE"
        i = 0
        while(i < len(unique_cookie_names)):
            #print unique_profile_cookies
            #print cookie_hosts[i], ":", unique_cookie_names[i],":", cookie_values[i]
            i = i + 1
        v = v + 1
    c = c + 1