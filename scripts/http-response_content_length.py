import sqlite3 as lite
from tld import get_tld

# connect to the output database
wpm_db = '/home/tobi/Schreibtisch/Tests/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

# MAIN CONFIG
selected_crawl = 35
show_index = 0 # 0 means landing page, 4 browsing 4 subpages
result = []

# get index and success from CrawlHistory, create result array
visited_crawl_sites = []
for crawl_id, cmd, visited_site, success, dtg in cur.execute("SELECT DISTINCT crawl_id, command, arguments, bool_success, dtg"
                                " FROM CrawlHistory"
								" WHERE crawl_id = ?"
                                " ORDER BY dtg;", (selected_crawl,)):
	if not visited_site in visited_crawl_sites:
		index = 0
		visited_crawl_sites.append(visited_site)
	else:
		count = visited_crawl_sites.count(visited_site)
		index = count
		visited_crawl_sites.append(visited_site)

	success_res = success
	if success == -1 or success == 0:
		success_res = False
	elif success == 1:
		success_res = True
	else :
		success_res = success
	
	if "GET" in cmd or "BROWSE" in cmd:
		obj = {}
		obj["crawl_id"] = crawl_id
		obj["cmd"] = str(cmd)
		obj["visited_site"] = str(visited_site)
		obj["success"] = success_res
		obj["index"] = index
		result.append(obj)

# add visit_id from site_visits
visited_sites = []
for visit_id, url in cur.execute("SELECT visit_id, site_url"
                            " FROM site_visits"
                            " WHERE crawl_id = ?", (selected_crawl,)):
	if url in visited_sites:
		count = visited_sites.count(url)
	else:
		count = 0
	for res in result:
		if res["visited_site"] == str(url) and res["index"] == count:
			res.update({"visit_id": visit_id})
	visited_sites.append(url)

# add Content-Length
for res in result:
	content_length = 0
	for header in cur.execute("SELECT headers"
									" FROM http_responses"
									" WHERE visit_id = ?"
									" AND crawl_id = ?", [res["visit_id"], res["crawl_id"]]):
			for http_header in header:
				if "Content-Length" in http_header:
					current_length = http_header.index("Content-Length")
					content_length = content_length + current_length
	res["content-length"] = content_length

# print result
for res in result:
	if res["success"] == True:
		if show_index is not None:
			if show_index == res["index"]:
				print res["visited_site"], res["content-length"], res["success"]
		else:
			print res["visited_site"], res["content-length"], res["success"]



