#!/usr/bin/env python3
"""
██╗  ██╗████████╗██████╗     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██║  ██║╚══██╔══╝██╔══██╗    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
███████║   ██║   ██████╔╝    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██║   ██║   ██╔══██╗    ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║   ██║   ██████╔╝    ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝   ╚═╝   ╚═════╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

HTB Auto-Recon Script by ABDUL JAFAROV
Concurrent enumeration: Nmap + FFUF Endpoint + FFUF Subdomain
"""

import subprocess
import threading
import re
import sys
import os
import json
import time
import shutil
import tempfile

# ═══════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════
class C:
    R   = '\033[91m'
    G   = '\033[92m'
    Y   = '\033[93m'
    B   = '\033[94m'
    M   = '\033[95m'
    CY  = '\033[96m'
    W   = '\033[97m'
    BD  = '\033[1m'
    DIM = '\033[2m'
    RS  = '\033[0m'

# Thread-safe print lock
_lock = threading.Lock()

def tprint(*args, **kwargs):
    """Thread-safe print."""
    with _lock:
        print(*args, **kwargs, flush=True)

def section(title, color=C.CY):
    """Print a section header."""
    w = 65
    tprint(f"\n{color}{C.BD}{'═'*w}")
    tprint(f"  {title}")
    tprint(f"{'═'*w}{C.RS}\n")

BANNER = f"""
{C.R}{C.BD}
    ██████╗ ██████╗ ██████╗ ██╗   ██╗██╗
   ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║
   ███████║██████╔╝██║  ██║██║   ██║██║
   ██╔══██║██╔══██╗██║  ██║██║   ██║██║
   ██║  ██║██████╔╝██████╔╝╚██████╔╝███████╗
   ╚═╝  ╚═╝╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
{C.CY}
         ██╗ █████╗ ███████╗ █████╗ ██████╗  ██████╗ ██╗   ██╗
         ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗██║   ██║
         ██║███████║█████╗  ███████║██████╔╝██║   ██║██║   ██║
    ██   ██║██╔══██║██╔══╝  ██╔══██║██╔══██╗██║   ██║╚██╗ ██╔╝
    ╚█████╔╝██║  ██║██║     ██║  ██║██║  ██║╚██████╔╝ ╚████╔╝
     ╚════╝ ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝
{C.RS}
{C.Y}{C.BD}  ╔═══════════════════════════════════════════════════════════╗
  ║          H T B   A U T O - R E C O N   v1.0              ║
  ║          Concurrent Enumeration Engine                    ║
  ╚═══════════════════════════════════════════════════════════╝{C.RS}
"""

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def get_hosts_info():
    """Read last non-comment line of /etc/hosts -> (ip, domain)."""
    with open('/etc/hosts', 'r') as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    if not lines:
        tprint(f"{C.R}[!] /etc/hosts boş veya geçerli satır yok!{C.RS}")
        sys.exit(1)
    parts = lines[-1].split()
    if len(parts) < 2:
        tprint(f"{C.R}[!] /etc/hosts son satırda IP ve domain bulunamadı!{C.RS}")
        sys.exit(1)
    return parts[0], parts[1]


