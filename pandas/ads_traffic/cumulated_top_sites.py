import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3 as lite
import tldextract

from ad_rules import AdRules
from adblockparser import AdblockRules

global rules_instance
rules_instance = AdRules()
raw_rules = rules_instance.rules
rules = AdblockRules(raw_rules, use_re2=True)
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

# add Content-Length
for resObject in result:
    content_length = 0
    first_party_content_length = 0
    third_party_content_length = 0
    advertisements_content_length = 0
    
    if resObject['index'] <= display_index:
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
                    if rules.should_block(url) is True:
                        advertisements_content_length = advertisements_content_length + current_length
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
    resObject["ad-content-length"] = advertisements_content_length

# Total Content-Lengths per Site
# CUMULATIVE
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

# Third-Party Percentage per Site
cumulative_get_0_tp_percentage = []
cumulative_get_1_tp_percentage = []
cumulative_get_2_tp_percentage = []
cumulative_get_3_tp_percentage = []
cumulative_get_4_tp_percentage = []
browse_tp_percentage = []

# Advertisements Content-Lengths per Site
cumulative_get_0_ad_content_lengths = []
cumulative_get_1_ad_content_lengths = []
cumulative_get_2_ad_content_lengths = []
cumulative_get_3_ad_content_lengths = []
cumulative_get_4_ad_content_lengths = []
browse_ad_content_lengths = []

# Advertisements Percentage per Site
cumulative_get_0_ad_percentage = []
cumulative_get_1_ad_percentage = []
cumulative_get_2_ad_percentage = []
cumulative_get_3_ad_percentage = []
cumulative_get_4_ad_percentage = []
browse_ad_percentage = []

