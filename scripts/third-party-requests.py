import sqlite3 as lite
from tld import get_tld

# connect to the output database
wpm_db = '/home/OpenWPM/Output/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# MAIN CONFIG
selected_crawl = 8
selected_index = 0 # 0 means landing page, 4 browsing 4 subpages
observing_domains = ['google', 'doubleclick'] # if array is empty it will be not investigated. Otherwise add domains as strings into this array
#
#
#
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

# add number of third-party requests
for res in result:
    visited_tld = ""
    sum_tp_requests = []
    unique_tp_sites = []
    domain_requests = []

    for url_tuple in cur.execute("SELECT url"
                                    " FROM http_requests"
                                    " WHERE visit_id = ?"
                                    " AND crawl_id = ?", [res["visit_id"], res["crawl_id"]]):
        visited_tld = get_tld(res["visited_site"])
        url = url_tuple[0]
        if "http" in url:
            third_tld = get_tld(url)
            # check if third-party
            if not visited_tld in third_tld:
                sum_tp_requests.append(third_tld)
                if not third_tld in unique_tp_sites:
                    unique_tp_sites.append(str(third_tld))
            # check if observing domain(s) is/are present
            if len(observing_domains) != 0:
                for domain in observing_domains:
                    if domain in third_tld:
                        domain_requests.append(str(third_tld))


    res["sum_third_party_requests"] = len(sum_tp_requests)
    res["sum_unique_requested_tp_sites"] = len(unique_tp_sites)
    res["unique_requested_tp_sites"] = unique_tp_sites
    res["sum_domain_requests"] = len(domain_requests)

# print result
# if all third-party domains want to be seen:
if len(observing_domains) != 0:
    print "Anzahl Requests auf die Domains:", observing_domains
for res in result:
    if res["success"] == True:
        if selected_index is not None:
            if selected_index == res["index"]:
                if len(observing_domains) == 0:
                    print res["visited_site"], res["sum_third_party_requests"], res["sum_unique_requested_tp_sites"]
                    #print res["visited_site"], res["unique_requested_tp_sites"]
                else:
                    print res["visited_site"], res["sum_domain_requests"]

        else:
            print "selected_index should be set"



