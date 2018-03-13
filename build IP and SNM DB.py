import sqlite3
from pprint import pprint
from common_functions import *
from cdp_work import *
from yed_work import *
import random
from swap_wcm_snm_cider import *

def pull_running_confs(db_name):
    tmp_conn = sqlite3.connect(db_name)
    tmp_cur = tmp_conn.cursor()
    command =""" select site_name,show_run  from devices;"""
    output = tmp_cur.execute(command)
    return output

def enter_info_into_db(subnet,cur,conn):
	cur.execute("INSERT INTO devices (site_name,IP,SNM) VALUES(?,?,?)",
		(subnet['site_name'],
         subnet['IP'],
         subnet['SNM'],
		))


print (get_time())
print ("\n")

conn = sqlite3.connect('subnet_DB.db')
cur = conn.cursor()

cur.execute("""
			CREATE TABLE devices(
				site_name  TEXT,
				IP  TEXT,
				SNM  TEXT
				)""")
conn.commit()
cur.close
conn.close

data = []
running_confs = pull_running_confs('Network_info.db')

#lines_i_dont_want = [
#    "no",
#    'match',
#    'nms',
#    'negotiated',
#    "dhcp",
#    "trusted",
#    'list',
#    'peer',
#    'default'
#    'pool',
#    'peer',
#]

for running_conf in running_confs:
    name =  running_conf[0]
    sh_run = running_conf[1].split("\n")
    for line in sh_run:
        skip_this = False
        if "ip address" in line:
           # print (line)
            #for bad_line in lines_i_dont_want:
            #    if bad_line in line:
            #        skip_this = True
            #if skip_this == True:
            #    continue
            #print (line)
            tmp_ip_snm = get_ip (line)
            #print (tmp_ip_snm)
            if  len(tmp_ip_snm) == 0:
                continue
            if len(tmp_ip_snm) == 1:
               # print (line)
                line_search = re.search("/", line)
                if line_search == None:
                    continue
                cider = "/"+remove_start(line, "/")
                snm = cider_to_snm(cider)
                line = remove_end(line, "/")
                line = line + " " + snm
                tmp_ip_snm = get_ip(line)
               # print (line)


            tmp_data = {}
            tmp_data['IP'] = tmp_ip_snm[0]
            tmp_data['SNM'] = tmp_ip_snm[1]
            tmp_data['site_name'] =  name
            data.append(tmp_data)

#pprint (data)

print (get_time())
print ("\n")


for subnet in data:
    enter_info_into_db(subnet, cur, conn)
conn.commit()