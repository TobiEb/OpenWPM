import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3 as lite
import tldextract
#
#
#
#
# MAIN CONFIG
selected_crawl = 1
observing_domains = [] # if array is empty it will be not investigated. Otherwise add domains as strings into this array
#
#
#

def getTldOfSubURL(subUrl):
    # ATTENTION: url is ...-subX so we have to subtract that again
    if subUrl.endswith('-sub1') or subUrl.endswith('-sub2') or subUrl.endswith('-sub3') or subUrl.endswith('-sub4'):
        tldUrl = subUrl[:-5]
        return tldUrl
    else:
        return subUrl

def getPercentage(subset, superset):
    if superset == 0:
        return 0
    else:
        percentage = (float(subset)/float(superset)) * 100
    return percentage

# connect to the output database
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

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

# add number of cookies
for resObject in result:
    unique_cookie_names = []
    cookie_hosts = []
    cookie_values = []
    unique_tp_cookie_names = []
    tp_cookie_hosts = []
    tp_cookie_values = []
    domain_cookies = []
    sessionCookies = 0

    for name, value, host, is_session in cur.execute("SELECT name, value, host, is_session"
                                    " FROM javascript_cookies"
                                    " WHERE visit_id = ?"
                                    " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):
        ext = tldextract.extract(resObject["visited_site"])
        visited_tld = ext.domain
        if name is not None:
            if not name in unique_cookie_names:
                unique_cookie_names.append(str(name))
                cookie_hosts.append(str(host))
                cookie_values.append(str(value))
                xt = tldextract.extract(host)
                third_party_tld = xt.domain
                # check if third-party
                if not visited_tld in third_party_tld:
                    unique_tp_cookie_names.append(str(name))
                    tp_cookie_hosts.append(str(host))
                    tp_cookie_values.append(str(value))
                    # check if domain(s) is/are present
                    if len(observing_domains) != 0:
                        for domain in observing_domains:
                            if domain in host:
                                domain_cookies.append(str(name))
                # check if session cookie
                if is_session == 1:
                    sessionCookies = sessionCookies + 1

    resObject["sum_unique_cookies_names"] = unique_cookie_names
    resObject["sum_unique_third_party_cookies_names"] = unique_tp_cookie_names
    resObject["sum_session_cookies"] = sessionCookies
    resObject["sum_domain_cookies"] = len(domain_cookies)

# Since GET subsites is cumulative, we have to check and add unique (!) requested third-party sites and add them to the next sub_site
# !!!! Success is not regarded yet

sites = []
get_0_unique_cookie_names = []
get_1_unique_cookie_names = []
get_2_unique_cookie_names = []
get_3_unique_cookie_names = []
get_4_unique_cookie_names = []
browse_unique_cookie_names = []

get_0_unique_tp_cookie_names = []
get_1_unique_tp_cookie_names = []
get_2_unique_tp_cookie_names = []
get_3_unique_tp_cookie_names = []
get_4_unique_tp_cookie_names = []
browse_unique_tp_cookie_names = []

for resObject in result:
    if resObject['index'] == 0:
        sites.append(resObject['visited_site'])
        get_0_unique_cookie_names = resObject['sum_unique_cookies_names']
        get_0_unique_tp_cookie_names = resObject['sum_unique_third_party_cookies_names']
        resObject.update({"final_sum_unique_cookies_names": len(get_0_unique_cookie_names)})
        resObject.update({"final_sum_unique_tp_cookies_names": len(get_0_unique_tp_cookie_names)})
    elif resObject['index'] == 1:
        get_1_unique_cookie_names = get_0_unique_cookie_names
        get_1_unique_tp_cookie_names = get_0_unique_tp_cookie_names
        for site in resObject['sum_unique_cookies_names']:
            if not site in get_0_unique_cookie_names:
                get_1_unique_cookie_names.append(site)
        for tp_site in resObject['sum_unique_third_party_cookies_names']:
            if not tp_site in get_0_unique_tp_cookie_names:
                get_1_unique_tp_cookie_names.append(tp_site)
        resObject.update({"final_sum_unique_cookies_names": len(get_1_unique_cookie_names)})
        resObject.update({"final_sum_unique_tp_cookies_names": len(get_1_unique_tp_cookie_names)})
    elif resObject['index'] == 2:
        get_2_unique_cookie_names = get_1_unique_cookie_names
        get_2_unique_tp_cookie_names = get_1_unique_tp_cookie_names
        for site in resObject['sum_unique_cookies_names']:
            if not site in get_1_unique_cookie_names:
                get_2_unique_cookie_names.append(site)
        for tp_site in resObject['sum_unique_third_party_cookies_names']:
            if not tp_site in get_1_unique_tp_cookie_names:
                get_2_unique_tp_cookie_names.append(tp_site)
        resObject.update({"final_sum_unique_cookies_names": len(get_2_unique_cookie_names)})
        resObject.update({"final_sum_unique_tp_cookies_names": len(get_2_unique_tp_cookie_names)})
    elif resObject['index'] == 3:
        get_3_unique_cookie_names = get_2_unique_cookie_names
        get_3_unique_tp_cookie_names = get_2_unique_tp_cookie_names
        for site in resObject['sum_unique_cookies_names']:
            if not site in get_2_unique_cookie_names:
                get_3_unique_cookie_names.append(site)
        for tp_site in resObject['sum_unique_third_party_cookies_names']:
            if not tp_site in get_2_unique_tp_cookie_names:
                get_3_unique_tp_cookie_names.append(tp_site)
        resObject.update({"final_sum_unique_cookies_names": len(get_3_unique_cookie_names)})
        resObject.update({"final_sum_unique_tp_cookies_names": len(get_3_unique_tp_cookie_names)})
    elif resObject['index'] == 4:
        get_4_unique_cookie_names = get_3_unique_cookie_names
        get_4_unique_tp_cookie_names = get_3_unique_tp_cookie_names
        for site in resObject['sum_unique_cookies_names']:
            if not site in get_3_unique_cookie_names:
                get_4_unique_cookie_names.append(site)
        for tp_site in resObject['sum_unique_third_party_cookies_names']:
            if not tp_site in get_3_unique_tp_cookie_names:
                get_4_unique_tp_cookie_names.append(tp_site)
        resObject.update({"final_sum_unique_cookies_names": len(get_4_unique_cookie_names)})
        resObject.update({"final_sum_unique_tp_cookies_names": len(get_4_unique_tp_cookie_names)})
    elif resObject['index'] == 5:
        # index 5 is BROWSE command
        browse_unique_cookie_names = resObject['sum_unique_cookies_names']
        browse_unique_tp_cookie_names = resObject['sum_unique_third_party_cookies_names']
        resObject.update({"final_sum_unique_cookies_names": len(browse_unique_cookie_names)})
        resObject.update({"final_sum_unique_tp_cookies_names": len(browse_unique_tp_cookie_names)})

        get_0_unique_cookie_names = []
        get_1_unique_cookie_names = []
        get_2_unique_cookie_names = []
        get_3_unique_cookie_names = []
        get_4_unique_cookie_names = []
        browse_unique_cookie_names = []

        get_0_unique_tp_cookie_names = []
        get_1_unique_tp_cookie_names = []
        get_2_unique_tp_cookie_names = []
        get_3_unique_tp_cookie_names = []
        get_4_unique_tp_cookie_names = []
        browse_unique_tp_cookie_names = []


# from sub_sites get the length to show in diagram

cumulative_get_0_unique_cookies = []
cumulative_get_1_unique_cookies = []
cumulative_get_2_unique_cookies = []
cumulative_get_3_unique_cookies = []
cumulative_get_4_unique_cookies = []
browse_unique_cookies = []

cumulative_get_0_unique_third_party_cookies = []
cumulative_get_1_unique_third_party_cookies = []
cumulative_get_2_unique_third_party_cookies = []
cumulative_get_3_unique_third_party_cookies = []
cumulative_get_4_unique_third_party_cookies = []
browse_unique_third_party_cookies = []

for resObject in result:
    if resObject['index'] == 0:
        cumulative_get_0_unique_cookies.append(resObject['final_sum_unique_cookies_names'])
        cumulative_get_0_unique_third_party_cookies.append(resObject['final_sum_unique_tp_cookies_names'])
    elif resObject['index'] == 1:
        cumulative_get_1_unique_cookies.append(resObject['final_sum_unique_cookies_names'])
        cumulative_get_1_unique_third_party_cookies.append(resObject['final_sum_unique_tp_cookies_names'])
    elif resObject['index'] == 2:
        cumulative_get_2_unique_cookies.append(resObject['final_sum_unique_cookies_names'])
        cumulative_get_2_unique_third_party_cookies.append(resObject['final_sum_unique_tp_cookies_names'])
    elif resObject['index'] == 3:
        cumulative_get_3_unique_cookies.append(resObject['final_sum_unique_cookies_names'])
        cumulative_get_3_unique_third_party_cookies.append(resObject['final_sum_unique_tp_cookies_names'])
    elif resObject['index'] == 4:
        cumulative_get_4_unique_cookies.append(resObject['final_sum_unique_cookies_names'])
        cumulative_get_4_unique_third_party_cookies.append(resObject['final_sum_unique_tp_cookies_names'])
    elif resObject['index'] == 5:
        browse_unique_cookies.append(resObject['final_sum_unique_cookies_names'])
        browse_unique_third_party_cookies.append(resObject['final_sum_unique_tp_cookies_names'])

# fix since last element in browse was not recorded
browse_unique_cookies.append(0)
browse_unique_third_party_cookies.append(0)

#######################################################
# CREATE CONSOLE RESULT
#######################################################

#######################################################
# CREATE PANDAS OBJECT
#######################################################

#plt.bar(sites, browse_unique_cookies, color="yellow")
plt.plot(sites, cumulative_get_0_unique_cookies, color="red")
plt.plot(sites, cumulative_get_0_unique_third_party_cookies, color="blue")
#plt.plot(sites, cumulative_get_1_tp_percentage_lengths, color="red")
#plt.plot(sites, cumulative_get_2_tp_percentage_lengths, color="green")
#plt.plot(sites, cumulative_get_3_tp_percentage_lengths, color="yellow")
plt.title("HTTP Cookies")
plt.xlabel("Site")
plt.ylabel("# of Unique Cookies")
plt.legend(['# Cookies GET 0', '# Third-Party Cookies GET 0'])
plt.xticks(rotation=90)
plt.show()



