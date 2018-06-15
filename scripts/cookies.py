import sqlite3 as lite
from tld import get_tld

# connect to the output database
wpm_db = '/home/tobi/Schreibtisch/Tests/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# MAIN CONFIG
selected_crawl = 1
show_index = 0 # 0 means landing page, 3 browsing 3 subpages
result = []

# get index and success from CrawlHistory, create result array
visited_crawl_sites = []
for crawl_id, cmd, visited_site, success, dtg in cur.execute("SELECT DISTINCT crawl_id, command, arguments, bool_success, dtg"
                                " FROM CrawlHistory"
                                " WHERE crawl_id = ?"
                                " ORDER BY dtg;", (selected_crawl,)):
    if not visited_site in visited_crawl_sites:
        index = 0
        visited_crawl_sites.append(visited_site)
    else:
        count = visited_crawl_sites.count(visited_site)
        index = count
        visited_crawl_sites.append(visited_site)

    success_res = success
    if success == -1 or success == 0:
        success_res = False
    elif success == 1:
        success_res = True
    else :
        success_res = success
    
    if "GET" in cmd or "BROWSE" in cmd:
        obj = {}
        obj["crawl_id"] = crawl_id
        obj["cmd"] = str(cmd)
        obj["visited_site"] = str(visited_site)
        obj["success"] = success_res
        obj["index"] = index
        result.append(obj)

# add visit_id from site_visits
visited_sites = []
for visit_id, url in cur.execute("SELECT visit_id, site_url"
                            " FROM site_visits"
                            " WHERE crawl_id = ?", (selected_crawl,)):
    if url in visited_sites:
        count = visited_sites.count(url)
    else:
        count = 0
    for res in result:
        if res["visited_site"] == str(url) and res["index"] == count:
            res.update({"visit_id": visit_id})
    visited_sites.append(url)

# add number of cookies
for res in result:
    unique_cookie_names = []
    cookie_hosts = []
    cookie_values = []
    unique_third_party_cookie_names = []
    third_party_cookie_hosts = []
    third_party_cookie_values = []
    sessionCookies = 0
    visited_tld = ""

    for name, value, host, is_session in cur.execute("SELECT name, value, host, is_session"
                                    " FROM javascript_cookies"
                                    " WHERE visit_id = ?"
                                    " AND crawl_id = ?", [res["visit_id"], res["crawl_id"]]):
        visited_tld = get_tld(res["visited_site"])
        if name is not None:
            if not name in unique_cookie_names:
                unique_cookie_names.append(str(name))
                cookie_hosts.append(str(host))
                cookie_values.append(str(value))
                # check if third-party
                if not visited_tld in host:
                    unique_third_party_cookie_names.append(str(name))
                    third_party_cookie_hosts.append(str(host))
                    third_party_cookie_values.append(str(value))
                    if is_session == 1:
                        sessionCookies = sessionCookies + 1

    res["sum_cookies"] = len(unique_cookie_names)
    res["sum_third_party_cookies"] = len(unique_third_party_cookie_names)

# print result
for res in result:
    if res["success"] == True:
        if show_index is not None:
            if show_index == res["index"]:
                print res["visited_site"], res["sum_cookies"], res["sum_third_party_cookies"], res["success"]
        else:
            print res["visited_site"], res["sum_cookies"], res["sum_third_party_cookies"], res["success"]



