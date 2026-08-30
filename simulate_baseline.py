import requests
import random
import time

BASE_URL = "http://localhost:5000"

def attempt_login(username, password):
    response = requests.post(f"{BASE_URL}/login", data={"username": username, "password": password})
    print(f"Login attempt: {username} -> {response.status_code}")

def change_role(admin_username, admin_password, target_username, new_role):
    response = requests.post(f"{BASE_URL}/change_role", data={
        "admin_username": admin_username,
        "admin_password": admin_password,
        "target_username": target_username,
        "new_role": new_role,
    })
    print(f"Role change attempt: {target_username} -> {new_role} -> {response.status_code}")

# --- Simulate a normal day ---

print("Simulating baseline day of normal identity activity...\n")

# jsmith (employee): several logins across the day, one natural typo
attempt_login("jsmith", "Employee@123")
time.sleep(random.uniform(1, 3))
attempt_login("jsmith", "Employee@123")
time.sleep(random.uniform(1, 3))
attempt_login("jsmith", "wrongpass123")  # a natural human typo, not an attack
time.sleep(random.uniform(1, 3))
attempt_login("jsmith", "Employee@123")

time.sleep(random.uniform(2, 4))

# svc_backup (service account): regular, mechanical, predictable
attempt_login("svc_backup", "ServiceKey@789")
time.sleep(random.uniform(2, 4))
attempt_login("svc_backup", "ServiceKey@789")
time.sleep(random.uniform(2, 4))
attempt_login("svc_backup", "ServiceKey@789")

time.sleep(random.uniform(2, 4))

# admin_dray (admin): fewer logins, one legitimate role change (onboarding-style)
attempt_login("admin_dray", "AdminPass@456")
time.sleep(random.uniform(1, 3))
change_role("admin_dray", "AdminPass@456", "jsmith", "employee")  # confirming/reasserting normal role
time.sleep(random.uniform(1, 3))
attempt_login("admin_dray", "AdminPass@456")

print("\nBaseline simulation complete.")
