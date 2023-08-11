import asyncio

from mcstatus import JavaServer


async def ping_server(ip: str) -> None:
    try:
        status = await (await JavaServer.async_lookup(ip)).async_status()
    except Exception:
        return

    print(f"{ip} - Latency: {status.latency}ms, Players: {status.players.online}")



async def ping_ips(ips: list[str]) -> None:
    to_process: list[str] = []

    for ip in ips:
        if len(to_process) < 10:
            to_process.append(ip)
        else:
            tasks = [asyncio.create_task(ping_server(ip)) for ip in to_process]
            await asyncio.wait(tasks)
            to_process = []

    # Handle remaining IPs
    if to_process:
        tasks = [asyncio.create_task(ping_server(ip)) for ip in to_process]
        await asyncio.wait(tasks)




def getips() -> None:
    ips = ["mchub.com", "play.hivemc.com", "play.cubecraft.net"]  # insert here your ips!
    asyncio.run(ping_ips(ips))
