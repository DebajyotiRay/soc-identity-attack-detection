import requests

BASE_URL = "http://localhost:5000"

print("Simulating risky sign-in: new IP and unfamiliar device...\n")

# Simulate jsmith logging in from an unusual location and an unfamiliar device,
# spoofing the source IP via X-Forwarded-For (as a real attacker behind a proxy/VPN might appear)
headers = {
    "X-Forwarded-For": "203.0.113.77",  # unusual external IP, not the normal 127.0.0.1
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A536E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
    # a mobile Android device - jsmith normally logs in from curl/desktop, not a phone
}

response = requests.post(f"{BASE_URL}/login",
    data={"username": "jsmith", "password": "Employee@123"},
    headers=headers
)

print(f"Risky sign-in attempt: jsmith from 203.0.113.77 (mobile device) -> {response.status_code}")
print("Simulation complete.")
