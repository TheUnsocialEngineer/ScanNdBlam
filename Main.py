import asyncio
import argparse
from utils.ports import port_parse
from utils.exclusions import exclusion_parse
from utils.check import check_minecraft_servers

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
    ports = port_parse(args.port)
    exclusion_ranges = exclusion_parse(args.exclusion) if args.exclusion else []
    versions = args.versions
    await check_minecraft_servers(start_ip, end_ip, ports, exclusion_ranges, versions)

asyncio.run(main())