#!/usr/bin/env bash
# nmap_wireless_scan.sh — Wireless device discovery and OS fingerprinting wrapper
#
# Three-phase scan: host discovery → OS fingerprinting → wireless service detection.
# Designed for authorized wireless security assessments in lab environments.
#
# Requires: nmap, root/sudo privileges
# Safety: Only run against networks you own or have explicit written authorization to test.

set -euo pipefail

# ─── Defaults ────────────────────────────────────────────────────────────────
DEFAULT_PORTS="80,443,161,5353,8080,8443,8888,53,67,68,1900"
SCAN_TIMEOUT=600  # seconds per scan phase
OUTPUT_DIR="./scan_results"
LOGFILE=""
PORTS=""
TARGET=""

# ─── Functions ───────────────────────────────────────────────────────────────

usage() {
  cat <<EOF
Usage: sudo $(basename "$0") [OPTIONS] <target-subnet>

Wireless device discovery and OS fingerprinting wrapper for Nmap.
Runs a three-phase scan: host discovery, OS fingerprinting, and
wireless-relevant service detection.

Arguments:
  <target-subnet>   Target in CIDR notation (e.g., 192.168.1.0/24)
                    or single host (e.g., 192.168.1.1)

Options:
  -h, --help        Show this help message and exit
  -p, --ports PORTS Comma-separated port list for service detection
                    (default: ${DEFAULT_PORTS})
  -o, --output DIR  Output directory for results (default: ./scan_results)
  -t, --timeout SEC Timeout in seconds per scan phase (default: 600)

Examples:
  sudo ./$(basename "$0") 192.168.1.0/24
  sudo ./$(basename "$0") -p 80,443,8080 10.0.0.0/16
  sudo ./$(basename "$0") -o /home/user/scans -t 300 172.16.0.0/24

Safety:
  This tool generates active network traffic. Only use against networks
  you own or have explicit written authorization to test. Scans may
  trigger IDS/IPS alerts.

EOF
  exit 0
}

log() {
  local msg
  msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$msg"
  if [[ -n "$LOGFILE" ]]; then
    echo "$msg" >> "$LOGFILE"
  fi
}

error_exit() {
  log "ERROR: $*" >&2
  exit 1
}

validate_cidr() {
  local target="$1"
  # Accept single IP (x.x.x.x) or CIDR (x.x.x.x/N)
  local ip_re='^([0-9]{1,3}\.){3}[0-9]{1,3}(/[0-9]{1,2})?$'
  if [[ ! "$target" =~ $ip_re ]]; then
    error_exit "Invalid target format: '$target'. Expected CIDR notation (e.g., 192.168.1.0/24) or single IP."
  fi
  # Validate each octet is 0-255
  local ip_part="${target%%/*}"
  IFS='.' read -ra octets <<< "$ip_part"
  for octet in "${octets[@]}"; do
    if (( octet < 0 || octet > 255 )); then
      error_exit "Invalid IP octet '$octet' in target '$target'. Each octet must be 0-255."
    fi
  done
  # Validate CIDR prefix if present
  if [[ "$target" == *"/"* ]]; then
    local prefix="${target##*/}"
    if (( prefix < 0 || prefix > 32 )); then
      error_exit "Invalid CIDR prefix '/$prefix'. Must be between /0 and /32."
    fi
  fi
}

validate_ports() {
  local ports="$1"
  local port_re='^[0-9]+(,[0-9]+)*$'
  if [[ ! "$ports" =~ $port_re ]]; then
    error_exit "Invalid port list: '$ports'. Use comma-separated numbers (e.g., 80,443,8080)."
  fi
  IFS=',' read -ra port_arr <<< "$ports"
  for p in "${port_arr[@]}"; do
    if (( p < 1 || p > 65535 )); then
      error_exit "Invalid port number '$p'. Must be between 1 and 65535."
    fi
  done
}

check_prerequisites() {
  if ! command -v nmap &>/dev/null; then
    error_exit "nmap is not installed or not in PATH. Install with: apt install nmap"
  fi
  if [[ $EUID -ne 0 ]]; then
    error_exit "This script requires root privileges. Run with: sudo $(basename "$0") ..."
  fi
}

run_with_timeout() {
  local description="$1"
  shift
  log "  Running: $*"
  if timeout "$SCAN_TIMEOUT" "$@"; then
    return 0
  else
    local rc=$?
    if [[ $rc -eq 124 ]]; then
      log "  WARNING: $description timed out after ${SCAN_TIMEOUT}s — partial results may be available."
      return 0  # Continue with partial results
    else
      log "  WARNING: $description exited with code $rc."
      return $rc
    fi
  fi
}

