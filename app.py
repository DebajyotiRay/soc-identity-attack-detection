from flask import Flask, request
import logging
from datetime import datetime

app = Flask(__name__)
# Simulated identity system: 3 users with different roles
USERS = {
    "jsmith": {"password": "Employee@123", "role": "employee"},
    "admin_dray": {"password": "AdminPass@456", "role": "admin"},
    "svc_backup": {"password": "ServiceKey@789", "role": "service_account"},
}
# Configure structured logging - this file is what Wazuh will monitor later
logging.basicConfig(
    filename="identity_lab.log",
    level=logging.INFO,
    format="%(message)s",
)
@app.route("/")
def home():
    return "Identity Lab is running."
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "unknown")
    user = USERS.get(username)

    if user and user["password"] == password:
        result = "SUCCESS"
        role = user["role"]
        logging.info(f"LOGIN_ATTEMPT timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} user={username} role={role} ip={ip_address} device=\"{user_agent}\" result={result}")
        return f"Login successful. Welcome, {username} ({role})."
    else:
        result = "FAILURE"
        role = user["role"] if user else "unknown"
        logging.info(f"LOGIN_ATTEMPT timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} user={username} role={role} ip={ip_address} device=\"{user_agent}\" result={result}")
        return "Login failed. Invalid username or password.", 401
@app.route("/mfa_reset", methods=["POST"])
def mfa_reset():
    username = request.form.get("username")
    password = request.form.get("password")
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "unknown")

    user = USERS.get(username)

    if not user or user["password"] != password:
        logging.info(f"MFA_EVENT timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} user={username} role=unknown ip={ip_address} device=\"{user_agent}\" action=RESET result=DENIED_INVALID_CREDENTIALS")
        return "Access denied. Invalid credentials.", 403

    logging.info(f"MFA_EVENT timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} user={username} role={user['role']} ip={ip_address} device=\"{user_agent}\" action=RESET result=SUCCESS")
    return f"MFA reset successfully for {username}. New MFA device may now be registered."

@app.route("/change_role", methods=["POST"])
def change_role():
    admin_username = request.form.get("admin_username")
    admin_password = request.form.get("admin_password")
    target_username = request.form.get("target_username")
    new_role = request.form.get("new_role")
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

    admin_user = USERS.get(admin_username)

    # Step A: confirm the requester is a real, valid admin
    if not admin_user or admin_user["password"] != admin_password or admin_user["role"] != "admin":
        logging.info(f"ROLE_CHANGE timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} actor={admin_username} ip={ip_address} target={target_username} old_role=N/A new_role={new_role} result=DENIED_NOT_ADMIN")
        return "Access denied. Admin privileges required.", 403

    # Step B: confirm the target user actually exists
    target_user = USERS.get(target_username)
    if not target_user:
        logging.info(f"ROLE_CHANGE timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} actor={admin_username} ip={ip_address} target={target_username} old_role=N/A new_role={new_role} result=FAILED_NO_SUCH_USER")
        return "Target user not found.", 404

    # Step C: apply the role change
    old_role = target_user["role"]
    target_user["role"] = new_role
    logging.info(f"ROLE_CHANGE timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} actor={admin_username} ip={ip_address} target={target_username} old_role={old_role} new_role={new_role} result=SUCCESS")
    return f"Role changed: {target_username} is now {new_role} (was {old_role})."
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)