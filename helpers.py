import json
import uuid
import requests
import allure

BASE_URL = "https://stellarburgers.education-services.ru/api"

def generate_unique_email():
    return f"test_user_{uuid.uuid4().hex}@example.com"

def delete_user(access_token):
    if not access_token:
        return
    headers = {"Authorization": access_token} 
    try:
        requests.delete(f"{BASE_URL}/auth/user", headers=headers)
    except Exception:
        pass

def api_post(endpoint, data=None, headers=None):
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, json=data, headers=headers)
    with allure.step("Request"):
        allure.attach(json.dumps(data or {}, indent=2, ensure_ascii=False), "Body", allure.attachment_type.JSON)
    with allure.step(f"Response {response.status_code}"):
        try:
            resp_json = response.json()
        except:
            resp_json = {"raw": response.text}
        allure.attach(json.dumps(resp_json, indent=2, ensure_ascii=False), "Body", allure.attachment_type.JSON)
    return response