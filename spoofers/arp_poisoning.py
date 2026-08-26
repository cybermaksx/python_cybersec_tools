from multiprocessing import Process
from scapy.all import ARP , Ether, conf , get_if_hwaddr, send , sniff ,sndrcv , srp , wrpcap


import os
import sys
import time

def get_mac(targetip):
    packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op="who-has", pdst=targetip)
    resp, _ = srp(packet, timeout= 2 , retry= 10 , verbose = False)
    for _, r in resp:
        return r[Ether].src
    return None


class Arper:
    def __init__(self, victim , gateway , interface= 'wlan0'):
        self.victim = victim 
        self.victim = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface = interface 
        conf.iface = interface
        conf.verb = 0

        print(f'Initialized {interface}:')
        print(f'Gateway ({gateway}) is at {selfgateway.mac}.')
        print(f'Victim {victim} is at {self.victimmac}.')
        print('-'*30)
    


def run (self):
    self.poison_thread = Process(target=self.poison)
    self.poison_thread.start()

    self.sniff_thread = Process(target=self.sniff)
    self.sniff_thread.start()
    


def poison(self):
    pass


def sniff(self, count=200):
    pass


def restore(self):
    pass


if __name__ == '__main__':
    (victim, gateway , interface) = (sys.argv[1] , sys.argv[2], sys.argv[3])

    myarp = Arper(victim, gateway , interface)


    myarp.run()
