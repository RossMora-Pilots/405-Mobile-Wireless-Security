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

## M2 — Quality Audit & Remediation (COMPLETED 2026-04-05)

### Phase 1: Initial Assessment (B+ grade, 31 findings)

- [x] Employer-perspective portfolio assessment (1,337 lines)
- [x] Document-by-document formatting review (10 documents)
- [x] Visualization gap analysis (16 diagrams inventoried)
- [x] Information utilization audit (source-by-source coverage)
- [x] 31 actionable improvements identified across P0-P3

### Phase 2: Full Remediation (31/31 items)

- [x] **P0 — Critical (5 items):** Kill chain PDF renamed, empty dirs cleaned, scripts created, statistics sourced, week framing fixed
- [x] **P1 — Strongly Recommended (9 items):** Network topology, heatmap description, cost estimates, Gantt chart, risk heat map, Next Steps, presentation note, Lab 1 expansion, Why section promoted
- [x] **P2 — Differentiation (8 items):** NAC vendor matrix, MDM vendor matrix, NIST/ISO cross-walk, STRIDE heat grid, Sankey diagram, Azure AD→Entra ID, MITRE ATT&CK update, publication context
- [x] **P3 — Polish (9 items):** Diagram legends, PDF cross-links, evidence index expansion, CI note, architecture dedup, collapsed repo structure, Pages badge, Lab 1 time-on-task, BYOD UX friction

### Phase 3: Validation (31/31 confirmed + 4 additional fixes)

- [x] Independent validation agents confirmed all 31 items
- [x] Fixed stale "Azure AD" reference in cost table
- [x] Fixed broken relative link (../../ → ../../../)
- [x] Added missing YAML frontmatter (2 files)
- [x] Resolved 17 markdownlint warnings → 0 errors

### Phase 4: Fresh Assessment (A- employer grade)

- [x] 4-dimension independent re-assessment
- [x] Formatting & Structure: A (9.2/10)
- [x] Visualizations: A- (8.5/10)
- [x] Information Utilization: B (82%)
- [x] Employer Readiness: A- (advance to technical screen)
- [x] 5 growth areas identified (not red flags)

### Phase 5: Growth Area Remediation (A employer grade)

- [x] Defense effectiveness validation (before/after tables in 3 labs + capstone simulation)
- [x] Production experience gap mitigated (Home Lab Roadmap with 4 concrete steps)
- [x] Quantified risk scoring (CVSS table, ALE estimates, 12×7 control-to-threat matrix)
- [x] Troubleshooting narratives (Lessons Learned in all 3 labs)
- [x] Standardized color palette (4-color system applied to all 18+ diagrams)
- [x] 3 new visualizations (802.1X flow, BYOD enrollment, IR playbook)
- [x] Wireless protocol comparison table (WEP→WPA3-Enterprise)

## Next

- [ ] Complete Home Lab Roadmap exercises (Azure Intune, Raspberry Pi, Splunk)
- [ ] Record walkthrough video of portfolio highlights
- [ ] Cross-link with other course portfolios (401, 402, 403, 404)
- [ ] Add CWSP exam domain deep-dive document
- [ ] Publish to GitHub (public repo)

## Later

- [ ] Integrate with unified skills framework
- [ ] Add interactive wireless coverage heatmap viewer (GitHub Pages)

## Milestones

### M1 — Portfolio Complete ✅ (completed 2026-04-04)

All content authored, assignments imported, CI passing, ready for employer review.

### M2 — Quality Audit Remediation ✅ (completed 2026-04-05)

41 total remediation items (31 original + 10 growth areas) implemented, validated, and documented. Employer grade: B+ → A. Zero markdownlint errors. 21 files changed, +1,762/-111 lines.

### M3 — Production Experience Bridge (target: TBD)

Complete Home Lab Roadmap exercises. Deploy Intune test tenant, build Raspberry Pi attack lab, create Splunk detection dashboard, and perform red team validation against own defenses.

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
