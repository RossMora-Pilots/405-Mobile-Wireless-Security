"""Extract key screenshots from lab PDFs for portfolio embedding."""
import fitz
import os

base = r"CC\Winter 2025\Mobile Wireless Security - Mohamed Jbeili - CSC-7306"
out_dir = os.path.join(base, "screenshots")
os.makedirs(out_dir, exist_ok=True)

lab01_pages = {
    "lab01_ghostapd_baseline": 2,
    "lab01_wpa2_config": 8,
    "lab01_mac_acl": 3,
    "lab01_linssid_scan": 6,
    "lab01_tx_power_reduction": 10,
    "lab01_kismet_decloak": 32,
    "lab01_wep_detection": 36,
}

lab03_pages = {
    "lab03_heatmap_5ghz": 1,
    "lab03_heatmap_2_4ghz": 2,
    "lab03_sir_analysis": 3,
    "lab03_dead_zone": 5,
    "lab03_phy_mode": 9,
}

lab05_pages = {
    "lab05_wireshark_ttl": 2,
    "lab05_p0f_passive": 3,
    "lab05_nmap_os_scan": 5,
    "lab05_clientjs_fingerprint": 7,
    "lab05_useragent_comparison": 10,
}

for pdf_name, pages_map in [
    ("Lab01_Wireless_Wardriving_Defense_Submission.pdf", lab01_pages),
    ("Lab03_WiFi_Site_Survey_Submission.pdf", lab03_pages),
    ("Lab05_Mobile_Device_Fingerprinting_Submission.pdf", lab05_pages),
]:
    pdf_path = os.path.join(base, "assignments", pdf_name)
    doc = fitz.open(pdf_path)
    for name, page_num in pages_map.items():
        page = doc[page_num - 1]
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat)
        out_path = os.path.join(out_dir, f"{name}.png")
        pix.save(out_path)
        kb = os.path.getsize(out_path) / 1024
        print(f"  {name}.png ({kb:.0f} KB)")
    doc.close()

# Clean up raw extraction files
cleaned = 0
for f in os.listdir(out_dir):
    if "_img" in f and f.startswith("lab0"):
        os.remove(os.path.join(out_dir, f))
        cleaned += 1
print(f"Cleaned {cleaned} raw extraction files")

remaining = [f for f in os.listdir(out_dir) if f.endswith(".png")]
print(f"Final screenshot count: {len(remaining)}")
for f in sorted(remaining):
    kb = os.path.getsize(os.path.join(out_dir, f)) / 1024
    print(f"  {f} ({kb:.0f} KB)")
