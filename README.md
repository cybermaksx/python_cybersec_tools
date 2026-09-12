#  python_cybersec_tools

> *"Why use Metasploit when you can spend 3 days writing something worse?"*

A collection of cybersecurity tools built from scratch in Python — no frameworks, no shortcuts.

This repo is my learning journal. Every tool here represents me actually understanding what's
happening at the packet level, not just importing `hack_everything` and calling it a day.

It is organised as **Done** and **Planned**. Done is what already runs. Planned is a list of
small tools — each one sized to fit in an hour — where every item exists to force one specific
piece of Python I don't know well enough yet. When the Planned list is empty, I can stop
wondering whether I know Python.

---

##  Repo layout

```
scanners/          TCP, SYN and UDP port scanners — from a 20-line socket to raw packets
spoofers/          layer 2 attacks. ARP poisoning MITM + the lab runbook for it
web_reconaninse/   directory bruteforcing and web tech fingerprinting
DNS_ENUMERATION/   zone transfers
automation/        wrappers that chain nmap/ffuf/dirsearch together for CTFs
TryHackMe_Exploits/one-off exploits written for specific rooms
TricksAndTests/    small experiments and snippets I keep forgetting
```

---

#  DONE

##  Scanners

| File | What it does | What it proves I can do |
|------|--------------|-------------------------|
| `scanners/tcp_scan.py` | One socket, one port, `connect()`. Where everyone starts | sockets, exceptions |
| `scanners/tcp_asyn_scan.py` | Same idea on `asyncio` with a 500-connection semaphore | coroutines, `gather`, backpressure |
| `scanners/syn_scanner.py` | Half-open SYN scan. Raw sockets, hand-built IP + TCP headers, manual checksum | `struct`, byte order, RFC 1071 |
| `scanners/syn_asyncio.py` | SYN scan with real flag parsing — SYN-ACK = open, RST = closed | bit masks, IHL-aware header offsets |
| `scanners/network_mapper.py` | The "product". Banner, menu-driven port selection, TCP or SYN mode | putting it together |
| `scanners/udp_scan.py` | UDP probe. **Known broken:** reports `open\|filtered` for everything — see Planned #12 | honest limits |

Raw sockets need `sudo`. `syn_scanner.py` / `syn_asyncio.py` still hardcode `wlan0`;
`network_mapper.py` uses the UDP-connect-to-8.8.8.8 trick instead and works on any interface.

##  Spoofers

| File | What it does |
|------|--------------|
| `spoofers/arp_poisoning.py` | Full ARP-poisoning MITM. Resolves both MACs, poisons victim and gateway every 2s in one process, sniffs the victim's traffic to `arper.pcap` in another, restores both ARP tables on exit |
| `spoofers/RUNBOOK.txt` | Operating notes: kernel settings, verification with tcpdump, cleanup, and every error I hit with its cause |

The first tool here that is genuinely mine and genuinely works. It is also the one that taught
the most, mostly by breaking: a venv named `scapy` shadowing the real package, methods defined
outside the class, `self.victim` overwritten with a MAC, `send()` broadcasting instead of
`sendp()` unicast, and Python 3.14 switching the default multiprocessing start method to
`forkserver`, which pickles `self` and dies on the `Process` objects `Arper` holds.

All of it is written down in the runbook, including section 8 — how the attack works, in
enough detail to explain it out loud.

**Proves:** classes, `multiprocessing`, scapy layers, `finally` cleanup, and debugging
something real instead of rewriting it.

First actual finding from it: comparing DNS answers per resolver showed the local router
returning a different address for `wikipedia.org` than upstream. Selective DNS filtering,
found with my own tool.

##  Web recon

| File | What it does |
|------|--------------|
| `web_reconaninse/mini_dirsearch.py` | Directory bruteforce over `common.txt` (~4700 entries) + `whatweb` fingerprint. 200/302 = FOUND, 401/403 = exists but you're not invited |
| `web_reconaninse/smart_dirsearch.py` | Imports the detection from `mini_dirsearch` and appends the extensions that match the stack — PHP target gets `.php`, ASP gets `.asp/.aspx` |

Run them from inside `web_reconaninse/` — `common.txt` is looked up in the working directory.
Needs `whatweb` on PATH.

**Proves:** importing my own modules instead of copy-pasting between them.

##  DNS

| File | What it does |
|------|--------------|
| `DNS_ENUMERATION/dns_axfr.py` | AXFR zone transfer against a list of nameservers, collects subdomains. Typed out by hand while working through the HTB Academy DNS module — the structure is theirs, not mine. First script here with a real `argparse` interface. Planned #15 is rewriting it from a blank file |

