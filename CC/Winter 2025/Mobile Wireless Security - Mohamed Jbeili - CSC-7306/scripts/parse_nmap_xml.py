#!/usr/bin/env python3
"""
parse_nmap_xml.py — Parse Nmap XML output and generate structured security reports.

Reads Nmap XML output files (generated with nmap -oX) and extracts host
information, OS fingerprints, open ports, running services, and potential
wireless/IoT devices identified by vendor OUI or service type.

Part of the CSC-7306 Mobile Wireless Security portfolio.

Usage:
    python parse_nmap_xml.py scan_results.xml
    python parse_nmap_xml.py scan_results.xml -o report.md --format markdown
    python parse_nmap_xml.py scan_results.xml --wireless-only
    python parse_nmap_xml.py scan_results.xml -o report.txt --format text

Example with nmap:
    sudo nmap -sS -sV -O --osscan-guess 192.168.1.0/24 -oX scan.xml
    python parse_nmap_xml.py scan.xml -o wireless_report.md --format markdown

Requirements:
    Python 3.7+ (standard library only — uses xml.etree.ElementTree)

Safety:
    This script only reads and parses files. It does not generate network
    traffic or interact with any remote systems.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

# Known wireless/IoT device vendor OUI prefixes (first 3 octets of MAC).
# This is a representative subset for educational purposes.
WIRELESS_VENDOR_OUIS = {
    "00:14:6C": "Netgear",
    "00:1A:2B": "Ayecom Technology",
    "00:1E:58": "D-Link",
    "00:22:6B": "Cisco-Linksys",
    "00:24:01": "D-Link",
    "00:26:F2": "Netgear",
    "00:50:F2": "Microsoft (Xbox/Surface)",
    "08:86:3B": "Belkin",
    "10:0D:7F": "Netgear",
    "10:DA:43": "Netgear",
    "14:59:C0": "Netgear",
    "18:E8:29": "Ubiquiti",
    "20:A6:CD": "TP-Link",
    "24:A4:3C": "Ubiquiti",
    "28:80:88": "Edimax",
    "2C:B0:5D": "Netgear",
    "30:B5:C2": "TP-Link",
    "34:97:F6": "Ubiquiti (ASUSTeK)",
    "38:2C:4A": "ASUSTek",
    "3C:37:86": "Netgear",
    "44:94:FC": "Ubiquiti",
    "50:6A:03": "Netgear",
    "58:EF:68": "Belkin",
    "60:38:E0": "Belkin",
    "6C:72:20": "D-Link",
    "70:4F:57": "TP-Link",
    "74:DA:38": "Edimax",
    "78:8A:20": "Ubiquiti",
    "80:2A:A8": "Ubiquiti",
    "84:D8:1B": "TP-Link",
    "90:72:40": "Apple (AirPort)",
    "94:10:3E": "Belkin",
    "A0:63:91": "Netgear",
    "A4:2B:B0": "TP-Link",
    "AC:84:C6": "TP-Link",
    "B0:4E:26": "TP-Link",
    "B4:75:0E": "Belkin",
    "B8:27:EB": "Raspberry Pi",
    "C0:25:E9": "TP-Link",
    "C0:56:27": "Belkin",
    "C4:E9:84": "TP-Link",
    "CC:40:D0": "Netgear",
    "D8:3A:DD": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "E4:F0:42": "Google (Nest/Chromecast)",
    "E8:48:B8": "Samsung (SmartThings)",
    "F0:9F:C2": "Ubiquiti",
    "F4:EC:38": "Espressif (ESP8266/ESP32 IoT)",
    "FC:EC:DA": "Ubiquiti",
}

# Service names that typically indicate wireless infrastructure or IoT devices.
WIRELESS_SERVICE_KEYWORDS = [
    "http-proxy", "upnp", "mdns", "ssdp", "snmp", "telnet",
    "mikrotik", "routeros", "dd-wrt", "openwrt", "aircontrol",
    "unifi", "captive", "hotspot", "radius", "hostapd",
    "bonjour", "avahi", "mqtt", "coap", "zigbee",
]


def parse_nmap_xml(filepath):
    """Parse an Nmap XML file and return structured host data.

    Args:
        filepath: Path to the Nmap XML output file.

    Returns:
        dict with keys:
            - scan_info: metadata about the scan
            - hosts: list of parsed host dicts
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        tree = ET.parse(filepath)
    except ET.ParseError as exc:
        raise ValueError(f"Failed to parse XML: {exc}") from exc

    root = tree.getroot()
    if root.tag != "nmaprun":
        raise ValueError(
            f"Not a valid Nmap XML file (root element is '{root.tag}', expected 'nmaprun')."
        )

    scan_info = {
        "scanner": root.get("scanner", "nmap"),
        "args": root.get("args", ""),
        "start_time": root.get("startstr", ""),
        "version": root.get("version", ""),
    }

    # Extract run stats if available
    runstats = root.find("runstats")
    if runstats is not None:
        finished = runstats.find("finished")
        if finished is not None:
            scan_info["end_time"] = finished.get("timestr", "")
            scan_info["elapsed"] = finished.get("elapsed", "")
        hosts_elem = runstats.find("hosts")
        if hosts_elem is not None:
            scan_info["hosts_up"] = int(hosts_elem.get("up", 0))
            scan_info["hosts_down"] = int(hosts_elem.get("down", 0))
            scan_info["hosts_total"] = int(hosts_elem.get("total", 0))

    hosts = []
    for host_elem in root.findall("host"):
        host = _parse_host(host_elem)
        if host:
            hosts.append(host)

    return {"scan_info": scan_info, "hosts": hosts}


