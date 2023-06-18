import asyncio
import concurrent.futures
import itertools
from datetime import datetime

from mcstatus import JavaServer
import pymongo
import ipinfo


# MongoDB config
myclient = pymongo.MongoClient("mongodb+srv://GarryNewburg:glitchpasswordforauth@cluster0.cibsmxb.mongodb.net/test")
mydb = myclient["Eoka"]
mycol = mydb["Servers 3"]


def is_private_ip(ip):
    # Check if IP address falls into private IP ranges
    ip_parts = ip.split('.')
    if (
        ip_parts[0] == '127'
        or (ip_parts[0] == '10' and ip_parts[1] == '10')
        or (ip_parts[0] == '192' and ip_parts[1] == '168')
        or (ip_parts[0] == '169' and ip_parts[1] == '254')
        or (ip_parts[0] == '172' and 16 <= int(ip_parts[1]) <= 31)
        or (ip_parts[0] == '192' and ip_parts[1] == '0' and ip_parts[2] == '2')
    ):
        return True
    return False


async def check_minecraft_servers(start_ip, end_ip, ports):
    start = list(map(int, start_ip.split('.')))
    end = list(map(int, end_ip.split('.')))

    # Calculate the number of IP addresses in the range
    num_ips = sum((end[i] - start[i] + 1) * (256 ** (3 - i)) for i in range(4))

    start_time = datetime.now()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = []

        for ip_parts in itertools.product(*(range(start[i], end[i] + 1) for i in range(4))):
            ip_address = '.'.join(map(str, ip_parts))
            if not is_private_ip(ip_address):
                for port in ports:
                    tasks.append(loop.run_in_executor(executor, process_ip, ip_address, port))

        await asyncio.gather(*tasks)

    end_time = datetime.now()
    processing_time = end_time - start_time

    print(f"Generated {num_ips} IP addresses.")
    print(f"Processed in {processing_time}.")


def process_ip(ip_address, port):
        print(F"{ip_address}:{port}")
        exists = mycol.find_one({"IP": ip_address})
        if exists:
            server = JavaServer(ip_address, port, timeout=1)
            status = server.status()
            motd = status.description
            favicon = status.favicon
            version = status.version.name
            protocol = status.version.protocol
            online = status.players.online
            max_players = status.players.max
            last_update = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            update_fields = {
                "MOTD": motd,
                "Favicon": favicon,
                "Version": version,
                "Protocol": protocol,
                "Online": online,
                "Maximum": max_players,
                "Last_updated": last_update
            }

            mycol.update_one({"IP": ip_address}, {"$set": update_fields})
            print(f"IP: {ip_address} - Updated: Server Is Up To Date!")
        else:
            try:
                server = JavaServer(ip_address, port, timeout=5)
                query = server.query()
                status = server.status()
                token = "51030d1b61679e"
                handler = ipinfo.getHandler(token)
                details = handler.getDetails(ip_address)

                motd = status.description
                favicon = status.favicon if status.favicon is not None else False
                version = status.version.name
                protocol = status.version.protocol
                brand = query.software.brand
                online = status.players.online
                max_players = status.players.max
                playerlist = []
                pluginlist = []
                seed = ""
                cracked = False
                p2w = False
                country = details.country
                region = details.region
                last_update = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                data = {
                    "IP": ip_address,
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
                    "P2W": p2w,
                    "Country": country,
                    "Region": region,
                    "Last_updated": last_update
                }
                mycol.insert_one(data)

                print(f"IP: {ip_address} - Query: Server is online! Players: {status.players.online}/{status.players.max}")

            except Exception as query_error:
                try:
                    server = JavaServer(ip_address, port, timeout=1)
                    status = server.status()
                    token = "51030d1b61679e"
                    handler = ipinfo.getHandler(token)
                    details = handler.getDetails(ip_address)

                    motd = status.description
                    favicon = status.favicon if status.favicon is not None else False
                    version = status.version.name
                    brand = ""
                    protocol = status.version.protocol
                    online = status.players.online
                    max_players = status.players.max
                    playerlist = status.players.sample if status.players.sample is not None else []
                    pluginlist = []
                    seed = ""
                    cracked = False
                    p2w = False
                    country = details.country
                    region = details.region
                    last_update = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                    data = {
                        "IP": ip_address,
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
                        "P2W": p2w,
                        "Country": country,
                        "Region": region,
                        "Last_updated": last_update
                    }

                    mycol.insert_one(data)

                    print(f"IP: {ip_address} - Status: Server is online! Players: {status.players.online}/{status.players.max}")

                except Exception as status_error:
                    #print(status_error)
                    pass


async def main():
    start_ip = input("Enter the starting IP address (default: 0.0.0.0): ")
    if not start_ip:
        start_ip="0.0.0.0"
    end_ip = input("Enter the ending IP address (default: 255.255.255.255): ")
    if not end_ip:
        end_ip="255.255.255.255"

    port_range = input("Enter the port or range of ports to scan (default: 25565): ")
    if not port_range:
        port_range = "25565"

    ports = parse_port_range(port_range)

    await check_minecraft_servers(start_ip, end_ip, ports)


def parse_port_range(port_range):
    if '-' in port_range:
        start_port, end_port = port_range.split('-')
        return range(int(start_port), int(end_port) + 1)
    else:
        return [int(port_range)]


asyncio.run(main())
