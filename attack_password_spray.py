import requests
import time

BASE_URL = "http://localhost:5000"

# Password spray: try one common (wrong) password against multiple accounts
target_users = ["jsmith", "admin_dray", "svc_backup"]
common_wrong_password = "Password123"

print("Simulating password spray attack...\n")

for username in target_users:
    response = requests.post(f"{BASE_URL}/login", data={
        "username": username,
        "password": common_wrong_password
    })
    print(f"Attempted: {username} -> {response.status_code}")
    time.sleep(0.5)  # spray attacks are often fast, but not always instant

# Repeat the spray pattern a couple more rounds, mimicking a real attacker retrying
for round_num in range(2):
    print(f"\nRound {round_num + 2} of spraying...")
    for username in target_users:
        response = requests.post(f"{BASE_URL}/login", data={
            "username": username,
            "password": common_wrong_password
        })
        print(f"Attempted: {username} -> {response.status_code}")
        time.sleep(0.5)

print("\nPassword spray simulation complete.")