##  Automation

| File | What it does |
|------|--------------|
| `automation/ctf_enumeration.py` | nmap (`-sS -sV -sC`, `-F` or `-p-`) → regex-parse the output → decide which ports look like web → build URLs → run `dirsearch` at each → parse its JSON |
| `automation/stupid_enum.py` | It's in the name. nmap, then a menu: ffuf / gobuster vhost / whatweb + curl |

**Requires:** `nmap`, `dirsearch`, `ffuf`, `gobuster`, `whatweb`, SecLists at `/usr/share/seclists/`.

Both still use `shell=True` with f-strings. That's Planned #9.

##  TryHackMe exploits

| File | Room / purpose |
|------|----------------|
| `TryHackMe_Exploits/matrix_tryhackme.py` | M4tr1x — recovers a time-based OTP: anchors to the box's own NTP clock once, advances it with a monotonic clock so my laptop's drift can't break it, then sweeps all 30 candidates in parallel inside the 60-second window |
| `TryHackMe_Exploits/exploit.py` | Robots — brute-forces `md5(username + ddmm)`. Learns the success and failure signatures from a known-good account *first*, then compares. Didn't crack the box; the approach is still the right one |
| `TryHackMe_Exploits/biteme_tryhackme_bruteforce_2mfa.py` | Bite Me — 2FA PIN bruteforce against `console/mfa.php` |
| `TryHackMe_Exploits/capture.py` | Username enumeration on a login form that leaks "does not exist" |

The M4tr1x one is the most advanced code in the repo: `ThreadPoolExecutor`, a generator for the
candidates, `itertools.combinations`, and a clock design that survives a drifting client.

These have **hardcoded IPs, cookies and session IDs** from the box I was on. Edit them before reuse.

##  Tricks and tests

| File | What it does |
|------|--------------|
| `TricksAndTests/check_sum.py` | RFC 1071 internet checksum, commented line by line. Every SYN scanner here reuses this function — by copy-paste, which is Planned #3 |
| `TricksAndTests/get_localip_via_dnstrick.py` | Local IP via a UDP socket to 8.8.8.8 that never sends anything. Interface-agnostic, my favourite |
| `TricksAndTests/getlocalip_via_OS.py` | Same goal by parsing `ip addr show wlan0`. Works until you switch interfaces |
| `TricksAndTests/test.py` | `gethostbyname(gethostname())`. Returns 127.0.0.1 half the time — kept as the reason the other two exist |

---

#  PLANNED

Rules I'm holding myself to:

- **One hour each.** If it doesn't fit, it's two tools.
- **Each one targets a hole**, not a feature. The point is the Python, the tool is the excuse.
- **Every item has a done-check** — a command whose output decides it, not a feeling.
- **No AI writes the first version.** Review after, never before. See `Box-Rules.md` logic.

### Tier 1 — language holes I can currently route around

| # | Tool | ~ | What it forces | Done when |
|---|------|---|----------------|-----------|
| 1 | `TricksAndTests/hexdump.py` — print any file as `xxd` does: offset, hex, ASCII column | 45m | `bytes` vs `str`, slicing, f-string format specs (`{b:02x}`, `{off:08x}`), chunking with a generator | `diff <(python hexdump.py f) <(xxd f)` is empty |
| 2 | `lib/net.py` — one shared module: `checksum()`, `local_ip()`, `parse_ports("22,80,1-1000")` | 30m | modules, `import` paths, why a directory named after a package breaks everything (I hit this once already) | `grep -rc "def calculate_checksum" .` returns 1 |
| 3 | `web_reconaninse/mutate.py` — read a wordlist, emit leet/caps/digit-suffix variants | 1h | **generators and `yield`**, `itertools.product`, sets for dedup, streaming instead of loading | runs on `common.txt` with `/usr/bin/time -v` showing flat memory |
| 4 | `lib/deco.py` — `@timed` and `@retry(times=3, delay=1)`, then put `@retry` on the requests in the dirsearchers | 45m | decorators, closures, `*args/**kwargs`, `functools.wraps` | a dirsearch run survives me pulling the network cable for 2 seconds |
| 5 | `lib/rawsock.py` — `with RawSocket() as s:` wrapping the raw socket the SYN scanners open by hand | 45m | `__enter__` / `__exit__`, cleanup that runs even on Ctrl-C | Ctrl-C mid-scan leaves no socket in `ss -ap`, no `try/finally` left in the scanners |

### Tier 2 — turning scripts into tools

