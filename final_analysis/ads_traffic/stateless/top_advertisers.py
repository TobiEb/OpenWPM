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
# NON CUMULATIVE
# MAIN CONFIG
selected_crawl = 1
display_index = 0 # 0 is landing page, 1-4 subsites
show_advertising_and_third_parties = False # True: show ads-percentage as part of third-party percentage in diagram
                                           # False: show only ads percentage in diagram
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

def getDomain(site):
    ext = tldextract.extract(site)
    d = ext.domain
    s = ext.suffix
    res = d + "." + s
    if res == "de.com":
        res = "research.de.com"
    return res

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

# add ad-urls
all_crawled_sites = []
all_advertising_sites = []
all_third_party_sites = []
for resObject in result:
    if resObject['index'] == display_index and resObject['success'] is True:
        third_party_sites = []
        advertising_sites = []
        ext = tldextract.extract(resObject["visited_site"])
        visited_tld = ext.domain
        all_crawled_sites.append(visited_tld)

        for url_tuple in cur.execute("SELECT url"
                                        " FROM http_requests"
                                        " WHERE visit_id = ?"
                                        " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):
            url = url_tuple[0]
            if "http" in url:
                xt = tldextract.extract(url)
                third_party_tld = xt.domain
                if not visited_tld in third_party_tld:
                    # check if third-party
                    if not third_party_tld in all_third_party_sites:
                        all_third_party_sites.append(str(third_party_tld))
                    if not third_party_tld in third_party_sites:
                        third_party_sites.append(str(third_party_tld))
                if rules.should_block(url) is True:
                    # check if advertisement
                    if not third_party_tld in all_advertising_sites:
                        all_advertising_sites.append(str(third_party_tld))
                    if not third_party_tld in advertising_sites:
                        advertising_sites.append(str(third_party_tld))
            else:
                raise ValueError('http is not in url!', url)

        resObject["third_party_sites"] = third_party_sites
        resObject["advertising_sites"] = advertising_sites

# Percentages (each percentage per third-party site)
third_party_percentages_array = []

# Percentages (each percentage per advertiser site)
advertiser_percentages_array = []

if show_advertising_and_third_parties is True:
    for third_party_site in all_third_party_sites:
        tp_occurences = 0
        advertiser_occurences = 0
        for resObject in result:
            if resObject['index'] == display_index and resObject['success'] is True:
                if third_party_site in resObject['third_party_sites']:
                    tp_occurences += 1
                if third_party_site in resObject['advertising_sites']:
                    advertiser_occurences += 1
        third_party_percentages_array.append(getPercentage(tp_occurences, len(all_crawled_sites)))
        advertiser_percentages_array.append(getPercentage(advertiser_occurences, len(all_crawled_sites)))
else:
    for ad_site in all_advertising_sites:
        advertiser_occurences = 0
        for resObject in result:
            if resObject['index'] == display_index and resObject['success'] is True:
                if ad_site in resObject['advertising_sites']:
                    advertiser_occurences += 1
        advertiser_percentages_array.append(getPercentage(advertiser_occurences, len(all_crawled_sites)))

#######################################################
# CREATE PANDAS RESULT
#######################################################

if show_advertising_and_third_parties is True:
    df = pd.DataFrame({'Site':all_third_party_sites, 'tp-Percentage':third_party_percentages_array, 'Ad-Percentage':advertiser_percentages_array})
    df = df.sort_values(by=['tp-Percentage'], ascending=False)
else:
    df = pd.DataFrame({'Site':all_advertising_sites, 'Ad-Percentage':advertiser_percentages_array})
    df = df.sort_values(by=['Ad-Percentage'], ascending=False)

df = df.head(15)

if show_advertising_and_third_parties is True:
    plt.bar(df['Site'], df['tp-Percentage'], color="blue")
    plt.bar(df['Site'], df['Ad-Percentage'], color="red")
    plt.title("Most prevalent Third-Parties and Advertizers")
    plt.xlabel("Third-Party and Advertizer Domain")
    plt.legend(['Third-Party Percentage', 'Ad-Percentage'])
else:
    plt.bar(df['Site'], df['Ad-Percentage'], color="red")
    plt.title("Most prevalent Advertisers")
    plt.xlabel("Advertiser Domain")
    plt.legend(['Ad-Percentage'])
plt.ylabel("Percentage of presence on sites")
plt.xticks(rotation=-45, horizontalalignment="left")
plt.grid()

plt.savefig('figures/top_advertisers_homepage.png', bbox_inches='tight')




