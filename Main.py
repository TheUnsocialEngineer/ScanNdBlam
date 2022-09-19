from mcstatus import JavaServer
import os
import math
import threading
import time
import asyncio
import pymongo


masscan = []
inputfile = "ips.txt"
outputfile = "servers.txt"
searchterm=""
publicserverlist="public.txt"
outfile = open(outputfile, 'a+')
outfile.close

fileHandler = open (inputfile, "r")
listOfLines = fileHandler.readlines()
fileHandler.close()

for line in listOfLines:
    if line.strip()[0] != "#":
        masscan.append(line.strip().split(' ',4)[3])



def split_array(L,n):
    return [L[i::n] for i in range(n)]

threads = int(input('How many threads so you want to use? (Recommended 20): '))

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
        asyncio.run(print_time(self.name))
        print ("Exiting Thread " + self.name)

async def print_time(threadName):
    for z in split[int(threadName)]:
        if exitFlag:
            threadName.exit()
        ip=z
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["Poopenheimer"]
        mycol = mydb["Servers"]
        try:
            server = JavaServer(ip,25565)
            query = server.query()
            print("[QUERY} Found server: " + ip + " " + query.software.version + " " + str(query.players.online))
            status=server.status()
            post = {"IP": ip,"MOTD":query.motd,"Version": query.software.version, "Players": str(query.players.online)+"/"+str(query.players.max), "Latency": status.latency,"playerlist":query.players.names,"Found_with":"QUERY","plugin_list":query.software.plugins,"P2W":"False"}
            mycol.insert_one(post)
        except Exception as e:
            try:
                ip=z
                server = JavaServer(ip,25565)
                status = server.status()
                print("[STATUS] Found server: " + ip + " " + status.version.name + " " + str(status.players.online))
                post = {"IP": ip, "Version": status.version.name, "Players": str(status.players.online)+"/"+str(status.players.max), "Latency": status.latency,"Found_with":"STATUS","P2W":"False"}
                mycol.insert_one(post)
            except Exception as e:
                #print(f"[Status FAILED] errord={e} moving on")
                pass

for x in range(threads):
    thread = myThread(x, str(x)).start()