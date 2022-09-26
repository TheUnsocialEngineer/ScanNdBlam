from mcstatus import JavaServer
import os
import math
import threading
import time
import asyncio
import pymongo
import ctypes
libgcc_s = ctypes.CDLL('libgcc_s.so.1')

masscan = []
inputfile = "ips.txt"
searchterm=""
publicserverlist="public.txt"

myclient = pymongo.MongoClient("mongodb://PoopenheimerAdministativeUserAccount:PoopenheimerSuperSecureAdminPasswordlol%3A)@45.79.194.63:27017/?authMechanism=DEFAULT&authSource=admin")
mydb = myclient["Poopenheimer"]
mycol = mydb["Servers"]


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
            if mycol.count_documents({"IP":ip})!=0:
                pass
            else:
                server = JavaServer(ip,25565)
                query = server.query()
                status=server.status()
                if query.software.version==version:
                    print("[QUERY} Found server: " + ip + " " + query.software.version + " " + str(query.players.online))
                    post = {"IP": ip,"MOTD":query.motd,"Version": query.software.version, "Players": str(query.players.online)+"/"+str(query.players.max), "Latency": status.latency,"playerlist":query.players.names,"Found_with":"QUERY","plugin_list":query.software.plugins,"P2W":"False"}
                    mycol.insert_one(post)
        except Exception as e:
            pass

for x in range(threads):
    thread = myThread(x, str(x)).start()