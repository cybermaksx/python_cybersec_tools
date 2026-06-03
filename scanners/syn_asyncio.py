import socket
import struct
import os
import asyncio

ip = input("\nWhat is your target_ip\n")
port = int(input("\nWhich port do you want to check\n"))

my_ip_raw = os.popen("ip -4 addr show wlan0 | awk '/inet/ {print $2}' | cut -d/ -f1").read().strip()
my_ip = my_ip_raw

MAX_CONCURRENT = 100

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

def syn_scan(target_ip, target_port):
    source_port = 1234
    
    # TCP header fields
    seq = 0 
    ack = 0
    offset_flags = (5 << 12) | 0x002  # Data offset=5, SYN flag
    window = 1024
    checksum = 0 
    urgent = 0

    tcp_header = struct.pack("!HHLLHHHH", source_port, target_port, seq, ack, offset_flags, window, checksum, urgent)

    # TCP checksum requires pseudo-header
    src_ip_bytes = socket.inet_aton(my_ip)
    dst_ip_bytes = socket.inet_aton(target_ip)
    pseudo_header = struct.pack("!4s4sBBH", src_ip_bytes, dst_ip_bytes, 0, 6, 20)
    tcp_checksum = calculate_checksum(pseudo_header + tcp_header)
    tcp_header = struct.pack("!HHLLHHHH", source_port, target_port, seq, ack, offset_flags, window, tcp_checksum, urgent)
    
    # IP header fields
    version_ihl = 0x45  # Version 4, IHL 5 (20 bytes)
    tos = 0
    total_length = 40  # 20 (IP) + 20 (TCP)
    identification = 54321
    flags_fragment = 0x4000  # Don't fragment
    ttl = 64
    protocol = 6  # TCP
    checksum = 0
    source_ip = socket.inet_aton(my_ip)
    dest_ip = socket.inet_aton(target_ip)

    ip_header = struct.pack("!BBHHHBBH4s4s", 
                            version_ihl, tos, total_length, 
                            identification, flags_fragment, 
                            ttl, protocol, checksum, 
                            source_ip, dest_ip)
    
    # Calculate IP checksum
    ip_checksum = calculate_checksum(ip_header)
    ip_header = struct.pack("!BBHHHBBH4s4s", 
                            version_ihl, tos, total_length, 
                            identification, flags_fragment, 
                            ttl, protocol, ip_checksum, 
                            source_ip, dest_ip)
    
    packet = ip_header + tcp_header

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        s.settimeout(3)
        s.sendto(packet, (target_ip, 0))
        
        response = s.recvfrom(1024)
        ip_response = response[0]
        
        # Parse TCP header from response (skip IP header)
        ip_header_length = (ip_response[0] & 0x0F) * 4
        tcp_data = ip_response[ip_header_length:ip_header_length+20]
        
        if len(tcp_data) >= 20:
            tcp_fields = struct.unpack("!HHLLHHHH", tcp_data)
            flags = tcp_fields[4] & 0x1FF
            
            if flags == 0x012:  # SYN-ACK
                print(f"[*] Port {target_port} is OPEN")
            elif flags & 0x004:  # RST
                print(f"[*] Port {target_port} is CLOSED")
            else:
                print(f"[*] Port {target_port} - Flags: {hex(flags)}")
        
        s.close()

    except socket.timeout:
        print(f"[*] Port {target_port} - TIMEOUT (filtered?)")
    except Exception as e:
        print(f"Error: {e}")

async def syn_scan_async(target_ip, target_port, semaphore):
    async with semaphore:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, syn_scan, target_ip, target_port)

async def main():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    await syn_scan_async(ip, port, semaphore)

if __name__ == "__main__":
    asyncio.run(main())
