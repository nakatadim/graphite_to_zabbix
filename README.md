Simple py script to get data from graphite and collect it in zabbix item
Example of command line check:
 check_graphite_data_artirix -u "http://graphite.artirix.com/render?target=apache.response.200&from=-12hours" -U nasko -P xxx
 Where:
-U - user for basic auth
-P - password for basic auth
Example of zabbix item:
1. Type of the item: External check
2. Key: check_graphite_data.py[-u,"http://graphite.artirix.com/render?target=api.search.GET.200.mean&from=-1min",-U,nasko,-P,xxx]
3. !!!Make sure the py script is in the directory configured in /etc/zabbix/zabbix-server.conf for "ExternalScripts" variable.
