# Runbook — Pilot 405 (Mobile & Wireless Security Portfolio)

## Overview

Daily operations and one-time setup for the Mobile Wireless Security portfolio repo.

## One-Time Setup

- Public repo (planned): `rossmoravec/405-Mobile-Wireless-Security` on GitHub
- Central remote: `ssh://synnasadmin@192.168.0.38/volume1/Share1/pilots-central/405-Mobile-Wireless-Security.git`
- Enable GitHub secret scanning and push protection after publishing publicly

## PM Loop

```bash
# Verify no student ID leaks
grep -ri "A00[0-9]\{5\}" . --include="*.md" --include="*.json" --include="*.pdf" 2>/dev/null

# Run markdown linter
npx markdownlint-cli2 "**/*.md"

# Check for excluded file types
find . -name "*.mp4" -o -name "*.exe" -o -name "*.msi" 2>/dev/null
```

## Content Import Procedure

1. Source content lives at `D:\CC\Winter2025\Mobile Wireless Security - Mohamed Jbeili - CSC-7306 - 11815 - 202501 - 002\`
2. For each student submission (DOCX/PPTX):
   - Convert to PDF via MS Word or LibreOffice headless
   - Rename per convention: `LabNN_Topic_Submission.pdf`
   - Strip student ID from filename
   - Verify no student ID in content before committing
3. Copy converted PDFs to `CC/Winter 2025/Mobile Wireless Security - Mohamed Jbeili - CSC-7306/assignments/`

## Large File Handling

- Preferred: convert DOCX/PPTX to PDF (smaller, version-control-friendly)
- LFS fallback: configured in `.gitattributes` for `*.pdf`, `*.docx`, `*.pptx`, `*.xlsx` in course paths
- Do not commit: MP4 lecture recordings, EXE installers

## Evidence & Health

- Roadmap status: [ROADMAP.md](../ROADMAP.md)
- Course content inventory: [Course README](../CC/Winter%202025/Mobile%20Wireless%20Security%20-%20Mohamed%20Jbeili%20-%20CSC-7306/README.md)
- Portfolio config: [portfolio/config.json](../portfolio/config.json)

## Security Posture

- No secrets committed; secret scanning enabled on public repo
- Student identifier (A00XXXXXX) must not appear anywhere in committed content
- If credentials needed for automation, fetch from providers per global AGENTS.md (no echo)
- Review [SECURITY.md](../SECURITY.md) for responsible disclosure guidance