print_summary() {
  local discovery_file="$1"
  local fingerprint_file="$2"
  local services_file="$3"

  log ""
  log "╔══════════════════════════════════════════════════════════════╗"
  log "║                     SCAN SUMMARY                           ║"
  log "╚══════════════════════════════════════════════════════════════╝"
  log ""
  log "Target:       $TARGET"
  log "Ports:        $PORTS"
  log "Timestamp:    $TIMESTAMP"
  log "Output Dir:   $OUTPUT_DIR"
  log ""

  # Host count
  local live_hosts=0
  if [[ -f "$discovery_file" ]]; then
    live_hosts=$(grep -c "Host is up" "$discovery_file" 2>/dev/null || echo 0)
  fi
  log "Live Hosts Discovered:  $live_hosts"

  # OS detection results
  if [[ -f "$fingerprint_file" ]]; then
    local os_count
    os_count=$(grep -c "OS details\|Running:" "$fingerprint_file" 2>/dev/null || echo 0)
    log "OS Fingerprints Found:  $os_count"

    local open_port_count
    open_port_count=$(grep -c "open" "$fingerprint_file" 2>/dev/null || echo 0)
    log "Open Port Entries:      $open_port_count"
  fi

  # Service detection
  if [[ -f "$services_file" ]]; then
    local service_count
    service_count=$(grep -c "open" "$services_file" 2>/dev/null || echo 0)
    log "Wireless Services:      $service_count"
  fi

  log ""
  log "Generated Files:"
  if ls "$OUTPUT_DIR/"*"${TIMESTAMP}"* &>/dev/null; then
    ls -lh "$OUTPUT_DIR/"*"${TIMESTAMP}"* 2>/dev/null | while read -r line; do
      log "  $line"
    done
  else
    log "  (no output files found)"
  fi
  log ""
  log "Log file: $LOGFILE"
}

# ─── Argument Parsing ────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      ;;
    -p|--ports)
      [[ -z "${2:-}" ]] && error_exit "Option $1 requires a port list argument."
      PORTS="$2"
      shift 2
      ;;
    -o|--output)
      [[ -z "${2:-}" ]] && error_exit "Option $1 requires a directory argument."
      OUTPUT_DIR="$2"
      shift 2
      ;;
    -t|--timeout)
      [[ -z "${2:-}" ]] && error_exit "Option $1 requires a numeric argument."
      SCAN_TIMEOUT="$2"
      shift 2
      ;;
    -*)
      error_exit "Unknown option: $1. Use -h for help."
      ;;
    *)
      if [[ -n "$TARGET" ]]; then
        error_exit "Multiple targets specified. Only one target subnet is supported."
      fi
      TARGET="$1"
      shift
      ;;
  esac
done

# ─── Validation ──────────────────────────────────────────────────────────────

if [[ -z "$TARGET" ]]; then
  echo "Error: No target specified." >&2
  echo "Usage: sudo $(basename "$0") [OPTIONS] <target-subnet>" >&2
  echo "Try '$(basename "$0") -h' for more information." >&2
  exit 1
fi

PORTS="${PORTS:-$DEFAULT_PORTS}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOGFILE="${OUTPUT_DIR}/scan_log_${TIMESTAMP}.log"

validate_cidr "$TARGET"
validate_ports "$PORTS"
check_prerequisites

mkdir -p "$OUTPUT_DIR"
touch "$LOGFILE"

# ─── Main Scan ───────────────────────────────────────────────────────────────

log "=== Wireless Network Device Scan ==="
log "Target: $TARGET"
log "Ports:  $PORTS"
log "Timeout per phase: ${SCAN_TIMEOUT}s"
log ""

# Phase 1: Host discovery (ping sweep)
DISCOVERY_FILE="$OUTPUT_DIR/discovery_${TIMESTAMP}.txt"
log "[1/3] Host discovery (ping sweep)..."
if run_with_timeout "Host discovery" \
    nmap -sn "$TARGET" -oN "$DISCOVERY_FILE" 2>/dev/null; then
  HOSTS=$(grep -c "Host is up" "$DISCOVERY_FILE" 2>/dev/null || echo 0)
  log "  Found $HOSTS live hosts"
else
  log "  Host discovery failed — continuing with direct scan."
fi

# Phase 2: OS fingerprinting on discovered hosts
FINGERPRINT_FILE="$OUTPUT_DIR/fingerprint_${TIMESTAMP}.txt"
FINGERPRINT_XML="$OUTPUT_DIR/fingerprint_${TIMESTAMP}.xml"
log "[2/3] OS fingerprinting (TCP SYN + version detection)..."
if run_with_timeout "OS fingerprinting" \
    nmap -sS -sV -O --osscan-guess "$TARGET" \
      -oN "$FINGERPRINT_FILE" \
      -oX "$FINGERPRINT_XML" 2>/dev/null; then
  log "  Results saved to $FINGERPRINT_FILE"
  log "  XML output: $FINGERPRINT_XML"
else
  log "  OS fingerprinting encountered errors — check partial results."
fi

# Phase 3: Wireless-relevant service detection
SERVICES_FILE="$OUTPUT_DIR/services_${TIMESTAMP}.txt"
log "[3/3] Wireless service detection on ports: $PORTS"
if run_with_timeout "Service detection" \
    nmap -sS -p "$PORTS" -sV "$TARGET" \
      -oN "$SERVICES_FILE" 2>/dev/null; then
  log "  Results saved to $SERVICES_FILE"
else
  log "  Service detection encountered errors — check partial results."
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

print_summary "$DISCOVERY_FILE" "$FINGERPRINT_FILE" "$SERVICES_FILE"

log "=== Scan Complete ==="
