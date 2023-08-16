import ipaddress
import asyncio
from datetime import datetime
from utils.privateip import is_private_ip
from utils.process import ping_ips

async def check_minecraft_servers(start_ip, end_ip, ports, exclusion_ranges, batch_size, versions=None):
    start_ip_obj = ipaddress.IPv4Address(start_ip)
    end_ip_obj = ipaddress.IPv4Address(end_ip)

    num_ips = int(end_ip_obj) - int(start_ip_obj) + 1
    start_time = datetime.now()

    # Calculate the number of batches needed
    num_batches = (num_ips + batch_size - 1) // batch_size

    tasks = []
    for batch_index in range(num_batches):
        batch_start = batch_index * batch_size
        batch_end = min((batch_index + 1) * batch_size, num_ips)
        
        batch_ips = []
        for ip_int in range(int(start_ip_obj) + batch_start, int(start_ip_obj) + batch_end):
            ip_address = str(ipaddress.IPv4Address(ip_int))
            if not is_private_ip(ip_address, exclusion_ranges):
                for port in ports:
                    batch_ips.append((ip_address, port))

        tasks.append(asyncio.create_task(ping_ips(batch_ips, versions, batch_size)))

    await asyncio.wait(tasks)

    end_time = datetime.now()
    processing_time = end_time - start_time

    print(f"Generated {num_ips} IP addresses.")
    print(f"Processed in {processing_time}.")