| # | Tool | ~ | What it forces | Done when |
|---|------|---|----------------|-----------|
| 6 | argparse for `network_mapper.py`, `tcp_scan.py`, `syn_scanner.py`, `udp_scan.py` — kill every module-level `input()` | 1h | `argparse` groups, defaults, `main()`, why import-time side effects make a file unusable | `for ip in (cat hosts.txt); python network_mapper.py -t $ip -p 1-1000 --syn; end` works |
| 7 | Replace `print` with `logging` in the scanners: `-v` / `-q`, results to stdout, progress to stderr | 45m | `logging` levels and handlers, stdout vs stderr | `python network_mapper.py -t X > ports.txt` puts only ports in the file, progress still on screen |
| 8 | `lib/report.py` — a `@dataclass Finding`, plus `--json out.json` on one scanner | 1h | `dataclasses`, `asdict`, `json`, and the trap that `set` isn't serialisable | `jq '.findings[] \| select(.port==80)' out.json` prints something |
| 9 | Kill `shell=True` everywhere in `automation/` and `mini_dirsearch.py` | 45m | `subprocess.run([...])` as a list, `shlex`, return codes, `timeout=`, `capture_output` | `grep -rn "shell=True" .` is empty, and a target named `8.8.8.8; id` runs no `id` |

### Tier 3 — proving it to myself

| # | Tool | ~ | What it forces | Done when |
|---|------|---|----------------|-----------|
| 10 | `tests/test_net.py` — pytest over `checksum()` and `parse_ports()` | 1h | `pytest`, `parametrize`, fixtures, writing code that can be tested at all | `pytest -v` green, and one test asserts my checksum equals scapy's on the same bytes |
| 11 | Type hints on `lib/` + `mypy lib/` clean | 45m | `typing`, `Optional`, what a signature actually promises | `mypy lib/` reports no errors |

### Tier 4 — network debts, where I'm already strong

| # | Tool | ~ | What it forces | Done when |
|---|------|---|----------------|-----------|
| 12 | Fix `udp_scan.py`. It says `open\|filtered` for everything because an *unconnected* UDP socket never surfaces the ICMP port-unreachable. Use `connect()` + `send()`, or read ICMP type 3 code 3 from a raw socket | 1h | socket semantics, `errno`, ICMP — the actual reason `nmap -sU` is slow | scanning a closed port on my own box prints CLOSED, `nc -u -l` port prints OPEN |
| 13 | `lib/oracle.py` — generalise the trick from `exploit.py`: take a known-good and a known-bad response, decide which fields (status, length, word count, `Location`) separate them, return a comparator | 1h | classes with a real job, tuples, `Session` reuse, turning a one-off into a library | `biteme` and `capture.py` both rewritten to use it, both still work |
| 14 | `spoofers/arp_watch.py` — the defensive flip of the poisoner: watch ARP replies, alert when one IP claims two MACs | 1h | `scapy.sniff` with a callback, `collections.defaultdict`, thinking as the blue team | it fires on my own `arp_poisoning.py` running against my lab |
| 15 | Rewrite `DNS_ENUMERATION/dns_axfr.py` from a blank file. Module closed, old file closed, `dnspython` docs open if needed | 30m | whether following along actually stuck — the `Box-Rules.md` re-run rule applied to code instead of boxes | it does a zone transfer against the lab without me opening either the module or the old version |

### Capstone (not an hour — do it last)

Rebuild `network_mapper.py` on top of `lib/`: argparse, logging, JSON output, `RawSocket`,
`parse_ports`, tests. Same tool, none of the same code. If that rewrite feels boring instead of
hard, the list did its job.

---

##  Requirements

```bash
pip install requests scapy dnspython paramiko ntplib
```

Everything else is stdlib: `socket`, `struct`, `asyncio`, `multiprocessing`, `subprocess`, `re`, `json`, `hashlib`.

External binaries: `nmap`, `dirsearch`, `ffuf`, `gobuster`, `whatweb`, `tcpdump`.

Linux. Raw sockets and layer-2 attacks need root.

---

##  Disclaimer

These tools are for **educational purposes** and **authorized testing only**.
The ARP poisoner was run against my own network, with my own devices.
Don't be stupid. Don't scan networks you don't own.
The FBI has better tools than mine anyway.

---

##  Philosophy

Write it myself first, understand why it broke, write down what fixed it.
No copy-paste from Stack Overflow without reading it first.
No magic. Just Python, Wireshark, and pain.

---

*If this repo has 0 stars — that's fine, the NSA is watching anyway*
