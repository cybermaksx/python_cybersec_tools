import asyncio
import socket
import struct

target_ip = input("\nWhat is your target_ip\n")

target_port = int(input("\nWhich port do you want to check\n"))

MAX_CONCURRENT = 100 #For syn we are using less than tcp_scan


def calculate_checksum(data):
    pass










def syn_scan(target_ip,target_port):
    pass







async def syn_scan_async(target_ip, target_port, semaphore):
    async with semaphore:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, syn_scan, target_ip, target_port)

async def main():


