import sqlite3
from pprint import pprint
from common_functions import *
from cdp_work import *
from yed_work import *
import random


map_name = "RH 6.graphml"

def do_i_want_this(host):
	i_want_these = [
	"peb_4506_06",
	]
	for i_want in i_want_these:
		if  i_want in host:
			return True
	return False


connected_hosts = []
def it_is_dupe(existing_conns, this_connectoin):
    if this_connection in existing_conns:
        return True
    swapped_direction  = {}
    swapped_direction["local_interface"]   =this_connectoin["remote_interface"]
    swapped_direction["remote_interface"]  =this_connectoin["local_interface"]
    swapped_direction["origin_host"]       =this_connectoin["other_host"]
    swapped_direction["other_host"]        =this_connectoin["origin_host"]
    if swapped_direction in existing_conns:
        return True
    else:
        return False


def sanatize_hostname(host):
	bad_charicters = ["&"]

	for bad_char in bad_charicters:
		if bad_char in host:
			print (host)
			host = host.replace(bad_char,"")
	return host


def pull_ips_from_running_config(running):
	running = running.split("\n")
	local_ips=[]
	ip_lines = find_child_text (running, "ip address")
	for ip_line in ip_lines:
		for each_line in ip_line:
			#print (each_line)
			try:
				local_ips.append(get_ip(each_line)[0])
			except:
				for ip in get_ip(each_line):
					local_ips.append(ip)
	return (local_ips)

def pull_count(db_name):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	command ="""select count(site_name)  from devices;
	"""
	output = cur.execute(command)
	return output


def pull_cdp_info(db_name):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	command =""" select site_name,CDP_nei  from devices;"""
	output = cur.execute(command)
	return output


def put_in_xml_start(map):
	map = map_start
	return map



#def dont_put_this_in_map(hostname):
#	bad_hostnames = ["SEP"]
#	for bad_host in bad_hostnames:
#		if bad_host in hostname:
#			return True
#	return False

def put_in_nodes(hosts,node ):
	map = ''
	for host in hosts:
		if is_it_a_phone(host) == True:
			continue


		host = sanatize_hostname(host)
		map = map +node.format(host, host, "rectangle")
	return map

def put_in_connections(map,connections_data,link):
	map = ""
	keys = []
	for connection in connections_data:
		# #ID,Source, Target, description, description
		if is_it_a_phone(connection['origin_host']) == True:
			continue
		if is_it_a_phone(connection['other_host']) == True:
			continue


		if connection['origin_host'] not in connected_hosts:
			connected_hosts.append(connection['origin_host'])
		if 	connection['other_host'] not in connected_hosts:
			connected_hosts.append(connection['other_host'])

		connection['origin_host'] = sanatize_hostname(connection['origin_host'])
		connection['other_host'] = sanatize_hostname(connection['other_host'])
		id = 10

		new_id_needed = True
		while new_id_needed == True:
			id = str(random.randint(1, 100000000))
			if id not in keys:
				keys.append(id)
				new_id_needed = False

		description = str(connection['local_interface'])+"  "+str(connection['remote_interface'])
		map = map+link.format(id,connection['origin_host'],connection['other_host'],description,description)
	return map




db_name = 'Network_info.db'

connections = []
pprint ("Pulling CDP data from database")
print (get_time())
print ("\n")
all_cpd_data = pull_cdp_info(db_name)
pprint ("Parsing CDP Data")
print (get_time())
print ("\n")
for tmp_site_cdp_data in all_cpd_data:
	hostname = tmp_site_cdp_data[0]
	site_cdp_data= tmp_site_cdp_data[1]
	cdp_neigh_data = cdpNeighbors(site_cdp_data)
	#print (hostname)
	#pprint(cdp_neigh_data)
	for each in cdp_neigh_data:
		#pprint (each)
		connections.append([hostname,each])
	#print ("\n\n\n\n\n\n\n")

print ("Building connection list")
print (get_time())
print ("\n")
connections_data = []
for each in connections:
	i_want = False
	this_connection = {}
	this_connection['origin_host'] = each[0]
	if do_i_want_this(this_connection['origin_host']) == True:
		i_want = True
	cdp_data = each[1]
	this_connection['other_host'] = cdp_data["deviceId"]
	if do_i_want_this(this_connection['other_host']) == True:
		i_want = True
	if i_want == False:
		continue
	this_connection['other_host'] = remove_end(this_connection['other_host'],"\.")
	this_connection['local_interface'] = cdp_data["localInterface"]
	this_connection['remote_interface'] = cdp_data["interface"]
	if len(connections_data) == 0:
		connections_data.append(this_connection)
	else:
		if it_is_dupe(connections_data, this_connection) == False:
			connections_data.append(this_connection)


hosts = []
print ("Building host list")
print (get_time())
print ("\n")
for this_connection in connections_data:
#	print (this_connection)
#	print (len(hosts))
	if this_connection['origin_host'] not in hosts:
		hosts.append(this_connection['origin_host'])
	if this_connection['other_host'] not in hosts:
		hosts.append(this_connection['other_host'])
		
#pprint (hosts)
#print (len(hosts))

pprint ("putting in connections")
print (get_time())
print ("\n")
connections = put_in_connections(map,connections_data,link)



print ("Making the map.")
print (get_time())
print ("\n")
map = ""

map = put_in_xml_start (map)
pprint ("putting in nodes")
print (get_time())
print ("\n")
nodes = put_in_nodes(connected_hosts,node )



map = put_in_xml_start (map)+nodes+connections+map_end


print ("Writting map to drive")
print (get_time())
print ("\n")
to_doc_w(map_name,map)
print ("Done")
print (get_time())
print ("\n")


pprint (connected_hosts)