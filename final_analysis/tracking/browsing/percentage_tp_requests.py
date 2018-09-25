import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3 as lite
import tldextract

def getDomain(site):
    ext = tldextract.extract(site)
    d = ext.domain
    s = ext.suffix
    res = d + "." + s
    if res == "de.com":
        res = "research.de.com"
    return res

def getTldOfSubURL(subUrl):
    # ATTENTION: url is ...-subX so we have to subtract that again
    if subUrl.endswith('-sub1') or subUrl.endswith('-sub2') or subUrl.endswith('-sub3') or subUrl.endswith('-sub4'):
        tldUrl = subUrl[:-5]
        return tldUrl
    else:
        return subUrl

def getPercentage(subset, superset):
    if np.isnan(subset) or np.isnan(superset):
        return np.nan
    if superset == 0:
        return 0
    else:
        percentage = (float(subset)/float(superset)) * 100
    return int(round(percentage))


# connect to the output database
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/1000_2.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# CUMULATIVE
# MAIN CONFIG
selected_crawl = 1
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
    
    if "GET" in cmd:
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
    visited_tld = getDomain(resObject['visited_site'])

    for url_tuple in cur.execute("SELECT url"
                                    " FROM http_requests"
                                    " WHERE visit_id = ?"
                                    " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):
        url = url_tuple[0]
        if "http" in url:
            third_party_tld = getDomain(url)
            total_requests.append(url)
            if not visited_tld in third_party_tld:
                # check if third-party
                total_third_party_requests.append(third_party_tld)
        else:
            raise ValueError('http is not in url!', url)


    resObject["total_requests"] = total_requests
    resObject["total_third_party_requests"] = total_third_party_requests

# Since GET subsites is cumulative, we have to add the sum of a next step to its value
sites0 = []
sites1 = []
sites2 = []
sites3 = []
sites4 = []

cumulative_get_0_total_requests = []
cumulative_get_1_total_requests = []
cumulative_get_2_total_requests = []
cumulative_get_3_total_requests = []
cumulative_get_4_total_requests = []

cumulative_get_0_tp_requests = []
cumulative_get_1_tp_requests = []
cumulative_get_2_tp_requests = []
cumulative_get_3_tp_requests = []
cumulative_get_4_tp_requests = []

# Third-Party Percentage per Site
cumulative_get_0_tp_percentage = []
cumulative_get_1_tp_percentage = []
cumulative_get_2_tp_percentage = []
cumulative_get_3_tp_percentage = []
cumulative_get_4_tp_percentage = []

get_0_mean_tp_percentage = 0
get_0_successes = 0
get_1_mean_tp_percentage = 0
get_1_successes = 0
get_2_mean_tp_percentage = 0
get_2_successes = 0
get_3_mean_tp_percentage = 0
get_3_successes = 0
get_4_mean_tp_percentage = 0
get_4_successes = 0

i = 0
for resObject in result:
    if resObject['index'] == 0:
        # ONLY USE DATA IF LANDING PAGE WAS SUCCESSFUL
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

            get_0_mean_tp_percentage += getPercentage(len(resObject['total_third_party_requests']), len(resObject['total_requests']))
            get_0_successes += 1

            sites0.append(resObject['visited_site'])
            cumulative_get_0_tp_percentage.append(getPercentage(cumulative_get_0_tp_requests[i], cumulative_get_0_total_requests[i]))
        else:
            cumulative_get_0_tp_requests.append(np.nan)
            cumulative_get_1_tp_requests.append(np.nan)
            cumulative_get_2_tp_requests.append(np.nan)
            cumulative_get_3_tp_requests.append(np.nan)
            cumulative_get_4_tp_requests.append(np.nan)

            cumulative_get_0_total_requests.append(np.nan)
            cumulative_get_1_total_requests.append(np.nan)
            cumulative_get_2_total_requests.append(np.nan)
            cumulative_get_3_total_requests.append(np.nan)
            cumulative_get_4_total_requests.append(np.nan)
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

            if not np.isnan(getPercentage(cumulative_get_1_tp_requests[i], cumulative_get_1_total_requests[i])):
                get_1_mean_tp_percentage += getPercentage(cumulative_get_1_tp_requests[i], cumulative_get_1_total_requests[i])
                get_1_successes += 1

                sites1.append(resObject['visited_site'])
                cumulative_get_1_tp_percentage.append(getPercentage(cumulative_get_1_tp_requests[i], cumulative_get_1_total_requests[i]))
    elif resObject['index'] == 2:
        if resObject['success'] == True:
            cumulative_get_2_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_3_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_4_tp_requests[i] += len(resObject['total_third_party_requests'])

            cumulative_get_2_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_3_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_4_total_requests[i] += len(resObject['total_requests'])

            if not np.isnan(getPercentage(cumulative_get_2_tp_requests[i], cumulative_get_2_total_requests[i])):
                get_2_mean_tp_percentage += getPercentage(cumulative_get_2_tp_requests[i], cumulative_get_2_total_requests[i])
                get_2_successes += 1

                sites2.append(resObject['visited_site'])
                cumulative_get_2_tp_percentage.append(getPercentage(cumulative_get_2_tp_requests[i], cumulative_get_2_total_requests[i]))
    elif resObject['index'] == 3:
        if resObject['success'] == True:
            cumulative_get_3_tp_requests[i] += len(resObject['total_third_party_requests'])
            cumulative_get_4_tp_requests[i] += len(resObject['total_third_party_requests'])

            cumulative_get_3_total_requests[i] += len(resObject['total_requests'])
            cumulative_get_4_total_requests[i] += len(resObject['total_requests'])

            if not np.isnan(getPercentage(cumulative_get_3_tp_requests[i], cumulative_get_3_total_requests[i])):
                get_3_mean_tp_percentage += getPercentage(cumulative_get_3_tp_requests[i], cumulative_get_3_total_requests[i])
                get_3_successes += 1

                sites3.append(resObject['visited_site'])
                cumulative_get_3_tp_percentage.append(getPercentage(cumulative_get_3_tp_requests[i], cumulative_get_3_total_requests[i]))
    elif resObject['index'] == 4:
        if resObject['success'] == True:
            cumulative_get_4_tp_requests[i] += len(resObject['total_third_party_requests'])

            cumulative_get_4_total_requests[i] += len(resObject['total_requests'])

            if not np.isnan(getPercentage(cumulative_get_4_tp_requests[i], cumulative_get_4_total_requests[i])):
                get_4_mean_tp_percentage += getPercentage(cumulative_get_4_tp_requests[i], cumulative_get_4_total_requests[i])
                get_4_successes += 1

                sites4.append(resObject['visited_site'])
                cumulative_get_4_tp_percentage.append(getPercentage(cumulative_get_4_tp_requests[i], cumulative_get_4_total_requests[i]))
        i += 1


#######################################################
# CREATE PANDAS RESULT
#######################################################

df0 = pd.DataFrame({'Site':list(sites0), 'Third-Party-Percentage':list(cumulative_get_0_tp_percentage)})
res0 = float(get_0_mean_tp_percentage)/float(get_0_successes), '%'
print "res0:", res0, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_0_tp_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "0 less than 10:", less_than_10
print "0 exactly 0:", exactly_0
print "0 length: ", len(cumulative_get_0_tp_percentage)

df1 = pd.DataFrame({'Site':list(sites1), 'Third-Party-Percentage':list(cumulative_get_1_tp_percentage)})
res1 = float(get_1_mean_tp_percentage)/float(get_1_successes), '%'
print "res1:", res1, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_1_tp_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "0 less than 10:", less_than_10
print "0 exactly 0:", exactly_0
print "0 length: ", len(cumulative_get_1_tp_percentage)

df2 = pd.DataFrame({'Site':list(sites2), 'Third-Party-Percentage':list(cumulative_get_2_tp_percentage)})
res2 = float(get_2_mean_tp_percentage)/float(get_2_successes), '%'
print "res2:", res2, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_2_tp_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "0 less than 10:", less_than_10
print "0 exactly 0:", exactly_0
print "0 length: ", len(cumulative_get_2_tp_percentage)

df3 = pd.DataFrame({'Site':list(sites3), 'Third-Party-Percentage':list(cumulative_get_3_tp_percentage)})
res3 = float(get_3_mean_tp_percentage)/float(get_3_successes), '%'
print "res3:", res3, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_3_tp_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "0 less than 10:", less_than_10
print "0 exactly 0:", exactly_0
print "0 length: ", len(cumulative_get_3_tp_percentage)

df4 = pd.DataFrame({'Site':list(sites4), 'Third-Party-Percentage':list(cumulative_get_4_tp_percentage)})
res4 = float(get_4_mean_tp_percentage)/float(get_4_successes), '%'
print "res4:", res4, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_4_tp_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "0 less than 10:", less_than_10
print "0 exactly 0:", exactly_0
print "0 length: ", len(cumulative_get_4_tp_percentage)

df0P = df0.sort_values(by=['Third-Party-Percentage'], ascending=False)
df0P.to_csv('tables/tp_percentage_0_P2.csv', sep='\t', encoding='utf-8', index=False)

# df1P = df1.sort_values(by=['Third-Party-Percentage'], ascending=False)
# df1P.to_csv('tables/cumulated_top_sites_1_P.csv', sep='\t', encoding='utf-8', index=False)
# df1T = df1.sort_values(by=['Ads'], ascending=False)
# df1T.to_csv('tables/cumulated_top_sites_1_T.csv', sep='\t', encoding='utf-8', index=False)

# df2P = df2.sort_values(by=['Third-Party-Percentage'], ascending=False)
# df2P.to_csv('tables/cumulated_top_sites_2_P.csv', sep='\t', encoding='utf-8', index=False)
# df2T = df2.sort_values(by=['Ads'], ascending=False)
# df2T.to_csv('tables/cumulated_top_sites_2_T.csv', sep='\t', encoding='utf-8', index=False)

# df3P = df3.sort_values(by=['Third-Party-Percentage'], ascending=False)
# df3P.to_csv('tables/cumulated_top_sites_3_P.csv', sep='\t', encoding='utf-8', index=False)
# df3T = df3.sort_values(by=['Ads'], ascending=False)
# df3T.to_csv('tables/cumulated_top_sites_3_T.csv', sep='\t', encoding='utf-8', index=False)

df4P = df4.sort_values(by=['Third-Party-Percentage'], ascending=False)
df4P.to_csv('tables/tp_percentage_4_P2.csv', sep='\t', encoding='utf-8', index=False)