def _parse_host(host_elem):
    """Parse a single <host> element into a structured dict."""
    status_elem = host_elem.find("status")
    if status_elem is None or status_elem.get("state") != "up":
        return None

    host = {
        "ip": "",
        "mac": "",
        "vendor": "",
        "hostnames": [],
        "os_matches": [],
        "ports": [],
        "is_wireless_candidate": False,
        "wireless_indicators": [],
    }

    # Addresses
    for addr in host_elem.findall("address"):
        if addr.get("addrtype") == "ipv4":
            host["ip"] = addr.get("addr", "")
        elif addr.get("addrtype") == "mac":
            host["mac"] = addr.get("addr", "")
            host["vendor"] = addr.get("vendor", "")

    # Hostnames
    hostnames_elem = host_elem.find("hostnames")
    if hostnames_elem is not None:
        for hn in hostnames_elem.findall("hostname"):
            host["hostnames"].append(hn.get("name", ""))

    # OS matches
    os_elem = host_elem.find("os")
    if os_elem is not None:
        for osmatch in os_elem.findall("osmatch"):
            match = {
                "name": osmatch.get("name", ""),
                "accuracy": osmatch.get("accuracy", ""),
            }
            classes = []
            for osclass in osmatch.findall("osclass"):
                classes.append({
                    "type": osclass.get("type", ""),
                    "vendor": osclass.get("vendor", ""),
                    "osfamily": osclass.get("osfamily", ""),
                    "osgen": osclass.get("osgen", ""),
                })
            match["classes"] = classes
            host["os_matches"].append(match)

    # Ports and services
    ports_elem = host_elem.find("ports")
    if ports_elem is not None:
        for port_elem in ports_elem.findall("port"):
            state = port_elem.find("state")
            if state is None:
                continue
            service = port_elem.find("service")
            port = {
                "portid": port_elem.get("portid", ""),
                "protocol": port_elem.get("protocol", ""),
                "state": state.get("state", ""),
                "service_name": service.get("name", "") if service is not None else "",
                "product": service.get("product", "") if service is not None else "",
                "version": service.get("version", "") if service is not None else "",
                "extrainfo": service.get("extrainfo", "") if service is not None else "",
            }
            host["ports"].append(port)

    # Wireless device identification
    _identify_wireless(host)

    return host


