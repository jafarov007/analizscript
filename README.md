<div align="center">

```
    ██████╗ ██████╗ ██████╗ ██╗   ██╗██╗
   ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║
   ███████║██████╔╝██║  ██║██║   ██║██║
   ██╔══██║██╔══██╗██║  ██║██║   ██║██║
   ██║  ██║██████╔╝██████╔╝╚██████╔╝███████╗
   ╚═╝  ╚═╝╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

         ██╗ █████╗ ███████╗ █████╗ ██████╗  ██████╗ ██╗   ██╗
         ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗██║   ██║
         ██║███████║█████╗  ███████║██████╔╝██║   ██║██║   ██║
    ██   ██║██╔══██║██╔══╝  ██╔══██║██╔══██╗██║   ██║╚██╗ ██╔╝
    ╚█████╔╝██║  ██║██║     ██║  ██║██║  ██║╚██████╔╝ ╚████╔╝
     ╚════╝ ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝
```

# HTB Auto-Recon

**Concurrent Enumeration Engine for Penetration Testing Labs**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-557C94?logo=kalilinux&logoColor=white)](https://www.kali.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## ⚠️ Legal Disclaimer / Yasal Uyarı

### 🇬🇧 English

> **This tool is developed solely for use in authorized penetration testing environments, CTF competitions, and legal security laboratory platforms (such as Hack The Box, TryHackMe, etc.).**
>
> **Unauthorized use of this tool against systems you do not own or do not have explicit written permission to test is strictly prohibited and is a criminal offense under applicable computer crime laws (e.g., CFAA in the US, Computer Misuse Act in the UK, TCK 243-245 in Turkey).**
>
> The author assumes **no liability** for any misuse, damage, or illegal activity caused by this tool. By using this software, you agree that you are solely responsible for ensuring that your actions comply with all applicable laws and regulations.
>
> **Use responsibly. Hack ethically. Always get permission.**

### 🇹🇷 Türkçe

> **Bu araç yalnızca izinli sızma testi ortamlarında, CTF yarışmalarında ve yasal güvenlik laboratuvar platformlarında (Hack The Box, TryHackMe vb.) kullanılmak üzere geliştirilmiştir.**
>
> **Bu aracın, sahibi olmadığınız veya açık yazılı izniniz bulunmayan sistemlerde izinsiz kullanımı kesinlikle yasaktır ve yürürlükteki bilişim suçları yasalarına (Türkiye'de TCK 243-245. maddeler) göre suç teşkil eder.**
>
> Yazar, bu aracın kötüye kullanımından, oluşabilecek zararlardan veya yasa dışı faaliyetlerden **hiçbir sorumluluk kabul etmez**. Bu yazılımı kullanarak, eylemlerinizin tüm geçerli yasa ve düzenlemelere uygun olmasını sağlamaktan yalnızca kendinizin sorumlu olduğunu kabul etmiş olursunuz.
>
> **Sorumlu kullanın. Etik hackleyin. Her zaman izin alın.**

---

## 🇬🇧 English

### 📖 About

**HTB Auto-Recon** is a multi-threaded Python reconnaissance script designed to accelerate the initial enumeration phase of penetration testing lab machines. It runs Nmap and FFUF scans **concurrently**, saving valuable time during CTF and lab engagements.

The script reads the **last line** of `/etc/hosts` to automatically extract the target **IP address** and **domain name**, then launches all scans simultaneously.

### 🔍 What It Does

| Phase | Task | Description |
|-------|------|-------------|
| **Phase 1** *(concurrent)* | `nmap -p- --min-rate 1000 -sS` | Full TCP port scan on target IP |
| **Phase 1** *(concurrent)* | `ffuf -u http://domain/FUZZ -ac -v` | Directory/endpoint brute-force |
| **Phase 1** *(concurrent)* | `ffuf -H "Host: FUZZ.domain" -fs <size>` | Subdomain/vhost enumeration with auto-calibration |
| **Phase 2** *(after Phase 1 nmap)* | `nmap -p <open_ports> -sC -sV` | Detailed service/version scan on discovered ports |
| **Phase 2** *(conditional)* | `nmap -sU -sV -p <filtered_ports>` | UDP scan if filtered ports < 10 |

### ✨ Features

- 🚀 **Concurrent execution** — Nmap and FFUF run in parallel threads
- 🎯 **Auto-calibration** — Subdomain scan automatically detects baseline response size using a fake subdomain, then filters with `-fs`
- 📝 **Auto /etc/hosts update** — Discovered subdomains (≤15) are automatically appended to `/etc/hosts`
- 🛡️ **Safety check** — If >15 subdomains found, no modification is made (likely false positives)
- 🎨 **Beautiful terminal output** — Color-coded sections, ASCII banner, and organized results
- ⏱️ **Timed scans** — Each scan reports its execution time
- 🔄 **Two-phase scanning** — Detailed Nmap runs only after initial port discovery

### 📋 Prerequisites

- **Operating System:** Kali Linux (or any Debian-based pentesting distro)
- **Python:** 3.8+
- **Required tools:**
  - `nmap`
  - `ffuf`
  - `curl`
- **Wordlist:** `/usr/share/wordlists/dirb/common.txt`

### 🚀 Installation & Usage

**1. Clone the repository:**
```bash
git clone https://github.com/abduljafarov/analizscript.git
cd analizscript
```

**2. Grant execute permission:**
```bash
chmod +x htbrecon.py
```

**3. Add your target to `/etc/hosts`:**
```bash
echo "10.10.11.100  target.htb" | sudo tee -a /etc/hosts
```

**4. Run the script with root privileges:**
```bash
sudo python3 htbrecon.py
```

> [!IMPORTANT]
> The script **must** be run with `sudo` or as `root` because Nmap's SYN scan (`-sS`) requires raw socket access.

### ⚙️ How It Works

```
/etc/hosts (last line):
┌─────────────────────────────────┐
│ 10.10.11.100   target.htb      │
└──────┬────────────┬─────────────┘
       │            │
       ▼            ▼
    [IP]         [DOMAIN]
       │            │
       ▼            ▼
┌──────────────────────────────────────────────┐
│           PHASE 1 (Concurrent)               │
│                                              │
│  Thread 1: nmap -p- -sS 10.10.11.100        │
│  Thread 2: ffuf http://target.htb/FUZZ       │
│  Thread 3: ffuf Host: FUZZ.target.htb        │
│            (auto-calibrated with -fs)        │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│       PHASE 2 (After Nmap completes)         │
│                                              │
│  Thread A: nmap -sC -sV -p <open_ports>      │
│  Thread B: nmap -sU (if filtered < 10)       │
└──────────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  /etc/hosts     │
         │  auto-updated   │
         │  with found     │
         │  subdomains     │
         └─────────────────┘
```

---

## 🇹🇷 Türkçe

### 📖 Hakkında

**HTB Auto-Recon**, sızma testi laboratuvar makinelerinin ilk keşif aşamasını hızlandırmak için tasarlanmış çok iş parçacıklı (multi-threaded) bir Python keşif betiğidir. Nmap ve FFUF taramalarını **eş zamanlı** olarak çalıştırarak CTF ve lab çalışmalarında değerli zaman kazandırır.

Betik, hedef **IP adresini** ve **domain adını** otomatik olarak çıkarmak için `/etc/hosts` dosyasının **son satırını** okur ve ardından tüm taramaları eş zamanlı başlatır.

### 🔍 Ne Yapar?

| Aşama | Görev | Açıklama |
|-------|-------|----------|
| **Aşama 1** *(eş zamanlı)* | `nmap -p- --min-rate 1000 -sS` | Hedef IP üzerinde tam TCP port taraması |
| **Aşama 1** *(eş zamanlı)* | `ffuf -u http://domain/FUZZ -ac -v` | Dizin/endpoint brute-force taraması |
| **Aşama 1** *(eş zamanlı)* | `ffuf -H "Host: FUZZ.domain" -fs <size>` | Otomatik kalibrasyonlu subdomain/vhost keşfi |
| **Aşama 2** *(Aşama 1 nmap sonrası)* | `nmap -p <açık_portlar> -sC -sV` | Keşfedilen portlarda detaylı servis/versiyon taraması |
| **Aşama 2** *(koşullu)* | `nmap -sU -sV -p <filtered_portlar>` | Filtered port sayısı <10 ise UDP taraması |

### ✨ Özellikler

- 🚀 **Eş zamanlı çalışma** — Nmap ve FFUF paralel thread'lerde çalışır
- 🎯 **Otomatik kalibrasyon** — Subdomain taraması, sahte subdomain ile varsayılan yanıt boyutunu tespit eder ve `-fs` ile filtreler
- 📝 **Otomatik /etc/hosts güncelleme** — Bulunan subdomainler (≤15) otomatik olarak `/etc/hosts`'a eklenir
- 🛡️ **Güvenlik kontrolü** — 15'ten fazla subdomain bulunursa değişiklik yapılmaz (muhtemelen yanlış pozitif)
- 🎨 **Güzel terminal çıktısı** — Renkli bölümler, ASCII banner ve düzenli sonuçlar
- ⏱️ **Zamanlı taramalar** — Her tarama çalışma süresini raporlar
- 🔄 **İki aşamalı tarama** — Detaylı Nmap yalnızca ilk port keşfinden sonra çalışır

### 📋 Gereksinimler

- **İşletim Sistemi:** Kali Linux (veya Debian tabanlı herhangi bir pentest dağıtımı)
- **Python:** 3.8+
- **Gerekli araçlar:**
  - `nmap`
  - `ffuf`
  - `curl`
- **Kelime listesi:** `/usr/share/wordlists/dirb/common.txt`

### 🚀 Kurulum ve Kullanım

**1. Depoyu klonlayın:**
```bash
git clone https://github.com/abduljafarov/analizscript.git
cd analizscript
```

**2. Çalıştırma izni verin:**
```bash
chmod +x htbrecon.py
```

**3. Hedefinizi `/etc/hosts`'a ekleyin:**
```bash
echo "10.10.11.100  hedef.htb" | sudo tee -a /etc/hosts
```

**4. Betiği root yetkileriyle çalıştırın:**
```bash
sudo python3 htbrecon.py
```

> [!IMPORTANT]
> Betik **mutlaka** `sudo` ile veya `root` kullanıcı olarak çalıştırılmalıdır. Çünkü Nmap'in SYN taraması (`-sS`) ham soket erişimi gerektirir.

### ⚙️ Nasıl Çalışır?

```
/etc/hosts (son satır):
┌─────────────────────────────────┐
│ 10.10.11.100   hedef.htb       │
└──────┬────────────┬─────────────┘
       │            │
       ▼            ▼
    [IP]         [DOMAIN]
       │            │
       ▼            ▼
┌──────────────────────────────────────────────┐
│           AŞAMA 1 (Eş Zamanlı)               │
│                                              │
│  Thread 1: nmap -p- -sS 10.10.11.100        │
│  Thread 2: ffuf http://hedef.htb/FUZZ        │
│  Thread 3: ffuf Host: FUZZ.hedef.htb         │
│            (otomatik kalibrasyon ile -fs)     │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│     AŞAMA 2 (Nmap tamamlandıktan sonra)      │
│                                              │
│  Thread A: nmap -sC -sV -p <açık_portlar>    │
│  Thread B: nmap -sU (filtered < 10 ise)      │
└──────────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  /etc/hosts     │
         │  bulunan        │
         │  subdomainlerle │
         │  güncellenir    │
         └─────────────────┘
```

---

## 👤 Author / Yazar

**Abdul Jafarov**

---

## 📄 License / Lisans

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.
