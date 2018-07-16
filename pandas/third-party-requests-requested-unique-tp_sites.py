import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3 as lite
import tldextract

def getTldOfSubURL(subUrl):
    # ATTENTION: url is ...-subX so we have to subtract that again
    if subUrl.endswith('-sub1') or subUrl.endswith('-sub2') or subUrl.endswith('-sub3') or subUrl.endswith('-sub4'):
        tldUrl = subUrl[:-5]
        return tldUrl
    else:
        return subUrl

# connect to the output database
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# MAIN CONFIG
selected_crawl = 1
observing_domains = [] # if array is empty it will be not investigated. Otherwise add domains as strings into this array
#
#
#
result = []

# get index and success from CrawlHistory, create result array
visited_crawl_history_sites = []
for crawl_id, cmd, visited_site, success, dtg in cur.execute("SELECT DISTINCT crawl_id, command, arguments, bool_success, dtg"
                                " FROM CrawlHistory"
                                " WHERE crawl_id = ?"
                                " ORDER BY dtg;", (selected_crawl,)):
    # first parse sub-URLs to their Top-Level-Domain
    site = getTldOfSubURL(visited_site)
    # if this site is not present yet set it to index 0
    if not site in visited_crawl_history_sites:
        index = 0
        visited_crawl_history_sites.append(site)
    else:
        # count() returns how many times the substring is present in it
        count = visited_crawl_history_sites.count(site)
        index = count
        visited_crawl_history_sites.append(site)

    if success == -1 or success == 0:
        success_res = False
    elif success == 1:
        success_res = True
    else :
        raise ValueError('Success in CrawlHistory is neither 0, -1 nor 1!')
    
    if "GET" in cmd or "BROWSE" in cmd:
        obj = {}
        obj["crawl_id"] = crawl_id
        obj["cmd"] = str(cmd)
        obj["visited_site"] = str(site)
        obj["success"] = success_res
        obj["index"] = index
        result.append(obj)

# add visit_id from site_visits
visited_site_visits_sites = []
for visit_id, site_url in cur.execute("SELECT visit_id, site_url"
                            " FROM site_visits"
                            " WHERE crawl_id = ?", (selected_crawl,)):
    count = 0
    # first parse sub-URLs to their Top-Level-Domain
    site = getTldOfSubURL(site_url)
    if site in visited_site_visits_sites:
        # count() returns how many times the substring is present in it
        count = visited_site_visits_sites.count(site)
    for res in result:
        if res["visited_site"] == str(site) and res["index"] == count:
            res.update({"visit_id": visit_id})
    visited_site_visits_sites.append(site)

################################################################################
# Now we have an object containing all necessary information, saved in result array
#################################################################################

