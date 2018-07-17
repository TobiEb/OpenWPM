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
show_in_percentage = True
show_in_total_amount = False
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
    tp_content_length = 0
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
                    tp_content_length = tp_content_length + current_length
                    # test
                    #if 'youtube' in resObject['visited_site'] and resObject['index'] == 0:
                    #    print third_party_tld

    resObject["total-content-length"] = content_length
    #print resObject['total-content-length']
    resObject["tp-content-length"] = tp_content_length

# Since GET subsites is cumulative, we have to add the sum of a next step to its value
# Total Content-Lengths per Site
sites = []
get_0_total_content_lengths = []
get_1_total_content_lengths = []
get_2_total_content_lengths = []
get_3_total_content_lengths = []
get_4_total_content_lengths = []
browse_total_content_lengths = []

# Third-Party Content-Lengths per Site
get_0_tp_content_lengths = []
get_1_tp_content_lengths = []
get_2_tp_content_lengths = []
get_3_tp_content_lengths = []
get_4_tp_content_lengths = []
browse_tp_content_lengths = []

# Third-Party Content Length Percentage of Total Content-Lengths per Site
cumulative_get_0_tp_percentage_lengths = []
cumulative_get_1_tp_percentage_lengths = []
cumulative_get_2_tp_percentage_lengths = []
cumulative_get_3_tp_percentage_lengths = []
cumulative_get_4_tp_percentage_lengths = []
non_cumulative_get_0_tp_percentage_lengths = []
non_cumulative_get_1_tp_percentage_lengths = []
non_cumulative_get_2_tp_percentage_lengths = []
non_cumulative_get_3_tp_percentage_lengths = []
non_cumulative_get_4_tp_percentage_lengths = []
browse_tp_percentage_lengths = []

i = 0
for resObject in result:
    if resObject['index'] == 0:
        sites.append(resObject['visited_site'])
        if resObject['success'] == True:
            # / 1000 to transform content length bytes to KB
            get_0_total_content_lengths.append((resObject['total-content-length'])/1000)
            get_1_total_content_lengths.append((resObject['total-content-length'])/1000)
            get_2_total_content_lengths.append((resObject['total-content-length'])/1000)
            get_3_total_content_lengths.append((resObject['total-content-length'])/1000)
            get_4_total_content_lengths.append((resObject['total-content-length'])/1000)

            get_0_tp_content_lengths.append((resObject['tp-content-length'])/1000)
            get_1_tp_content_lengths.append((resObject['tp-content-length'])/1000)
            get_2_tp_content_lengths.append((resObject['tp-content-length'])/1000)
            get_3_tp_content_lengths.append((resObject['tp-content-length'])/1000)
            get_4_tp_content_lengths.append((resObject['tp-content-length'])/1000)
        else:
            get_0_total_content_lengths.append(0)
            get_1_total_content_lengths.append(0)
            get_2_total_content_lengths.append(0)
            get_3_total_content_lengths.append(0)
            get_4_total_content_lengths.append(0)

            get_0_tp_content_lengths.append(0)
            get_1_tp_content_lengths.append(0)
            get_2_tp_content_lengths.append(0)
            get_3_tp_content_lengths.append(0)
            get_4_tp_content_lengths.append(0)

        #Percentage
        cumulative_get_0_tp_percentage_lengths.append(getPercentage(get_0_tp_content_lengths[i],get_0_total_content_lengths[i]))
        non_cumulative_get_0_tp_percentage_lengths.append(getPercentage(resObject['tp-content-length'],resObject['total-content-length']))
    elif resObject['index'] == 1:
        if resObject['success'] == True:
            get_1_total_content_lengths[i] += (resObject['total-content-length']/1000)
            get_2_total_content_lengths[i] += (resObject['total-content-length']/1000)
            get_3_total_content_lengths[i] += (resObject['total-content-length']/1000)
            get_4_total_content_lengths[i] += (resObject['total-content-length']/1000)

            get_1_tp_content_lengths[i] += (resObject['tp-content-length']/1000)
            get_2_tp_content_lengths[i] += (resObject['tp-content-length']/1000)
            get_3_tp_content_lengths[i] += (resObject['tp-content-length']/1000)
            get_4_tp_content_lengths[i] += (resObject['tp-content-length']/1000)

        #Percentage
        cumulative_get_1_tp_percentage_lengths.append(getPercentage(get_1_tp_content_lengths[i],get_1_total_content_lengths[i]))
        non_cumulative_get_1_tp_percentage_lengths.append(getPercentage(resObject['tp-content-length'],resObject['total-content-length']))
    elif resObject['index'] == 2:
        if resObject['success'] == True:
            get_2_total_content_lengths[i] += (resObject['total-content-length']/1000)
            get_3_total_content_lengths[i] += (resObject['total-content-length']/1000)
            get_4_total_content_lengths[i] += (resObject['total-content-length']/1000)

            get_2_tp_content_lengths[i] += (resObject['tp-content-length']/1000)
            get_3_tp_content_lengths[i] += (resObject['tp-content-length']/1000)
            get_4_tp_content_lengths[i] += (resObject['tp-content-length']/1000)

        #Percentage
        cumulative_get_2_tp_percentage_lengths.append(getPercentage(get_2_tp_content_lengths[i],get_2_total_content_lengths[i]))
        non_cumulative_get_2_tp_percentage_lengths.append(getPercentage(resObject['tp-content-length'],resObject['total-content-length']))
    elif resObject['index'] == 3:
        if resObject['success'] == True:
            get_3_total_content_lengths[i] += (resObject['total-content-length']/1000)
            get_4_total_content_lengths[i] += (resObject['total-content-length']/1000)

            get_3_tp_content_lengths[i] += (resObject['tp-content-length']/1000)
            get_4_tp_content_lengths[i] += (resObject['tp-content-length']/1000)

        #Percentage
        cumulative_get_3_tp_percentage_lengths.append(getPercentage(get_3_tp_content_lengths[i],get_3_total_content_lengths[i]))
        non_cumulative_get_3_tp_percentage_lengths.append(getPercentage(resObject['tp-content-length'],resObject['total-content-length']))
    elif resObject['index'] == 4:
        if resObject['success'] == True:
            get_4_total_content_lengths[i] += (resObject['total-content-length']/1000)

            get_4_tp_content_lengths[i] += (resObject['tp-content-length']/1000)

        #Percentage
        cumulative_get_4_tp_percentage_lengths.append(getPercentage(get_4_tp_content_lengths[i],get_4_total_content_lengths[i]))
        non_cumulative_get_4_tp_percentage_lengths.append(getPercentage(resObject['tp-content-length'],resObject['total-content-length']))
        i += 1
    elif resObject['index'] == 5:
        # index 5 is BROWSE command
        if resObject['success'] == True:
            browse_total_content_lengths.append((resObject['total-content-length'])/1000)

            browse_tp_content_lengths.append((resObject['tp-content-length'])/1000)
        else:
            browse_total_content_lengths.append(0)
            browse_tp_content_lengths.append(0)

        #Percentage
        browse_tp_percentage_lengths.append(getPercentage(resObject['tp-content-length'],resObject['total-content-length']))

