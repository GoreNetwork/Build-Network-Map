import sqlite3
from pprint import pprint
from common_functions import *
from cdp_work import *
from yed_work import *
import random
from swap_wcm_snm_cider import *

def pull_subnet_data(db_name):
    tmp_conn = sqlite3.connect(db_name)
    tmp_cur = tmp_conn.cursor()
    command =""" select site_name,IP,SNM  from devices;"""
    output = tmp_cur.execute(command)
    return output

subnet_database = "subnet_DB.db"
subnets_data = pull_subnet_data(subnet_database)

all_data = []

for subnet in subnets_data:
   # print (subnet)
    tmp_data = {}
    tmp_data['site_name'] = subnet[0]
    tmp_data['ip'] = ipaddress.ip_address(subnet[1])
    tmp_data['snm'] = subnet[2]
    tmp_data['cider'] = snm_to_cider(tmp_data['snm'])
    #print (tmp_data['ip'])
    #print (tmp_data['cider'])
    network = subnet[1]+tmp_data['cider']
    tmp_data['subnet'] = ipaddress.ip_network(network, strict = False)
    all_data.append(tmp_data)

while 1==1:
    tmp_address = input("IP address: ")
    for each_subnet in all_data:
        if ipaddress.ip_address(tmp_address) in each_subnet['subnet']:
            print (each_subnet)




