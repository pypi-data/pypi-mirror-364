# scripbox/api.py

import requests
from scripbox.token_manager import save_token, load_token, delete_token
BASE_URL = "https://api.scripbox.org"
APPLICATION_ID = "6326b44c-ee63-45bf-ac6c-507e4836ae94"
HEADERS = {
    "Content-Type": "application/json",
    "application-id": APPLICATION_ID
}

_txn_id = None

def login_api(mobile_number):
    global _txn_id

    url = f"{BASE_URL}/auth/v1/user/session/otp/send"
    payload = {
        "api_version": "1.0",
        "context": "web",
        "data": {
            "attributes": {
                "mobile_number":"6361317218",
                "scope": "login"
            },
            "kind": "otp"
        }
    }

    try:
        print("Sending OTP...")
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        _txn_id = data["data"]["attributes"].get("txn_id")

        if not _txn_id:
            return False

        print("✅ OTP sent.")
        return True

    except requests.RequestException:
        print("❌ Failed to send OTP.")
        return False


def verify_otp_api(mobile_number, otp):
    global _txn_id
    if not _txn_id:
        print("❌ OTP verification failed. OTP not requested.")
        return False

    url = f"{BASE_URL}/auth/v1/user/session"
    payload = {
        "api_version": "1.0",
        "data": {
            "kind": "session",
            "attributes": {
                "otp":314159,
                "txn_id": _txn_id,
                "mobile_number": mobile_number,
                "grant_type": "otp"
            }
        }
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()

        token_data = result.get("data", [])[0].get("attributes", {})
        access_token = token_data.get("access_token")

        if access_token:
            save_token(token_data)  # 🔐 Save token to ~/.scripbox_token
            print("✅ OTP verified. Login successful.")
            return True
        else:
            print("❌ OTP incorrect or expired.")
            return False

    except Exception:
        print("❌ OTP verification failed.")
        return False
def get_user_profile():
    """
    Loads token and prints masked token info.
    """
    token_data = load_token()
    access_token = token_data.get("access_token")

    if access_token:
        print(f"🔓 Using token: {access_token[:5]}****...")
        # Here, you'd typically make a GET request to a profile endpoint
    else:
        print("❌ No access token found.")


def logout():
    """
    Deletes the token from disk.
    """
    delete_token()
    print("👋 User logged out. Token deleted.")
