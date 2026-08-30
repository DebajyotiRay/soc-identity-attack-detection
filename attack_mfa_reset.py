import requests

BASE_URL = "http://localhost:5000"

print("Simulating suspicious MFA reset attempt...\n")

# Simulate an attacker attempting to reset MFA using a compromised/guessed credential,
# from an unfamiliar IP - mirroring a real account-takeover pattern
headers = {
    "X-Forwarded-For": "198.51.100.23",
    "User-Agent": "python-requests/attack-tool"
}

response = requests.post(f"{BASE_URL}/mfa_reset",
    data={"username": "jsmith", "password": "Employee@123"},
    headers=headers
)

print(f"MFA reset attempt: jsmith from 198.51.100.23 -> {response.status_code}")
print("Simulation complete.")