# add number of third-party requests
for resObject in result:
    visited_tld = ""
    sum_third_party_requests = []
    unique_third_party_sites = []
    requests_per_domain = []

    for url_tuple in cur.execute("SELECT url"
                                    " FROM http_requests"
                                    " WHERE visit_id = ?"
                                    " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):
        ext = tldextract.extract(resObject["visited_site"])
        visited_tld = ext.domain
        url = url_tuple[0]
        if "http" in url:
            xt = tldextract.extract(url)
            third_party_tld = xt.domain
            # check if is a third-party
            if not visited_tld in third_party_tld:
                sum_third_party_requests.append(third_party_tld)
                if not third_party_tld in unique_third_party_sites:
                    unique_third_party_sites.append(str(third_party_tld))
            # check if observing domain(s) is/are present
            if len(observing_domains) != 0:
                for domain in observing_domains:
                    if domain in third_party_tld:
                        requests_per_domain.append(str(third_party_tld))
        else:
            raise ValueError('http is not in url!', url)

    resObject["sum_third_party_requests"] = len(sum_third_party_requests)
    resObject["unique_third_party_sites"] = unique_third_party_sites
    resObject["sum_requests_per_domain"] = len(requests_per_domain)

# Since GET subsites is cumulative, we have to check and add unique (!) requested third-party sites and add them to the next sub_site
# !!!! Success is not regarded yet

sites = []
get_0_tp_request_sites = []
get_1_tp_request_sites = []
get_2_tp_request_sites = []
get_3_tp_request_sites = []
get_4_tp_request_sites = []
browse_tp_request_sites = []

for resObject in result:
    if resObject['index'] == 0:
        sites.append(resObject['visited_site'])
        get_0_tp_request_sites = resObject['unique_third_party_sites']
        resObject.update({"final_unique_third_party_sites": len(get_0_tp_request_sites)})
    elif resObject['index'] == 1:
        get_1_tp_request_sites = get_0_tp_request_sites
        for site in resObject['unique_third_party_sites']:
            if not site in get_0_tp_request_sites:
                get_1_tp_request_sites.append(site)
        resObject.update({"final_unique_third_party_sites": len(get_1_tp_request_sites)})
    elif resObject['index'] == 2:
        get_2_tp_request_sites = get_1_tp_request_sites
        for site in resObject['unique_third_party_sites']:
            if not site in get_1_tp_request_sites:
                get_2_tp_request_sites.append(site)
        resObject.update({"final_unique_third_party_sites": len(get_2_tp_request_sites)})
    elif resObject['index'] == 3:
        get_3_tp_request_sites = get_2_tp_request_sites
        for site in resObject['unique_third_party_sites']:
            if not site in get_2_tp_request_sites:
                get_3_tp_request_sites.append(site)
        resObject.update({"final_unique_third_party_sites": len(get_3_tp_request_sites)})
    elif resObject['index'] == 4:
        get_4_tp_request_sites = get_3_tp_request_sites
        for site in resObject['unique_third_party_sites']:
            if not site in get_3_tp_request_sites:
                get_4_tp_request_sites.append(site)
        resObject.update({"final_unique_third_party_sites": len(get_4_tp_request_sites)})
    elif resObject['index'] == 5:
        # index 5 is BROWSE command
        browse_tp_request_sites = resObject['unique_third_party_sites']
        resObject.update({"final_unique_third_party_sites": len(browse_tp_request_sites)})
        get_0_tp_request_sites = []
        get_1_tp_request_sites = []
        get_2_tp_request_sites = []
        get_3_tp_request_sites = []
        get_4_tp_request_sites = []
        browse_tp_request_sites = []


# from sub_sites get the length to show in diagram

get_0_tp_requests = []
get_1_tp_requests = []
get_2_tp_requests = []
get_3_tp_requests = []
get_4_tp_requests = []
browse_tp_requests = []

for resObject in result:
    if resObject['index'] == 0:
        get_0_tp_requests.append(resObject['final_unique_third_party_sites'])
    elif resObject['index'] == 1:
        get_1_tp_requests.append(resObject['final_unique_third_party_sites'])
    elif resObject['index'] == 2:
        get_2_tp_requests.append(resObject['final_unique_third_party_sites'])
    elif resObject['index'] == 3:
        get_3_tp_requests.append(resObject['final_unique_third_party_sites'])
    elif resObject['index'] == 4:
        get_4_tp_requests.append(resObject['final_unique_third_party_sites'])
    elif resObject['index'] == 5:
        browse_tp_requests.append(resObject['final_unique_third_party_sites'])

# fix since last element in browse was not recorded
browse_tp_requests.append(0)

#######################################################
# CREATE PANDAS OBJECT
#######################################################

plt.bar(sites, browse_tp_requests, color="yellow")
#plt.plot(sites, get_1_tp_requests, color="blue")
#plt.plot(sites, get_2_tp_requests, color="green")
#plt.plot(sites, get_3_tp_requests, color="yellow")
plt.plot(sites, get_4_tp_requests, color="blue")
plt.plot(sites, get_0_tp_requests, color="red")
plt.title("Unique requested third-party domains")
plt.xlabel("Site")
plt.ylabel("# of third-party domains")
plt.legend(['Get 4 subsites', 'Landing page', 'Browse'])
#plt.legend(['Landing page', 'Get 1 subsites', 'Get 2 subsites', 'Get 3 subsites', 'Get 4 subsites'])
plt.xticks(rotation=90)
plt.show()


