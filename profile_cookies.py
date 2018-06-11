import sqlite3 as lite
from tld import get_tld

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
    visited_tld = ""
    errors = 0
    profile_cookies_hosts = []
    unique_profile_cookies_name = []
    profile_cookies_values = []
    third_party_hosts = []
    unique_third_party_cookies_name = []
    third_party_values = []
    for name, value, host, visited_site in cur.execute("SELECT c.name, c.value, c.host, s.site_url"
                                " FROM profile_cookies as c JOIN site_visits as s"
                                " WHERE c.visit_id = s.visit_id AND c.visit_id = ?", visits[i]):
        #print name, value, host
        visited_tld = get_tld(visited_site)
        if name is not None:
            if not name in unique_profile_cookies_name:
                profile_cookies_hosts.append(str(host))
                unique_profile_cookies_name.append(str(name))
                profile_cookies_values.append(str(value))
                # check if third-party
                if not visited_tld in host:
                    third_party_hosts.append(str(host))
                    unique_third_party_cookies_name.append(str(name))
                    third_party_values.append(str(value))
    
    if visited_tld == "":
        visited_tld = "ERROR"    

    print "Visit:", visits[i][0], "auf", visited_tld, ". Insgesamt", len(unique_profile_cookies_name), "Unique Cookies, davon third party Cookies: ", len(unique_third_party_cookies_name)
    print "HOST : NAME : VALUE"
    j = 0
    while(j < len(unique_profile_cookies_name)):
        #print unique_profile_cookies
        #print profile_cookies_hosts[j], ":", unique_profile_cookies_name[j],":", profile_cookies_values[j]
        j = j + 1
    i = i + 1