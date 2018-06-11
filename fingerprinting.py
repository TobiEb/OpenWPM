import sqlite3 as lite
from tld import get_tld
import ast

# connect to the output database
wpm_db = '/home/tobi/Schreibtisch/Tests/crawl-data.sqlite'
conn = lite.connect(wpm_db)
cur = conn.cursor()

visits = []

for visit_id in cur.execute("SELECT visit_id"
                                " FROM site_visits;"):
    # tuple is needed to add in sql query
    visits.append(visit_id)

i = 0
while(i < len(visits)):
    visited_tld = ""
    canvas_script_urls = []
    canvasAccess = 0
    canvas_font_script_urls = []
    canvasFontAccess = 0
    for script_url, value, args, symbol, visited_site in cur.execute("SELECT j.script_url, j.value, j.arguments, j.symbol, s.site_url"
                                " FROM javascript as j JOIN site_visits as s"
                                " WHERE j.visit_id = s.visit_id AND j.visit_id = ?", visits[i]):
        #print symbol
        visited_tld = get_tld(visited_site)
        if "CanvasRenderingContext2D" in symbol:
            if "fillRect" in symbol:
                # convert unicode to dict datatype to use keys
                d = ast.literal_eval(args)
                # width and height should be at least 16 px
                if d["2"] >= 16 and d["3"] >= 16:
                    canvasAccess = canvasAccess + 1
                    canvas_script_urls.append(str(script_url))
            elif "measureText" in symbol:
                canvasFontAccess = canvasFontAccess + 1
                canvas_font_script_urls.append(str(script_url))
        elif "Battery" in symbol:
            print symbol
    print "Visit:", visits[i][0], "auf", visited_tld,"\n", "Anzahl auf Canvas zugegriffen:", canvasAccess,"\n", canvas_script_urls, "\n", "Anzahl Canvas Font zugegriffen:", canvasFontAccess, "\n", canvas_font_script_urls
    i = i + 1