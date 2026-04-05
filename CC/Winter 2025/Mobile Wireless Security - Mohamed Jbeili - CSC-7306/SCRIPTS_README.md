---
title: Scripts — Mobile Wireless Security
description: Student-created scripts and automation utilities from the CSC-7306 Mobile Wireless Security course.
permalink: /scripts/
---

# Scripts — Mobile Wireless Security

Scripts and automation utilities developed during or inspired by the Mobile Wireless Security course (CSC-7306).

## Contents

### Student-Created Scripts (`scripts/`)

| Script | Purpose | Tools Used |
|---|---|---|
| [`nmap_wireless_scan.sh`](scripts/nmap_wireless_scan.sh) | Wireless device discovery and OS fingerprinting wrapper. Three-phase scan: host discovery → OS fingerprinting → wireless service detection (HTTP admin panels, SNMP, mDNS). | Nmap |
| [`wireshark_filters.txt`](scripts/wireshark_filters.txt) | Curated collection of Wireshark display filters for wireless security analysis — management frame inspection, EAPOL handshake capture, rogue AP detection, OS fingerprinting, and mobile traffic analysis. | Wireshark |
| [`mdm_compliance_policy.json`](scripts/mdm_compliance_policy.json) | Microsoft Intune MDM compliance policy template implementing the Bluegreen Media case study's BYOD security requirements — device encryption, jailbreak detection, VPN enforcement, app containerization, and conditional access. | Microsoft Intune |

### Reference Scripts (`scripts-extra/`)

_No external scripts provided as part of the course materials. The Jones & Bartlett labs used pre-configured Mininet-WiFi environments with GHostAPd._

## Safety Notes

- Review scripts before running; test in lab VMs only
- Use appropriate privileges (principle of least privilege)
- Wireless testing tools require explicit authorization from the network owner
- Never run wardriving, packet capture, or MITM tools against networks you do not own or lack explicit permission to test
- The Nmap scan script requires root/sudo privileges and generates network traffic that may trigger IDS/IPS alerts

---

*Ross Moravec | Mobile Wireless Security Portfolio*
