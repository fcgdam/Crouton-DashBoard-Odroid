import paho.mqtt.client as mqtt
import time
import json
import random
import os
import psutil
import datetime

clientName = "Odroid" 
MQTTBroker = "192.168.1.17"
MQTTPort   = 1883

#device setup
j = """
{
    "deviceInfo": {
        "status": "good",
        "color": "#FD90FE",
        "endPoints": {
            "RootDisk": {
                "values": {
                    "labels": [],
                    "series": [0]
                },
                "total": 100,
                "centerSum": true,
                "units": "%",
                "card-type": "crouton-chart-donut",
                "title": "Root Disk"
            },
            "PrimBackup": {
                "values": {
                    "labels": [],
                    "series": [0]
                },
                "total": 100,
                "centerSum": true,
                "units": "%",
                "card-type": "crouton-chart-donut",
                "title": " Prim Bck Disk"
            },
            "SecBackup": {
                "values": {
                    "labels": [],
                    "series": [0]
                },
                "total": 100,
                "centerSum": true,
                "units": "%",
                "card-type": "crouton-chart-donut",
                "title": " Sec Bck Disk"
            },
            "CpuLoad": {
                "values": {
                    "labels": [1],
                    "series": [[60]],
                    "update": ""
                },
                "max": 10,
                "low": 0,
                "high": 100,
                "card-type": "crouton-chart-line",
                "title": "CPU Load %"
            }
        },
        "description": "Odroid Server"
    }
}

"""

device = json.loads(j)
device["deviceInfo"]["name"] = clientName
deviceJson = json.dumps(device)

print "Client Name is: " + clientName

#callback when we recieve a connack
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

#callback when we receive a published message from the server
def on_message(client, userdata, msg):
    print(msg.topic + ": " + str(msg.payload))
    box = msg.topic.split("/")[1]
    name = msg.topic.split("/")[2]
    address = msg.topic.split("/")[3]

    if box == "inbox" and str(msg.payload) == "get" and address == "deviceInfo":
        client.publish("/outbox/"+clientName+"/deviceInfo", deviceJson)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Broker disconnection")
    time.sleep(10)
    client.connect(MQTTBroker, MQTTPort, 60)

def disk_usage(path):
    """Return disk usage associated with path."""
    st    = os.statvfs(path)
    free  = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used  = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    # NB: the percentage is -5% than what shown by df due to
    # reserved blocks that we are currently not considering:
    # http://goo.gl/sWGbH
    #return usage_ntuple(total, used, free, round(percent, 1))
    return round(percent,1)


client = mqtt.Client(clientName)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.username_pw_set("","")
client.will_set('/outbox/'+clientName+'/lwt', 'anythinghere', 0, False)


client.connect(MQTTBroker, MQTTPort, 60)

client.subscribe("/inbox/"+clientName+"/deviceInfo")
client.publish("/outbox/"+clientName+"/deviceInfo", deviceJson) #for autoreconnect

for key in device["deviceInfo"]["endPoints"]:
    #print key
    client.subscribe("/inbox/"+clientName+"/"+str(key))



client.loop_start()
while True:
    time.sleep(30)	# Change here the interval to send info to the dashboard.
    rootPath = '/'
    client.publish("/outbox/"+clientName+"/RootDisk"  , '{"series":['+str(disk_usage(rootPath))+']}')
    client.publish("/outbox/"+clientName+"/PrimBackup", '{"series":['+str(disk_usage("/media/PrimBackup"))+']}')
    client.publish("/outbox/"+clientName+"/SecBackup" , '{"series":['+str(disk_usage("/media/SecBackup"))+']}')
    client.publish("/outbox/"+clientName+"/CpuLoad"   , '{"update":{"labels":["'+str(datetime.datetime.now().strftime('%H:%M:%S'))+'"],"series":[['+str(psutil.cpu_percent())+']]}}')