def add_subdomains_to_hosts(ip, domain, subdomains):
    """Append found subdomains to the relevant /etc/hosts line."""
    if not subdomains:
        return
    if len(subdomains) > 15:
        tprint(f"{C.R}{C.BD}[!] {len(subdomains)} subdomain bulundu (>15). "
               f"Yanlış sonuç olabilir — eklenmedi, manuel kontrol et!{C.RS}")
        return
    try:
        with open('/etc/hosts', 'r') as f:
            lines = f.readlines()
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if not stripped or stripped.startswith('#'):
                continue
            if ip in stripped and domain in stripped:
                existing = stripped.split()
                new_subs = []
                for s in subdomains:
                    fqdn = f"{s}.{domain}"
                    if fqdn not in existing:
                        new_subs.append(fqdn)
                if new_subs:
                    lines[i] = stripped + ' ' + ' '.join(new_subs) + '\n'
                    with open('/etc/hosts', 'w') as f:
                        f.writelines(lines)
                    tprint(f"{C.G}{C.BD}[+] /etc/hosts güncellendi — eklenen: "
                           f"{', '.join(new_subs)}{C.RS}")
                else:
                    tprint(f"{C.Y}[*] Tüm subdomainler zaten /etc/hosts'ta mevcut.{C.RS}")
                return
        tprint(f"{C.R}[!] /etc/hosts'ta {ip} {domain} satırı bulunamadı!{C.RS}")
    except PermissionError:
        tprint(f"{C.R}[!] /etc/hosts yazma izni yok! sudo ile çalıştırın.{C.RS}")
    except Exception as e:
        tprint(f"{C.R}[!] /etc/hosts güncellenirken hata: {e}{C.RS}")


# ═══════════════════════════════════════════════════════════
# NMAP TASKS
# ═══════════════════════════════════════════════════════════

def nmap_full_scan(ip, results):
    """Phase-1: nmap -p- --min-rate 1000 -sS <ip>"""
    cmd = ['nmap', '-p-', '--min-rate', '1000', '-sS', ip]
    section("NMAP  ►  FULL PORT SCAN  (-p- -sS)", C.M)
    tprint(f"{C.Y}[*] Komut: {' '.join(cmd)}{C.RS}\n")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    output = proc.stdout

    section(f"NMAP  ◄  FULL PORT SCAN SONUÇLARI  ({elapsed:.0f}s)", C.G)
    tprint(output)

    # Parse open / filtered ports
    open_ports = re.findall(r'^(\d+)/\w+\s+open\s', output, re.MULTILINE)
    filtered_ports = re.findall(r'^(\d+)/\w+\s+filtered\s', output, re.MULTILINE)

    # "Not shown: N filtered ..." bulk count
    m = re.search(r'Not shown:.*?(\d+)\s+filtered', output)
    bulk_filtered = int(m.group(1)) if m else 0
    total_filtered = len(filtered_ports) + bulk_filtered

    results['open_ports'] = open_ports
    results['filtered_ports'] = filtered_ports
    results['total_filtered'] = total_filtered

    tprint(f"{C.G}{C.BD}[+] Açık portlar  : "
           f"{', '.join(open_ports) if open_ports else 'YOK'}{C.RS}")
    tprint(f"{C.Y}[*] Filtered port : {total_filtered}{C.RS}")


def nmap_detailed_scan(ip, open_ports, results):
    """Phase-2: nmap -p <ports> -sC -sV <ip>"""
    if not open_ports:
        return
    ports_str = ','.join(open_ports)
    cmd = ['nmap', '-p', ports_str, '-sC', '-sV', ip]
    section("NMAP  ►  DETAILED SCAN  (-sC -sV)", C.M)
    tprint(f"{C.Y}[*] Komut: {' '.join(cmd)}{C.RS}\n")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    section(f"NMAP  ◄  DETAILED SCAN SONUÇLARI  ({elapsed:.0f}s)", C.G)
    tprint(proc.stdout)
    results['detailed'] = proc.stdout


def nmap_udp_scan(ip, filtered_ports, results):
    """Phase-2: UDP scan on individually-listed filtered ports (<10)."""
    if not filtered_ports:
        return
    ports_str = ','.join(filtered_ports)
    cmd = ['nmap', '-sU', '-sV', '-p', ports_str, ip]
    section("NMAP  ►  UDP SCAN  (-sU -sV)", C.M)
    tprint(f"{C.Y}[*] Komut: {' '.join(cmd)}{C.RS}\n")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    section(f"NMAP  ◄  UDP SCAN SONUÇLARI  ({elapsed:.0f}s)", C.G)
    tprint(proc.stdout)
    results['udp'] = proc.stdout


