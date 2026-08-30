# Identity Attack Detection & False-Positive Reduction Lab

**Author:** Debajyoti Ray
**Project type:** Independent detection engineering project

## Why I Built This

Most breaches today don't start with malware — they start with a compromised identity. A stolen password, a reused session, an MFA reset that shouldn't have gone through. I wanted to understand this problem from the inside: not just reading about identity attacks, but actually building a system, attacking it myself, writing the detections that catch those attacks, and then doing the less glamorous but arguably more important work — making sure the detections don't drown analysts in noise.

This project is the result: a small identity environment, five realistic attack simulations, five working Wazuh detection rules mapped to MITRE ATT&CK, and two documented rounds of false-positive tuning with measurable before/after results.

Everything here runs locally at zero cost, using open-source tooling (Flask, Wazuh, Docker) — no cloud spend, no trial credits, nothing that expires.

---

## Environment

I built a small Flask application to act as the identity provider, with three accounts representing different real-world roles:

- **jsmith** — a regular employee account. Logs in during normal hours, occasionally mistypes a password (that's a real human, not an attacker).
- **admin_dray** — an admin account. Lower login frequency, occasionally performs legitimate role changes such as onboarding.
- **svc_backup** — a service account. Logs in on a predictable, mechanical schedule and, by design, should never be the one initiating a role change.

Before simulating any attacks, I ran a clean "baseline day" of normal activity across all three accounts. This baseline became the yardstick I used later to check whether my detections were actually tuned well, rather than just technically correct.

---

## Attacks Simulated

| # | Attack | What it looks like |
|---|---|---|
| 1 | Password spray | One IP, several different accounts, repeated failed logins in a short window |
| 2 | Risky sign-in | A successful login from an IP/device the account has never used before |
| 3 | MFA reset abuse | An MFA reset triggered from an untrusted IP — a classic account-takeover step |
| 4 | Privilege escalation | An employee account elevated straight to admin |
| 5 | Off-hours admin activity | The same escalation, but happening well outside business hours |

Each attack is its own small Python script hitting the identity app's real endpoints — no fabricated log lines, just genuine traffic generating genuine logs.

---

## Detections

I wrote five Wazuh rules, each mapped to a specific MITRE ATT&CK technique and tuned to a severity level that actually reflects how dangerous the behavior is:

| Rule | Detection Logic | Severity | MITRE Technique |
|---|---|---|---|
| 100005 | 3+ failed logins, different accounts, same source IP, within 120 seconds | 10 | T1110.003 — Password Spraying |
| 100006 | Successful login from an IP outside the trusted list | 9 | T1078 — Valid Accounts |
| 100007 | MFA reset from an untrusted IP | 12 | T1556 — Modify Authentication Process |
| 100008 | Privilege escalation to admin outside business hours | 13 | T1078.003 — Local Accounts |
| 100009 | A service account performing a role change | 13 | T1078.001 — Default Accounts |

Every rule was validated using Wazuh's `wazuh-logtest` engine, confirming correct field extraction, correct rule firing, and correct MITRE mapping for each attack scenario before I called it done.

I added the fifth rule (service account role changes) myself, beyond the original four-detection scope, because it came directly out of how I'd designed the service account's baseline behavior in the first place — if svc_backup ever does something a service account has no business doing, that's a strong signal worth alerting on.

---

## False-Positive Reduction

Writing a detection is the easy half. Making sure it doesn't cry wolf is the part that actually matters in a real SOC, so I ran two tuning cycles and measured the results.

**Tuning #1 — a legitimate second location for a privileged account.**
admin_dray occasionally logs in from a home-office IP that isn't the "default" office location. Before tuning, this correctly-but-annoyingly triggered the risky sign-in alert every time — a textbook false positive. I added the IP to a trusted allowlist used by the detection logic. After the change, that specific login no longer alerts, while a simulated attacker IP still triggers the same rule exactly as before. Net result: one recurring false positive removed, zero reduction in real detection coverage.

**Tuning #2 — baseline validation across the board.**
I replayed the clean baseline day (the natural password typo, the legitimate admin role reassignment, routine logins from the trusted IP) against all five rules. Every single baseline event stayed at low severity, generic-rule-only. None of the five attack-specific, high-severity rules false-fired on ordinary daily activity.

---

## What I Learned Along the Way

- **Time-based detection rules evaluate against the moment they're processed, not the timestamp written in the log line.** This only matters when you're testing with simulated or backdated data, like I was — in a real deployment, events get processed essentially as they happen, so this isn't an issue in production. Worth knowing if you ever try to replay historical data against a time-window rule.
- **Service accounts are a genuinely useful detection surface.** Because they're expected to behave mechanically, any deviation is a stronger signal than the same action from a human account — this insight is what led me to add the fifth detection.
- **Infrastructure isn't free of its own lessons.** Midway through this project I ran into a Docker/WSL2 disk-growth issue where repeated container restarts (each triggering Wazuh's own internal scans) caused the virtual disk to balloon well past what the actual data justified. I diagnosed the cause, and settled on a "rebuild the environment fresh each session" workflow — since all the real substance of this project (the Flask app, the detection rules, the logs) lives as plain version-controlled files, treating the container runtime itself as disposable turned out to be the more resilient approach.

---

## Summary

This project covers the full loop a detection engineer actually works in: build a system, attack it, detect the attack, prove the detection works, then tune it so it's usable in practice — not just technically correct. Everything here is reproducible from the code and configuration in this repository.
