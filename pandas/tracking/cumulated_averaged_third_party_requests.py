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

def getPercentage(subset, superset):
    if superset == 0:
        return 0
    else:
        percentage = (float(subset)/float(superset)) * 100
    return int(round(percentage))



# connect to the output database
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# MAIN CONFIG
selected_crawl = 1
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
    total_requests = []
    total_third_party_requests = []
    ext = tldextract.extract(resObject["visited_site"])
    visited_tld = ext.domain

    for url_tuple in cur.execute("SELECT url"
                                    " FROM http_requests"
                                    " WHERE visit_id = ?"
                                    " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):
        url = url_tuple[0]
        if "http" in url:
            xt = tldextract.extract(url)
            third_party_tld = xt.domain
            total_requests.append(url)
            if not visited_tld in third_party_tld:
                # check if third-party
                total_third_party_requests.append(third_party_tld)
        else:
            raise ValueError('http is not in url!', url)


    resObject["total_requests"] = total_requests
    resObject["total_third_party_requests"] = total_third_party_requests

# Since GET subsites is cumulative, we have to add the sum of a next step to its value
sites = []

cumulative_get_0_total_requests = []
cumulative_get_1_total_requests = []
cumulative_get_2_total_requests = []
cumulative_get_3_total_requests = []
cumulative_get_4_total_requests = []
cumulative_browse_total_requests = []

cumulative_get_0_tp_requests = []
cumulative_get_1_tp_requests = []
cumulative_get_2_tp_requests = []
cumulative_get_3_tp_requests = []
cumulative_get_4_tp_requests = []
cumulative_browse_tp_requests = []

i = 0
for resObject in result:
    if resObject['index'] == 0:
        sites.append(resObject['visited_site'])
        if resObject['success'] == True:
            cumulative_get_0_tp_requests.append(len(resObject['total_third_party_requests']))
            cumulative_get_1_tp_requests.append(len(resObject['total_third_party_requests']))
            cumulative_get_2_tp_requests.append(len(resObject['total_third_party_requests']))
            cumulative_get_3_tp_requests.append(len(resObject['total_third_party_requests']))
            cumulative_get_4_tp_requests.append(len(resObject['total_third_party_requests']))

            cumulative_get_0_total_requests.append(len(resObject['total_requests']))
            cumulative_get_1_total_requests.append(len(resObject['total_requests']))
            cumulative_get_2_total_requests.append(len(resObject['total_requests']))
            cumulative_get_3_total_requests.append(len(resObject['total_requests']))
            cumulative_get_4_total_requests.append(len(resObject['total_requests']))
        else:
            cumulative_get_0_tp_requests.append(0)
            cumulative_get_1_tp_requests.append(0)
            cumulative_get_2_tp_requests.append(0)
            cumulative_get_3_tp_requests.append(0)
            cumulative_get_4_tp_requests.append(0)

            cumulative_get_0_total_requests.append(0)
            cumulative_get_1_total_requests.append(0)
            cumulative_get_2_total_requests.append(0)
            cumulative_get_3_total_requests.append(0)
            cumulative_get_4_total_requests.append(0)
    elif resObject['index'] == 1:
        if resObject['success'] == True:
            cumulative_get_1_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_2_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_3_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_4_tp_requests[i] += len(resObject['total_third_party_requests'])

            cumulative_get_1_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_2_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_3_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_4_total_requests[i] += len(resObject['total_requests'])
    elif resObject['index'] == 2:
        if resObject['success'] == True:
            cumulative_get_2_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_3_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_4_tp_requests[i] += len(resObject['total_third_party_requests'])

            cumulative_get_2_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_3_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_4_total_requests[i] += len(resObject['total_requests'])
    elif resObject['index'] == 3:
        if resObject['success'] == True:
            cumulative_get_3_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_4_tp_requests[i] += len(resObject['total_third_party_requests'])

            cumulative_get_3_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_4_total_requests[i] += len(resObject['total_requests'])
    elif resObject['index'] == 4:
        if resObject['success'] == True:
            cumulative_get_4_tp_requests[i] += len(resObject['total_third_party_requests'])

            cumulative_get_4_total_requests[i] += len(resObject['total_requests'])
        i += 1
    elif resObject['index'] == 5:
        # only append if is true, since the result is devided by len(), so unsuccesful ones are removed from result.
        if resObject['success'] == True:
            cumulative_browse_tp_requests.append(len(resObject['total_third_party_requests']))

            cumulative_browse_total_requests.append(len(resObject['total_requests']))


#######################################################
# CREATE PANDAS RESULT
#######################################################

# LANDING PAGE
get_0_third_party_requests = 0
for res in cumulative_get_0_tp_requests:
    get_0_third_party_requests += res

get_0_total_requests = 0
for res in cumulative_get_0_total_requests:
    get_0_total_requests += res

# SUBSITE 1
get_1_third_party_requests = 0
for res in cumulative_get_1_tp_requests:
    get_1_third_party_requests += res

get_1_total_requests = 0
for res in cumulative_get_1_total_requests:
    get_1_total_requests += res

# SUBSITE 2
get_2_third_party_requests = 0
for res in cumulative_get_2_tp_requests:
    get_2_third_party_requests += res

get_2_total_requests = 0
for res in cumulative_get_2_total_requests:
    get_2_total_requests += res

# SUBSITE 3
get_3_third_party_requests = 0
for res in cumulative_get_3_tp_requests:
    get_3_third_party_requests += res

get_3_total_requests = 0
for res in cumulative_get_3_total_requests:
    get_3_total_requests += res

# SUBSITE 4
get_4_third_party_requests = 0
for res in cumulative_get_4_tp_requests:
    get_4_third_party_requests += res

get_4_total_requests = 0
for res in cumulative_get_4_total_requests:
    get_4_total_requests += res

# BROWSE 4 FOR COMPARISON
browse_third_party_requests = 0
for res in cumulative_browse_tp_requests:
    browse_third_party_requests += res

browse_total_requests = 0
for res in cumulative_browse_total_requests:
    browse_total_requests += res


print "Averaged Total Requests vs Third-Party Requests (and in Percentage)"
print "Landing Page", int(round(float(get_0_total_requests)/float(len(cumulative_get_0_total_requests)))), "Requests | ",int(round(float(get_0_third_party_requests)/float(len(cumulative_get_0_tp_requests)))), "Third-Party Requests"
print "Das sind: ", getPercentage(get_0_third_party_requests, get_0_total_requests), "%"
print "Subsite 1", int(round(float(get_1_total_requests)/float(len(cumulative_get_1_total_requests)))), "Requests | ",int(round(float(get_1_third_party_requests)/float(len(cumulative_get_1_tp_requests)))), "Third-Party Requests"
print "Das sind: ", getPercentage(get_1_third_party_requests, get_1_total_requests), "%"
print "Subsite 2", int(round(float(get_2_total_requests)/float(len(cumulative_get_2_total_requests)))), "Requests | ",int(round(float(get_2_third_party_requests)/float(len(cumulative_get_2_tp_requests)))), "Third-Party Requests"
print "Das sind: ", getPercentage(get_2_third_party_requests, get_2_total_requests), "%"
print "Subsite 3", int(round(float(get_3_total_requests)/float(len(cumulative_get_3_total_requests)))), "Requests | ",int(round(float(get_3_third_party_requests)/float(len(cumulative_get_3_tp_requests)))), "Third-Party Requests"
print "Das sind: ", getPercentage(get_3_third_party_requests, get_3_total_requests), "%"
print "Subsite 4", int(round(float(get_4_total_requests)/float(len(cumulative_get_4_total_requests)))), "Requests | ",int(round(float(get_4_third_party_requests)/float(len(cumulative_get_4_tp_requests)))), "Third-Party Requests"
print "Das sind: ", getPercentage(get_4_third_party_requests, get_4_total_requests), "%"
print "BROWSE 4", int(round(float(browse_total_requests)/float(len(cumulative_browse_total_requests)))), "Requests | ",int(round(float(browse_third_party_requests)/float(len(cumulative_browse_tp_requests)))), "Third-Party Requests"
print "Das sind: ", getPercentage(browse_third_party_requests, browse_total_requests), "%"



