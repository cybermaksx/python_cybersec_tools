import socket 
import struct
import os
'''
I am not going to spend much time for this script

The purpose is reminding myself how UDP scan works so i can add to my network_mapper.py

You can use it just to understand how  
    sudo nmap -sU -p1002 

works underhood

And i would be incredibly happy if this helps you to learn something new

'''

target_ip = input("\nWhat is your target's ip?\n")
port = int(input("Which port you are going to scan?"))  

timeout = 2  

def udp_scan(target_ip,port):

    try:
        # UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        sock.sendto(b'', (target_ip, port))  
        
        data, addr = sock.recvfrom(1024)
        
        sock.close()
        return True 
        
    except socket.timeout:
        
        sock.close()
        return True
        
    except ConnectionRefusedError:
        
        sock.close()
        return False
        
    except OSError as e:
        
        sock.close()
        if e.errno == 111: 
            return False
        return None  



result = udp_scan(target_ip, port)

if result is True:
    print(f"[+] Port {port}/udp is OPEN|FILTERED")
elif result is False:
    print(f"[-] Port {port}/udp is CLOSED")
else:
    print(f"[?] Port {port}/udp status is UNKNOWN")