i = 0
for resObject in result:
    if resObject['index'] == 0:
        sites.append(resObject['visited_site'])
        if resObject['success'] is True:
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

            cumulative_get_0_ad_content_lengths.append(resObject['ad-content-length'])
            cumulative_get_1_ad_content_lengths.append(resObject['ad-content-length'])
            cumulative_get_2_ad_content_lengths.append(resObject['ad-content-length'])
            cumulative_get_3_ad_content_lengths.append(resObject['ad-content-length'])
            cumulative_get_4_ad_content_lengths.append(resObject['ad-content-length'])

            cumulative_get_0_tp_percentage.append(getPercentage(cumulative_get_0_tp_content_lengths[i], cumulative_get_0_total_content_lengths[i]))
            cumulative_get_0_ad_percentage.append(getPercentage(cumulative_get_0_ad_content_lengths[i], cumulative_get_0_total_content_lengths[i]))
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

            cumulative_get_0_ad_content_lengths.append(0)
            cumulative_get_1_ad_content_lengths.append(0)
            cumulative_get_2_ad_content_lengths.append(0)
            cumulative_get_3_ad_content_lengths.append(0)
            cumulative_get_4_ad_content_lengths.append(0)

            cumulative_get_0_tp_percentage.append(np.nan)
            cumulative_get_0_ad_percentage.append(np.nan)
    elif resObject['index'] == 1:
        if resObject['success'] is True:
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

            cumulative_get_1_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_2_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_3_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_4_ad_content_lengths[i] += resObject['ad-content-length']

        cumulative_get_1_tp_percentage.append(getPercentage(cumulative_get_1_tp_content_lengths[i], cumulative_get_1_total_content_lengths[i]))
        cumulative_get_1_ad_percentage.append(getPercentage(cumulative_get_1_ad_content_lengths[i], cumulative_get_1_total_content_lengths[i]))
    elif resObject['index'] == 2:
        if resObject['success'] is True:
            cumulative_get_2_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_3_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']

            cumulative_get_2_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_3_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_4_fp_content_lengths[i] += resObject['first-party-content-length']

            cumulative_get_2_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_3_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']

            cumulative_get_2_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_3_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_4_ad_content_lengths[i] += resObject['ad-content-length']

        cumulative_get_2_tp_percentage.append(getPercentage(cumulative_get_2_tp_content_lengths[i], cumulative_get_2_total_content_lengths[i]))
        cumulative_get_2_ad_percentage.append(getPercentage(cumulative_get_2_ad_content_lengths[i], cumulative_get_2_total_content_lengths[i]))
    elif resObject['index'] == 3:
        if resObject['success'] is True:
            cumulative_get_3_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']

            cumulative_get_3_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_4_fp_content_lengths[i] += resObject['first-party-content-length']

            cumulative_get_3_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']

            cumulative_get_3_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_4_ad_content_lengths[i] += resObject['ad-content-length']

        cumulative_get_3_tp_percentage.append(getPercentage(cumulative_get_3_tp_content_lengths[i], cumulative_get_3_total_content_lengths[i]))
        cumulative_get_3_ad_percentage.append(getPercentage(cumulative_get_3_ad_content_lengths[i], cumulative_get_3_total_content_lengths[i]))
    elif resObject['index'] == 4:
        if resObject['success'] is True:
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_fp_content_lengths[i] += resObject['first-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_ad_content_lengths[i] += resObject['ad-content-length']

        cumulative_get_4_tp_percentage.append(getPercentage(cumulative_get_4_tp_content_lengths[i], cumulative_get_4_total_content_lengths[i]))
        cumulative_get_4_ad_percentage.append(getPercentage(cumulative_get_4_ad_content_lengths[i], cumulative_get_4_total_content_lengths[i]))
        i += 1
    elif resObject['index'] == 5:
        if resObject['success'] is True:
            browse_total_content_lengths.append(resObject['total-content-length'])
            browse_fp_content_lengths.append(resObject['first-party-content-length'])
            browse_tp_content_lengths.append(resObject['third-party-content-length'])
            browse_ad_content_lengths.append(resObject['ad-content-length'])

            browse_tp_percentage.append(getPercentage(resObject['third-party-content-length'], resObject['total-content-length']))
            browse_ad_percentage.append(getPercentage(resObject['ad-content-length'], resObject['total-content-length']))
        else:
            browse_tp_percentage.append(np.nan)
            browse_ad_percentage.append(np.nan)

#######################################################
# CREATE PANDAS RESULT
#######################################################
# show if landing page
if display_index == 0:
    df = pd.DataFrame({'Site':list(sites), 'Total':list(cumulative_get_0_total_content_lengths), 'First-Party':list(cumulative_get_0_fp_content_lengths), 'Third-Party':list(cumulative_get_0_tp_content_lengths), 'Third-Party-Percentage':list(cumulative_get_0_tp_percentage), 'Ads':list(cumulative_get_0_ad_content_lengths), 'Ads-Percentage':list(cumulative_get_0_ad_percentage)})
# show if subsite 1
if display_index == 1:
    df = pd.DataFrame({'Site':list(sites), 'Total':list(cumulative_get_1_total_content_lengths), 'First-Party':list(cumulative_get_1_fp_content_lengths), 'Third-Party':list(cumulative_get_1_tp_content_lengths), 'Third-Party-Percentage':list(cumulative_get_1_tp_percentage), 'Ads':list(cumulative_get_1_ad_content_lengths), 'Ads-Percentage':list(cumulative_get_1_ad_percentage)})
# show if subsite 2
if display_index == 2:
    df = pd.DataFrame({'Site':list(sites), 'Total':list(cumulative_get_2_total_content_lengths), 'First-Party':list(cumulative_get_2_fp_content_lengths), 'Third-Party':list(cumulative_get_2_tp_content_lengths), 'Third-Party-Percentage':list(cumulative_get_2_tp_percentage), 'Ads':list(cumulative_get_2_ad_content_lengths), 'Ads-Percentage':list(cumulative_get_2_ad_percentage)})
# show if subsite 3
if display_index == 3:
    df = pd.DataFrame({'Site':list(sites), 'Total':list(cumulative_get_3_total_content_lengths), 'First-Party':list(cumulative_get_3_fp_content_lengths), 'Third-Party':list(cumulative_get_3_tp_content_lengths), 'Third-Party-Percentage':list(cumulative_get_3_tp_percentage), 'Ads':list(cumulative_get_3_ad_content_lengths), 'Ads-Percentage':list(cumulative_get_3_ad_percentage)})
# show if subsite 4
if display_index == 4:
    df = pd.DataFrame({'Site':list(sites), 'Total':list(cumulative_get_4_total_content_lengths), 'First-Party':list(cumulative_get_4_fp_content_lengths), 'Third-Party':list(cumulative_get_4_tp_content_lengths), 'Third-Party-Percentage':list(cumulative_get_4_tp_percentage), 'Ads':list(cumulative_get_4_ad_content_lengths), 'Ads-Percentage':list(cumulative_get_4_ad_percentage)})
# show if browse
if display_index == 5:
    df = pd.DataFrame({'Site':list(sites), 'Total':list(browse_total_content_lengths), 'First-Party':list(browse_fp_content_lengths), 'Third-Party':list(browse_tp_content_lengths), 'Third-Party-Percentage':list(browse_tp_percentage), 'Ads':list(browse_ad_content_lengths), 'Ads-Percentage':list(browse_ad_percentage)})


df = df.sort_values(by=['Ads-Percentage'], ascending=False)
df = df.head(20)
print(df)



