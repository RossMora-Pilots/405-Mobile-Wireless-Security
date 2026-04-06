---
title: Scripts — Mobile Wireless Security
description: Automation scripts for wireless device discovery, Nmap XML analysis, and MDM compliance checking — CSC-7306 Mobile Wireless Security.
permalink: /scripts/
---

# Scripts — Mobile Wireless Security (CSC-7306)

Automation scripts and utilities for wireless security assessment, network scan analysis, and BYOD compliance auditing. Developed as part of the Mobile Wireless Security course (CSC-7306, Winter 2025).

---

## Table of Contents

- [Overview](#overview)
- [Scripts](#scripts)
  - [nmap_wireless_scan.sh](#nmap_wireless_scansh)
  - [parse_nmap_xml.py](#parse_nmap_xmlpy)
  - [wireless_compliance_checker.py](#wireless_compliance_checkerpy)
- [Data Files](#data-files)
  - [mdm_compliance_policy.json](#mdm_compliance_policyjson)
  - [wireshark_filters.txt](#wireshark_filterstxt)
  - [sample_device_inventory.json](#sample_device_inventoryjson)
- [Requirements](#requirements)
- [Safety Notes](#safety-notes)
- [Attribution](#attribution)

---

## Overview

| File | Type | Purpose |
|------|------|---------|
| [`nmap_wireless_scan.sh`](scripts/nmap_wireless_scan.sh) | Bash | Wireless device discovery and OS fingerprinting wrapper for Nmap |
| [`parse_nmap_xml.py`](scripts/parse_nmap_xml.py) | Python | Parse Nmap XML output into structured text/Markdown reports |
| [`wireless_compliance_checker.py`](scripts/wireless_compliance_checker.py) | Python | Audit device inventory against MDM compliance policy |
| [`mdm_compliance_policy.json`](scripts/mdm_compliance_policy.json) | JSON | Intune-style MDM compliance policy (BYOD baseline) |
| [`wireshark_filters.txt`](scripts/wireshark_filters.txt) | Text | Curated Wireshark display filters for wireless analysis |
| [`sample_device_inventory.json`](scripts/sample_device_inventory.json) | JSON | Sample device inventory for compliance checker testing |

---

## Scripts

### nmap_wireless_scan.sh

**Purpose:** Three-phase wireless network scanner that wraps Nmap to perform host discovery, OS fingerprinting, and wireless service detection. Outputs structured results with timestamped logging.

**Features:**

- `-h` / `--help` flag with full usage documentation
- Configurable port list via `-p` argument
- CIDR format input validation (IP octets, prefix length)
- Timestamped log file for every scan
- Per-phase timeout handling (partial results preserved)
- Summary report with host counts, OS fingerprints, and open ports
- XML output for downstream parsing with `parse_nmap_xml.py`

**Usage:**

```bash
# Basic subnet scan
sudo ./nmap_wireless_scan.sh 192.168.1.0/24

# Custom ports and output directory
sudo ./nmap_wireless_scan.sh -p 80,443,8080,5353 -o ./my_scans 10.0.0.0/24

# With timeout (seconds per phase)
sudo ./nmap_wireless_scan.sh -t 300 172.16.0.0/24

# Show help
./nmap_wireless_scan.sh -h
```

**Sample output:**

```
[2025-01-15 14:30:00] === Wireless Network Device Scan ===
[2025-01-15 14:30:00] Target: 192.168.1.0/24
[2025-01-15 14:30:00] Ports:  80,443,161,5353,8080,8443,8888,53,67,68,1900
[2025-01-15 14:30:00] [1/3] Host discovery (ping sweep)...
[2025-01-15 14:30:05]   Found 12 live hosts
[2025-01-15 14:30:05] [2/3] OS fingerprinting (TCP SYN + version detection)...
...
[2025-01-15 14:32:00] ╔══════════════════════════════════════════════════════════════╗
[2025-01-15 14:32:00] ║                     SCAN SUMMARY                           ║
[2025-01-15 14:32:00] ╚══════════════════════════════════════════════════════════════╝
[2025-01-15 14:32:00] Live Hosts Discovered:  12
[2025-01-15 14:32:00] OS Fingerprints Found:  8
[2025-01-15 14:32:00] Open Port Entries:      34
```

---

### parse_nmap_xml.py

**Purpose:** Parses Nmap XML output files (`-oX` format) and extracts host information, OS fingerprints, open ports, and running services. Identifies potential wireless/IoT devices by vendor OUI prefix and service name patterns.

**Features:**

- Parses standard Nmap XML output (`-oX` format)
- Extracts hosts, MAC addresses, OS fingerprints, open ports, and services
- Identifies wireless/IoT devices via 50+ vendor OUI prefixes and service keywords
- Generates text or Markdown reports
- `--wireless-only` filter to show only suspected wireless devices

**Usage:**

```bash
# Generate a scan first
sudo nmap -sS -sV -O --osscan-guess 192.168.1.0/24 -oX scan.xml

# Parse and display text report
python parse_nmap_xml.py scan.xml

# Markdown report to file
python parse_nmap_xml.py scan.xml -o report.md --format markdown

# Show only wireless/IoT candidates
python parse_nmap_xml.py scan.xml --wireless-only
```

**Sample output (text):**

```
======================================================================
NMAP SCAN REPORT — WIRELESS DEVICE ANALYSIS
======================================================================

Scanner:    nmap 7.94
Hosts Up:   12

----------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------
Total live hosts:              12
Potential wireless/IoT devices: 3
Total open ports:              34

----------------------------------------------------------------------
WIRELESS / IoT DEVICE CANDIDATES
----------------------------------------------------------------------
  Host: 192.168.1.1
  MAC:  18:E8:29:AA:BB:CC (Ubiquiti)
    → Vendor OUI match: Ubiquiti (18:E8:29)
    → Service match: 443/tcp — https UniFi Controller
```

---

### wireless_compliance_checker.py

**Purpose:** Reads an MDM compliance policy and a device inventory, evaluates each device against the policy requirements, and generates a compliance report with pass/fail details, failure analysis, and risk assessment.

**Features:**

- Checks 11 compliance categories: encryption, device lock, PIN length, jailbreak/root, auto-lock timeout, OS version, security patch recency, VPN, open Wi-Fi, sideloaded apps, backup encryption
- Platform-aware (separate iOS/Android version thresholds)
- Risk level assessment (Low → Critical)
- Failure frequency analysis to identify systemic issues
- Text or Markdown output

**Usage:**

```bash
# Run compliance check with text output
python wireless_compliance_checker.py \
    --policy mdm_compliance_policy.json \
    --inventory sample_device_inventory.json

# Markdown report to file
python wireless_compliance_checker.py \
    --policy mdm_compliance_policy.json \
    --inventory sample_device_inventory.json \
    --format markdown -o compliance_report.md
```

**Sample output (text):**

```
=================================================================
          WIRELESS COMPLIANCE REPORT
=================================================================

Policy:          BYOD-Wireless-Security-Baseline
Devices Evaluated: 6
Compliant:       2 (33.3%)
Non-Compliant:   4 (66.7%)

Risk Level: CRITICAL — Majority of devices non-compliant.

-----------------------------------------------------------------
NON-COMPLIANT DEVICES
-----------------------------------------------------------------

  ✗ Charlie-GalaxyS21 (android) — 5/11 checks passed
    Failures (6):
      • PIN length (4) below minimum (6)
      • Auto-lock timeout (10 min) exceeds maximum (5 min)
      • OS version (11.0) below minimum (12.0) for android
      • Security patch overdue (45 days since last patch, max 30)
      • VPN is not enabled (corporate VPN required)
      • Connected to open (unsecured) Wi-Fi network
```

---

## Data Files

### mdm_compliance_policy.json

Microsoft Intune-style MDM compliance policy template implementing the Bluegreen Media case study's BYOD security requirements. Defines thresholds for device encryption, jailbreak detection, OS versions, VPN enforcement, app containerization, and conditional access. Used as the policy baseline by `wireless_compliance_checker.py`.

### wireshark_filters.txt

Curated collection of Wireshark display filters for wireless security analysis organized by category:

- **WLAN Management Frames** — beacons, probes, deauth, disassociation
- **EAPOL / WPA Handshake** — 4-way handshake capture
- **Rogue AP / Evil Twin Detection** — SSID and BSSID filtering
- **OS / Device Fingerprinting** — TTL-based identification, HTTP User-Agent
- **Mobile Security Analysis** — TLS Client Hello, unencrypted HTTP, mDNS, DHCP

Copy individual filters into Wireshark's display filter bar or use as reference.

### sample_device_inventory.json

Sample device inventory with 6 BYOD devices (3 iOS, 3 Android) representing a realistic mix of compliance states:

| Device | Platform | Expected Result |
|--------|----------|----------------|
| Alice-iPhone15 | iOS 17.2 | ✅ Compliant |
| Bob-Pixel8 | Android 14.0 | ✅ Compliant |
| Charlie-GalaxyS21 | Android 11.0 | ❌ Outdated OS, weak PIN, no VPN, open Wi-Fi |
| Dana-iPhone12 | iOS 15.7 | ❌ Jailbroken, outdated OS, overdue patches |
| Eve-Pixel6 | Android 13.0 | ❌ Rooted, no encryption, no lock, many failures |
| Frank-iPadAir | iOS 17.0 | ❌ Backup not encrypted |

---

## Requirements

| Requirement | Version | Used By |
|-------------|---------|---------|
| **Bash** | 4.0+ | `nmap_wireless_scan.sh` |
| **Nmap** | 7.x+ | `nmap_wireless_scan.sh` |
| **Python** | 3.7+ | `parse_nmap_xml.py`, `wireless_compliance_checker.py` |
| **Root/sudo** | — | `nmap_wireless_scan.sh` (OS fingerprinting requires raw sockets) |

All Python scripts use **standard library only** — no pip installs required. Modules used: `xml.etree.ElementTree`, `json`, `argparse`, `os`, `sys`, `datetime`, `collections`.

---

## Safety Notes

> **⚠️ These tools are for authorized security testing and educational use only.**

- **Authorization first.** Never scan, capture, or test networks without explicit written authorization from the network owner. Unauthorized network scanning may violate computer crime laws (CFAA, state equivalents).
- **Lab environments.** Test all scripts in isolated lab VMs or purpose-built lab networks before any other use.
- **Least privilege.** Only use `sudo` when required (Nmap OS fingerprinting). The Python analysis scripts require no elevated privileges.
- **IDS/IPS awareness.** Active Nmap scans generate network traffic that will trigger intrusion detection systems. Coordinate with network administrators before scanning.
- **Data handling.** Scan results may contain sensitive network topology information. Store securely, do not commit to public repositories, and follow your organization's data handling policy.
- **No warranty.** These scripts are provided as-is for educational purposes. Review all code before execution.

---

## Attribution

Scripts developed for the **CSC-7306 Mobile Wireless Security** course (Winter 2025).

- Policy template references: [NIST SP 800-124r2](https://csrc.nist.gov/publications/detail/sp/800-124/rev-2/final), [CIS Mobile Device Benchmark](https://www.cisecurity.org/benchmark/mobile)
- Wireless vendor OUI data: [IEEE OUI Registry](https://standards-oui.ieee.org/)
- Wireshark filters: [Wireshark Display Filter Reference](https://www.wireshark.org/docs/dfref/)

*Ross Moravec | Mobile Wireless Security Portfolio*
