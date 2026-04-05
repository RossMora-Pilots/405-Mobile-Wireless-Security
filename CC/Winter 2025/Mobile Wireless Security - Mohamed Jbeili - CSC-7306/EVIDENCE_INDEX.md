# Evidence & Screenshots Index — Mobile Wireless Security

Comprehensive evidence index for the Mobile Wireless Security portfolio. All artifacts are contained within the PDF submissions — visual evidence is embedded in the lab PDFs exported by the Jones & Bartlett LMS.

## Table of Contents

- [Lab Submissions](#lab-submissions)
- [Capstone Deliverables](#capstone-deliverables)
- [Scripts & Automation](#scripts--automation)
- [Detailed Evidence Catalog](#detailed-evidence-catalog)

## Lab Submissions

### Lab 1 — Wireless Wardriving Defense (Week 2)

- [Lab01_Wireless_Wardriving_Defense_Submission.pdf](assignments/Lab01_Wireless_Wardriving_Defense_Submission.pdf) — 21 screenshots with student analysis covering GHostAPd configuration, LinSSID scanning, MAC ACL enforcement, association logs, Kismet hidden-SSID decloaking, and WEP detection.

### Lab 3 — Wi-Fi Site Survey (Week 10)

- [Lab03_WiFi_Site_Survey_Submission.pdf](assignments/Lab03_WiFi_Site_Survey_Submission.pdf) — 13+ screenshots spanning signal-level heatmaps, SIR analysis, PHY mode identification, frequency band comparison (2.4 GHz vs 5 GHz), dead zone documentation, and AP placement recommendations.

### Lab 5 — Mobile Device Fingerprinting (Week 12)

- [Lab05_Mobile_Device_Fingerprinting_Submission.pdf](assignments/Lab05_Mobile_Device_Fingerprinting_Submission.pdf) — 10+ screenshots covering Wireshark TTL captures, Nmap `-O` scan results, p0f Android 9.x passive identification, ClientJS browser fingerprints (Chrome + Firefox), User-Agent string comparison, and Cover Your Tracks cookie analysis.

## Capstone Deliverables

### Week 6 — Bluegreen Media WLAN & Mobile Security Plan

- [CaseStudy_WLAN_Mobile_Security_Plan.pdf](assignments/CaseStudy_WLAN_Mobile_Security_Plan.pdf) — Main case study report (Parts 1-3): vulnerability analysis plan, audit & risk assessment plan, BYOD policy framework, 3 strategic recommendations (NAC, MDM+Zero Trust, WIPS). ~5,500 words.
- [CyberKillChain_Quiz_Evidence.pdf](assignments/CyberKillChain_Quiz_Evidence.pdf) — Cyber Kill Chain (Part 1) and Networking Concepts (Part 2) quiz completion evidence, submitted 2025-01-26. The substantive kill chain analysis is in [CYBER_KILL_CHAIN_ANALYSIS.md](CYBER_KILL_CHAIN_ANALYSIS.md).
- [CaseStudy_Final_Presentation.pdf](assignments/CaseStudy_Final_Presentation.pdf) — Final presentation deck (10 slides) delivered 2025-03-05. Slides are verbal delivery prompts; full analysis is in [CASE_STUDY_CAPSTONE.md](CASE_STUDY_CAPSTONE.md).

## Scripts & Automation

| Artifact | Description |
|---|---|
| [nmap_wireless_scan.sh](scripts/nmap_wireless_scan.sh) | Nmap wireless device discovery and OS fingerprinting wrapper |
| [wireshark_filters.txt](scripts/wireshark_filters.txt) | Curated Wireshark display filters for wireless security analysis |
| [mdm_compliance_policy.json](scripts/mdm_compliance_policy.json) | Microsoft Intune MDM compliance policy template (BYOD baseline) |

## Detailed Evidence Catalog

### Lab 1 Evidence (21 items in PDF)

| # | Evidence Description | Type | Key Finding |
|---|---|---|---|
| 1 | GHostAPd status page — baseline open config | Screenshot | Security: None, Channel 1, 100% Tx power |
| 2 | LinSSID scan — pre-hardening WLAN discovery | Screenshot | `simplewifi` visible at -79 dBm, no encryption |
| 3 | GHostAPd — WPA2-PSK configuration | Screenshot | CCMP encryption enabled, 8-char passphrase |
| 4 | GHostAPd — MAC ACL Default Deny configuration | Screenshot | Allow list with `sta1-wlan0` MAC only |
| 5 | GHostAPd — Transmit power reduction to 75% | Screenshot | Signal leakage reduced beyond physical perimeter |
| 6 | LinSSID scan — post-hardening verification | Screenshot | `simplewifi` now shows PSK/CCMP encryption |
| 7 | GHostAPd association logs — authenticated client | Screenshot | `sta1-wlan0: associated` with timestamp sequence |
| 8 | `notsosimplewifi` neighbor detection | Screenshot | Channel 4, -88 dBm, PSK/CCMP |
| 9 | Kismet — hidden SSID `TheGatesofHeck` decloaked | Screenshot | Hidden SSID captured from probe responses |
| 10 | Kismet — `BananaStand` WEP network detected | Screenshot | WEP encryption flagged as critical vulnerability |
| 11 | Probe request capture — `youcantseeme` | Screenshot | PNL leakage from client probing hidden network |
| 12-21 | Additional GHostAPd config screens, channel analysis, signal measurements | Screenshots | Progressive hardening documentation |

### Lab 3 Evidence (13+ items in PDF)

| # | Evidence Description | Type | Key Finding |
|---|---|---|---|
| 1 | Signal-level heatmap — NETGEAR01-5G | Heatmap | -40 to -60 dBm center, sharp falloff at edges |
| 2 | Signal-level heatmap — NETGEAR01 (2.4 GHz) | Heatmap | Broader coverage, more interference |
| 3 | SIR heatmap — primary coverage area | Heatmap | GM right side +13 dB; left side +3-5 dB |
| 4 | Frequency band comparison — 2.4 GHz vs 5 GHz | Heatmap | 5 GHz cleaner spectrum, tighter coverage |
| 5 | Dead zone — AFSIWPA at -88 dBm | Screenshot | BSSID 04:18:D6:B4:1C:70 below usable threshold |
| 6 | Dead zone — AFSISupport2G at -85 dBm | Screenshot | BSSID 84:78:AC:A1:B2:C3 |
| 7 | Dead zone — AFSISupport2G at -90 dBm | Screenshot | BSSID A0:21:B7:12:34:56 |
| 8 | Dead zone — AFSI-WPA at -93 dBm | Screenshot | BSSID 2C:30:33:11:22:33, worst signal |
| 9 | PHY mode identification — 802.11n vs 802.11ac | Screenshot | NETGEAR01 = n, NETGEAR01-5G = ac |
| 10-13 | Additional sample point measurements, DIRECT- SSID interference | Screenshots | Miracast/Wi-Fi Direct sources identified |

### Lab 5 Evidence (10+ items in PDF)

| # | Evidence Description | Type | Key Finding |
|---|---|---|---|
| 1 | Wireshark TTL analysis — target 172.30.0.4 | Capture | TTL=64 indicating Linux/Android OS |
| 2 | p0f passive fingerprint result | Output | "Linux 2.6.x or newer" — Android 9.x confirmed |
| 3 | Nmap `-O -v` active scan result | Output | OS fingerprint with accuracy percentage |
| 4 | Nmap scan traffic in Wireshark | Capture | SYN/SYNACK probe flood visible (noisy) |
| 5 | ClientJS fingerprint — Chrome on Android | Output | Browser datapoints captured |
| 6 | ClientJS fingerprint — Firefox on Android | Output | Different datapoints despite same device |
| 7 | User-Agent string — Chrome/Android 9 | Output | `Mobile Safari/537.36 · Chrome/[v]` |
| 8 | User-Agent string — Firefox/Android 9 | Output | `Gecko/[v] · Firefox/[v]` |
| 9 | User-Agent string — Edge/Windows | Output | Dual `Chrome/` + `Edg/` Chromium tokens |
| 10 | Cover Your Tracks — cookie analysis | Screenshot | Browser tracking protection assessment |

### Capstone Evidence

| # | Evidence Description | Type | Key Finding |
|---|---|---|---|
| 1 | Bluegreen Media case study report (Parts 1-3) | PDF (759 lines) | 3 WLAN + 3 mobile threats, 5-phase vuln methodology, BYOD framework |
| 2 | Cyber Kill Chain quiz completion | PDF (2 pages) | Part 1 + Part 2 quizzes completed 2025-01-26 |
| 3 | Final presentation (10 slides) | PDF | Executive summary → Recommendations → Timeline |
| 4 | Network topology diagram | Mermaid (in MD) | 10 APs, WLAN controller, 4 VLANs, remote reps |
| 5 | Combined implementation Gantt | Mermaid (in MD) | NAC + MDM + WIPS overlapping 16-20 week rollout |
| 6 | Risk heat map (5×5) | Table (in MD) | 12 threats plotted by likelihood × impact |

---

*Ross Moravec | Mobile Wireless Security Portfolio*
