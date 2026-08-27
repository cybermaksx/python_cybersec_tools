#  python_cybersec_tools

> *"Why use Metasploit when you can spend 3 days writing something worse?"*

A collection of cybersecurity tools built from scratch in Python — no frameworks, no shortcuts, no AI writing the code (yes, really).

This repo is my learning journal. Every tool here represents me actually understanding what's happening at the packet level, not just importing `hack_everything` and calling it a day.

---

##  Repo layout

```
scanners/          — port scanners, from a 20-line socket to raw SYN packets
spoofers/          — layer 2 attacks. ARP cache poisoning and the MITM that follows
web_reconaninse/   — directory bruteforcing and web tech fingerprinting
automation/        — wrappers that chain nmap/ffuf/dirsearch together for CTFs
TryHackMe_Exploits/— one-off exploits written for specific THM rooms
TricksAndTests/    — small experiments and snippets I keep forgetting
```

---

##  Scanners

| File | What it does |
|------|--------------|
| `scanners/tcp_scan.py` | The absolute basics. One socket, one port, `connect()`. Where everyone starts |
| `scanners/tcp_asyn_scan.py` | Same idea, but `asyncio` + a semaphore capped at 500 concurrent connections. Fast and boring, exactly how it should be |
| `scanners/syn_scanner.py` | Half-open SYN scan. Raw sockets, hand-built IP + TCP headers, manual checksum. Needs root |
| `scanners/syn_asyncio.py` | SYN scan with proper flag parsing (SYN-ACK = open, RST = closed) and a thread executor wrapped in asyncio |
| `scanners/network_mapper.py` | The "product". ASCII banner, menu-driven port selection (common / all 65535 / range / manual list), then TCP or SYN mode. Basically nmap but worse and I'm proud of it |

**Notes:**
- SYN scanning requires `sudo` — raw sockets are not a suggestion, the kernel really means it.
- `syn_scanner.py` / `syn_asyncio.py` grab the local IP from `wlan0` via `ip addr`. Change the interface if you're on ethernet.
- `network_mapper.py` uses the UDP-connect-to-8.8.8.8 trick instead, which works on any interface.

---

##  Spoofers

| File | What it does |
|------|--------------|
| `spoofers/arp_poisoning.py` | Full ARP cache poisoner. Resolves both MACs, forks a poison process that lies to the victim and the gateway every 2 seconds, forks a sniffer that writes `arper.pcap`, and restores both ARP tables on exit |
| `spoofers/RUNBOOK.txt` | Every command needed to run it, verify it and clean up afterwards, plus every error I hit getting there and why |

ARP has no authentication, so anyone can send an unsolicited "is-at" reply and
have it cached without question. Two lies, refreshed every 2 seconds:

```
to the victim:   "the gateway is at <my MAC>"
to the gateway:  "the victim is at <my MAC>"
```

Both sides then address their frames to me, `ip_forward` passes them along, and
neither notices. Poisoning only one side gives you half the conversation and
usually just breaks it.

**Notes:**
- Needs `sudo`, and needs `scapy` — so call the venv interpreter directly. `sudo python3` uses the system Python and will not find it.
- Argument order is **victim, gateway, interface**. Confirm the gateway with `ip route show default` first. I attacked a random phone for two runs because I assumed the wrong address.
- `sudo sysctl -w net.ipv4.ip_forward=1`, or you have written a denial of service instead of a MITM.
- `sudo sysctl -w net.ipv4.conf.all.send_redirects=0`, or the kernel helpfully tells the victim to route around you.
- The capture is only written after 200 packets or a 60 second timeout. Wait for the `Got N packets` line instead of killing it early like I did twice.
- On Wi-Fi, client isolation on the AP will stop this dead. That is the network, not the script.
- `*.pcap` is gitignored. Captures hold real traffic from real devices and do not belong in a public repo.

```bash
sudo .venv/bin/python arp_poisoning.py <victim-ip> <gateway-ip> wlan0
```

