# Identity Attack Detection & False-Positive Reduction

A small, self-built SOC lab: I created a fake identity system, attacked it five different ways myself, wrote SIEM detection rules to catch each attack, and then tuned those rules against normal daily activity so they don't drown an analyst in false alarms.

Everything here runs locally and cost me nothing — no cloud trial, no expiring credits. Just Python, Docker, and Wazuh.

## Why this project

Most breaches these days don't start with malware. They start with a password that shouldn't have worked, a login from somewhere it shouldn't have come from, or an MFA reset that nobody actually asked for. I wanted to understand that problem properly — not by reading about it, but by building the system, attacking it, and then writing (and fixing, and re-writing) the detection logic myself.

The full write-up of what I built, why, and what I learned is in [PROJECT_REPORT.md](./PROJECT_REPORT.md). The response playbook an analyst would actually use during triage is in [RESPONSE_PLAYBOOK.md](./RESPONSE_PLAYBOOK.md).

## How it's put together

```
User login attempt
        |
        v
  Flask identity app  --------> identity_lab.log
   (3 test accounts:               |
   employee, admin,                v
   service account)          Wazuh (SIEM)
        |                          |
        v                          v
  Attack scripts              Custom rules fire
  simulate 5 attack               |
  patterns                        v
                            Analyst reviews alert
```

I wrote a small Flask app to act as the identity system, with three accounts that behave the way real ones would: a regular employee, an admin, and a service account that's supposed to only ever do its own automated thing. Every login, MFA reset, and role change gets logged. Wazuh reads that log, decodes it, and runs it through rules I wrote myself.

## The five attacks I simulated

| Attack | What actually happens |
|---|---|
| Password spray | One IP tries the same password against several different accounts in quick succession |
| Risky sign-in | A login succeeds from an IP/device that account has never used before |
| MFA reset abuse | Someone resets MFA from an IP that isn't trusted — a common account-takeover step |
| Privilege escalation | A normal employee account gets bumped up to admin |
| Off-hours admin activity | The same escalation, but happening at 3am instead of during the workday |

Each one is its own script (`attack_password_spray.py`, `attack_risky_signin.py`, etc.) that hits the real Flask endpoints — not fake log lines, actual traffic.

## The five detections I wrote

| Rule ID | Catches | Severity | MITRE ATT&CK |
|---|---|---|---|
| 100005 | 3+ failed logins across different accounts, same IP, under 2 minutes | 10 | T1110.003 — Password Spraying |
| 100006 | Successful login from an untrusted IP | 9 | T1078 — Valid Accounts |
| 100007 | MFA reset from an untrusted IP | 12 | T1556 — Modify Authentication Process |
| 100008 | Privilege escalation to admin outside 9am–6pm | 13 | T1078.003 — Local Accounts |
| 100009 | A service account performing a role change (it never legitimately should) | 13 | T1078.001 — Default Accounts |

The fifth one wasn't part of my original plan — it came out of noticing that service accounts behave mechanically by design, so any deviation from that is a stronger signal than the same action from a person. I added it because it made the project genuinely better, not because a checklist told me to.

All five rules were tested and confirmed working using Wazuh's own `wazuh-logtest` tool — screenshots of each one firing correctly, with the MITRE mapping attached, are in [`/screenshots`](./screenshots).

## Cutting the noise

Writing a detection that fires is the easy part. Making sure it doesn't fire on normal, boring, everyday activity is the part that actually separates a usable detection from an annoying one. I did two rounds of this:

**Round 1 — a legitimate second location.** My admin account regularly logs in from what I set up as a home-office IP. Before tuning, every single one of those logins triggered the "risky sign-in" alert — technically correct, practically useless. I added that IP to a small trusted list. After the change, that login goes quiet, but a genuine attacker IP still trips the same rule exactly as before. One recurring false alarm gone, no loss of real detection.

**Round 2 — a full baseline check.** I replayed a clean day of normal activity (a natural mistyped password, a routine admin role reassignment, ordinary logins) through all five rules. None of the high-severity attack rules fired. Everything stayed at the generic, low-severity level it should.

## What I ran into

Building this wasn't just writing rules — a good chunk of the actual work was troubleshooting infrastructure, which taught me things I didn't expect going in:

- Wazuh's time-based rules check the moment an event is *processed*, not the timestamp written inside the log. That's a non-issue in a real deployment where things happen close to real-time, but it matters if you're testing with simulated, backdated log data like I was.
- Docker on WSL2 has a habit of letting its internal disk balloon well past what the data inside it actually justifies, especially with a lot of container restarts during rule debugging. I ended up treating the whole Docker/Wazuh environment as disposable — rebuild it fresh each session from saved config files — since the actual substance of the project (the code, the rules, the logs) was version-controlled and never at risk.

## Running it yourself

1. `pip install -r requirements.txt`, then `python3 app.py` to start the identity app
2. Stand up Wazuh via the official Docker setup (see Wazuh's own docs for the single-node Docker install)
3. Copy the three files from [`/wazuh_rules`](./wazuh_rules) into your Wazuh manager's `etc/decoders/`, `etc/rules/`, and `etc/lists/` respectively
4. Run any of the `attack_*.py` scripts to simulate an attack
5. Check the alert fired correctly with `wazuh-logtest`, or through the Wazuh dashboard

## What's in this repo

- `app.py` — the identity system (Flask)
- `attack_password_spray.py`, `attack_risky_signin.py`, `attack_mfa_reset.py`, `attack_privilege_escalation.py` — the five attack scripts
- `simulate_baseline.py` — generates a clean day of normal activity for tuning/testing against
- `wazuh_rules/` — the actual decoder and rule XML files, plus the trusted-IP list
- `screenshots/` — proof each detection fires correctly, MITRE mapping included
- `PROJECT_REPORT.md` — the full story of what I built and what I learned
- `RESPONSE_PLAYBOOK.md` — first-response steps for each alert, written for an analyst
