from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
import json
import os
from pathlib import Path
from starlette.templating import Jinja2Templates

# Adjust this path to your actual users.json location
USERS_FILE = "/etc/hysteria/users.json"  # TODO: set correct path

# Template directory (reuse webpanel templates dir)
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[3] / "webpanel/templates"))

router = APIRouter()

@router.get("/subscription/{token}", response_class=HTMLResponse)
async def subscription_page(request: Request, token: str):
    if not os.path.isfile(USERS_FILE):
        raise HTTPException(status_code=404, detail="User database not found.")
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    user = None
    for u in users.values():
        if u.get("token") == token:
            user = u
            break
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    # Calculate usage and expiry
    max_bytes = user.get("max_download_bytes", 0)
    used_bytes = user.get("download_bytes", 0) + user.get("upload_bytes", 0)
    expire_days = user.get("expiration_days", 0)
    creation = user.get("account_creation_date", "-")
    blocked = user.get("blocked", False)
    unlimited = user.get("unlimited_user", False)
    status = user.get("status", "-")
    return templates.TemplateResponse("subscription.html", {
        "request": request,
        "user": user,
        "max_bytes": max_bytes,
        "used_bytes": used_bytes,
        "expire_days": expire_days,
        "creation": creation,
        "blocked": blocked,
        "unlimited": unlimited,
        "status": status,
    })
