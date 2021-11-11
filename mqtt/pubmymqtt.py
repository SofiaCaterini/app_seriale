import paho.mqtt.client as paho

broker = "localhost"
port = 1883
username = 'sofia'
password = 'mqtt'


def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")
    pass


client1 = paho.Client("control1")  # create client object
client1.username_pw_set(username, password)
client1.on_publish = on_publish  # assign function to callback
# client1.connect(broker, port)  # establish connection
try:
    client1.connect(broker, port)  # connect to broker
except:
    print("connection failed")
    exit(1)  # Should quit or raise flag to quit or retry
ret = client1.publish("house/bulb1", "on")  # publish