# ═══════════════════════════════════════════════════════════
# FFUF TASKS
# ═══════════════════════════════════════════════════════════

def ffuf_endpoint(domain, results):
    """FFUF directory / endpoint brute-force."""
    url = f"http://{domain}/FUZZ"
    cmd = ['ffuf','-s', '-u', url,
           '-w', '/usr/share/wordlists/dirb/common.txt',
           '-ac', '-v', '-c']
    section("FFUF  ►  ENDPOINT TARAMASI", C.B)
    tprint(f"{C.Y}[*] Komut: {' '.join(cmd)}{C.RS}\n")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    section(f"FFUF  ◄  ENDPOINT SONUÇLARI  ({elapsed:.0f}s)", C.G)
    output = proc.stdout + proc.stderr
    tprint(output)
    results['endpoints'] = output


def ffuf_subdomain(ip, domain, results):
    """FFUF virtual-host / subdomain brute-force with auto-calibration."""
    section("FFUF  ►  SUBDOMAIN TARAMASI  (kalibrasyon)", C.CY)

    # --- Step 1: Get baseline response size with a fake subdomain ---
    tprint(f"{C.Y}[*] Sahte subdomain ile baseline size belirleniyor...{C.RS}")
    baseline_size = None
    try:
        curl = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{size_download}',
             '-H', f'Host: SAHTESUBDOMAIN123456.{domain}',
             f'http://{ip}/'],
            capture_output=True, text=True, timeout=15
        )
        val = curl.stdout.strip()
        if val.isdigit():
            baseline_size = int(val)
    except Exception as e:
        tprint(f"{C.R}[!] Kalibrasyon hatası: {e}{C.RS}")

    if baseline_size is not None and baseline_size > 0:
        tprint(f"{C.G}[+] Baseline response size: {baseline_size} bytes → -fs {baseline_size}{C.RS}")
        fs_args = ['-fs', str(baseline_size)]
    else:
        tprint(f"{C.Y}[*] Baseline belirlenemedi, -ac ile devam ediliyor...{C.RS}")
        fs_args = ['-ac']

    # --- Step 2: Actual subdomain scan ---
    json_out = tempfile.mktemp(suffix='.json', prefix='htbrecon_sub_')
    cmd = ['ffuf', '-s', '-u', f'http://{ip}/',
           '-H', f'Host: FUZZ.{domain}',
           '-w', '/usr/share/wordlists/dirb/common.txt',
           *fs_args, '-v', '-c',
           '-o', json_out, '-of', 'json']

    section("FFUF  ►  SUBDOMAIN TARAMASI", C.CY)
    tprint(f"{C.Y}[*] Komut: {' '.join(cmd)}{C.RS}\n")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    section(f"FFUF  ◄  SUBDOMAIN SONUÇLARI  ({elapsed:.0f}s)", C.G)
    tprint(proc.stdout)
    if proc.stderr:
        tprint(proc.stderr)

    # --- Step 3: Parse results ---
    subdomains = []
    try:
        if os.path.exists(json_out):
            with open(json_out, 'r') as f:
                data = json.load(f)
            for r in data.get('results', []):
                inp = r.get('input', {}).get('FUZZ', '')
                if inp:
                    subdomains.append(inp)
            os.unlink(json_out)
    except Exception:
        pass

    # Fallback: regex parse from stdout
    if not subdomains:
        for line in (proc.stdout + proc.stderr).splitlines():
            m = re.search(r'Host:\s*(\S+?)\.' + re.escape(domain), line)
            if m:
                val = m.group(1).strip()
                if val and val != 'FUZZ' and 'SAHTE' not in val.upper():
                    subdomains.append(val)

    subdomains = sorted(set(subdomains))
    results['subdomains'] = subdomains

    if subdomains:
        tprint(f"\n{C.G}{C.BD}[+] Bulunan subdomainler ({len(subdomains)}):{C.RS}")
        for s in subdomains:
            tprint(f"    {C.CY}● {s}.{domain}{C.RS}")
        add_subdomains_to_hosts(ip, domain, subdomains)
    else:
        tprint(f"{C.Y}[*] Subdomain bulunamadı.{C.RS}")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    print(BANNER)

    # Root check
    if os.geteuid() != 0:
        print(f"{C.R}{C.BD}[!] Bu script sudo/root olarak çalıştırılmalıdır!{C.RS}")
        sys.exit(1)

    # Tool check
    for tool in ['nmap', 'ffuf', 'curl']:
        if not shutil.which(tool):
            print(f"{C.R}[!] '{tool}' bulunamadı! Lütfen yükleyin.{C.RS}")
            sys.exit(1)

    ip, domain = get_hosts_info()
    print(f"{C.G}{C.BD}  ┌─ Hedef IP     : {ip}{C.RS}")
    print(f"{C.G}{C.BD}  └─ Hedef Domain : {domain}{C.RS}")
    print(f"{C.DIM}  {'─'*60}{C.RS}\n")

    results = {}

    # ═══════════════════════════════════════════════════
    # PHASE 1 — Concurrent: nmap full + ffuf endpoint + ffuf subdomain
    # ═══════════════════════════════════════════════════
    tprint(f"{C.Y}{C.BD}[⚡] PHASE 1 — Eş zamanlı taramalar başlatılıyor...{C.RS}")

    t_nmap = threading.Thread(target=nmap_full_scan, args=(ip, results), name='nmap-full')
    t_ep   = threading.Thread(target=ffuf_endpoint,  args=(domain, results), name='ffuf-ep')
    t_sub  = threading.Thread(target=ffuf_subdomain, args=(ip, domain, results), name='ffuf-sub')

    t_nmap.start()
    t_ep.start()
    t_sub.start()

    # Wait for all Phase-1 threads
    t_ep.join()
    t_sub.join()
    t_nmap.join()

    # ═══════════════════════════════════════════════════
    # PHASE 2 — After nmap full: detailed + UDP (concurrent)
    # ═══════════════════════════════════════════════════
    open_ports      = results.get('open_ports', [])
    filtered_ports  = results.get('filtered_ports', [])
    total_filtered  = results.get('total_filtered', 0)

    phase2 = []

    if open_ports:
        tprint(f"\n{C.Y}{C.BD}[⚡] PHASE 2 — Detaylı taramalar başlatılıyor...{C.RS}")
        t_det = threading.Thread(target=nmap_detailed_scan,
                                 args=(ip, open_ports, results), name='nmap-detail')
        phase2.append(t_det)
        t_det.start()

    # UDP only if individually-listed filtered ports < 10
    if filtered_ports and total_filtered < 10:
        t_udp = threading.Thread(target=nmap_udp_scan,
                                 args=(ip, filtered_ports, results), name='nmap-udp')
        phase2.append(t_udp)
        t_udp.start()

    for t in phase2:
        t.join()

    # ═══════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════
    section("TARAMA TAMAMLANDI ✓", C.G)

    if open_ports:
        tprint(f"  {C.G}{C.BD}Açık TCP Portlar : {', '.join(open_ports)}{C.RS}")
    else:
        tprint(f"  {C.R}Açık TCP port bulunamadı.{C.RS}")

    subs = results.get('subdomains', [])
    if subs:
        tprint(f"  {C.CY}{C.BD}Subdomainler     : {', '.join(s + '.' + domain for s in subs)}{C.RS}")
    else:
        tprint(f"  {C.Y}Subdomain bulunamadı.{C.RS}")

    tprint(f"\n  {C.DIM}Filtered ports: {total_filtered} | "
           f"UDP tarandı: {'Evet' if 'udp' in results else 'Hayır'}{C.RS}")
    tprint(f"\n{C.G}{C.BD}  [✓] Tüm taramalar tamamlandı! Hack the planet! 🚀{C.RS}\n")


if __name__ == '__main__':
    main()
