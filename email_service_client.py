import requests


def send_email():
    url = "http://localhost:8001/email"  # Replace with the actual API endpoint URL
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Raise an exception for any HTTP errors (optional)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
