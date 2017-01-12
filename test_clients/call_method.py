import time

from MeteorClient import MeteorClient


client = MeteorClient('ws://127.0.0.1:3000', debug=True)
client.connect()

client.call("test", [2,])
time.sleep(1)
