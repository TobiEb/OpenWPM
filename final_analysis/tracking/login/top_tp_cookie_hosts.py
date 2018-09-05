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
wpm_db = '/media/tobi/Daten/Workspace/OpenWPM/Output/facebook.sqlite'
selected_crawl = 2
show_percentage = False # either show percentage, or show total amount of cookies
observing_domains = ['facebook']
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
all_crawled_sites = []
all_tp_cookie_hosts = []

for resObject in result:
    if resObject['index'] == 0 and resObject['success'] is True:
        cookie_hosts = []
        cookie_names = []
        cookie_values = []
        
        tp_cookie_hosts = []
        tp_cookie_names = []
        tp_cookie_values = []

        ext = tldextract.extract(resObject["visited_site"])
        visited_tld = ext.domain
        all_crawled_sites.append(visited_tld)

        for name, value, host, raw_host, is_session in cur.execute("SELECT name, value, host, raw_host, is_session"
                                        " FROM javascript_cookies"
                                        " WHERE visit_id = ?"
                                        " AND crawl_id = ?", [resObject["visit_id"], resObject["crawl_id"]]):

            if name is not None:
                # if not name in unique_cookie_names:
                cookie_hosts.append(str(raw_host))
                cookie_names.append(str(name))
                cookie_values.append(str(value))

                # xt = tldextract.extract(host)
                # third_party_tld = xt.domain
                if not visited_tld in raw_host:
                # check if third-party
                    tp_cookie_hosts.append(str(raw_host))
                    tp_cookie_names.append(str(name))
                    tp_cookie_values.append(str(value))

                    if not raw_host in all_tp_cookie_hosts:
                            all_tp_cookie_hosts.append(str(raw_host))

                # check if session cookie
                # if is_session == 1:
                #     sessionCookies = sessionCookies + 1

        # if 'dict' in resObject['visited_site'] and resObject['index'] == 0:
        resObject["tp_cookie_hosts"] = tp_cookie_hosts

# Amount of third-party cookies 
host_occurences_percentages_array = []
host_amount_array = []

for tp_cookie_host in all_tp_cookie_hosts:
    print_data = False
    for domain in observing_domains:
        if domain in tp_cookie_host:
            print_data = True
    host_occurences = 0
    host_amount = 0
    for resObject in result:
        if resObject['index'] == 0 and resObject['success'] is True:
            if tp_cookie_host in resObject['tp_cookie_hosts']:
                host_occurences += 1
            count = resObject['tp_cookie_hosts'].count(tp_cookie_host)
            host_amount += count
    if print_data is True:
        print getPercentage(host_occurences, len(all_crawled_sites)), "%"
        print host_amount
    host_occurences_percentages_array.append(getPercentage(host_occurences, len(all_crawled_sites)))
    host_amount_array.append(host_amount)

#######################################################
# CREATE PANDAS RESULT
#######################################################

if show_percentage is True:
    df = pd.DataFrame({'Cookie_Host':all_tp_cookie_hosts, 'Cookie_Percentage':host_occurences_percentages_array})
    df = df.sort_values(by=['Cookie_Percentage'], ascending=False)
    df = df.head(20)
    plt.bar(df['Cookie_Host'], df['Cookie_Percentage'], color="red")
    plt.title("Most prevalent Cookie Hosts")
    plt.xlabel("Cookie Host")
    plt.legend(['Percentage of First-Parties'])
    plt.ylabel("Percentage of presence on sites")
    plt.xticks(rotation=90)
    plt.grid()
    plt.savefig('figures/top_cookie_hosts_percentage_after_fb_login.png', bbox_inches='tight')
else:
    df = pd.DataFrame({'Cookie_Host':all_tp_cookie_hosts, 'Cookie_Amount':host_amount_array})
    df = df.sort_values(by=['Cookie_Amount'], ascending=False)
    df = df.head(20)
    plt.bar(df['Cookie_Host'], df['Cookie_Amount'], color="red")
    plt.title("Most prevalent Cookie Hosts")
    plt.xlabel("Cookie Host")
    plt.legend(['# of Cookies Set'])
    plt.ylabel("# of Cookies Set")
    plt.xticks(rotation=90)
    plt.grid()
    # plt.savefig('figures/top_cookie_hosts_amount.png', bbox_inches='tight')
