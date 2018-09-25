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
# CUMULATED
# MAIN CONFIG
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/1000_1.sqlite'
display_index = 4 # 0 is UNTIL landing page, UNTIL 1-4 subsites
selected_crawl = 1

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

# add Content-Length
for resObject in result:
    content_length = 0
    third_party_content_length = 0
    advertisements_content_length = 0
    
    if resObject['index'] <= display_index:
        visited_tld = getDomain(resObject["visited_site"])

        for header, url in cur.execute("SELECT headers, url"
                                        " FROM http_responses"
                                        " WHERE visit_id = ?"
                                        " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):
            if "Content-Length" in header:
                current_length = header.index("Content-Length")
                content_length = content_length + current_length
                if "http" in url:
                    if rules.should_block(url) is True:
                        # it is advertisement
                        advertisements_content_length = advertisements_content_length + current_length
                    third_party_tld = getDomain(url)
                    if not visited_tld in third_party_tld:
                        # it is third-party
                        third_party_content_length = third_party_content_length + current_length

    resObject["total-content-length"] = content_length
    resObject["third-party-content-length"] = third_party_content_length
    resObject["ad-content-length"] = advertisements_content_length

# Total Content-Lengths per Site
sites0 = []
sites1 = []
sites2 = []
sites3 = []
sites4 = []

cumulative_get_0_total_content_lengths = []
cumulative_get_1_total_content_lengths = []
cumulative_get_2_total_content_lengths = []
cumulative_get_3_total_content_lengths = []
cumulative_get_4_total_content_lengths = []

# Third-Party Content-Lengths per Site
cumulative_get_0_tp_content_lengths = []
cumulative_get_1_tp_content_lengths = []
cumulative_get_2_tp_content_lengths = []
cumulative_get_3_tp_content_lengths = []
cumulative_get_4_tp_content_lengths = []

# Third-Party Percentage per Site
cumulative_get_0_tp_percentage = []
cumulative_get_1_tp_percentage = []
cumulative_get_2_tp_percentage = []
cumulative_get_3_tp_percentage = []
cumulative_get_4_tp_percentage = []

# Advertisements Content-Lengths per Site
cumulative_get_0_ad_content_lengths = []
cumulative_get_1_ad_content_lengths = []
cumulative_get_2_ad_content_lengths = []
cumulative_get_3_ad_content_lengths = []
cumulative_get_4_ad_content_lengths = []

# Advertisements Percentage per Site
cumulative_get_0_ad_percentage = []
cumulative_get_1_ad_percentage = []
cumulative_get_2_ad_percentage = []
cumulative_get_3_ad_percentage = []
cumulative_get_4_ad_percentage = []

cumulative_get_0_ads = []
cumulative_get_1_ads = []
cumulative_get_2_ads = []
cumulative_get_3_ads = []
cumulative_get_4_ads = []

# mean advertisement percentage of all sites
total_get_0_mean_ad_percentage = 0
total_get_0_successes = 0
total_get_1_mean_ad_percentage = 0
total_get_1_successes = 0
total_get_2_mean_ad_percentage = 0
total_get_2_successes = 0
total_get_3_mean_ad_percentage = 0
total_get_3_successes = 0
total_get_4_mean_ad_percentage = 0
total_get_4_successes = 0

i = 0
for resObject in result:
    if resObject['index'] == 0:
        # ONLY USE DATA IF LANDING PAGE WAS SUCCESSFUL
        if resObject['success'] is True:
            cumulative_get_0_total_content_lengths.append(resObject['total-content-length'])
            cumulative_get_1_total_content_lengths.append(resObject['total-content-length'])
            cumulative_get_2_total_content_lengths.append(resObject['total-content-length'])
            cumulative_get_3_total_content_lengths.append(resObject['total-content-length'])
            cumulative_get_4_total_content_lengths.append(resObject['total-content-length'])

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

            total_get_0_mean_ad_percentage += getPercentage(cumulative_get_0_ad_content_lengths[i], cumulative_get_0_total_content_lengths[i])
            total_get_0_successes += 1

            sites0.append(resObject['visited_site'])
            cumulative_get_0_tp_percentage.append(getPercentage(cumulative_get_0_tp_content_lengths[i], cumulative_get_0_total_content_lengths[i]))
            cumulative_get_0_ad_percentage.append(getPercentage(cumulative_get_0_ad_content_lengths[i], cumulative_get_0_total_content_lengths[i]))
            cumulative_get_0_ads.append(cumulative_get_4_ad_content_lengths[i])
        else:
            cumulative_get_0_total_content_lengths.append(np.nan)
            cumulative_get_1_total_content_lengths.append(np.nan)
            cumulative_get_2_total_content_lengths.append(np.nan)
            cumulative_get_3_total_content_lengths.append(np.nan)
            cumulative_get_4_total_content_lengths.append(np.nan)

            cumulative_get_0_tp_content_lengths.append(np.nan)
            cumulative_get_1_tp_content_lengths.append(np.nan)
            cumulative_get_2_tp_content_lengths.append(np.nan)
            cumulative_get_3_tp_content_lengths.append(np.nan)
            cumulative_get_4_tp_content_lengths.append(np.nan)

            cumulative_get_0_ad_content_lengths.append(np.nan)
            cumulative_get_1_ad_content_lengths.append(np.nan)
            cumulative_get_2_ad_content_lengths.append(np.nan)
            cumulative_get_3_ad_content_lengths.append(np.nan)
            cumulative_get_4_ad_content_lengths.append(np.nan)
    elif resObject['index'] == 1:
        if resObject['success'] is True:
            cumulative_get_1_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_2_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_3_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']

            cumulative_get_1_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_2_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_3_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']

            cumulative_get_1_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_2_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_3_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_4_ad_content_lengths[i] += resObject['ad-content-length']

            if not np.isnan(getPercentage(cumulative_get_1_ad_content_lengths[i], cumulative_get_1_total_content_lengths[i])):
                total_get_1_mean_ad_percentage += getPercentage(cumulative_get_1_ad_content_lengths[i], cumulative_get_1_total_content_lengths[i])
                total_get_1_successes += 1

                sites1.append(resObject['visited_site'])
                cumulative_get_1_tp_percentage.append(getPercentage(cumulative_get_1_tp_content_lengths[i], cumulative_get_1_total_content_lengths[i]))
                cumulative_get_1_ad_percentage.append(getPercentage(cumulative_get_1_ad_content_lengths[i], cumulative_get_1_total_content_lengths[i]))
                cumulative_get_1_ads.append(cumulative_get_1_ad_content_lengths[i])
    elif resObject['index'] == 2:
        if resObject['success'] is True:
            cumulative_get_2_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_3_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']

            cumulative_get_2_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_3_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']

            cumulative_get_2_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_3_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_4_ad_content_lengths[i] += resObject['ad-content-length']

            if not np.isnan(getPercentage(cumulative_get_2_ad_content_lengths[i], cumulative_get_2_total_content_lengths[i])):
                total_get_2_mean_ad_percentage += getPercentage(cumulative_get_2_ad_content_lengths[i], cumulative_get_2_total_content_lengths[i])
                total_get_2_successes += 1

                sites2.append(resObject['visited_site'])
                cumulative_get_2_tp_percentage.append(getPercentage(cumulative_get_2_tp_content_lengths[i], cumulative_get_2_total_content_lengths[i]))
                cumulative_get_2_ad_percentage.append(getPercentage(cumulative_get_2_ad_content_lengths[i], cumulative_get_2_total_content_lengths[i]))
                cumulative_get_2_ads.append(cumulative_get_2_ad_content_lengths[i])
    elif resObject['index'] == 3:
        if resObject['success'] is True:
            cumulative_get_3_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']

            cumulative_get_3_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']

            cumulative_get_3_ad_content_lengths[i] += resObject['ad-content-length']
            cumulative_get_4_ad_content_lengths[i] += resObject['ad-content-length']

            if not np.isnan(getPercentage(cumulative_get_3_ad_content_lengths[i], cumulative_get_3_total_content_lengths[i])):
                total_get_3_mean_ad_percentage += getPercentage(cumulative_get_3_ad_content_lengths[i], cumulative_get_3_total_content_lengths[i])
                total_get_3_successes += 1

                sites3.append(resObject['visited_site'])
                cumulative_get_3_tp_percentage.append(getPercentage(cumulative_get_3_tp_content_lengths[i], cumulative_get_3_total_content_lengths[i]))
                cumulative_get_3_ad_percentage.append(getPercentage(cumulative_get_3_ad_content_lengths[i], cumulative_get_3_total_content_lengths[i]))
                cumulative_get_3_ads.append(cumulative_get_3_ad_content_lengths[i])
    elif resObject['index'] == 4:
        if resObject['success'] is True:
            cumulative_get_4_total_content_lengths[i] += resObject['total-content-length']
            cumulative_get_4_tp_content_lengths[i] += resObject['third-party-content-length']
            cumulative_get_4_ad_content_lengths[i] += resObject['ad-content-length']

            if not np.isnan(getPercentage(cumulative_get_4_ad_content_lengths[i], cumulative_get_4_total_content_lengths[i])):
                total_get_4_mean_ad_percentage += getPercentage(cumulative_get_4_ad_content_lengths[i], cumulative_get_4_total_content_lengths[i])
                total_get_4_successes += 1

                sites4.append(resObject['visited_site'])
                cumulative_get_4_tp_percentage.append(getPercentage(cumulative_get_4_tp_content_lengths[i], cumulative_get_4_total_content_lengths[i]))
                cumulative_get_4_ad_percentage.append(getPercentage(cumulative_get_4_ad_content_lengths[i], cumulative_get_4_total_content_lengths[i]))
                cumulative_get_4_ads.append(cumulative_get_4_ad_content_lengths[i])
        i += 1

#######################################################
# CREATE PANDAS RESULT
#######################################################


df0 = pd.DataFrame({'Site':list(sites0), 'Third-Party-Percentage':list(cumulative_get_0_tp_percentage), 'Ads-Percentage':list(cumulative_get_0_ad_percentage), 'Ads':list(cumulative_get_0_ads)})
res0 = float(total_get_0_mean_ad_percentage)/float(total_get_0_successes), '%'
print "res0:", res0, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_0_ad_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "0 less than 10:", less_than_10
print "0 exactly 0:", exactly_0
print "0 length: ", len(cumulative_get_0_ad_percentage)

df1 = pd.DataFrame({'Site':list(sites1), 'Third-Party-Percentage':list(cumulative_get_1_tp_percentage), 'Ads-Percentage':list(cumulative_get_1_ad_percentage)})
res1 = float(total_get_1_mean_ad_percentage)/float(total_get_1_successes), '%'
print "res1:", res1, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_1_ad_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "1 less than 10:", less_than_10
print "1 exactly 0:", exactly_0
print "1 length: ", len(cumulative_get_1_ad_percentage)

df2 = pd.DataFrame({'Site':list(sites2), 'Third-Party-Percentage':list(cumulative_get_2_tp_percentage), 'Ads-Percentage':list(cumulative_get_2_ad_percentage)})
res2 = float(total_get_2_mean_ad_percentage)/float(total_get_2_successes), '%'
print "res2:", res2, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_2_ad_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "2 less than 10:", less_than_10
print "2 exactly 0:", exactly_0
print "2 length: ", len(cumulative_get_2_ad_percentage)

df3 = pd.DataFrame({'Site':list(sites3), 'Third-Party-Percentage':list(cumulative_get_3_tp_percentage), 'Ads-Percentage':list(cumulative_get_3_ad_percentage)})
res3 = float(total_get_3_mean_ad_percentage)/float(total_get_3_successes), '%'
print "res3:", res3, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_3_ad_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "3 less than 10:", less_than_10
print "3 exactly 0:", exactly_0
print "3 length: ", len(cumulative_get_3_ad_percentage)

df4 = pd.DataFrame({'Site':list(sites4), 'Third-Party-Percentage':list(cumulative_get_4_tp_percentage), 'Ads-Percentage':list(cumulative_get_4_ad_percentage), 'Ads':list(cumulative_get_4_ads)})
res4 = float(total_get_4_mean_ad_percentage)/float(total_get_4_successes)
print "res4:", res4, '%'
less_than_10 = 0
exactly_0 = 0
for u in cumulative_get_4_ad_percentage:
    if u < 10:
        less_than_10 += 1
    if u == 0:
        exactly_0 += 1
print "4 less than 10:", less_than_10
print "4 exactly 0:", exactly_0
print "4 length: ", len(cumulative_get_4_ad_percentage)

df0P = df0.sort_values(by=['Ads-Percentage'], ascending=False)
df0P.to_csv('tables/cumulated_top_sites_0_P1.csv', sep='\t', encoding='utf-8', index=False)
df0T = df0.sort_values(by=['Ads'], ascending=False)
df0T.to_csv('tables/cumulated_top_sites_0_T1.csv', sep='\t', encoding='utf-8', index=False)

# df1P = df1.sort_values(by=['Ads-Percentage'], ascending=False)
# df1P.to_csv('tables/cumulated_top_sites_1_P.csv', sep='\t', encoding='utf-8', index=False)
# df1T = df1.sort_values(by=['Ads'], ascending=False)
# df1T.to_csv('tables/cumulated_top_sites_1_T.csv', sep='\t', encoding='utf-8', index=False)

# df2P = df2.sort_values(by=['Ads-Percentage'], ascending=False)
# df2P.to_csv('tables/cumulated_top_sites_2_P.csv', sep='\t', encoding='utf-8', index=False)
# df2T = df2.sort_values(by=['Ads'], ascending=False)
# df2T.to_csv('tables/cumulated_top_sites_2_T.csv', sep='\t', encoding='utf-8', index=False)

# df3P = df3.sort_values(by=['Ads-Percentage'], ascending=False)
# df3P.to_csv('tables/cumulated_top_sites_3_P.csv', sep='\t', encoding='utf-8', index=False)
# df3T = df3.sort_values(by=['Ads'], ascending=False)
# df3T.to_csv('tables/cumulated_top_sites_3_T.csv', sep='\t', encoding='utf-8', index=False)

df4P = df4.sort_values(by=['Ads-Percentage'], ascending=False)
df4P.to_csv('tables/cumulated_top_sites_4_P4.csv', sep='\t', encoding='utf-8', index=False)
df4T = df4.sort_values(by=['Ads'], ascending=False)
df4T.to_csv('tables/cumulated_top_sites_4_T4.csv', sep='\t', encoding='utf-8', index=False)

# TEST SHOW DISTRIBUTION CURVE
df0 = df0.sort_values(by=['Ads-Percentage'], ascending=False)

# Create Figure and Axes instances
fig,ax = plt.subplots()

# Make your plot, set your axes labels
ax.plot(df0['Site'],df0['Ads-Percentage'],'k')
ax.set_ylabel('% of Advertisements Traffic')
ax.set_xlabel('Sites')

# Turn off tick labels
# ax.set_yticklabels([])
ax.set_xticklabels([])

# plt.plot(df0['Site'], df0['Ads-Percentage'], color="black")
# plt.xlabel("Sites")
# plt.ylabel("% of Advertisements Traffic")
# plt.tick_params(axis='x', which='both', labelbottom=False)
plt.grid()

plt.savefig('figures/cumulated0_1.png', bbox_inches='tight')



