import requests

BASE_URL = "http://localhost:5000"

print("Simulating privilege escalation attack...\n")

# Attacker (having already compromised jsmith's credentials via MFA reset)
# now attempts to escalate jsmith's own account to admin - but this requires
# admin credentials, so first let's simulate a more realistic scenario:
# the attacker has ALSO somehow obtained admin credentials (e.g. from a
# separate compromise) and uses them from the same suspicious IP/device.

headers = {
    "X-Forwarded-For": "198.51.100.23",  # same suspicious IP as the MFA attack
    "User-Agent": "python-requests/attack-tool"
}

response = requests.post(f"{BASE_URL}/change_role",
    data={
        "admin_username": "admin_dray",
        "admin_password": "AdminPass@456",
        "target_username": "jsmith",
        "new_role": "admin"
    },
    headers=headers
)

print(f"Privilege escalation attempt: jsmith -> admin, from suspicious IP -> {response.status_code}")
print(f"Response: {response.text}")
print("Simulation complete.")
