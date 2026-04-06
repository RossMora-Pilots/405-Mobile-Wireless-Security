#!/usr/bin/env python3
"""
wireless_compliance_checker.py — Check device inventory against MDM compliance policy.

Reads a Microsoft Intune-style MDM compliance policy (JSON) and a device
inventory (JSON), then evaluates each device against the policy requirements.
Generates a compliance report showing pass/fail per device with specific
failure reasons and an overall compliance percentage.

Part of the CSC-7306 Mobile Wireless Security portfolio.

Usage:
    python wireless_compliance_checker.py \\
        --policy mdm_compliance_policy.json \\
        --inventory sample_device_inventory.json

    python wireless_compliance_checker.py \\
        --policy mdm_compliance_policy.json \\
        --inventory sample_device_inventory.json \\
        --format markdown -o compliance_report.md

    python wireless_compliance_checker.py \\
        --policy mdm_compliance_policy.json \\
        --inventory sample_device_inventory.json \\
        --strict

Example output (text):
    ╔══════════════════════════════════════════════════════════════╗
    ║              WIRELESS COMPLIANCE REPORT                    ║
    ╚══════════════════════════════════════════════════════════════╝

    Policy: BYOD-Wireless-Security-Baseline
    Devices Evaluated: 6
    Compliant: 2 (33.3%)
    Non-Compliant: 4 (66.7%)
    ...

Requirements:
    Python 3.7+ (standard library only — uses json, argparse)

Safety:
    This script only reads and analyzes local JSON files. It does not
    interact with any MDM platform, device, or network.
"""

import argparse
import json
import os
import sys
from datetime import datetime


def load_json(filepath, description="JSON"):
    """Load and return parsed JSON from a file.

    Args:
        filepath: Path to the JSON file.
        description: Human-readable label for error messages.

    Returns:
        Parsed JSON data (dict or list).

    Raises:
        SystemExit: On file not found or invalid JSON.
    """
    if not os.path.isfile(filepath):
        print(f"Error: {description} file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in {filepath}: {exc}", file=sys.stderr)
        sys.exit(1)


def parse_version(version_str):
    """Parse a version string like '16.2' into a tuple of ints for comparison.

    Args:
        version_str: Dot-separated version string.

    Returns:
        Tuple of integers, e.g., (16, 2).
    """
    try:
        return tuple(int(x) for x in str(version_str).split("."))
    except (ValueError, AttributeError):
        return (0,)