---

##  Web recon

| File | What it does |
|------|--------------|
| `web_reconaninse/mini_dirsearch.py` | Directory bruteforce over `common.txt` (~4700 entries). Also runs `whatweb` to guess the backend stack. 200/302 = FOUND, 401/403 = exists but you're not invited |
| `web_reconaninse/smart_dirsearch.py` | Imports the tech detection from `mini_dirsearch` and appends the right extensions for it — PHP target gets `.php`, ASP gets `.asp/.aspx`, and so on. Fewer useless requests, same wordlist |

Both take the URL and port interactively, prepend `http://` if you forgot it, and expect `common.txt` in the **current working directory** — run them from inside `web_reconaninse/`.

Requires `whatweb` on PATH for fingerprinting.

---

##  Automation

| File | What it does |
|------|--------------|
| `automation/ctf_enumeration.py` | The actually-usable one. Runs nmap (`-sS -sV -sC`, fast `-F` or full `-p-`), regex-parses `nmap.txt` for open ports, decides which of them look like web services, builds `http(s)://ip:port` URLs and fires `dirsearch` at each one, then parses the JSON results |
| `automation/stupid_enum.py` | It's in the name. Nmap first, then a menu: ffuf directory bruteforce / gobuster vhost / whatweb + curl headers. Quick and dirty for when I already know what I want |

**Requires:** `nmap`, `dirsearch`, `ffuf`, `gobuster`, `whatweb`, and SecLists at `/usr/share/seclists/`.

---

##  TryHackMe exploits

| File | Room / purpose |
|------|----------------|
| `TryHackMe_Exploits/biteme_tryhackme_bruteforce_2mfa.py` | Bite Me — bruteforces the 2FA PIN on `console/mfa.php` using a session cookie and `pins.txt` |
| `TryHackMe_Exploits/capture.py` | Username enumeration against a login form — the app leaks "does not exist", so valid users fall out. Writes hits to `valid_users.txt` |

These have **hardcoded IPs, cookies and session IDs** from the box I was on at the time. They will not work as-is; edit the values at the top before reusing.

---

##  Tricks and tests

| File | What it does |
|------|--------------|
| `TricksAndTests/check_sum.py` | The RFC 1071 internet checksum, commented line by line. This is the function every SYN scanner here reuses |
| `TricksAndTests/get_localip_via_dnstrick.py` | Get your local IP by opening a UDP socket to 8.8.8.8 without sending anything. Interface-agnostic, my favourite |
| `TricksAndTests/getlocalip_via_OS.py` | Same goal, but by parsing `ip addr show wlan0`. Works until you switch interfaces |
| `TricksAndTests/test.py` | `gethostbyname(gethostname())`. Returns 127.0.0.1 half the time — kept as a reminder of why the other two exist |

---

##  Requirements

```bash
pip install requests
pip install scapy      # spoofers/ only
```

Everything else is stdlib (`socket`, `struct`, `asyncio`, `subprocess`, `re`, `json`, `multiprocessing`).
External binaries used by the automation scripts: `nmap`, `dirsearch`, `ffuf`, `gobuster`, `whatweb`.
`spoofers/` also wants `tcpdump` or `wireshark` for reading what you captured.

`spoofers/` keeps its own venv in `spoofers/.venv`. Do not name a venv after a
package you import from that directory — I named mine `scapy/` and spent an
evening watching Python import an empty folder instead of the library.

Tested on Linux. Raw socket scripts need `sudo`.

---

##  Disclaimer

These tools are for **educational purposes** and **authorized testing only**.
Don't be stupid. Don't scan networks you don't own.
The FBI has better tools than mine anyway.

---

##  Philosophy

Built without AI assistance to actually understand what I'm doing.
No copy-paste from Stack Overflow without reading it first.
No magic. Just Python, Wireshark, and pain.

---

*If this repo has 0 stars — that's fine, the NSA is watching anyway* 