def _identify_wireless(host):
    """Flag a host as a potential wireless device based on OUI and services."""
    indicators = []

    # Check MAC vendor OUI
    mac = host.get("mac", "").upper()
    if mac:
        oui = mac[:8]
        if oui in WIRELESS_VENDOR_OUIS:
            indicators.append(f"Vendor OUI match: {WIRELESS_VENDOR_OUIS[oui]} ({oui})")

    # Check vendor string
    vendor = host.get("vendor", "").lower()
    wireless_vendors = [
        "netgear", "tp-link", "ubiquiti", "belkin", "d-link", "linksys",
        "asus", "edimax", "mikrotik", "raspberry", "espressif", "aruba",
        "ruckus", "meraki", "fortinet", "sonicwall", "zyxel", "apple",
    ]
    for wv in wireless_vendors:
        if wv in vendor:
            indicators.append(f"Vendor name match: {host['vendor']}")
            break

    # Check service names
    for port in host.get("ports", []):
        svc = port.get("service_name", "").lower()
        product = port.get("product", "").lower()
        combined = f"{svc} {product}"
        for keyword in WIRELESS_SERVICE_KEYWORDS:
            if keyword in combined:
                indicators.append(
                    f"Service match: {port['portid']}/{port['protocol']} "
                    f"— {port['service_name']} {port['product']}".strip()
                )
                break

    # Check OS matches for wireless/embedded indicators
    for osmatch in host.get("os_matches", []):
        os_name = osmatch.get("name", "").lower()
        wireless_os_keywords = [
            "openwrt", "dd-wrt", "routeros", "vxworks", "embedded",
            "wireless", "access point", "freertos", "android", "ios",
        ]
        for keyword in wireless_os_keywords:
            if keyword in os_name:
                indicators.append(f"OS match: {osmatch['name']}")
                break

    host["wireless_indicators"] = indicators
    host["is_wireless_candidate"] = len(indicators) > 0


def format_text_report(data):
    """Format parsed scan data as a plain-text report."""
    lines = []
    info = data["scan_info"]
    hosts = data["hosts"]

    lines.append("=" * 70)
    lines.append("NMAP SCAN REPORT — WIRELESS DEVICE ANALYSIS")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Scanner:    {info.get('scanner', 'nmap')} {info.get('version', '')}")
    lines.append(f"Command:    {info.get('args', 'N/A')}")
    lines.append(f"Start:      {info.get('start_time', 'N/A')}")
    lines.append(f"End:        {info.get('end_time', 'N/A')}")
    lines.append(f"Elapsed:    {info.get('elapsed', 'N/A')}s")
    lines.append(f"Hosts Up:   {info.get('hosts_up', 'N/A')}")
    lines.append(f"Hosts Down: {info.get('hosts_down', 'N/A')}")
    lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary statistics
    total = len(hosts)
    wireless_count = sum(1 for h in hosts if h["is_wireless_candidate"])
    total_open_ports = sum(
        len([p for p in h["ports"] if p["state"] == "open"]) for h in hosts
    )
    lines.append("-" * 70)
    lines.append("SUMMARY")
    lines.append("-" * 70)
    lines.append(f"Total live hosts:              {total}")
    lines.append(f"Potential wireless/IoT devices: {wireless_count}")
    lines.append(f"Total open ports:              {total_open_ports}")
    lines.append("")

    # Wireless candidates
    if wireless_count > 0:
        lines.append("-" * 70)
        lines.append("WIRELESS / IoT DEVICE CANDIDATES")
        lines.append("-" * 70)
        for host in hosts:
            if host["is_wireless_candidate"]:
                lines.append(f"\n  Host: {host['ip']}")
                if host["mac"]:
                    lines.append(f"  MAC:  {host['mac']} ({host['vendor']})")
                for ind in host["wireless_indicators"]:
                    lines.append(f"    → {ind}")
        lines.append("")

    # Per-host detail
    lines.append("-" * 70)
    lines.append("HOST DETAILS")
    lines.append("-" * 70)
    for host in hosts:
        lines.append("")
        header = f"  {host['ip']}"
        if host["mac"]:
            header += f"  (MAC: {host['mac']}"
            if host["vendor"]:
                header += f" — {host['vendor']}"
            header += ")"
        lines.append(header)

        if host["hostnames"]:
            lines.append(f"  Hostnames: {', '.join(host['hostnames'])}")

        if host["os_matches"]:
            best = host["os_matches"][0]
            lines.append(f"  OS Best Guess: {best['name']} ({best['accuracy']}% confidence)")

        open_ports = [p for p in host["ports"] if p["state"] == "open"]
        if open_ports:
            lines.append(f"  Open Ports ({len(open_ports)}):")
            for p in open_ports:
                svc = p["service_name"]
                detail = " ".join(
                    filter(None, [p["product"], p["version"], p["extrainfo"]])
                )
                lines.append(f"    {p['portid']}/{p['protocol']:4s} {svc:20s} {detail}")
        else:
            lines.append("  Open Ports: none")

    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)
    return "\n".join(lines)


