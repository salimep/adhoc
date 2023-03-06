#!/usr/bin/python3
# Auther: Salim
# Syntax : ./vmware.py 0 APP_STORE_1 ( script name, number of datacenter ( for 2 DC - 0,1), datastore name
# Threshold , for now hardcoded , you can change it to arguments if  you wants to
from pyVim.connect import SmartConnect,Disconnect
import ssl
import sys
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.verify_mode = ssl.CERT_NONE

def vcenter_conn (IP,user,password):

    try:
        si= SmartConnect(host=IP,user=user,pwd=password,sslContext=context)
        return si
    except IOError as e:
        return 'I/O error({0}): {1}'.format(e.errno,e.strerror)



con=vcenter_conn('XXXXXXX','XXXX','XXX')

location_id= int(sys.argv[1])
root_folder = con.RetrieveContent()
datacenter_1 = root_folder.rootFolder.childEntity[location_id]

def extract_datastore_info(datacenter_name):

    datastore_folder = datacenter_name.datastoreFolder
    datastores = datastore_folder.childEntity

    my_dict={}

    for a in datastores:
        summary=a.summary
       # print (summary)
        if summary.uncommitted:
            my_dict[summary.name] = {'capacity' : (summary.capacity/1024/1024/1024),'freespace':(summary.freeSpace/1024/1024/1024),'ussage':round(((summary.capacity-summary.freeSpace)/1024/1024/1024)/(summary.capacity/1024/1024/1024)*100) }

    return my_dict



result=extract_datastore_info(datacenter_1)

Disconnect(con)

store_name= sys.argv[2]

graph='usage_GB={},total_GB={};0;0;0;0'.format(round((result[store_name]['capacity']-result[store_name]['freespace'])),round(result[store_name]['capacity']))
if store_name in result:
    if result[store_name]['ussage'] > 95:
        print ('CRITICAL - {} Gb left in {} datastore | {}'.format(round(result[store_name]['freespace']),store_name,graph))
        sys.exit(2)
    elif  result[store_name]['ussage'] <  95 and result[store_name]['ussage'] > 80:
        print('WARNING - {} Gb left in {} datastore | {}'.format(round(result[store_name]['freespace']), store_name,graph))
        sys.exit(1)
    else:
        print('OK - {} Gb left in {} datastore | {}'.format(round(result[store_name]['freespace']), store_name,graph))
        sys.exit(0)
else:
   print (store_name +'doesnt exist in datastore')
   sys.exit(2)
#print (result['WSUS'])


