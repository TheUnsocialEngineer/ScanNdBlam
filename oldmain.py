import asyncio
import concurrent.futures
import itertools
from datetime import datetime

from mcstatus import JavaServer
import pymongo
import ipinfo
import argparse
import ipaddress


# MongoDB config
myclient = pymongo.MongoClient("mongodb+srv://GarryNewburg:glitchpasswordforauth@cluster0.cibsmxb.mongodb.net/test")
mydb = myclient["Eoka"]
mycol = mydb["Servers bleeding"]

#ipinfo config
token = "51030d1b61679e"
handler = ipinfo.getHandler(token)

def is_ip_in_subnet(ip, subnet):
    try:
        ip_obj = ipaddress.ip_address(ip)
        subnet_obj = ipaddress.ip_network(subnet, strict=False)
        return ip_obj in subnet_obj
    except ValueError:
        return False


def is_private_ip(ip, exclusion_ranges):
    # Check if IP address falls into excluded IP ranges, including private IP ranges
    ip_parts = ip.split('.')

    # Check excluded IP ranges (individual IP ranges and subnet notation)
    for exclusion_range in exclusion_ranges:
        if '/' in exclusion_range:  # Check subnet notation
            if is_ip_in_subnet(ip, exclusion_range):
                return True
        else:  # Check individual IP range
            start, end = exclusion_range.split('-')
            start_parts = start.split('.')
            end_parts = end.split('.')
            ip_parts_int = list(map(int, ip_parts))
            start_parts_int = list(map(int, start_parts))
            end_parts_int = list(map(int, end_parts))

            if (
                start_parts_int[0] <= ip_parts_int[0] <= end_parts_int[0]
                and start_parts_int[1] <= ip_parts_int[1] <= end_parts_int[1]
                and start_parts_int[2] <= ip_parts_int[2] <= end_parts_int[2]
                and start_parts_int[3] <= ip_parts_int[3] <= end_parts_int[3]
            ):
                return True

    return False


async def check_minecraft_servers(start_ip, end_ip, ports, exclusion_ranges, versions=None):
    start_ip_obj = ipaddress.IPv4Address(start_ip)
    end_ip_obj = ipaddress.IPv4Address(end_ip)

    # Calculate the number of IP addresses in the range
    num_ips = int(end_ip_obj) - int(start_ip_obj) + 1

    start_time = datetime.now()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = []

        for ip_int in range(int(start_ip_obj), int(end_ip_obj) + 1):
            ip_address = str(ipaddress.IPv4Address(ip_int))
            if not is_private_ip(ip_address, exclusion_ranges):
                for port in ports:
                    if versions is None:
                        tasks.append(loop.run_in_executor(executor, process_ip, ip_address, port))
                    else:
                        tasks.append(loop.run_in_executor(executor, process_ip_with_versions, ip_address, port, versions))

        await asyncio.gather(*tasks)

    end_time = datetime.now()
    processing_time = end_time - start_time

    print(f"Generated {num_ips} IP addresses.")
    print(f"Processed in {processing_time}.")

def process_ip_with_versions(ip_address, port, versions):
    print(F"{ip_address}:{port}")
    exists = mycol.find_one({"IP": ip_address})
    if exists:
        server = JavaServer(ip_address, port, timeout=1)
        status = server.status()
        version = status.version.name
        if versions and version not in versions:
            print(f"IP: {ip_address} - Skipped: Version '{version}' not in specified versions.")
            return

        motd = status.description
        favicon = status.favicon
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
            version = status.version.name
            if version not in versions:
                print(f"IP: {ip_address} - Skipped: Version '{version}' not in specified versions.")
                return
            
            #gets ip details
            details = handler.getDetails(ip_address)

            motd = status.description
            favicon = status.favicon if status.favicon is not None else False
            protocol = status.version.protocol
            brand = query.software.brand
            online = status.players.online
            max_players = status.players.max
            playerlist = []
            pluginlist = []
            seed = ""
            cracked = False
            p2w = False
            
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
                version = status.version.name
                if version not in versions:
                    print(f"IP: {ip_address} - Skipped: Version '{version}' not in specified versions.")
                    return

                details = handler.getDetails(ip_address)

                motd = status.description
                favicon = status.favicon if status.favicon is not None else False
                protocol = status.version.protocol
                brand = ""
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

def load_exclusion_ranges(file_path):
    exclusion_ranges = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('-')
            if len(parts) == 1:  # CIDR notation
                exclusion_ranges.append(parts[0])
            elif len(parts) == 2:  # Individual IP range
                exclusion_ranges.append((parts[0], parts[1]))
            else:
                print(f"Invalid exclusion range format in file: {line.strip()}")

    return exclusion_ranges
    
async def main():
    parser = argparse.ArgumentParser(description="Check Minecraft servers in a given IP range.")
    parser.add_argument("-s", "--start", type=str, default="0.0.0.0", help="Starting IP address")
    parser.add_argument("-e", "--end", type=str,default="255.255.255.255", help="Ending IP address")
    parser.add_argument("--port", type=str, default="25565", help="Port or range of ports to scan (e.g., 25565 or 25565-25575)")
    parser.add_argument("--exclusion", type=str, help="Text file containing IP ranges to exclude")
    parser.add_argument("--versions", nargs="*", help="List of Minecraft versions to search for")
    args = parser.parse_args()

    start_ip = args.start
    end_ip = args.end
    ports = parse_port_range(args.port)
    exclusion_ranges = load_exclusion_ranges(args.exclusion) if args.exclusion else []
    versions = args.versions

    await check_minecraft_servers(start_ip, end_ip, ports, exclusion_ranges, versions)


def parse_port_range(port_range):
    if '-' in port_range:
        start_port, end_port = port_range.split('-')
        return range(int(start_port), int(end_port) + 1)
    else:
        return [int(port_range)]


asyncio.run(main())