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
display_index = 1 # 0 is UNTIL landing page, UNTIL 1-4 subsites, 5 browse, since it is cumulated here
selected_crawl = 1
#
#
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
    return int(round(percentage))

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

# add number of third-party requests
for resObject in result:
    total_requests = []
    total_third_party_requests = []

    if resObject['index'] == display_index:
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

## NON CUMULATIVE
# Total Requests per Site
sites = []
get_0_total_requests = []
get_1_total_requests = []
get_2_total_requests = []
get_3_total_requests = []
get_4_total_requests = []
browse_total_requests = []

# Third-Party Requests per Site
get_0_tp_requests = []
get_1_tp_requests = []
get_2_tp_requests = []
get_3_tp_requests = []
get_4_tp_requests = []
browse_tp_requests = []

# Third-Party Percentage per Site
get_0_tp_percentage = []
get_1_tp_percentage = []
get_2_tp_percentage = []
get_3_tp_percentage = []
get_4_tp_percentage = []
browse_tp_percentage = []

for resObject in result:
    if resObject['index'] == 0 and resObject['index'] == display_index:
        sites.append(resObject['visited_site'])
        if resObject['success'] is True:
            get_0_total_requests.append(len(resObject['total_requests']))
            get_0_tp_requests.append(len(resObject['total_third_party_requests']))
            get_0_tp_percentage.append(getPercentage(len(resObject['total_third_party_requests']), len(resObject['total_requests'])))
        else:
            get_0_total_requests.append(np.nan)
            get_0_tp_requests.append(np.nan)
            get_0_tp_percentage.append(np.nan)
    elif resObject['index'] == 1 and resObject['index'] == display_index:
        sites.append(resObject['visited_site'])
        if resObject['success'] is True:
            get_1_total_requests.append(len(resObject['total_requests']))
            get_1_tp_requests.append(len(resObject['total_third_party_requests']))
            get_1_tp_percentage.append(getPercentage(len(resObject['total_third_party_requests']), len(resObject['total_requests'])))
        else:
            get_1_total_requests.append(np.nan)
            get_1_tp_requests.append(np.nan)
            get_1_tp_percentage.append(np.nan)
    elif resObject['index'] == 2 and resObject['index'] == display_index:
        sites.append(resObject['visited_site'])
        if resObject['success'] is True:
            get_2_total_requests.append(len(resObject['total_requests']))
            get_2_tp_requests.append(len(resObject['total_third_party_requests']))
            get_2_tp_percentage.append(getPercentage(len(resObject['total_third_party_requests']), len(resObject['total_requests'])))
        else:
            get_2_total_requests.append(np.nan)
            get_2_tp_requests.append(np.nan)
            get_2_tp_percentage.append(np.nan)
    elif resObject['index'] == 3 and resObject['index'] == display_index:
        sites.append(resObject['visited_site'])
        if resObject['success'] is True:
            get_3_total_requests.append(len(resObject['total_requests']))
            get_3_tp_requests.append(len(resObject['total_third_party_requests']))
            get_3_tp_percentage.append(getPercentage(len(resObject['total_third_party_requests']), len(resObject['total_requests'])))
        else:
            get_3_total_requests.append(np.nan)
            get_3_tp_requests.append(np.nan)
            get_3_tp_percentage.append(np.nan)
    elif resObject['index'] == 4 and resObject['index'] == display_index:
        sites.append(resObject['visited_site'])
        if resObject['success'] is True:
            get_4_total_requests.append(len(resObject['total_requests']))
            get_4_tp_requests.append(len(resObject['total_third_party_requests']))
            get_4_tp_percentage.append(getPercentage(len(resObject['total_third_party_requests']), len(resObject['total_requests'])))
        else:
            get_4_total_requests.append(np.nan)
            get_4_tp_requests.append(np.nan)
            get_4_tp_percentage.append(np.nan)
    elif resObject['index'] == 5 and resObject['index'] == display_index:
        sites.append(resObject['visited_site'])
        if resObject['success'] is True:
            browse_total_requests.append(len(resObject['total_requests']))
            browse_tp_requests.append(len(resObject['total_third_party_requests']))
            browse_tp_percentage.append(getPercentage(len(resObject['total_third_party_requests']), len(resObject['total_requests'])))
        else:
            browse_total_requests.append(np.nan)
            browse_tp_requests.append(np.nan)
            browse_tp_percentage.append(np.nan)


#######################################################
# CREATE PANDAS RESULT
#######################################################

# show if landing page
if display_index == 0:
    df = pd.DataFrame({'Site':list(sites), 'Total_Requests':list(get_0_total_requests), 'Third-Party-Requests':list(get_0_tp_requests), 'Third-Party-Percentage':list(get_0_tp_percentage)})
# show if subsite 1
if display_index == 1:
    df = pd.DataFrame({'Site':list(sites), 'Total_Requests':list(get_1_total_requests), 'Third-Party-Requests':list(get_1_tp_requests), 'Third-Party-Percentage':list(get_1_tp_percentage)})
# show if subsite 2
if display_index == 2:
    df = pd.DataFrame({'Site':list(sites), 'Total_Requests':list(get_2_total_requests), 'Third-Party-Requests':list(get_2_tp_requests), 'Third-Party-Percentage':list(get_2_tp_percentage)})
# show if subsite 3
if display_index == 3:
    df = pd.DataFrame({'Site':list(sites), 'Total_Requests':list(get_3_total_requests), 'Third-Party-Requests':list(get_3_tp_requests), 'Third-Party-Percentage':list(get_3_tp_percentage)})
# show if subsite 4
if display_index == 4:
    df = pd.DataFrame({'Site':list(sites), 'Total_Requests':list(get_4_total_requests), 'Third-Party-Requests':list(get_4_tp_requests), 'Third-Party-Percentage':list(get_4_tp_percentage)})
# show if browse
if display_index == 5:
    df = pd.DataFrame({'Site':list(sites), 'Total_Requests':list(browse_total_requests), 'Third-Party-Requests':list(browse_tp_requests), 'Third-Party-Percentage':list(browse_tp_percentage)})


df = df.sort_values(by=['Third-Party-Percentage'], ascending=False)
df = df.head(20)
print(df)



