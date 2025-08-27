from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

class User(BaseModel):
    username: str
    status: str
    quota: str
    traffic_used: str
    expiry_date: str
    expiry_days: str
    enable: bool
    unlimited_ip: bool

    @staticmethod
    def from_dict(username: str, user_data: dict):
        user_data = {'username': username, **user_data}
        user_data = User.__parse_user_data(user_data)
        return User(**user_data)

    @staticmethod
    def __parse_user_data(user_data: dict) -> dict:
        essential_keys = [
            'password', 
            'max_download_bytes', 
            'expiration_days', 
            'blocked',
            'unlimited_user'
        ]

        if not all(key in user_data for key in essential_keys):
            return {
                'username': user_data.get('username', 'Unknown'),
                'status': 'Conflict',
                'quota': 'N/A',
                'traffic_used': 'N/A',
                'expiry_date': 'N/A',
                'expiry_days': 'N/A',
                'enable': False,
                'unlimited_ip': False
            }

        expiration_days = user_data.get('expiration_days', 0)
        creation_date_str = user_data.get("account_creation_date")

        if not creation_date_str:
            display_expiry_days = "On-hold"
            display_expiry_date = "On-hold"
        elif expiration_days <= 0:
            display_expiry_days = "Unlimited"
            display_expiry_date = "Unlimited"
        else:
            display_expiry_days = str(expiration_days)
            try:
                creation_date = datetime.strptime(creation_date_str, "%Y-%m-%d")
                expiry_dt_obj = creation_date + timedelta(days=expiration_days)
                display_expiry_date = expiry_dt_obj.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                display_expiry_date = "Error"

        used_bytes = user_data.get("download_bytes", 0) + user_data.get("upload_bytes", 0)
        quota_bytes = user_data.get('max_download_bytes', 0)
        
        used_formatted = User.__format_traffic(used_bytes)
        quota_formatted = "Unlimited" if quota_bytes <= 0 else User.__format_traffic(quota_bytes)
        
        percentage = 0
        if quota_bytes > 0:
            percentage = (used_bytes / quota_bytes) * 100
        
        traffic_used_display = f"{used_formatted}/{quota_formatted} ({percentage:.1f}%)"

        return {
            'username': user_data['username'],
            'status': user_data.get('status', 'Not Active'),
            'quota': quota_formatted,
            'traffic_used': traffic_used_display,
            'expiry_date': display_expiry_date,
            'expiry_days': display_expiry_days,
            'enable': not user_data.get('blocked', False),
            'unlimited_ip': user_data.get('unlimited_user', False)
        }

    @staticmethod
    def __format_traffic(traffic_bytes) -> str:
        if traffic_bytes <= 0:
            return "0 B"
        if traffic_bytes < 1024:
            return f'{traffic_bytes} B'
        elif traffic_bytes < 1024**2:
            return f'{traffic_bytes / 1024:.2f} KB'
        elif traffic_bytes < 1024**3:
            return f'{traffic_bytes / 1024**2:.2f} MB'
        else:
            return f'{traffic_bytes / 1024**3:.2f} GB'