# fix since last element in browse was not recorded
browse_total_content_lengths.append(0)
browse_tp_content_lengths.append(0)

#######################################################
# CREATE CONSOLE RESULT
#######################################################
amount_sites_with_increased_tp = 0
# check if increased or not
j = 0
for value in cumulative_get_0_tp_percentage_lengths:
    if value < cumulative_get_4_tp_percentage_lengths[j]:
        amount_sites_with_increased_tp += 1
    j += 1
print "Von GET 0 zu GET 4 steigt der Anteil der Third-Party Content-Lengths bei ",amount_sites_with_increased_tp, "von insgesamt", len(sites), " Seiten. Das sind", getPercentage(amount_sites_with_increased_tp,len(sites)), "%"

#######################################################
# CREATE PANDAS OBJECT
#######################################################

if show_in_percentage is True:
    #plt.bar(sites, browse_tp_percentage_lengths, color="yellow")
    plt.bar(sites, cumulative_get_0_tp_percentage_lengths, color="red")
    plt.plot(sites, cumulative_get_4_tp_percentage_lengths, color="blue")
    #plt.plot(sites, cumulative_get_1_tp_percentage_lengths, color="red")
    #plt.plot(sites, cumulative_get_2_tp_percentage_lengths, color="green")
    #plt.plot(sites, cumulative_get_3_tp_percentage_lengths, color="yellow")
    plt.title("HTTP Response Content-Length")
    plt.xlabel("Site")
    plt.ylabel("Content-Length of Third-Party Requests compared to Total Requests in %")
    plt.legend(['Third-Party Traffic Prozentsatz GET 4', 'Third-Party Traffic Prozentsatz GET 0'])
    plt.xticks(rotation=90)
    plt.show()
elif show_in_total_amount is True:
    #plt.bar(sites, browse_tp_percentage_lengths, color="yellow")
    plt.bar(sites, cumulative_get_0_tp_percentage_lengths, color="red")
    plt.plot(sites, cumulative_get_4_tp_percentage_lengths, color="blue")
    #plt.plot(sites, cumulative_get_1_tp_percentage_lengths, color="red")
    #plt.plot(sites, cumulative_get_2_tp_percentage_lengths, color="green")
    #plt.plot(sites, cumulative_get_3_tp_percentage_lengths, color="yellow")
    plt.title("HTTP Response Content-Length")
    plt.xlabel("Site")
    plt.ylabel("Content-Length of Third-Party Requests compared to Total Requests in %")
    plt.legend(['Third-Party Traffic Prozentsatz GET 0', 'Third-Party Traffic Prozentsatz GET 1'])
    plt.xticks(rotation=90)
    plt.show()



