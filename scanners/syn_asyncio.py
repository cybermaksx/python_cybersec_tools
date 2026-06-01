import asyncio
import socket
import struct

target_ip = input("\nWhat is your target_ip\n")

target_port = int(input("\nWhich port do you want to check\n"))

MAX_CONCURRENT = 100 #For syn we are using less than tcp_scan


def calculate_checksum(data):
    if len(data) % 2 != 0:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        s += word
    s = (s >> 16) + (s & 0xFFFF)
    s += (s >> 16)
    return ~s & 0xFFFF








def syn_scan(target_ip,target_port):
    pass







async def syn_scan_async(target_ip, target_port, semaphore):
    async with semaphore:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, syn_scan, target_ip, target_port)

async def main():


