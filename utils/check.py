import ipaddress
import asyncio
import concurrent.futures
from datetime import datetime
from utils.privateip import is_private_ip
from utils.process import ping_ips

async def check_minecraft_servers(start_ip, end_ip, ports, exclusion_ranges, versions=None):
    start_ip_obj = ipaddress.IPv4Address(start_ip)
    end_ip_obj = ipaddress.IPv4Address(end_ip)

    num_ips = int(end_ip_obj) - int(start_ip_obj) + 1
    start_time = datetime.now()

    batch_size = 3500
    batch_ips = []

    for ip_int in range(int(start_ip_obj), int(end_ip_obj) + 1):
        ip_address = str(ipaddress.IPv4Address(ip_int))
        if not is_private_ip(ip_address, exclusion_ranges):
            for port in ports:
                batch_ips.append((ip_address, port))
                if len(batch_ips) >= batch_size:
                    await ping_ips(batch_ips, versions)  # Call ping_ips with the batch
                    batch_ips = []  # Reset the batch

    # Process any remaining IPs
    if batch_ips:
        await ping_ips(batch_ips, versions)

    end_time = datetime.now()
    processing_time = end_time - start_time

    print(f"Generated {num_ips} IP addresses.")
    print(f"Processed in {processing_time}.")