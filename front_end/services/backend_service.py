import requests
import streamlit as st
from typing import List, Dict, Any, Optional

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def handle_response(response, success_code=200):
    """Helper to check for HTTP errors and return JSON."""
    if response.status_code == success_code or (200 <= response.status_code < 300 and success_code != 204):
        if success_code == 204: # No content
            return True
        return response.json()
    else:
        try:
            detail = response.json().get("detail", "No detail provided.")
        except requests.exceptions.JSONDecodeError:
            detail = response.text
        st.error(f"API Error (Status {response.status_code}): {detail}")
        return None

# --- Analytics API ---
def get_analytics_dashboard() -> Optional[Dict[str, Any]]:
    response = requests.get(f"{BACKEND_URL}/analytics/dashboard")
    return handle_response(response)

# --- Admin User Management ---
def list_users() -> List[Dict[str, Any]]:
    response = requests.get(f"{BACKEND_URL}/admin/users/")
    data = handle_response(response)
    return data if data else []

def create_user(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = requests.post(f"{BACKEND_URL}/admin/users/", json=user_data)
    return handle_response(response, success_code=201)

# --- Admin Team Management ---
def list_teams() -> List[Dict[str, Any]]:
    response = requests.get(f"{BACKEND_URL}/admin/teams/")
    data = handle_response(response)
    return data if data else []

def create_team(team_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = requests.post(f"{BACKEND_URL}/admin/teams/", json=team_data)
    return handle_response(response, success_code=201)

# --- Admin Alert Management ---
def create_alert(alert_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = requests.post(f"{BACKEND_URL}/admin/alerts/", json=alert_data)
    return handle_response(response, success_code=201)

def get_all_alerts_for_admin(params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    response = requests.get(f"{BACKEND_URL}/admin/alerts/", params=params)
    data = handle_response(response)
    return data if data else []
    
def get_alert_by_id(alert_id: int) -> Optional[Dict[str, Any]]:
    response = requests.get(f"{BACKEND_URL}/admin/alerts/{alert_id}")
    return handle_response(response)

def update_alert(alert_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = requests.put(f"{BACKEND_URL}/admin/alerts/{alert_id}", json=update_data)
    return handle_response(response)

def archive_alert(alert_id: int) -> bool:
    response = requests.delete(f"{BACKEND_URL}/admin/alerts/{alert_id}")
    return handle_response(response, success_code=204) is not None

# --- Admin Actions ---
def trigger_reminders() -> Optional[Dict[str, Any]]:
    response = requests.post(f"{BACKEND_URL}/admin/alerts/trigger-reminders")
    return handle_response(response)

# --- End-User Alert Interaction ---
def get_alerts_for_user(user_id: int) -> List[Dict[str, Any]]:
    response = requests.get(f"{BACKEND_URL}/users/{user_id}/alerts")
    data = handle_response(response)
    return data if data else []

def mark_as_read(user_id: int, alert_id: int) -> bool:
    response = requests.post(f"{BACKEND_URL}/users/{user_id}/alerts/{alert_id}/read")
    return handle_response(response, success_code=204) is not None

def snooze_alert(user_id: int, alert_id: int) -> bool:
    response = requests.post(f"{BACKEND_URL}/users/{user_id}/alerts/{alert_id}/snooze")
    return handle_response(response, success_code=204) is not None