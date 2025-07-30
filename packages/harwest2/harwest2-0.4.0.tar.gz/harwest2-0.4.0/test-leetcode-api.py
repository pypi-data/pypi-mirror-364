import requests

# User credentials
USERNAME = "your_leetcode_username"
PASSWORD = "your_leetcode_password"

# Start session
session = requests.Session()

# Get the CSRF token from the login page first
resp = session.get("https://leetcode.com/accounts/login/")
csrf_token = session.cookies.get("csrftoken")

# Prepare headers and payload for login
headers = {
    "Referer": "https://leetcode.com/accounts/login/",
    "X-CSRFToken": csrf_token,
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0",
}

payload = {
    "login": USERNAME,
    "password": PASSWORD,
    "csrfmiddlewaretoken": csrf_token,
}

# Perform login
resp = session.post("https://leetcode.com/accounts/login/", data=payload, headers=headers)

# Check if login was successful
if resp.status_code == 200 and "LEETCODE_SESSION" in session.cookies:
    print("✅ Login successful")
    print("csrftoken:", session.cookies.get("csrftoken"))
    print("LEETCODE_SESSION:", session.cookies.get("LEETCODE_SESSION"))
else:
    print("❌ Login failed:", resp.status_code)
