#!/usr/bin/env bash
# nmap_wireless_scan.sh — Wireless device discovery and OS fingerprinting wrapper
# Usage: sudo ./nmap_wireless_scan.sh <target-subnet>
# Example: sudo ./nmap_wireless_scan.sh 192.168.1.0/24
#
# Requires: nmap, root/sudo privileges
# Safety: Only run against networks you own or have explicit written authorization to test.

set -euo pipefail

TARGET="${1:?Usage: $0 <target-subnet>}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./scan_results"
mkdir -p "$OUTPUT_DIR"

echo "=== Wireless Network Device Scan ==="
echo "Target: $TARGET"
echo "Timestamp: $TIMESTAMP"
echo ""

# Phase 1: Host discovery (ping sweep)
echo "[1/3] Host discovery..."
nmap -sn "$TARGET" -oN "$OUTPUT_DIR/discovery_${TIMESTAMP}.txt" 2>/dev/null
HOSTS=$(grep -c "Host is up" "$OUTPUT_DIR/discovery_${TIMESTAMP}.txt" || echo 0)
echo "  Found $HOSTS live hosts"

# Phase 2: OS fingerprinting on discovered hosts
echo "[2/3] OS fingerprinting (passive-safe: TCP SYN + version detection)..."
nmap -sS -sV -O --osscan-guess "$TARGET" \
  -oN "$OUTPUT_DIR/fingerprint_${TIMESTAMP}.txt" \
  -oX "$OUTPUT_DIR/fingerprint_${TIMESTAMP}.xml" 2>/dev/null
echo "  Results saved to $OUTPUT_DIR/fingerprint_${TIMESTAMP}.txt"

# Phase 3: Wireless-relevant service detection
echo "[3/3] Wireless service detection (HTTP admin panels, SNMP, mDNS)..."
nmap -sS -p 80,443,161,5353,8080,8443 -sV "$TARGET" \
  -oN "$OUTPUT_DIR/services_${TIMESTAMP}.txt" 2>/dev/null
echo "  Results saved to $OUTPUT_DIR/services_${TIMESTAMP}.txt"

echo ""
echo "=== Scan Complete ==="
echo "Results directory: $OUTPUT_DIR/"
echo "Files generated:"
ls -la "$OUTPUT_DIR/"*"${TIMESTAMP}"* 2>/dev/null
