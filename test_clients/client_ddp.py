import time

from MeteorClient import MeteorClient


client = MeteorClient('ws://127.0.0.1:9000')
client.connect()

client.subscribe('kittens')
client.subscribe('a')

while True:
    time.sleep(.5)
