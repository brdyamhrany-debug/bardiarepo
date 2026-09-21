import os
import subprocess
import sys

# --- COLORS ---
RED = "\033[1;31m"
RESET = "\033[0m"
BOLD = "\033[1m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def execute_cmd(cmd):
    try:
        # اجرای دستور memhub و چاپ خروجی در ترمینال
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(f"{RED}{line}{RESET}", end="")
        process.wait()
    except Exception as e:
        print(f"{RED}[-] Error executing command: {e}{RESET}")

def main():
    clear_screen()
    # نمایش خط فرمان قرمز ساده در ابتدای اجرا
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  MEMHUB LOCATION TRACKER - ACTIVE & READY")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    while True:
        try:
            # خط فرمان قرمز رنگ
            user_input = input(f"{RED}memhub-shell ➜ {RESET}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'clear']:
                if user_input.lower() == 'clear':
                    clear_screen()
                    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    print(f"  MEMHUB LOCATION TRACKER - ACTIVE & READY")
                    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
                    continue
                else:
                    break

            # تجزیه دستور (Parsing)
            # فرض می‌کنیم کاربر دستور را به فرمت memhub -u [target] [switch] وارد می‌کند
            parts = user_input.split(' ')
            
            if len(parts) < 3 or parts[0] != 'memhub':
                print(f"{RED}[!] Invalid Command Format. Use: memhub -u [ip/link] [switch]{RESET}")
                continue

            # استخراج تارگت و سوییچ‌ها
            # memhub -u target switch
            target = parts[2]
            switches = " ".join(parts[3:]) if len(parts) > 3 else ""
            
            # ساخت دستور نهایی برای ارسال به سیستم
            final_command = f"memhub -u {target} {switches}"
            
            print(f"{RED}[*] Processing request for: {target}...{RESET}")
            execute_cmd(final_command)

        except KeyboardInterrupt:
            print(f"\n{RED}[!] Exiting...{RESET}")
            break

if __name__ == "__main__":
    main()
          