def format_markdown_report(data):
    """Format parsed scan data as a Markdown report."""
    lines = []
    info = data["scan_info"]
    hosts = data["hosts"]

    lines.append("# Nmap Scan Report — Wireless Device Analysis")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Scanner | {info.get('scanner', 'nmap')} {info.get('version', '')} |")
    lines.append(f"| Command | `{info.get('args', 'N/A')}` |")
    lines.append(f"| Start Time | {info.get('start_time', 'N/A')} |")
    lines.append(f"| End Time | {info.get('end_time', 'N/A')} |")
    lines.append(f"| Duration | {info.get('elapsed', 'N/A')}s |")
    lines.append(f"| Hosts Up | {info.get('hosts_up', 'N/A')} |")
    lines.append(f"| Report Generated | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    lines.append("")

    total = len(hosts)
    wireless_count = sum(1 for h in hosts if h["is_wireless_candidate"])
    total_open_ports = sum(
        len([p for p in h["ports"] if p["state"] == "open"]) for h in hosts
    )

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total live hosts:** {total}")
    lines.append(f"- **Potential wireless/IoT devices:** {wireless_count}")
    lines.append(f"- **Total open ports:** {total_open_ports}")
    lines.append("")

    # Wireless candidates
    if wireless_count > 0:
        lines.append("## Wireless / IoT Device Candidates")
        lines.append("")
        lines.append("| IP Address | MAC | Vendor | Indicators |")
        lines.append("|------------|-----|--------|------------|")
        for host in hosts:
            if host["is_wireless_candidate"]:
                indicators = "; ".join(host["wireless_indicators"])
                lines.append(
                    f"| {host['ip']} | {host['mac']} | {host['vendor']} | {indicators} |"
                )
        lines.append("")

    # Per-host detail
    lines.append("## Host Details")
    lines.append("")
    for host in hosts:
        wireless_tag = " 📡" if host["is_wireless_candidate"] else ""
        lines.append(f"### {host['ip']}{wireless_tag}")
        lines.append("")

        if host["mac"]:
            lines.append(f"- **MAC:** {host['mac']} ({host['vendor']})")
        if host["hostnames"]:
            lines.append(f"- **Hostnames:** {', '.join(host['hostnames'])}")
        if host["os_matches"]:
            best = host["os_matches"][0]
            lines.append(f"- **OS:** {best['name']} ({best['accuracy']}% confidence)")
        lines.append("")

        open_ports = [p for p in host["ports"] if p["state"] == "open"]
        if open_ports:
            lines.append("| Port | Protocol | Service | Product | Version |")
            lines.append("|------|----------|---------|---------|---------|")
            for p in open_ports:
                lines.append(
                    f"| {p['portid']} | {p['protocol']} | {p['service_name']} "
                    f"| {p['product']} | {p['version']} |"
                )
            lines.append("")
        else:
            lines.append("_No open ports detected._")
            lines.append("")

    lines.append("---")
    lines.append("*Generated by parse_nmap_xml.py — CSC-7306 Mobile Wireless Security*")
    return "\n".join(lines)


def main():
    """Entry point: parse arguments, process XML, and write report."""
    parser = argparse.ArgumentParser(
        description="Parse Nmap XML output and generate wireless device analysis reports.",
        epilog=(
            "Examples:\n"
            "  python parse_nmap_xml.py scan.xml\n"
            "  python parse_nmap_xml.py scan.xml -o report.md --format markdown\n"
            "  python parse_nmap_xml.py scan.xml --wireless-only\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "xmlfile",
        help="Path to Nmap XML output file (generated with nmap -oX).",
    )
    parser.add_argument(
        "-o", "--output",
        help="Write report to file instead of stdout.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Report format: text (default) or markdown.",
    )
    parser.add_argument(
        "--wireless-only",
        action="store_true",
        help="Only include hosts identified as potential wireless/IoT devices.",
    )

    args = parser.parse_args()

    try:
        data = parse_nmap_xml(args.xmlfile)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.wireless_only:
        data["hosts"] = [h for h in data["hosts"] if h["is_wireless_candidate"]]

    if args.format == "markdown":
        report = format_markdown_report(data)
    else:
        report = format_text_report(data)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(report)
            print(f"Report written to {args.output}")
        except OSError as exc:
            print(f"Error writing report: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(report)


if __name__ == "__main__":
    main()
