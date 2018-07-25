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

# add Content-Length
for resObject in result:
    content_length = 0
    first_party_content_length = 0
    third_party_content_length = 0
    ext = tldextract.extract(resObject["visited_site"])
    visited_tld = ext.domain

    for header, url in cur.execute("SELECT headers, url"
                                    " FROM http_responses"
                                    " WHERE visit_id = ?"
                                    " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):
        if "Content-Length" in header:
            current_length = header.index("Content-Length")
            content_length = content_length + current_length
            if "http" in url:
                xt = tldextract.extract(url)
                third_party_tld = xt.domain
                if not visited_tld in third_party_tld:
                # it is third-party
                    third_party_content_length = third_party_content_length + current_length
                else:
                    first_party_content_length = first_party_content_length + current_length

    resObject["total-content-length"] = content_length
    resObject["first-party-content-length"] = first_party_content_length
    resObject["third-party-content-length"] = third_party_content_length

# Since GET subsites is cumulative, we have to add the sum of a next step to its value
# Total Content-Lengths per Site
sites = []
cumulative_get_0_total_content_lengths = []
cumulative_get_1_total_content_lengths = []
cumulative_get_2_total_content_lengths = []
cumulative_get_3_total_content_lengths = []
cumulative_get_4_total_content_lengths = []
browse_total_content_lengths = []

# First-Party Content-Lengths per Site
cumulative_get_0_fp_content_lengths = []
cumulative_get_1_fp_content_lengths = []
cumulative_get_2_fp_content_lengths = []
cumulative_get_3_fp_content_lengths = []
cumulative_get_4_fp_content_lengths = []
browse_fp_content_lengths = []

# Third-Party Content-Lengths per Site
cumulative_get_0_tp_content_lengths = []
cumulative_get_1_tp_content_lengths = []
cumulative_get_2_tp_content_lengths = []
cumulative_get_3_tp_content_lengths = []
cumulative_get_4_tp_content_lengths = []
browse_tp_content_lengths = []

i = 0
for resObject in result:
    if resObject['index'] == 0:
        sites.append(resObject['visited_site'])
        if resObject['success'] == True:
            cumulative_get_0_total_content_lengths.append(resObject['total-content-length'])
            cumulative_get_1_total_content_lengths.append(resObject['total-content-length'])
            cumulative_get_2_total_content_lengths.append(resObject['total-content-length'])
            cumulative_get_3_total_content_lengths.append(resObject['total-content-length'])
            cumulative_get_4_total_content_lengths.append(resObject['total-content-length'])

            cumulative_get_0_fp_content_lengths.append(resObject['first-party-content-length'])
            cumulative_get_1_fp_content_lengths.append(resObject['first-party-content-length'])
            cumulative_get_2_fp_content_lengths.append(resObject['first-party-content-length'])
            cumulative_get_3_fp_content_lengths.append(resObject['first-party-content-length'])
            cumulative_get_4_fp_content_lengths.append(resObject['first-party-content-length'])

            cumulative_get_0_tp_content_lengths.append(resObject['third-party-content-length'])
            cumulative_get_1_tp_content_lengths.append(resObject['third-party-content-length'])
            cumulative_get_2_tp_content_lengths.append(resObject['third-party-content-length'])
            cumulative_get_3_tp_content_lengths.append(resObject['third-party-content-length'])
            cumulative_get_4_tp_content_lengths.append(resObject['third-party-content-length'])

        else:
            cumulative_get_0_total_content_lengths.append(0)
            cumulative_get_1_total_content_lengths.append(0)
            cumulative_get_2_total_content_lengths.append(0)
            cumulative_get_3_total_content_lengths.append(0)
            cumulative_get_4_total_content_lengths.append(0)

            cumulative_get_0_fp_content_lengths.append(0)
            cumulative_get_1_fp_content_lengths.append(0)
            cumulative_get_2_fp_content_lengths.append(0)
            cumulative_get_3_fp_content_lengths.append(0)
            cumulative_get_4_fp_content_lengths.append(0)

            cumulative_get_0_tp_content_lengths.append(0)
            cumulative_get_1_tp_content_lengths.append(0)
            cumulative_get_2_tp_content_lengths.append(0)
            cumulative_get_3_tp_content_lengths.append(0)
            cumulative_get_4_tp_content_lengths.append(0)

    elif resObject['index'] == 1:
        if resObject['success'] == True:
            cumulative_get_1_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_2_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_3_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']

            cumulative_get_1_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_2_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_3_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_4_fp_content_lengths[i] += resObject['first-party-content-length']

            cumulative_get_1_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_2_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_3_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']

    elif resObject['index'] == 2:
        if resObject['success'] == True:
            cumulative_get_2_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_3_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']

            cumulative_get_2_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_3_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_4_fp_content_lengths[i] += resObject['first-party-content-length']

            cumulative_get_2_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_3_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']

    elif resObject['index'] == 3:
        if resObject['success'] == True:
            cumulative_get_3_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']

            cumulative_get_3_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_4_fp_content_lengths[i] += resObject['first-party-content-length']

            cumulative_get_3_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']

    elif resObject['index'] == 4:
        if resObject['success'] == True:
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']
        i += 1
    elif resObject['index'] == 5:
        # index 5 is BROWSE command
        if resObject['success'] == True:
            browse_total_content_lengths.append(resObject['total-content-length'])
            browse_fp_content_lengths.append(resObject['first-party-content-length'])
            browse_tp_content_lengths.append(resObject['third-party-content-length'])
        else:
            browse_total_content_lengths.append(0)
            browse_fp_content_lengths.append(0)
            browse_tp_content_lengths.append(0)


#######################################################
# CREATE PANDAS RESULT
#######################################################

# LANDING PAGE
get_0_total_length = 0
for res in cumulative_get_0_total_content_lengths:
    get_0_total_length += res

get_0_first_party_length = 0
for res in cumulative_get_0_fp_content_lengths:
    get_0_first_party_length += res

get_0_third_party_length = 0
for res in cumulative_get_0_tp_content_lengths:
    get_0_third_party_length += res

# SUBSITE 1
get_1_total_length = 0
for res in cumulative_get_1_total_content_lengths:
    get_1_total_length += res

get_1_first_party_length = 0
for res in cumulative_get_1_fp_content_lengths:
    get_1_first_party_length += res

get_1_third_party_length = 0
for res in cumulative_get_1_tp_content_lengths:
    get_1_third_party_length += res

# SUBSITE 2
get_2_total_length = 0
for res in cumulative_get_2_total_content_lengths:
    get_2_total_length += res

get_2_first_party_length = 0
for res in cumulative_get_2_fp_content_lengths:
    get_2_first_party_length += res

get_2_third_party_length = 0
for res in cumulative_get_2_tp_content_lengths:
    get_2_third_party_length += res

# SUBSITE 3
get_3_total_length = 0
for res in cumulative_get_3_total_content_lengths:
    get_3_total_length += res

get_3_first_party_length = 0
for res in cumulative_get_3_fp_content_lengths:
    get_3_first_party_length += res

get_3_third_party_length = 0
for res in cumulative_get_3_tp_content_lengths:
    get_3_third_party_length += res

# SUBSITE 4
get_4_total_length = 0
for res in cumulative_get_4_total_content_lengths:
    get_4_total_length += res

get_4_first_party_length = 0
for res in cumulative_get_4_fp_content_lengths:
    get_4_first_party_length += res

get_4_third_party_length = 0
for res in cumulative_get_4_tp_content_lengths:
    get_4_third_party_length += res

# BROWSE 4 FOR COMPARISON
browse_total_length = 0
for res in browse_total_content_lengths:
    browse_total_length += res

browse_first_party_length = 0
for res in browse_fp_content_lengths:
    browse_first_party_length += res

browse_third_party_length = 0
for res in browse_tp_content_lengths:
    browse_third_party_length += res


print "Averaged Total HTTP Bytes vs First-Party Bytes vs Third-Party Bytes (and in Percentage)"
print "Landing Page", (get_0_total_length/len(cumulative_get_0_total_content_lengths)), "Bytes | ",(get_0_first_party_length/len(cumulative_get_0_fp_content_lengths)), "Bytes | ", (get_0_third_party_length/len(cumulative_get_0_tp_content_lengths)), "Bytes"
print "Das sind: ",getPercentage(get_0_first_party_length, get_0_total_length),"% | ", getPercentage(get_0_third_party_length, get_0_total_length), "%"
print "Subsite 1", (get_1_total_length/len(cumulative_get_1_total_content_lengths)), "Bytes | ",(get_1_first_party_length/len(cumulative_get_1_fp_content_lengths)), "Bytes | ", (get_1_third_party_length/len(cumulative_get_1_tp_content_lengths)), "Bytes"
print "Das sind: ",getPercentage(get_1_first_party_length, get_1_total_length),"% | ", getPercentage(get_1_third_party_length, get_1_total_length), "%"
print "Subsite 2", (get_2_total_length/len(cumulative_get_2_total_content_lengths)), "Bytes | ",(get_2_first_party_length/len(cumulative_get_2_fp_content_lengths)), "Bytes | ", (get_2_third_party_length/len(cumulative_get_2_tp_content_lengths)), "Bytes"
print "Das sind: ",getPercentage(get_2_first_party_length, get_2_total_length),"% | ", getPercentage(get_2_third_party_length, get_2_total_length), "%"
print "Subsite 3", (get_3_total_length/len(cumulative_get_3_total_content_lengths)), "Bytes | ",(get_3_first_party_length/len(cumulative_get_3_fp_content_lengths)), "Bytes | ", (get_3_third_party_length/len(cumulative_get_3_tp_content_lengths)), "Bytes"
print "Das sind: ",getPercentage(get_3_first_party_length, get_3_total_length),"% | ", getPercentage(get_3_third_party_length, get_3_total_length), "%"
print "Subsite 4", (get_4_total_length/len(cumulative_get_4_total_content_lengths)), "Bytes | ",(get_4_first_party_length/len(cumulative_get_4_fp_content_lengths)), "Bytes | ", (get_4_third_party_length/len(cumulative_get_4_tp_content_lengths)), "Bytes"
print "Das sind: ",getPercentage(get_4_first_party_length, get_4_total_length),"% | ", getPercentage(get_4_third_party_length, get_4_total_length), "%"
print "BROWSE 4", (browse_total_length/len(browse_total_content_lengths)), "Bytes | ",(browse_first_party_length/len(browse_fp_content_lengths)), "Bytes | ", (browse_third_party_length/len(browse_tp_content_lengths)), "Bytes"
print "Das sind: ",getPercentage(browse_first_party_length, browse_total_length),"% | ", getPercentage(browse_third_party_length, browse_total_length), "%"


