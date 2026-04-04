# Roadmap — Mobile & Wireless Security Portfolio (Pilot 405)

## Now

- [x] Bootstrap repository from pilot 009 template conventions
- [x] Configure portfolio/config.json with CSC-7306 metrics and skills
- [x] Scaffold course directory structure
- [x] Convert DOCX student submissions to PDF
- [x] Import and rename assignment PDFs (sanitize filenames, strip student ID)
- [x] Write WEEKLY_TOPIC_MAP.md (12-week curriculum map)
- [x] Write WEEKLY_LABS_SUMMARY.md (progressive lab portfolio)
- [x] Write CASE_STUDY_CAPSTONE.md (Week 6 WLAN & Mobile Security Plan)
- [x] Write CYBER_KILL_CHAIN_ANALYSIS.md (Week 6 Part 1/2 deliverable)
- [x] Write WIRELESS_THREAT_MODEL.md (WLAN + mobile threat taxonomy)
- [x] Write BYOD_POLICY_FRAMEWORK.md (BYOD/MDM/NAC/Zero Trust synthesis)
- [x] Write course-level README.md (full showcase with diagrams)
- [x] Write root README.md (employer-facing landing page)
- [x] Final PII scan and verification
- [x] Add LICENSE and SECURITY.md
- [x] Add shield.io technology badges

## Next

- [ ] Add screenshots and populate EVIDENCE_INDEX.md
- [ ] Record walkthrough video of portfolio highlights
- [ ] Cross-link with other course portfolios (401, 402, 403, 404)
- [ ] Add CWSP exam domain deep-dive document
- [ ] Publish to GitHub (public repo)

## Later

- [ ] Integrate with unified skills framework
- [ ] Add interactive wireless coverage heatmap viewer (GitHub Pages)
- [ ] Add MDM vendor comparison matrix

## Milestones

### M1 — Portfolio Complete (target 2026-04-04)

All content authored, assignments imported, CI passing, ready for employer review.

### M2 — Quality Audit Remediation

PII verified, formatting polished, diagrams added, professional grade.

## Runbook

```bash
# Verify no PII leaks
grep -ri "A00[0-9]\{5\}" . --include="*.md" --include="*.json" --include="*.pdf" 2>/dev/null

# Run markdown linter
npx markdownlint-cli2 "**/*.md"

# Check for lecture videos (should be empty)
find . -name "*.mp4" -type f 2>/dev/null

# Check for third-party installers (should be empty)
find . -name "*.exe" -o -name "*.msi" 2>/dev/null
```
