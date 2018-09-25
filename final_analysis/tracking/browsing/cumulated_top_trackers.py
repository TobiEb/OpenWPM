import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3 as lite
import tldextract

from tracking_rules import TrackingRules
from ad_rules import AdRules
from adblockparser import AdblockRules

global rules_instance
ad_rules_instance = AdRules()
tracking_rules_instance = TrackingRules()
raw_rules = ad_rules_instance.rules
raw_rules += tracking_rules_instance.rules
rules = AdblockRules(raw_rules, use_re2=True)
#
#
#
#
# CUMULATIVE
# MAIN CONFIG
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/1000_1.sqlite'
selected_crawl = 1
display_index = 4 # 0 is UNTIL landing page, 1-4 subsites
show_tracking_and_third_parties = True # True: show tracking-percentage as part of third-party percentage in diagram
                                           # False: show only tracking percentage in diagram

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

def getDomain(site):
    ext = tldextract.extract(site)
    d = ext.domain
    s = ext.suffix
    res = d + "." + s
    if res == "de.com":
        res = "research.de.com"
    return res

# connect to the output database
conn = lite.connect(wpm_db)
cur = conn.cursor()

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

# add tracking-urls
all_crawled_sites = []
all_ad_and_tracking_sites = []
all_third_party_sites = []
for resObject in result:
    if resObject['index'] <= display_index:
        third_party_sites = []
        tracking_sites = []
        visited_tld = getDomain(resObject['visited_site'])
        if resObject['index'] == 0 and resObject['success'] is True:
            # only add once per successful site
            all_crawled_sites.append(visited_tld)

        for url_tuple in cur.execute("SELECT url"
                                        " FROM http_requests"
                                        " WHERE visit_id = ?"
                                        " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):
            url = url_tuple[0]
            if "http" in url:
                third_party_tld = getDomain(url)
                if not visited_tld in third_party_tld:
                    # check if third-party
                    if not third_party_tld in all_third_party_sites:
                        all_third_party_sites.append(str(third_party_tld))
                    if not third_party_tld in third_party_sites:
                        third_party_sites.append(str(third_party_tld))
                    if rules.should_block(url) is True:
                        # check if tracking site
                        if not third_party_tld in all_ad_and_tracking_sites:
                            all_ad_and_tracking_sites.append(str(third_party_tld))
                        if not third_party_tld in tracking_sites:
                            tracking_sites.append(str(third_party_tld))
            else:
                raise ValueError('http is not in url!', url)

        resObject["third_party_sites"] = third_party_sites
        resObject["tracking_sites"] = tracking_sites

# Percentages (each percentage per third-party site)
third_party_percentages_array = []

# Percentages (each percentage per tracking site)
tracker_percentages_array = []

if show_tracking_and_third_parties is True:
    for third_party_site in all_third_party_sites:
        tp_occurences = 0
        site_has_tp = False
        tracker_occurences = 0
        site_has_tracker = False
        site_was_successful = False
        for resObject in result:
            if resObject['index'] <= display_index:
                if resObject['index'] == 0 and resObject['success'] is True:
                    # for each successful site set to false
                    site_has_tp = False
                    site_has_tracker = False
                    site_was_successful = True
                elif resObject['index'] == 0 and resObject['success'] is False:
                    site_was_successful = False
                if site_was_successful is True:
                    if site_has_tp is False:
                        if third_party_site in resObject['third_party_sites']:
                            tp_occurences += 1
                            site_has_tp = True
                    if site_has_tracker is False:
                        if third_party_site in resObject['tracking_sites']:
                            tracker_occurences += 1
                            site_has_tracker = True
        third_party_percentages_array.append(getPercentage(tp_occurences, len(all_crawled_sites)))
        tracker_percentages_array.append(getPercentage(tracker_occurences, len(all_crawled_sites)))
else:
    for tracker_site in all_ad_and_tracking_sites:
        tracker_occurences = 0
        site_has_tracker = False
        site_was_successful = False
        for resObject in result:
            if resObject['index'] <= display_index:
                if resObject['index'] == 0 and resObject['success'] is True:
                    # for each successful site set to false
                    site_has_tracker = False
                    site_was_successful = True
                elif resObject['index'] == 0 and resObject['success'] is False:
                    site_was_successful = False
                if site_was_successful is True and site_has_tracker is False:
                    # check if ad is already matched to this crawled site
                    if tracker_site in resObject['tracking_sites']:
                        tracker_occurences += 1
                        site_has_tracker = True
        tracker_percentages_array.append(getPercentage(tracker_occurences, len(all_crawled_sites)))

#######################################################
# CREATE PANDAS RESULT
#######################################################

if show_tracking_and_third_parties is True:
    df = pd.DataFrame({'Site':all_third_party_sites, 'TP-Percentage':third_party_percentages_array, 'Tracker-Percentage':tracker_percentages_array})
    df = df.sort_values(by=['TP-Percentage'], ascending=False)
else:
    df = pd.DataFrame({'Site':all_ad_and_tracking_sites, 'Tracker-Percentage':tracker_percentages_array})
    df = df.sort_values(by=['Tracker-Percentage'], ascending=False)

# df = df.head(50)
df.to_csv('tables/cumulated_top_trackers_4_1.csv', sep='\t', encoding='utf-8', index=False)

# if show_tracking_and_third_parties is True:
#     plt.bar(df['Site'], df['TP-Percentage'], color="grey")
#     plt.bar(df['Site'], df['Tracker-Percentage'], color="black")
#     # plt.title("Most prevalent Third-Parties and Trackers")
#     plt.xlabel("Third-Party or Tracker")
#     plt.legend(['Third-Party Percentage', 'Tracker Percentage'])
# else:
#     plt.bar(df['Site'], df['Tracker-Percentage'], color="black")
#     # plt.title("Most prevalent Trackers")
#     plt.xlabel("Tracker")
#     plt.legend(['Tracker Percentage'])
# plt.ylabel("% of First-Party Sites")
# plt.xticks(rotation=-45, horizontalalignment="left")
# # plt.grid()
# # plt.show()
# plt.savefig('figures/top_third-parties_and_trackers.png', bbox_inches='tight')
