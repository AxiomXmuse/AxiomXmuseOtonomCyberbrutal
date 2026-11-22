---
name: hykingcr-ctf-toolindex
description: "CTF tool reference index — searchable catalog from awesome-ctf: bruteforcers (Hashcat, Hydra, John), crypto (RSACTFTool, CyberChef), exploits (pwntools, ROPgadget, Metasploit), forensics (Volatility, Wireshark, Foremost), reversing (Ghidra, IDA, angr, Frida, Jadx), web CTF, platforms."
---

# HYKINGCR — CTF Tool Index

Source: `repos/awesome-ctf/README.md`

## Lookup

```bash
# Search by keyword
python3 '${CLAUDE_SKILL_DIR}/scripts/lookup.py' --search 'crypto'

# List by category
python3 '${CLAUDE_SKILL_DIR}/scripts/lookup.py' --category 'Reversing'

# All categories
python3 '${CLAUDE_SKILL_DIR}/scripts/lookup.py' --list-categories
```

## Tool Catalog

### Bruteforcers
| Tool | URL | Description |
|---|---|---|
| Aircrack-ng | https://github.com/aircrack-ng/aircrack-ng | Wi-Fi WEP/WPA brute |
| Hashcat | https://hashcat.net | GPU-accelerated hash cracker |
| Hydra | https://github.com/vanhauser-thc/thc-hydra | Network login brute forcer |
| John the Ripper | https://www.openwall.com/john/ | Password hash cracker |
| Nozzlr | https://github.com/intrd/nozzlr | Brute-force framework, modular |
| Ophcrack | https://ophcrack.sourceforge.io | LM/NTLM rainbow table cracker |
| Patator | https://github.com/lanjelot/patator | Multi-protocol brute forcer |

### Cryptography
| Tool | URL | Description |
|---|---|---|
| CyberChef | https://gchq.github.io/CyberChef | Browser-based crypto/encoding kitchen |
| RSACTFTool | https://github.com/Ganapati/RsaCtfTool | RSA attack toolkit (weak keys, factoring) |
| FeatherDuster | https://github.com/nccgroup/featherduster | Automated crypto analysis |
| HashID | https://github.com/psypanda/hashID | Hash type identification |
| msieve | https://sourceforge.net/projects/msieve/ | Integer factorization |
| PkCrack | https://www.unix-ag.uni-kl.de/~conrad/krypto/pkcrack.html | ZIP encryption crack (known-plaintext) |
| QuipQuip | https://quipqiup.com | Substitution cipher solver |
| Xortool | https://github.com/hellman/xortool | XOR key recovery / analysis |
| Yafu | https://sourceforge.net/projects/yafu/ | Fast integer factorization |

### Exploits
| Tool | URL | Description |
|---|---|---|
| pwntools | https://github.com/Gallopsled/pwntools | CTF exploit framework (Python) |
| ROPgadget | https://github.com/JonathanSalwan/ROPgadget | ROP chain gadget finder |
| Metasploit | https://www.metasploit.com | Exploit framework |
| libformatstr | https://github.com/hellman/libformatstr | Format string exploit helper |
| one_gadget | https://github.com/david942j/one_gadget | libc one-gadget RCE finder |
| pwndbg | https://github.com/pwndbg/pwndbg | GDB plugin for exploit dev |
| GEF | https://github.com/hugsy/gef | GDB Enhanced Features |
| PEDA | https://github.com/longld/peda | Python Exploit Development Assistance for GDB |

### Forensics
| Tool | URL | Description |
|---|---|---|
| Autopsy | https://www.autopsy.com | Digital forensics platform |
| DumpZilla | http://www.dumpzilla.com | Firefox forensics |
| EnCase | https://security.opentext.com/encase-forensic | Commercial forensics suite |
| ExifTool | https://exiftool.org | Metadata read/write for all file types |
| Foremost | https://foremost.sourceforge.net | File carving by header/footer |
| Volatility | https://github.com/volatilityfoundation/volatility3 | Memory forensics framework |
| Wireshark | https://www.wireshark.org | Network protocol analyzer |
| networkminer | https://www.netresec.com/index.ashx?page=NetworkMiner | PCAP analyzer / file extractor |
| pdf-parser | https://blog.didierstevens.com/programs/pdf-tools/ | PDF structure analysis |
| Binwalk | https://github.com/ReFirmLabs/binwalk | Firmware/binary extraction |