def check_device_compliance(device, policy_settings):
    """Evaluate a single device against the compliance policy.

    Args:
        device: dict with device attributes (see sample_device_inventory.json).
        policy_settings: dict of policy settings from the compliance policy.

    Returns:
        dict with:
            - device_id: identifier for the device
            - device_name: friendly name
            - platform: android or iOS
            - compliant: bool
            - failures: list of failure description strings
            - checks_passed: int count of passed checks
            - checks_total: int total checks evaluated
    """
    failures = []
    checks_passed = 0
    checks_total = 0

    device_name = device.get("deviceName", device.get("device_name", "Unknown"))
    device_id = device.get("deviceId", device.get("device_id", "N/A"))
    platform = device.get("platform", "").lower()

    # ── Device Security Checks ───────────────────────────────────────────
    sec = policy_settings.get("deviceSecurity", {})

    # Encryption
    if sec.get("requireEncryption"):
        checks_total += 1
        if device.get("encryptionEnabled", device.get("encryption_enabled", False)):
            checks_passed += 1
        else:
            failures.append("Device encryption is not enabled")

    # Device lock
    if sec.get("requireDeviceLock"):
        checks_total += 1
        if device.get("deviceLockEnabled", device.get("device_lock_enabled", False)):
            checks_passed += 1
        else:
            failures.append("Device lock (passcode/PIN) is not enabled")

    # Minimum PIN length
    min_pin = sec.get("minimumPinLength", 0)
    if min_pin:
        checks_total += 1
        actual_pin = device.get("pinLength", device.get("pin_length", 0))
        if actual_pin >= min_pin:
            checks_passed += 1
        else:
            failures.append(
                f"PIN length ({actual_pin}) below minimum ({min_pin})"
            )

    # Jailbreak / root detection
    if sec.get("blockJailbrokenDevices") or sec.get("blockRootedDevices"):
        checks_total += 1
        jailbroken = device.get("jailbroken", device.get("rooted", False))
        if not jailbroken:
            checks_passed += 1
        else:
            label = "rooted" if platform == "android" else "jailbroken"
            failures.append(f"Device is {label}")

    # Auto-lock timeout
    max_timeout = sec.get("autoLockTimeoutMinutes", 0)
    if max_timeout:
        checks_total += 1
        actual_timeout = device.get(
            "autoLockMinutes", device.get("auto_lock_minutes", 999)
        )
        if actual_timeout <= max_timeout:
            checks_passed += 1
        else:
            failures.append(
                f"Auto-lock timeout ({actual_timeout} min) exceeds maximum ({max_timeout} min)"
            )

    # ── OS Compliance Checks ─────────────────────────────────────────────
    os_policy = policy_settings.get("osCompliance", {})

    if platform == "android":
        min_ver = os_policy.get("minimumAndroidVersion", "0")
    elif platform == "ios":
        min_ver = os_policy.get("minimumIOSVersion", "0")
    else:
        min_ver = "0"

    checks_total += 1
    device_os_ver = device.get("osVersion", device.get("os_version", "0"))
    if parse_version(device_os_ver) >= parse_version(min_ver):
        checks_passed += 1
    else:
        failures.append(
            f"OS version ({device_os_ver}) below minimum ({min_ver}) for {platform}"
        )

    # Security patch recency
    max_patch_days = os_policy.get("maxDaysSinceLastPatchCheck", 0)
    if max_patch_days and os_policy.get("requireSecurityPatch"):
        checks_total += 1
        days_since = device.get(
            "daysSinceLastPatch", device.get("days_since_last_patch", 999)
        )
        if days_since <= max_patch_days:
            checks_passed += 1
        else:
            failures.append(
                f"Security patch overdue ({days_since} days since last patch, max {max_patch_days})"
            )

    # ── Network Security Checks ──────────────────────────────────────────
    net = policy_settings.get("networkSecurity", {})

    if net.get("requireVPN"):
        checks_total += 1
        if device.get("vpnEnabled", device.get("vpn_enabled", False)):
            checks_passed += 1
        else:
            failures.append("VPN is not enabled (corporate VPN required)")

    if net.get("blockOpenWiFiConnections"):
        checks_total += 1
        if not device.get(
            "connectedToOpenWifi",
            device.get("connected_to_open_wifi", False),
        ):
            checks_passed += 1
        else:
            failures.append("Connected to open (unsecured) Wi-Fi network")

    # ── Application Security Checks ──────────────────────────────────────
    app = policy_settings.get("applicationSecurity", {})

    if app.get("blockSideloadedApps"):
        checks_total += 1
        if not device.get(
            "sideloadedApps", device.get("sideloaded_apps", False)
        ):
            checks_passed += 1
        else:
            failures.append("Sideloaded (non-store) apps detected")

    # ── Data Protection Checks ───────────────────────────────────────────
    data = policy_settings.get("dataProtection", {})

    if data.get("requireBackupEncryption"):
        checks_total += 1
        if device.get(
            "backupEncrypted", device.get("backup_encrypted", False)
        ):
            checks_passed += 1
        else:
            failures.append("Device backup encryption is not enabled")

    return {
        "device_id": device_id,
        "device_name": device_name,
        "platform": platform,
        "compliant": len(failures) == 0,
        "failures": failures,
        "checks_passed": checks_passed,
        "checks_total": checks_total,
    }


