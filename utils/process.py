from datetime import datetime
import pymongo

from mcstatus import JavaServer
import ipinfo
import asyncio
import json

import os
from dotenv import load_dotenv

load_dotenv()

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

ipinfo_token = config["ipinfo_token"]
database_name = config["database_name"]
collection_name = config["collection_name"]

#ipinfo config
token = "51030d1b61679e"
handler = ipinfo.getHandler(ipinfo_token)

myclient = pymongo.MongoClient(os.getenv("MONGODB_URI"))
mydb = myclient[database_name]
mycol = mydb[collection_name]


async def ping_server(ip: str,port) -> None:
    try:
        status = await (await JavaServer.async_lookup(ip,port)).async_status()
    except Exception as e:
        return

    print(f"{ip} - Latency: {status.latency}ms, Version: {status.version.name} Players: {status.players.online}")
    version=status.version.name
    motd =status.description.to_plain()
    favicon = status.favicon if status.favicon is not None else False
    protocol = status.version.protocol
    brand = ""
    software=""
    online = status.players.online
    max_players = status.players.max
    playerlist = status.players.sample if status.players.sample is not None else []
    pluginlist = []
    seed = ""
    cracked = False
    last_update = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    data = {
        "IP": ip,
        "Port": port,
        "MOTD": motd,
        "Favicon": favicon,
        "Version": version,
        "Brand": brand,
        "Protocol": protocol,
        "Online": online,
        "Maximum": max_players,
        "player_list": playerlist,
        "plugin_list": pluginlist,
        "Seed": seed,
        "Cracked": cracked,
        "Last_updated": last_update
    }
    mycol.insert_one(data)



async def ping_ips(ips: list[tuple], versions, batch_size) -> None:
    to_process: list[tuple] = []

    for ip, port in ips:  # Iterate through tuples (ip, port)
        print(ip, port)
        if len(to_process) < batch_size:  # Compare with batch_size
            to_process.append((ip, port))
        else:
            tasks = [asyncio.create_task(ping_server(ip_address, port)) for ip_address, port in to_process]
            await asyncio.wait(tasks)
            to_process = []

    if to_process:
        tasks = [asyncio.create_task(ping_server(ip_address, port)) for ip_address, port in to_process]
        await asyncio.wait(tasks)