### Networking
| Tool | URL | Description |
|---|---|---|
| Bettercap | https://github.com/bettercap/bettercap | Network attack / MITM tool |
| nmap | https://nmap.org | Network scanner |
| Pwncat | https://github.com/cytopia/pwncat | Netcat with advanced features |
| Zeek (Bro) | https://zeek.org | Network analysis framework |
| Zmap | https://zmap.io | Fast internet-wide scanner |

### Reversing
| Tool | URL | Description |
|---|---|---|
| Ghidra | https://ghidra-sre.org | NSA open-source decompiler/disassembler |
| IDA Pro | https://hex-rays.com/ida-pro | Industry-standard disassembler/debugger |
| Binary Ninja | https://binary.ninja | Modern disassembler with IL analysis |
| angr | https://angr.io | Binary analysis + symbolic execution |
| Radare2 | https://rada.re/n/radare2.html | Open-source RE framework |
| Frida | https://frida.re | Dynamic instrumentation toolkit |
| Jadx | https://github.com/skylot/jadx | Android DEX/APK decompiler |
| apktool | https://ibotpeaches.github.io/Apktool/ | Android APK reverse engineering tool |
| Cutter | https://cutter.re | Radare2 GUI frontend |
| pwndbg | https://github.com/pwndbg/pwndbg | GDB plugin for RE |
| x64dbg | https://x64dbg.com | Windows debugger |
| dnSpy | https://github.com/dnSpy/dnSpy | .NET debugger/decompiler |
| dotPeek | https://www.jetbrains.com/decompiler | .NET decompiler (JetBrains) |
| JADX | https://github.com/skylot/jadx | DEX → Java decompiler |
| Java Decompiler | http://java-decompiler.github.io | Java .class decompiler |

### Steganography
| Tool | URL | Description |
|---|---|---|
| Steghide | http://steghide.sourceforge.net | Hide data in JPEG/BMP/WAV/AU |
| OpenStego | https://www.openstego.com | Steganography + watermark |
| Stegsolve | http://www.caesum.com/handbook/Stegsolve.jar | Image stego analyzer |
| zsteg | https://github.com/zed-0xff/zsteg | PNG/BMP stego detection |
| jsteg | https://github.com/lukechampine/jsteg | JPEG LSB steganography |
| Sonic Visualizer | https://www.sonicvisualiser.org | Audio analysis (spectrogram) |
| Stegoveritas | https://github.com/bannsec/stegoveritas | Image stego analysis suite |
| exiftool | https://exiftool.org | Metadata extraction |

### Web
| Tool | URL | Description |
|---|---|---|
| Burp Suite | https://portswigger.net/burp | Web app security testing platform |
| OWASP ZAP | https://www.zaproxy.org | Web app scanner |
| dirsearch | https://github.com/maurosoria/dirsearch | Web path discovery |
| sqlmap | https://sqlmap.org | SQL injection automation |
| XSStrike | https://github.com/s0md3v/XSStrike | XSS detection and exploitation |
| wfuzz | https://github.com/xmendez/wfuzz | Web fuzzer |
| ffuf | https://github.com/ffuf/ffuf | Fast web fuzzer |
| gobuster | https://github.com/OJ/gobuster | Dir/DNS/VHost brute forcer |

### CTF Platforms
| Platform | URL |
|---|---|
| CTFd | https://github.com/isislab/CTFd |
| FBCTF | https://github.com/facebook/fbctf |
| PicoCTF | https://picoctf.org |
| HackTheBox | https://www.hackthebox.com |
| TryHackMe | https://tryhackme.com |
| pwn.college | https://pwn.college |
| CTFtime | https://ctftime.org |
