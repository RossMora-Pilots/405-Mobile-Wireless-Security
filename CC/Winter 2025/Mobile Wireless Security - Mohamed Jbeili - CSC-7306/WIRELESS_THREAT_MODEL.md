---
title: Wireless & Mobile Threat Model
description: Threat taxonomy for WLAN and mobile attack surfaces, with STRIDE classification, MITRE ATT&CK Mobile mapping, and mitigation controls.
permalink: /threats/
---

# Wireless & Mobile Threat Model

> Threat taxonomy covering the top 6 WLAN threats and top 6 mobile threats, with STRIDE categorization, MITRE ATT&CK Mobile mapping, and concrete mitigation controls.

## Table of Contents

- [Modeling Approach](#modeling-approach)
- [WLAN Threat Catalog](#wlan-threat-catalog)
- [Mobile Threat Catalog](#mobile-threat-catalog)
- [STRIDE Summary](#stride-summary)
- [Attack Surface Diagram](#attack-surface-diagram)
- [References](#references)

## Modeling Approach

Threats are classified using **STRIDE** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) and mapped to **MITRE ATT&CK Mobile Matrix** tactics and techniques where applicable. Each threat entry documents:

- **Attack vector** — the technical mechanism
- **Attacker motivation** — what the attacker gains
- **Impact severity** — business consequence
- **STRIDE category** — the security property violated
- **Mitigation stack** — layered controls that break the attack

## WLAN Threat Catalog

### 1. Wardriving / RF Reconnaissance

| Attribute | Detail |
|---|---|
| Attack vector | Drive/walk with Wi-Fi scanner, capture SSIDs/BSSIDs/encryption types/signals |
| Motivation | Target identification, Preferred Network List (PNL) harvesting |
| Impact | Low direct; enables subsequent phases (evil twin, KRACK, etc.) |
| STRIDE | Information Disclosure |
| MITRE ATT&CK | TA0043 Reconnaissance |
| Mitigations | Transmit power tuning · WIPS detection · Honeypot SSIDs · Reduced SSID broadcast zones |

### 2. Rogue Access Point

| Attribute | Detail |
|---|---|
| Attack vector | Unauthorized AP connected to corp network (external attacker, shadow-IT, malicious insider) |
| Motivation | Establish backdoor bypassing perimeter defenses |
| Impact | Critical — full internal network exposure |
| STRIDE | Elevation of Privilege, Tampering |
| MITRE ATT&CK | T1200 (Hardware Additions) |
| Mitigations | WIPS with automated containment · 802.1X port-based NAC · Physical security · Regular wireless sweeps |

### 3. Evil Twin AP

| Attribute | Detail |
|---|---|
| Attack vector | Spoof legitimate SSID with stronger signal to attract client associations |
| Motivation | Credential capture via captive portal, MITM interception |
| Impact | High — credential theft, session hijacking, data capture |
| STRIDE | Spoofing, Information Disclosure |
| MITRE ATT&CK | T1557 Adversary-in-the-Middle |
| Mitigations | WPA2/WPA3-Enterprise with server certificate validation · WIPS evil twin detection · Client-side AP certificate pinning · User training on network validation |

### 4. KRACK (Key Reinstallation Attack)

| Attribute | Detail |
|---|---|
| Attack vector | Replay WPA2 4-way handshake messages to force nonce reuse |
| Motivation | Decrypt encrypted wireless traffic without knowing the passphrase |
| Impact | High — encrypted traffic decryption, packet injection |
| STRIDE | Information Disclosure, Tampering |
| MITRE ATT&CK | T1040 Network Sniffing |
| Mitigations | AP + client firmware patches · Migrate to WPA3-SAE · Use VPN as defense-in-depth |

### 5. Dragonblood (WPA3 Vulnerabilities)

| Attribute | Detail |
|---|---|
| Attack vector | Timing side-channel attacks on WPA3-SAE password element derivation |
| Motivation | Recover WPA3 passphrase via offline brute force |
| Impact | High — passphrase recovery |
| STRIDE | Information Disclosure, Elevation of Privilege |
| MITRE ATT&CK | T1110 Brute Force |
| Mitigations | Firmware updates implementing H2E (Hash-to-Element) · Strong passphrase length · Disable vulnerable groups (MODP 22/23/24) |

### 6. Deauthentication / DoS

| Attribute | Detail |
|---|---|
| Attack vector | Forge 802.11 deauth frames to disconnect legitimate clients |
| Motivation | Disrupt connectivity, force reconnect to evil twin, degrade availability |
| Impact | Medium — service disruption, reconnection attacks |
| STRIDE | Denial of Service |
| MITRE ATT&CK | T1498 Network Denial of Service |
| Mitigations | 802.11w Protected Management Frames (PMF) · WIPS deauth detection · Redundant AP coverage |

## Mobile Threat Catalog

### 1. Malicious Applications (Trojanized Apps / Spyware)

| Attribute | Detail |
|---|---|
| Attack vector | Sideloaded trojanized app, modified legitimate app, enterprise spyware |
| Motivation | Data theft, credential capture, device surveillance, corporate espionage |
| Impact | Critical — persistent device compromise |
| STRIDE | Spoofing, Tampering, Information Disclosure, Elevation of Privilege |
| MITRE ATT&CK Mobile | T1660 Phishing (delivery) · T1407 Download New Code at Runtime (persistence) — *replaces deprecated T1476* |
| Mitigations | MDM app whitelisting · App store validation · Mobile Threat Defense (MTD) · App containerization · Jailbreak/root detection |

### 2. Smishing / Vishing / QR Phishing

| Attribute | Detail |
|---|---|
| Attack vector | SMS, voice call, or QR code delivering phishing link |
| Motivation | Credential theft, malware delivery, social engineering |
| Impact | High — account compromise, corporate access |
| STRIDE | Spoofing, Information Disclosure |
| MITRE ATT&CK Mobile | T1660 Phishing |
| Mitigations | MTD URL filtering · MFA on all corporate accounts · User awareness training · SMS filtering policies |

### 3. Insecure Cloud Sync / Shadow IT Data Leakage

| Attribute | Detail |
|---|---|
| Attack vector | Corporate data auto-synced to personal cloud accounts (Google Drive, Dropbox, iCloud) |
| Motivation | Usually unintentional user behavior, occasionally malicious insider |
| Impact | High — uncontrolled data exposure, compliance violations |
| STRIDE | Information Disclosure |
| MITRE ATT&CK Mobile | T1639 Exfiltration Over Alternative Protocol |
| Mitigations | CASB (Cloud Access Security Broker) · MAM with per-app DLP · App containerization · Corporate cloud alternatives |

### 4. Jailbreaking / Rooting

| Attribute | Detail |
|---|---|
| Attack vector | User or malware bypasses OS sandbox to gain root privileges |
| Motivation | Install restricted apps, bypass corporate policies, enable deeper malware |
| Impact | Critical — all OS-level security controls bypassable |
| STRIDE | Elevation of Privilege, Tampering |
| MITRE ATT&CK Mobile | T1404 Exploitation for Privilege Escalation |
| Mitigations | MDM root/jailbreak detection · Automated device quarantine · Certificate-based device identity revocation |

### 5. Unsecured Public Wi-Fi Connection

| Attribute | Detail |
|---|---|
| Attack vector | Device auto-connects to open or familiar-named network in public space |
| Motivation | Attacker MITM via coffee-shop Wi-Fi, airport hotspots |
| Impact | High — credential theft, session hijacking |
| STRIDE | Spoofing, Information Disclosure |
| MITRE ATT&CK Mobile | T1638 Adversary-in-the-Middle |
| Mitigations | MDM always-on VPN · Disable auto-join for open networks · DNS-over-HTTPS enforcement · User awareness |

### 6. Lost / Stolen Device

| Attribute | Detail |
|---|---|
| Attack vector | Physical theft or loss of unlocked/weakly-protected device |
| Motivation | Data theft, account takeover via persistent sessions |
| Impact | Critical (without remote wipe) |
| STRIDE | Information Disclosure, Elevation of Privilege |
| MITRE ATT&CK Mobile | T1420 File and Directory Discovery |
| Mitigations | Mandatory device encryption · Strong lock (PIN + biometric) · Auto-lock timeout · Remote wipe via MDM · Selective wipe for BYOD |

## STRIDE Summary

Count of threats per STRIDE category across the 12 cataloged threats:

| STRIDE Category | RF Perimeter | Protocol Layer | Mobile Device | User Layer | **Total** |
|---|---|---|---|---|---|
| **Spoofing** | Evil Twin · Rogue AP | | | Smishing/Vishing · Unsecured Wi-Fi | **4** |
| **Tampering** | Rogue AP | KRACK | Malicious Apps · Jailbreak/Root | | **4** |
| **Repudiation** | | | | | **0** |
| **Information Disclosure** | Wardriving · Evil Twin | KRACK · Dragonblood | Lost/Stolen Device | Smishing · Unsecured Wi-Fi · Cloud Sync | **7** |
| **Denial of Service** | Deauth/DoS | | | | **1** |
| **Elevation of Privilege** | Rogue AP | Dragonblood | Malicious Apps · Jailbreak/Root | | **4** |

**Observations:**

- **Information Disclosure dominates** (7/12 threats) — wireless and mobile are inherently about data accessibility across trust boundaries
- **No repudiation threats** in this catalog — wireless attacks rarely revolve around deniability
- **Denial of Service appears only once** — deauth attacks are the main availability concern; most wireless threats target confidentiality

### Risk Heat Map (Likelihood × Impact)

Each of the 12 cataloged threats plotted on a 5×5 risk matrix. Likelihood and impact assessed qualitatively based on the Bluegreen Media scenario (60-employee SMB, 10 APs, BYOD, pre-IPO).

| | **Impact: Negligible** | **Impact: Low** | **Impact: Moderate** | **Impact: High** | **Impact: Critical** |
|---|---|---|---|---|---|
| **Likelihood: Almost Certain** | | | | Unsecured Public Wi-Fi | Data Leakage via Cloud Sync |
| **Likelihood: Likely** | | | Deauth/DoS | Smishing/Vishing | Malicious Apps |
| **Likelihood: Possible** | | | | Evil Twin AP · Lost/Stolen Device | Rogue AP · Jailbreak/Root |
| **Likelihood: Unlikely** | | Wardriving (recon only) | | KRACK | |
| **Likelihood: Rare** | | | | Dragonblood | |

**Risk treatment priorities (red = mitigate immediately, orange = mitigate within 90 days):**

- **Critical risk (top-right):** Data Leakage via Cloud Sync, Malicious Apps, Rogue AP, Jailbreak/Root — require immediate MDM + CASB + NAC controls
- **High risk:** Evil Twin, Lost/Stolen Device, Smishing, Unsecured Public Wi-Fi — require WIPS + MDM + user training
- **Medium risk:** Deauth/DoS, KRACK — require PMF + firmware patching
- **Low risk:** Wardriving (recon only), Dragonblood (rare in practice with H2E) — monitor via WIPS

> **Methodology:** Likelihood based on threat actor accessibility and Bluegreen Media's current control posture (pre-remediation). Impact based on potential data exposure, business disruption, and IPO-readiness implications. Assessment follows NIST SP 800-30 qualitative risk analysis guidance.

## Attack Surface Diagram

```mermaid
flowchart TB
    subgraph Perimeter["RF Perimeter"]
        War["Wardriving"]
        Rogue["Rogue AP"]
        Evil["Evil Twin"]
        Deauth["Deauth/DoS"]
    end

    subgraph Protocol["Protocol Layer"]
        KRACK["KRACK"]
        Dragon["Dragonblood"]
    end

    subgraph Device["Mobile Device"]
        Malicious["Malicious Apps"]
        Root["Jailbreak/Root"]
        Lost["Lost/Stolen"]
    end

    subgraph User["User Layer"]
        Smish["Smishing/Vishing/QR"]
        PublicWifi["Unsecured Wi-Fi"]
        Shadow["Cloud Sync Leakage"]
    end

    Perimeter -.->|Enables| Protocol
    Protocol -.->|Enables| Device
    User -.->|Enables| Device
    Device -->|Exfiltrates to| Attacker((Attacker))
```

### Threat-to-Control Flow

How the 12 cataloged threats flow through the three defensive control layers before reaching corporate data:

```mermaid
sankey-beta

Wardriving,WLAN Defense,1
Rogue AP,WLAN Defense,1
Evil Twin,WLAN Defense,1
Deauth DoS,WLAN Defense,1
KRACK,WLAN Defense,1
Dragonblood,WLAN Defense,1
Malicious Apps,Mobile Defense,1
Smishing Vishing,Mobile Defense,1
Cloud Sync Leakage,Mobile Defense,1
Jailbreak Root,Mobile Defense,1
Unsecured Wi-Fi,Mobile Defense,1
Lost Stolen Device,Mobile Defense,1
WLAN Defense,Zero Trust Layer,6
Mobile Defense,Zero Trust Layer,6
Zero Trust Layer,Corporate Data Protected,10
Zero Trust Layer,Residual Risk,2
```

> **Reading the diagram:** Each threat enters its primary control layer (WLAN or Mobile Defense). Both layers feed into the Zero Trust Layer for continuous verification. The majority of threats are neutralized before reaching corporate data; residual risk represents threats that bypass multiple layers (e.g., zero-day + compromised credential + compliant-looking device).

## References

- [MITRE ATT&CK Mobile Matrix](https://attack.mitre.org/matrices/mobile/)
- [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
- [OWASP MASVS](https://mas.owasp.org/MASVS/)
- [Microsoft STRIDE Threat Model](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [KRACK Attacks](https://www.krackattacks.com/)
- [Dragonblood (WPA3)](https://papers.mathyvanhoef.com/dragonblood.pdf)

---

*Ross Moravec | Mobile Wireless Security Portfolio*
