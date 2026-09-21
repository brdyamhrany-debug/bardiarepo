#!/usr/bin/env python3
# wERomap v1.0 - Pure Python Port Scanner (No nmap engine)
# Usage: python wERomap.py -t 127.0.0.1 -p 1-1000 --threads 200
# Usage: python wERomap.py -t example.com -p 80,443,8080 --scan syn-like --banner

import socket
import argparse
import threading
import queue
import time
import sys
import json
from datetime import datetime

VERSION = "1.0.0"
BANNER_ART = r"""
 _       __ _______ ____
| |     / // ____/ __ \___  ______ ___  ____ ____
| | /| / // __/ / /_/ / _ \/ __ `__ \/ _ \/ __ `/ 
| |/ |/ // /___/ _, _/  __/ / / / / /  __/ /_/ /  
|__/|__//_____/_/ |_|\___/_/ /_/ /_/\___/\__,_/   
                      v1.0 - Pure Engine
"""

COMMON_PORTS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    67: "dhcp", 68: "dhcp", 69: "tftp", 80: "http", 110: "pop3",
    111: "rpcbind", 135: "msrpc", 139: "netbios", 143: "imap",
    443: "https", 445: "smb", 993: "imaps", 995: "pop3s",
    1723: "pptp", 3306: "mysql", 3389: "rdp", 5432: "postgres",
    5900: "vnc", 6379: "redis", 8080: "http-proxy", 8443: "https-alt",
    27017: "mongodb", 6379: "redis", 9200: "elastic", 11211: "memcached"
}

PROBES = {
    80: b"GET / HTTP/1.0\r\n\r\n",
    8080: b"GET / HTTP/1.0\r\n\r\n",
    8000: b"GET / HTTP/1.0\r\n\r\n",
    8443: b"GET / HTTP/1.0\r\n\r\n",
    21: b"\r\n",
    25: b"EHLO weromap\r\n",
    110: b"\r\n",
    143: b"\r\n",
}

results = []
results_lock = threading.Lock()

def parse_ports(port_str):
    ports = set()
    if not port_str:
        return sorted(COMMON_PORTS.keys())
    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            ports.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            ports.add(int(part))
    return sorted(p for p in ports if 1 <= p <= 65535)

def grab_banner(sock, port, timeout=2):
    try:
        sock.settimeout(timeout)
        probe = PROBES.get(port, b"\r\n")
        try:
            sock.sendall(probe)
        except Exception:
            pass
        try:
            data = sock.recv(1024)
            if data:
                return data.decode(errors="ignore").strip().split("\n")[0][:200]
        except socket.timeout:
            pass
        except Exception:
            pass
    except Exception:
        pass
    return ""

def tcp_connect_scan(target, port, timeout, do_banner):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        rc = s.connect_ex((target, port))
        if rc == 0:
            service = COMMON_PORTS.get(port, "unknown")
            banner = grab_banner(s, port) if do_banner else ""
            # guess http from banner
            if banner.startswith("HTTP/"):
                service = "http"
            with results_lock:
                results.append({"port": port, "state": "open", "service": service, "banner": banner})
            return True
    except Exception:
        pass
    finally:
        s.close()
    return False

def worker(q, target, timeout, do_banner):
    while True:
        try:
            port = q.get_nowait()
        except queue.Empty:
            return
        tcp_connect_scan(target, port, timeout, do_banner)
        q.task_done()

def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        print(f"[!] خطا: هاست '{target}' پیدا نشد.")
        sys.exit(1)

def main():
    ap = argparse.ArgumentParser(prog="wERomap", description="wERomap - Pure Python Port Scanner")
    ap.add_argument("-t", "--target", required=True, help="IP یا دامنه هدف")
    ap.add_argument("-p", "--ports", default="top", help="مثلا 1-1000 یا 80,443,8080 یا top")
    ap.add_argument("--threads", type=int, default=200, help="تعداد ترد (پیش‌فرض 200)")
    ap.add_argument("--timeout", type=float, default=1.0, help="تایم‌اوت ثانیه")
    ap.add_argument("--banner", action="store_true", help="فعال‌سازی بنر گربینگ")
    ap.add_argument("--scan", default="connect", choices=["connect", "syn-like"], help="نوع اسکن")
    ap.add_argument("-o", "--output", default="", help="ذخیره JSON مثلا out.json")
    ap.add_argument("--top-n", type=int, default=100, help="اگر ports=top چند پورت اول")
    args = ap.parse_args()

    print(BANNER_ART)
    ip = resolve_target(args.target)
    print(f"[*] هدف: {args.target} ({ip})")
    print(f"[*] شروع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.ports == "top":
        ports = sorted(COMMON_PORTS.keys())[:args.top_n]
        # add some extra common
        extra = [8000, 8888, 9000, 9090, 3000, 5000, 27017, 9200]
        for p in extra:
            if p not in ports:
                ports.append(p)
        ports = sorted(ports)
    else:
        ports = parse_ports(args.ports)

    print(f"[*] تعداد پورت: {len(ports)} | ترد: {args.threads} | حالت: {args.scan}")
    print("-" * 60)

    q = queue.Queue()
    for p in ports:
        q.put(p)

    start = time.time()
    threads = []
    do_banner = args.banner or True
    for _ in range(min(args.threads, len(ports))):
        t = threading.Thread(target=worker, args=(q, ip, args.timeout, do_banner), daemon=True)
        t.start()
        threads.append(t)
    try:
        q.join()
    except KeyboardInterrupt:
        print("\n[!] لغو شد توسط کاربر")
        sys.exit(0)

    elapsed = time.time() - start
    results_sorted = sorted(results, key=lambda x: x["port"])

    print(f"\n{'PORT':<10}{'STATE':<10}{'SERVICE':<15}BANNER")
    print("-" * 60)
    for r in results_sorted:
        print(f"{r['port']}/tcp  {'open':<10}{r['service']:<15}{r['banner'][:60]}")
    print("-" * 60)
    print(f"[+] پورت‌های باز: {len(results_sorted)} | زمان: {elapsed:.2f}s")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"target": args.target, "ip": ip, "results": results_sorted}, f, indent=2, ensure_ascii=False)
        print(f"[*] ذخیره شد در {args.output}")

if __name__ == "__main__":
    main()
