# Incident Response Playbook — Identity Attack Detection Lab

**Author:** Debajyoti Ray

This playbook covers first-response steps for each of the five alerts produced by this project's detection rules. It's written the way I'd want it handed to me on day one of a SOC analyst role: short, specific, and built around the question every analyst actually asks first — "is this real, and what do I do about it right now?"

---

## Password Spray Detected
**Rule 100005 · Severity 10 · MITRE T1110.003 (Password Spraying)**

**What triggered it:** three or more failed logins across different accounts, from the same source IP, within 120 seconds.

**Check first:**
- Which accounts were targeted, and does the source IP show up in any other recent alert?
- Did any targeted account have a successful login shortly after the failed attempts? That would mean the spray worked.

**Escalate when:** any targeted account shows a follow-up success, or the IP matches a known bad range.

**Contain:** block the source IP, force a password reset on any account with a suspicious follow-up success.

---

## Risky Sign-In — Untrusted IP
**Rule 100006 · Severity 9 · MITRE T1078 (Valid Accounts)**

**What triggered it:** a successful login from an IP that isn't on the trusted list.

**Check first:**
- Ask the account owner directly whether they traveled, changed networks, or switched devices.
- Look at what the account did immediately after logging in — role changes, MFA changes, and data access are the things worth checking.

**Escalate when:** the user denies logging in, or the account is an admin or service account.

**Contain:** if you can't confirm it was legitimate, log the account out and force a password reset. Add the IP to a watchlist — not straight onto the trusted list — until it's confirmed.

---

## MFA Reset from Untrusted IP
**Rule 100007 · Severity 12 · MITRE T1556 (Modify Authentication Process)**

**What triggered it:** an MFA reset or new device registration from an IP that isn't trusted. This is one of the strongest signals in the whole system — MFA is usually the last thing standing between a stolen password and full account takeover.

**Check first:**
- Reach the account owner through a channel other than email, in case email is compromised too.
- Check whether this alert followed a risky sign-in or password spray alert on the same account — that sequence is a textbook takeover chain.

**Escalate immediately if:** the user didn't request the reset. Treat it as a confirmed compromise until proven otherwise — don't wait for more evidence.

**Contain:** disable the account, kill every active session, and re-verify identity out-of-band before restoring access.

---

## Privilege Escalation Outside Business Hours
**Rule 100008 · Severity 13 · MITRE T1078.003 (Local Accounts)**

**What triggered it:** an account was elevated to admin outside the 9 AM–6 PM window.

**Check first:**
- Ask the admin who made the change whether it was planned.
- Check the source IP against the trusted list.
- Watch the newly elevated account for anything suspicious afterward.

**Escalate when:** the admin didn't authorize the change, or it came from an untrusted IP.

**Contain:** revert the role change if it wasn't authorized, and disable the acting admin's account if it looks compromised.

---

## Service Account Performed a Role Change
**Rule 100009 · Severity 13 · MITRE T1078.001 (Default Accounts)**

**What triggered it:** a service account initiated a role change. In this environment, that should never happen — service accounts run on fixed automation and have no legitimate reason to touch user privileges.

**Check first:**
- Confirm there's no scheduled job that would explain this (there shouldn't be one).
- Review the service account's recent login history for anything unusual.

**Escalate immediately:** there's no expected legitimate explanation for this in this environment. Treat it as a compromised service account from the start.

**Contain:** disable the account, rotate its credentials, and review everything it's done recently.

---

## One general rule of thumb
Any alert on a privileged account — admin or service account — should be treated one severity tier more seriously than the identical alert on a standard employee account. The blast radius is bigger, so the response speed should be too.
