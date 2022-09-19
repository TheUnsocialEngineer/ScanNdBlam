from mcstatus import JavaServer
import os
import math
import threading
import time
import asyncio
import pymongo


masscan = []
inputfile = "ips.txt"
searchterm=""
publicserverlist="public.txt"


fileHandler = open (inputfile, "r")
listOfLines = fileHandler.readlines()
fileHandler.close()

for line in listOfLines:
    if line.strip()[0] != "#":
        masscan.append(line.strip().split(' ',4)[3])



def split_array(L,n):
    return [L[i::n] for i in range(n)]

version=input("version to search for: ")
threads = int(input('How many threads so you want to use? (Recommended 250): '))
time.sleep(2)

if len(masscan) < int(threads):
    threads = len(masscan)

split = list(split_array(masscan, threads))

exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print ("Starting Thread " + self.name)
        time.sleep(5)
        asyncio.run(print_time(self.name))
        print ("Exiting Thread " + self.name)

async def print_time(threadName):
    for z in split[int(threadName)]:
        if exitFlag:
            threadName.exit()
        try:
            ip = z
            server = JavaServer(ip,25565)
            query = server.query()
            with open(f"{version}.txt","a")as f:
                f.write(f"[QUERY] Found server: IP: {ip}, Version: {query.software.version}, Player Count: {query.players.online}/{query.players.max}, Player List: {query.players.names}, MOTD: {query.motd}\n")
        except Exception as e:
            pass

for x in range(threads):
    thread = myThread(x, str(x)).start()