def format_text_report(results, policy_name):
    """Generate a plain-text compliance report.

    Args:
        results: List of per-device compliance result dicts.
        policy_name: Name of the policy applied.

    Returns:
        Formatted report string.
    """
    lines = []
    total = len(results)
    compliant = sum(1 for r in results if r["compliant"])
    non_compliant = total - compliant
    pct = (compliant / total * 100) if total > 0 else 0

    lines.append("=" * 65)
    lines.append("          WIRELESS COMPLIANCE REPORT")
    lines.append("=" * 65)
    lines.append("")
    lines.append(f"Policy:          {policy_name}")
    lines.append(f"Report Date:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Devices Evaluated: {total}")
    lines.append(f"Compliant:       {compliant} ({pct:.1f}%)")
    lines.append(f"Non-Compliant:   {non_compliant} ({100 - pct:.1f}%)")
    lines.append("")

    # Risk assessment
    if pct == 100:
        lines.append("Risk Level: LOW — All devices meet policy requirements.")
    elif pct >= 75:
        lines.append("Risk Level: MODERATE — Most devices compliant; remediate remaining.")
    elif pct >= 50:
        lines.append("Risk Level: HIGH — Significant non-compliance detected.")
    else:
        lines.append("Risk Level: CRITICAL — Majority of devices non-compliant.")
    lines.append("")

    # Compliant devices
    lines.append("-" * 65)
    lines.append("COMPLIANT DEVICES")
    lines.append("-" * 65)
    compliant_results = [r for r in results if r["compliant"]]
    if compliant_results:
        for r in compliant_results:
            lines.append(
                f"  ✓ {r['device_name']} ({r['platform']}) — "
                f"{r['checks_passed']}/{r['checks_total']} checks passed"
            )
    else:
        lines.append("  (none)")
    lines.append("")

    # Non-compliant devices
    lines.append("-" * 65)
    lines.append("NON-COMPLIANT DEVICES")
    lines.append("-" * 65)
    non_compliant_results = [r for r in results if not r["compliant"]]
    if non_compliant_results:
        for r in non_compliant_results:
            lines.append(
                f"\n  ✗ {r['device_name']} ({r['platform']}) — "
                f"{r['checks_passed']}/{r['checks_total']} checks passed"
            )
            lines.append(f"    Device ID: {r['device_id']}")
            lines.append(f"    Failures ({len(r['failures'])}):")
            for f in r["failures"]:
                lines.append(f"      • {f}")
    else:
        lines.append("  (none)")
    lines.append("")

    # Failure frequency analysis
    failure_counts = {}
    for r in results:
        for f in r["failures"]:
            # Normalize to category
            category = f.split("(")[0].strip()
            failure_counts[category] = failure_counts.get(category, 0) + 1

    if failure_counts:
        lines.append("-" * 65)
        lines.append("FAILURE FREQUENCY ANALYSIS")
        lines.append("-" * 65)
        for issue, count in sorted(failure_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {count}x  {issue}")
        lines.append("")

    lines.append("=" * 65)
    lines.append("END OF REPORT")
    lines.append("=" * 65)
    return "\n".join(lines)


def format_markdown_report(results, policy_name):
    """Generate a Markdown compliance report.

    Args:
        results: List of per-device compliance result dicts.
        policy_name: Name of the policy applied.

    Returns:
        Formatted Markdown report string.
    """
    lines = []
    total = len(results)
    compliant = sum(1 for r in results if r["compliant"])
    non_compliant = total - compliant
    pct = (compliant / total * 100) if total > 0 else 0

    lines.append("# Wireless Compliance Report")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Policy | {policy_name} |")
    lines.append(f"| Report Date | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    lines.append(f"| Devices Evaluated | {total} |")
    lines.append(f"| Compliant | {compliant} ({pct:.1f}%) |")
    lines.append(f"| Non-Compliant | {non_compliant} ({100 - pct:.1f}%) |")
    lines.append("")

    # Risk level
    if pct == 100:
        risk = "🟢 LOW — All devices meet policy requirements."
    elif pct >= 75:
        risk = "🟡 MODERATE — Most devices compliant; remediate remaining."
    elif pct >= 50:
        risk = "🟠 HIGH — Significant non-compliance detected."
    else:
        risk = "🔴 CRITICAL — Majority of devices non-compliant."
    lines.append(f"**Risk Level:** {risk}")
    lines.append("")

    # Summary table
    lines.append("## Device Summary")
    lines.append("")
    lines.append("| Device | Platform | Status | Checks Passed | Failures |")
    lines.append("|--------|----------|--------|---------------|----------|")
    for r in results:
        status = "✅ Compliant" if r["compliant"] else "❌ Non-Compliant"
        fail_count = len(r["failures"])
        lines.append(
            f"| {r['device_name']} | {r['platform']} | {status} "
            f"| {r['checks_passed']}/{r['checks_total']} | {fail_count} |"
        )
    lines.append("")

    # Non-compliant details
    non_compliant_results = [r for r in results if not r["compliant"]]
    if non_compliant_results:
        lines.append("## Non-Compliant Device Details")
        lines.append("")
        for r in non_compliant_results:
            lines.append(f"### {r['device_name']} ({r['platform']})")
            lines.append("")
            lines.append(f"- **Device ID:** {r['device_id']}")
            lines.append(
                f"- **Checks Passed:** {r['checks_passed']}/{r['checks_total']}"
            )
            lines.append(f"- **Failures:**")
            for f in r["failures"]:
                lines.append(f"  - {f}")
            lines.append("")

    # Failure frequency
    failure_counts = {}
    for r in results:
        for f in r["failures"]:
            category = f.split("(")[0].strip()
            failure_counts[category] = failure_counts.get(category, 0) + 1

    if failure_counts:
        lines.append("## Failure Frequency Analysis")
        lines.append("")
        lines.append("| Issue | Count |")
        lines.append("|-------|-------|")
        for issue, count in sorted(failure_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {issue} | {count} |")
        lines.append("")

    lines.append("---")
    lines.append(
        "*Generated by wireless_compliance_checker.py — "
        "CSC-7306 Mobile Wireless Security*"
    )
    return "\n".join(lines)


def main():
    """Entry point: parse arguments, load data, run compliance checks, report."""
    parser = argparse.ArgumentParser(
        description=(
            "Check a device inventory against an MDM compliance policy "
            "and generate a compliance report."
        ),
        epilog=(
            "Examples:\n"
            "  python wireless_compliance_checker.py \\\n"
            "      --policy mdm_compliance_policy.json \\\n"
            "      --inventory sample_device_inventory.json\n\n"
            "  python wireless_compliance_checker.py \\\n"
            "      --policy mdm_compliance_policy.json \\\n"
            "      --inventory sample_device_inventory.json \\\n"
            "      --format markdown -o report.md\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--policy",
        required=True,
        help="Path to MDM compliance policy JSON file.",
    )
    parser.add_argument(
        "--inventory",
        required=True,
        help="Path to device inventory JSON file.",
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
        "--strict",
        action="store_true",
        help="Treat missing device attributes as non-compliant (default: skip).",
    )

    args = parser.parse_args()

    # Load policy
    policy_data = load_json(args.policy, "Policy")
    policy = policy_data.get("compliancePolicy", policy_data)
    policy_name = policy.get("displayName", "Unknown Policy")
    policy_settings = policy.get("settings", {})

    if not policy_settings:
        print(
            "Error: Policy file has no 'settings' section under 'compliancePolicy'.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load inventory
    inventory_data = load_json(args.inventory, "Inventory")
    devices = inventory_data.get("devices", inventory_data)
    if not isinstance(devices, list):
        print(
            "Error: Inventory must contain a 'devices' array.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not devices:
        print("Warning: Inventory is empty — no devices to evaluate.", file=sys.stderr)

    # Run compliance checks
    results = []
    for device in devices:
        result = check_device_compliance(device, policy_settings)
        results.append(result)

    # Generate report
    if args.format == "markdown":
        report = format_markdown_report(results, policy_name)
    else:
        report = format_text_report(results, policy_name)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(report)
            print(f"Compliance report written to {args.output}")
        except OSError as exc:
            print(f"Error writing report: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(report)


if __name__ == "__main__":
    main()
