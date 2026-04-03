"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                               ║
║   ██╗   ██╗███████╗ ██████╗████████╗╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗███████╗         ║
║   ██║   ██║██╔════╝██╔════╝╚══██╔══╝║     ████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝         ║
║   ██║   ██║█████╗  ██║        ██║   ║     ██╔██╗ ██║██║   ██║██║  ██║█████╗  ███████╗         ║
║   ╚██╗ ██╔╝██╔══╝  ██║        ██║   ║     ██║╚██╗██║██║   ██║██║  ██║██╔══╝  ╚════██║         ║
║    ╚████╔╝ ███████╗╚██████╗   ██║   ║     ██║ ╚████║╚██████╔╝██████╔╝███████╗███████║         ║
║     ╚═══╝  ╚══════╝ ╚═════╝   ╚═╝   ║     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝         ║
║                                                                                               ║
║                        ᴛʜᴇ ꜱᴛʀᴏɴɢᴇꜱᴛ ʜᴏꜱᴛɪɴɢ ᴘʟᴀᴛꜰᴏʀᴍ                                    ║
║                                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets
import string
import random
import re
import json
import os
import time
from typing import Dict, List, Optional, Any, Tuple

# ============================================================================
# ᴀᴘᴘʟɪᴄᴀᴛɪᴏɴ ɪɴɪᴛɪᴀʟɪᴢᴀᴛɪᴏɴ
# ============================================================================

app = Flask(__name__)
app.secret_key = "vecto_nodes_super_secret_key_2026_ultra_secure"
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ============================================================================
# ʜᴇʟᴘᴇʀ ꜰᴜɴᴄᴛɪᴏɴꜱ
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def generate_api_key() -> str:
    """Generate unique API key"""
    return f"vk_{secrets.token_hex(16)}"

def generate_server_password() -> str:
    """Generate random server password"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(chars) for _ in range(12))

def generate_reset_token() -> str:
    """Generate password reset token"""
    return secrets.token_urlsafe(32)

def generate_temp_password() -> str:
    """Generate temporary password"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(10))

def send_email_simulation(email: str, subject: str, body: str) -> bool:
    """Simulate sending email (for demo)"""
    print(f"\n{'='*60}")
    print(f"📧 EMAIL SIMULATION")
    print(f"{'='*60}")
    print(f"To: {email}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print(f"{'='*60}\n")
    return True

def get_user_location() -> str:
    """Get user location based on IP (simulated)"""
    if 'user_location' in session:
        return session['user_location']
    accept_language = request.headers.get('Accept-Language', '').lower()
    if 'in' in accept_language:
        session['user_location'] = 'IN'
        return 'IN'
    session['user_location'] = 'US'
    return 'US'

def get_price_for_location(plan: Dict) -> Dict:
    """Return price based on user location"""
    location = get_user_location()
    raw_price = plan.get('raw_price_usd', float(plan.get('price', '0').replace('$', '')))
    if location == 'IN':
        inr_price = int(raw_price * 84)
        return {
            "currency": "INR",
            "symbol": "₹",
            "price": f"₹{inr_price}",
            "price_raw": inr_price,
            "display": f"₹{inr_price}/month"
        }
    else:
        return {
            "currency": "USD",
            "symbol": "$",
            "price": f"${raw_price:.2f}",
            "price_raw": raw_price,
            "display": f"${raw_price:.2f}/month"
        }

def log_activity(user_email: str, action: str, details: str = "", ip: str = None):
    """Log user activity"""
    activity_logs.insert(0, {
        "id": str(uuid.uuid4())[:8],
        "user_email": user_email,
        "action": action,
        "details": details,
        "ip": ip or request.remote_addr,
        "timestamp": datetime.now().isoformat()
    })
    while len(activity_logs) > 1000:
        activity_logs.pop()

def add_review(user_email: str, product: str, rating: int, comment: str) -> Dict:
    """Add a review after purchase"""
    user = users.get(user_email, {})
    review = {
        "id": f"rev_{uuid.uuid4().hex[:6]}",
        "user_name": user.get("username", "Anonymous"),
        "user_avatar": user.get("avatar", "👤"),
        "rating": rating,
        "comment": comment,
        "product": product,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "verified": True,
        "user_email": user_email,
        "approved": False
    }
    reviews.insert(0, review)
    return review

def get_system_stats() -> Dict:
    """Get overall system statistics"""
    total_servers = sum(len(services) for services in user_services.values())
    active_servers = sum(1 for services in user_services.values() for s in services if s.get('status') == 'active')
    total_revenue = sum(o.get('price_raw', 0) for o in orders if o.get('status') == 'completed')
    
    return {
        "total_users": len(users),
        "total_servers": total_servers,
        "active_servers": active_servers,
        "total_orders": len(orders),
        "pending_orders": len([o for o in orders if o.get('status') == 'pending']),
        "completed_orders": len([o for o in orders if o.get('status') == 'completed']),
        "total_reviews": len(reviews),
        "approved_reviews": len([r for r in reviews if r.get('approved', False)]),
        "total_revenue": total_revenue,
        "uptime_current": 99.99,
        "response_time_avg": 124
    }

# ============================================================================
# ᴅᴇᴄᴏʀᴀᴛᴏʀꜱ
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_email' not in session:
            if request.is_json:
                return jsonify({"error": "ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", "code": "AUTH_REQUIRED"}), 401
            return redirect(url_for('login_page'))
        
        user = users.get(session['user_email'])
        if user and user.get('banned', False):
            session.clear()
            return redirect(url_for('login_page'))
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            if request.is_json:
                return jsonify({"error": "ᴀᴅᴍɪɴ ᴀᴄᴄᴇꜱꜱ ʀᴇQᴜɪʀᴇᴅ"}), 403
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ============================================================================
# ᴡᴇʙꜱɪᴛᴇ ꜱᴇᴛᴛɪɴɢꜱ (ᴄʜᴀɴɢᴇᴀʙʟᴇ ʙʏ ᴀᴅᴍɪɴ)
# ============================================================================

website_settings = {
    "site_name": "VECTŌ NODES",
    "site_name_small": "ᴠᴇᴄᴛō ɴᴏᴅᴇꜱ",
    "slogan": "ᴛʜᴇ ꜱᴛʀᴏɴɢᴇꜱᴛ ʜᴏꜱᴛɪɴɢ ᴘʟᴀᴛꜰᴏʀᴍ",
    "description": "Enterprise NVMe infrastructure for Minecraft, VPS & domains. Instant deployment, always-on protection, 24/7 support.",
    "uptime_guarantee": "99.99%",
    "main_page_gif": "https://media4.giphy.com/media/3o7abB06u9bNzA8LC8/giphy.gif",
    "vps_plans_gif": "https://media2.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif",
    "mc_plans_gif": "https://media1.giphy.com/media/3o7abKhOpu0N9H8OQ/giphy.gif",
    "bot_plans_gif": "https://media3.giphy.com/media/26BRv0ThflBHCxLOk/giphy.gif",
    "discord_plans_gif": "https://media4.giphy.com/media/l0MYEqEzwMWFCg8rm/giphy.gif",
    "footer_text": "© 2024 VECTŌ NODES. All rights reserved.",
    "contact_email": "support@vecto.nodes",
    "discord_invite": "https://discord.gg/vectonodes",
    "twitter_handle": "@vectonodes",
    "maintenance_mode": False,
    "registration_enabled": True,
    "cart_system_enabled": True
}

# ============================================================================
# ᴘᴀʏᴍᴇɴᴛ ᴅᴇᴛᴀɪʟꜱ (ᴄᴏɴꜰɪɢᴜʀᴀʙʟᴇ ʙʏ ᴀᴅᴍɪɴ)
# ============================================================================

payment_details = {
    "upi": {
        "enabled": True,
        "id": "vectonodes@okhdfcbank",
        "name": "VECTŌ NODES PVT LTD",
        "qr_code": ""
    },
    "bank_transfer": {
        "enabled": True,
        "account_name": "VECTŌ NODES PRIVATE LIMITED",
        "account_number": "1234567890123456",
        "ifsc_code": "HDFC0001234",
        "bank_name": "HDFC Bank",
        "branch": "Cyber City, Gurgaon",
        "account_type": "Current"
    },
    "crypto": {
        "enabled": True,
        "bitcoin": "bc1qxyz789abc456def123ghi789jklm456",
        "ethereum": "0xABCD1234EFGH5678IJKL9012MNOP3456QRST7890",
        "litecoin": "LTC_8x7c6v5b4n3m2a1s0d9f8g7h6j5k4l3",
        "usdt_trc20": "TXYZ789ABC123DEF456GHI789JKL012MNO345"
    }
}

# ============================================================================
# ᴘᴛᴇʀᴏᴅᴀᴄᴛʏʟ ᴘᴀɴᴇʟ ꜱᴇᴛᴜᴘ
# ============================================================================

ptero_settings = {
    "panel_url": "https://panel.vecto.nodes",
    "api_key": "ptero_" + secrets.token_hex(24),
    "location_id": "1",
    "node_id": "1",
    "nest_id": "1",
    "egg_id": "1",
    "enabled": True
}

# ============================================================================
# ᴠᴘꜱ ꜱᴇᴛᴜᴘ
# ============================================================================

vps_settings = {
    "panel_url": "https://vps.vecto.nodes",
    "api_key": "vps_" + secrets.token_hex(24),
    "hypervisor": "Proxmox",
    "default_os": "Ubuntu 22.04",
    "enabled": True
}

# ============================================================================
# ꜱᴇʀᴠᴇʀ ʟᴏᴄᴀᴛɪᴏɴꜱ
# ============================================================================

server_locations = [
    {"id": "us_east", "name": "🇺🇸 US East (Virginia)", "flag": "🇺🇸", "city": "Virginia", "country": "USA", "latency": "12ms", "enabled": True},
    {"id": "us_west", "name": "🇺🇸 US West (California)", "flag": "🇺🇸", "city": "California", "country": "USA", "latency": "28ms", "enabled": True},
    {"id": "eu_central", "name": "🇪🇺 EU Central (Frankfurt)", "flag": "🇪🇺", "city": "Frankfurt", "country": "Germany", "latency": "35ms", "enabled": True},
    {"id": "asia_south", "name": "🇮🇳 Asia South (Mumbai)", "flag": "🇮🇳", "city": "Mumbai", "country": "India", "latency": "45ms", "enabled": True},
    {"id": "asia_east", "name": "🇸🇬 Asia East (Singapore)", "flag": "🇸🇬", "city": "Singapore", "country": "Singapore", "latency": "89ms", "enabled": True},
    {"id": "au_south", "name": "🇦🇺 Australia (Sydney)", "flag": "🇦🇺", "city": "Sydney", "country": "Australia", "latency": "142ms", "enabled": True}
]

# ============================================================================
# ᴘᴀꜱꜱᴡᴏʀᴅ ʀᴇꜱᴇᴛ ᴛᴏᴋᴇɴꜱ
# ============================================================================

reset_tokens: Dict[str, Dict] = {}

# ============================================================================
# ʀᴇᴠɪᴇᴡꜱ ᴅᴀᴛᴀʙᴀꜱᴇ
# ============================================================================

reviews: List[Dict] = [
    {
        "id": "rev1", "user_name": "ᴀʀᴜɴ ᴋᴜᴍᴀʀ", "user_avatar": "👨‍💻", "rating": 5,
        "comment": "Best hosting platform I've ever used! The 99.99% uptime is real and support responds within minutes.",
        "product": "VPS Pro 8GB", "date": "2024-01-15", "verified": True, "approved": True
    },
    {
        "id": "rev2", "user_name": "ɴᴇʜᴀ ꜱʜᴀʀᴍᴀ", "user_avatar": "👩‍🎮", "rating": 5,
        "comment": "My Minecraft server runs flawlessly with zero lag. The panel is amazing!",
        "product": "Minecraft Pro 8GB", "date": "2024-01-20", "verified": True, "approved": True
    },
    {
        "id": "rev3", "user_name": "ʀᴀᴊ ᴠᴇʀᴍᴀ", "user_avatar": "🤖", "rating": 5,
        "comment": "Discord bot hosting is super reliable. 24/7 uptime and great pricing!",
        "product": "Bot Pro 2GB", "date": "2024-01-25", "verified": True, "approved": True
    },
    {
        "id": "rev4", "user_name": "ᴘʀɪʏᴀ ᴘᴀᴛᴇʟ", "user_avatar": "👩‍💼", "rating": 5,
        "comment": "Very satisfied with the VPS performance. Will definitely recommend!",
        "product": "VPS Business 16GB", "date": "2024-01-28", "verified": True, "approved": True
    }
]

# ============================================================================
# ᴀᴄᴛɪᴠɪᴛʏ ʟᴏɢꜱ
# ============================================================================

activity_logs: List[Dict] = [
    {"id": "log1", "user_email": "admin@vecto.co", "action": "SYSTEM_START", "details": "System started", "timestamp": datetime.now().isoformat(), "ip": "localhost"}
]

# ============================================================================
# ᴜꜱᴇʀ ᴅᴀᴛᴀʙᴀꜱᴇ
# ============================================================================

users: Dict[str, Dict] = {
    "admin@vecto.co": {
        "password": hash_password("admin123"),
        "username": "ᴀᴅᴍɪɴᴍᴀꜱᴛᴇʀ",
        "role": "admin",
        "avatar": "👑",
        "joined": "2024-01-01",
        "verified": True,
        "banned": False,
        "email_verified": True,
        "last_login": None,
        "login_count": 0,
        "location": "US",
        "api_key": generate_api_key(),
        "vps_api_key": generate_api_key(),
        "mc_api_key": generate_api_key(),
        "bot_api_key": generate_api_key(),
        "discord_api_key": generate_api_key(),
        "nitro_verified": True,
        "two_factor_enabled": False,
        "vps_password": generate_server_password(),
        "ptero_password": generate_server_password(),
        "vps_username": "admin_vps",
        "ptero_username": "admin_ptero"
    }
}

# ============================================================================
# ᴏʀᴅᴇʀꜱ, ꜱᴇʀᴠɪᴄᴇꜱ, ᴘᴀʏᴍᴇɴᴛꜱ
# ============================================================================

orders: List[Dict] = []
user_services: Dict[str, List[Dict]] = {}
payments: List[Dict] = []
order_counter = 1000
payment_counter = 5000

# ============================================================================
# ᴠᴘꜱ ᴘʟᴀɴꜱ - ʙᴀꜱɪᴄ, ᴘᴏᴡᴇʀꜰᴜʟ, ᴇʟɪᴛᴇ
# ============================================================================

vps_basic_plans: List[Dict] = [
    {"id": "vps_basic_2", "type": "vps", "category": "basic", "name": "ʙᴀꜱɪᴄ ᴠᴘꜱ 2GB 💻", "ram": "2GB DDR5", "cpu": "1 vCore AMD EPYC", "storage": "50GB NVMe", "bandwidth": "2TB/mo", "price": "$6.99", "raw_price_usd": 6.99, "enabled": True, "popular": False, "backup": False, "ddos": True, "location": "us_east"},
    {"id": "vps_basic_4", "type": "vps", "category": "basic", "name": "ʙᴀꜱɪᴄ ᴠᴘꜱ 4GB 💪", "ram": "4GB DDR5", "cpu": "2 vCores AMD EPYC", "storage": "80GB NVMe", "bandwidth": "5TB/mo", "price": "$12.99", "raw_price_usd": 12.99, "enabled": True, "popular": True, "backup": True, "ddos": True, "location": "us_east"},
    {"id": "vps_basic_6", "type": "vps", "category": "basic", "name": "ʙᴀꜱɪᴄ ᴠᴘꜱ 6GB 🚀", "ram": "6GB DDR5", "cpu": "3 vCores AMD EPYC", "storage": "120GB NVMe", "bandwidth": "8TB/mo", "price": "$18.99", "raw_price_usd": 18.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "eu_central"},
    {"id": "vps_basic_8", "type": "vps", "category": "basic", "name": "ʙᴀꜱɪᴄ ᴠᴘꜱ 8GB 🔥", "ram": "8GB DDR5", "cpu": "4 vCores AMD EPYC", "storage": "160GB NVMe", "bandwidth": "10TB/mo", "price": "$24.99", "raw_price_usd": 24.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "asia_south"}
]

vps_powerful_plans: List[Dict] = [
    {"id": "vps_power_12", "type": "vps", "category": "powerful", "name": "ᴘᴏᴡᴇʀꜰᴜʟ ᴠᴘꜱ 12GB ⚡", "ram": "12GB DDR5", "cpu": "6 vCores AMD EPYC", "storage": "240GB NVMe", "bandwidth": "15TB/mo", "price": "$39.99", "raw_price_usd": 39.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "us_west"},
    {"id": "vps_power_14", "type": "vps", "category": "powerful", "name": "ᴘᴏᴡᴇʀꜰᴜʟ ᴠᴘꜱ 14GB 💥", "ram": "14GB DDR5", "cpu": "7 vCores AMD EPYC", "storage": "280GB NVMe", "bandwidth": "18TB/mo", "price": "$49.99", "raw_price_usd": 49.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "eu_central"},
    {"id": "vps_power_16", "type": "vps", "category": "powerful", "name": "ᴘᴏᴡᴇʀꜰᴜʟ ᴠᴘꜱ 16GB 🦾", "ram": "16GB DDR5", "cpu": "8 vCores AMD EPYC", "storage": "320GB NVMe", "bandwidth": "20TB/mo", "price": "$59.99", "raw_price_usd": 59.99, "enabled": True, "popular": True, "backup": True, "ddos": True, "location": "us_east"},
    {"id": "vps_power_18", "type": "vps", "category": "powerful", "name": "ᴘᴏᴡᴇʀꜰᴜʟ ᴠᴘꜱ 18GB 🎯", "ram": "18GB DDR5", "cpu": "9 vCores AMD EPYC", "storage": "360GB NVMe", "bandwidth": "22TB/mo", "price": "$69.99", "raw_price_usd": 69.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "asia_south"},
    {"id": "vps_power_20", "type": "vps", "category": "powerful", "name": "ᴘᴏᴡᴇʀꜰᴜʟ ᴠᴘꜱ 20GB 🏆", "ram": "20GB DDR5", "cpu": "10 vCores AMD EPYC", "storage": "400GB NVMe", "bandwidth": "25TB/mo", "price": "$79.99", "raw_price_usd": 79.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "us_west"},
    {"id": "vps_power_24", "type": "vps", "category": "powerful", "name": "ᴘᴏᴡᴇʀꜰᴜʟ ᴠᴘꜱ 24GB 👑", "ram": "24GB DDR5", "cpu": "12 vCores AMD EPYC", "storage": "480GB NVMe", "bandwidth": "30TB/mo", "price": "$99.99", "raw_price_usd": 99.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "eu_central"}
]

vps_elite_plans: List[Dict] = [
    {"id": "vps_elite_32", "type": "vps", "category": "elite", "name": "ᴇʟɪᴛᴇ ᴠᴘꜱ 32GB 🧬", "ram": "32GB DDR5", "cpu": "16 vCores AMD EPYC", "storage": "640GB NVMe", "bandwidth": "40TB/mo", "price": "$149.99", "raw_price_usd": 149.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "us_east"},
    {"id": "vps_elite_64", "type": "vps", "category": "elite", "name": "ᴇʟɪᴛᴇ ᴠᴘꜱ 64GB 🚀", "ram": "64GB DDR5", "cpu": "24 vCores AMD EPYC", "storage": "1TB NVMe", "bandwidth": "60TB/mo", "price": "$249.99", "raw_price_usd": 249.99, "enabled": True, "popular": True, "backup": True, "ddos": True, "location": "us_west"},
    {"id": "vps_elite_128", "type": "vps", "category": "elite", "name": "ᴇʟɪᴛᴇ ᴠᴘꜱ 128GB 💎", "ram": "128GB DDR5", "cpu": "32 vCores AMD EPYC", "storage": "2TB NVMe", "bandwidth": "100TB/mo", "price": "$449.99", "raw_price_usd": 449.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "eu_central"},
    {"id": "vps_elite_256", "type": "vps", "category": "elite", "name": "ᴇʟɪᴛᴇ ᴠᴘꜱ 256GB 👑", "ram": "256GB DDR5", "cpu": "48 vCores AMD EPYC", "storage": "4TB NVMe", "bandwidth": "200TB/mo", "price": "$849.99", "raw_price_usd": 849.99, "enabled": True, "popular": False, "backup": True, "ddos": True, "location": "asia_south"}
]

# ============================================================================
# ᴍᴄ (ᴍɪɴᴇᴄʀᴀꜰᴛ) ᴘʟᴀɴꜱ
# ============================================================================

mc_plans: List[Dict] = [
    {"id": "mc_4", "type": "mc", "name": "ᴍᴄ 4GB 🎮", "ram": "4GB DDR5", "cpu": "2 vCores", "storage": "40GB NVMe", "slots": "50", "price": "$9.99", "raw_price_usd": 9.99, "enabled": True, "popular": False, "location": "us_east"},
    {"id": "mc_6", "type": "mc", "name": "ᴍᴄ 6GB ⚔️", "ram": "6GB DDR5", "cpu": "3 vCores", "storage": "60GB NVMe", "slots": "75", "price": "$14.99", "raw_price_usd": 14.99, "enabled": True, "popular": False, "location": "eu_central"},
    {"id": "mc_8", "type": "mc", "name": "ᴍᴄ 8GB 🔥", "ram": "8GB DDR5", "cpu": "4 vCores", "storage": "80GB NVMe", "slots": "100", "price": "$19.99", "raw_price_usd": 19.99, "enabled": True, "popular": True, "location": "us_east"},
    {"id": "mc_12", "type": "mc", "name": "ᴍᴄ 12GB 👑", "ram": "12GB DDR5", "cpu": "6 vCores", "storage": "120GB NVMe", "slots": "150", "price": "$29.99", "raw_price_usd": 29.99, "enabled": True, "popular": False, "location": "asia_south"},
    {"id": "mc_16", "type": "mc", "name": "ᴍᴄ 16GB 🚀", "ram": "16GB DDR5", "cpu": "8 vCores", "storage": "160GB NVMe", "slots": "200", "price": "$39.99", "raw_price_usd": 39.99, "enabled": True, "popular": False, "location": "us_west"}
]

# ============================================================================
# ʙᴏᴛ ᴘʟᴀɴꜱ
# ============================================================================

bot_plans: List[Dict] = [
    {"id": "bot_1", "type": "bot", "name": "ʙᴏᴛ 1GB 🤖", "ram": "1GB DDR5", "cpu": "1 vCore", "storage": "10GB NVMe", "servers": "10", "price": "$4.99", "raw_price_usd": 4.99, "enabled": True, "popular": False, "location": "us_east"},
    {"id": "bot_2", "type": "bot", "name": "ʙᴏᴛ 2GB ⚡", "ram": "2GB DDR5", "cpu": "2 vCores", "storage": "25GB NVMe", "servers": "50", "price": "$9.99", "raw_price_usd": 9.99, "enabled": True, "popular": True, "location": "eu_central"},
    {"id": "bot_4", "type": "bot", "name": "ʙᴏᴛ 4GB 🚀", "ram": "4GB DDR5", "cpu": "4 vCores", "storage": "50GB NVMe", "servers": "200", "price": "$19.99", "raw_price_usd": 19.99, "enabled": True, "popular": False, "location": "asia_south"},
    {"id": "bot_8", "type": "bot", "name": "ʙᴏᴛ 8GB 💎", "ram": "8GB DDR5", "cpu": "8 vCores", "storage": "100GB NVMe", "servers": "500", "price": "$39.99", "raw_price_usd": 39.99, "enabled": True, "popular": False, "location": "us_west"}
]

# ============================================================================
# ᴅɪꜱᴄᴏʀᴅ/ɴɪᴛʀᴏ ᴘʟᴀɴꜱ
# ============================================================================

discord_plans: List[Dict] = [
    {"id": "nitro_basic", "type": "discord", "name": "ɴɪᴛʀᴏ ʙᴀꜱɪᴄ 💎", "features": "Custom Emojis, Nitro Badge, 2 Server Boosts", "duration": "1 Month", "price": "$2.99", "raw_price_usd": 2.99, "enabled": True, "popular": False},
    {"id": "nitro_pro", "type": "discord", "name": "ɴɪᴛʀᴏ ᴘʀᴏ ✨", "features": "HD Streaming, Nitro Badge, 5 Server Boosts, Custom Stickers", "duration": "1 Month", "price": "$4.99", "raw_price_usd": 4.99, "enabled": True, "popular": True},
    {"id": "nitro_trial", "type": "discord", "name": "ɴɪᴛʀᴏ ᴛʀɪᴀʟ 🎁", "features": "Test Features, 1 Server Boost", "duration": "3 Days", "price": "$0.99", "raw_price_usd": 0.99, "enabled": True, "popular": False},
    {"id": "nitro_yearly", "type": "discord", "name": "ɴɪᴛʀᴏ ᴘʀᴏ ʏᴇᴀʀʟʏ 🎯", "features": "All Pro Features + 10% OFF", "duration": "12 Months", "price": "$49.99", "raw_price_usd": 49.99, "enabled": True, "popular": False}
]

# ============================================================================
# ᴄᴏᴍʙɪɴᴇᴅ ᴘʟᴀɴꜱ (ꜰᴏʀ ᴛᴇᴍᴘʟᴀᴛᴇꜱ)
# ============================================================================

all_plans = vps_basic_plans + vps_powerful_plans + vps_elite_plans + mc_plans + bot_plans + discord_plans

# ============================================================================
# ʀᴏᴜᴛᴇꜱ - ᴘᴜʙʟɪᴄ ᴘᴀɢᴇꜱ
# ============================================================================

@app.route('/')
def index():
    """Home page with GIF support and reviews"""
    if website_settings.get('maintenance_mode', False):
        return render_template('maintenance.html', settings=website_settings)
    
    return render_template('index.html',
                         settings=website_settings,
                         vps_basic_plans=vps_basic_plans,
                         vps_powerful_plans=vps_powerful_plans,
                         vps_elite_plans=vps_elite_plans,
                         mc_plans=mc_plans,
                         bot_plans=bot_plans,
                         discord_plans=discord_plans,
                         reviews=[r for r in reviews if r.get('approved', True)],
                         server_locations=server_locations,
                         payment_details=payment_details,
                         get_price_for_location=get_price_for_location,
                         get_location_name=lambda x: next((loc['name'] for loc in server_locations if loc['id'] == x), 'US East'))

@app.route('/login')
def login_page():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html', settings=website_settings)

@app.route('/register')
def register_page():
    if not website_settings.get('registration_enabled', True):
        return render_template('registration_closed.html', settings=website_settings)
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html', settings=website_settings)

@app.route('/forgot-password')
def forgot_page():
    return render_template('forgot.html', settings=website_settings)

@app.route('/reset-password/<token>')
def reset_password_page(token):
    return render_template('reset_password.html', token=token, settings=website_settings)

@app.route('/dashboard')
@login_required
def dashboard():
    user_email = session['user_email']
    user = users.get(user_email, {})
    services = user_services.get(user_email, [])
    
    api_keys = {
        "vps": user.get("vps_api_key", generate_api_key()),
        "mc": user.get("mc_api_key", generate_api_key()),
        "bot": user.get("bot_api_key", generate_api_key()),
        "discord": user.get("discord_api_key", generate_api_key())
    }
    
    return render_template('dashboard.html',
                         user=user,
                         services=services,
                         api_keys=api_keys,
                         settings=website_settings,
                         stats=get_system_stats())

@app.route('/user/profile')
@login_required
def user_profile():
    user_email = session['user_email']
    user = users.get(user_email, {})
    return render_template('user_profile.html', user=user, settings=website_settings)

@app.route('/user/orders')
@login_required
def user_orders():
    user_orders_list = [o for o in orders if o.get('user_email') == session['user_email']]
    return render_template('user_orders.html', orders=user_orders_list, settings=website_settings)

@app.route('/user/api-keys')
@login_required
def user_api_keys():
    user_email = session['user_email']
    user = users.get(user_email, {})
    api_keys = {
        "api_key": user.get("api_key"),
        "vps_api_key": user.get("vps_api_key"),
        "mc_api_key": user.get("mc_api_key"),
        "bot_api_key": user.get("bot_api_key"),
        "discord_api_key": user.get("discord_api_key")
    }
    return render_template('user_api_keys.html', api_keys=api_keys, settings=website_settings)

@app.route('/vps-panel')
@login_required
def vps_panel():
    user = users.get(session['user_email'], {})
    return render_template('vps_panel.html',
                         user=user,
                         vps_basic_plans=vps_basic_plans,
                         vps_powerful_plans=vps_powerful_plans,
                         vps_elite_plans=vps_elite_plans,
                         server_locations=server_locations,
                         get_price_for_location=get_price_for_location,
                         settings=website_settings)

@app.route('/mc-panel')
@login_required
def mc_panel():
    user = users.get(session['user_email'], {})
    return render_template('mc_panel.html',
                         user=user,
                         mc_plans=mc_plans,
                         server_locations=server_locations,
                         get_price_for_location=get_price_for_location,
                         settings=website_settings)

@app.route('/bot-panel')
@login_required
def bot_panel():
    user = users.get(session['user_email'], {})
    return render_template('bot_panel.html',
                         user=user,
                         bot_plans=bot_plans,
                         server_locations=server_locations,
                         get_price_for_location=get_price_for_location,
                         settings=website_settings)

@app.route('/discord-panel')
@login_required
def discord_panel():
    user = users.get(session['user_email'], {})
    return render_template('discord_panel.html',
                         user=user,
                         discord_plans=discord_plans,
                         get_price_for_location=get_price_for_location,
                         settings=website_settings)

# ============================================================================
# ᴀᴅᴍɪɴ ʀᴏᴜᴛᴇꜱ
# ============================================================================

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html',
                         settings=website_settings,
                         users=users,
                         orders=orders,
                         all_plans=all_plans,
                         reviews=reviews,
                         activity_logs=activity_logs[:100],
                         stats=get_system_stats(),
                         payment_details=payment_details,
                         ptero_settings=ptero_settings,
                         vps_settings=vps_settings,
                         server_locations=server_locations)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html',
                         settings=website_settings,
                         stats=get_system_stats(),
                         recent_orders=orders[:10],
                         recent_users=list(users.items())[:10],
                         activity_logs=activity_logs[:20])

@app.route('/admin/users')
@admin_required
def admin_users():
    return render_template('admin_users.html', settings=website_settings, users=users)

@app.route('/admin/plans')
@admin_required
def admin_plans():
    return render_template('admin_plans.html',
                         settings=website_settings,
                         vps_basic_plans=vps_basic_plans,
                         vps_powerful_plans=vps_powerful_plans,
                         vps_elite_plans=vps_elite_plans,
                         mc_plans=mc_plans,
                         bot_plans=bot_plans,
                         discord_plans=discord_plans)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    return render_template('admin_orders.html', settings=website_settings, orders=orders)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin_settings.html', settings=website_settings, payment_details=payment_details)

@app.route('/admin/vps-setup')
@admin_required
def admin_vps_setup():
    return render_template('admin_vps_setup.html', settings=website_settings, vps_settings=vps_settings)

@app.route('/admin/ptero-setup')
@admin_required
def admin_ptero_setup():
    return render_template('admin_ptero_setup.html', settings=website_settings, ptero_settings=ptero_settings)

@app.route('/admin/create-user')
@admin_required
def admin_create_user():
    return render_template('admin_create_user.html', settings=website_settings)

@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    return render_template('admin_reviews.html', settings=website_settings, reviews=reviews)

@app.route('/admin/logs')
@admin_required
def admin_logs():
    return render_template('admin_logs.html', settings=website_settings, logs=activity_logs)

# ============================================================================
# ᴀᴘɪ ᴇɴᴅᴘᴏɪɴᴛꜱ - ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ
# ============================================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    if not website_settings.get('registration_enabled', True):
        return jsonify({"success": False, "message": "Registration is currently disabled"}), 400
    
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    username = data.get('username', '').strip()
    confirm_password = data.get('confirm_password', '')
    
    if not email or not password or not username:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
    
    if len(username) < 3:
        return jsonify({"success": False, "message": "Username must be at least 3 characters"}), 400
    
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return jsonify({"success": False, "message": "Invalid email format"}), 400
    
    if email in users:
        return jsonify({"success": False, "message": "Email already registered"}), 400
    
    users[email] = {
        "password": hash_password(password),
        "username": username,
        "role": "user",
        "avatar": "👤",
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "verified": True,
        "banned": False,
        "email_verified": True,
        "last_login": None,
        "login_count": 0,
        "api_key": generate_api_key(),
        "vps_api_key": generate_api_key(),
        "mc_api_key": generate_api_key(),
        "bot_api_key": generate_api_key(),
        "discord_api_key": generate_api_key(),
        "nitro_verified": False,
        "two_factor_enabled": False,
        "vps_password": generate_server_password(),
        "ptero_password": generate_server_password(),
        "vps_username": username[:10],
        "ptero_username": username[:10]
    }
    
    log_activity(email, "REGISTER", "New user registered")
    
    send_email_simulation(email, "Welcome to VECTŌ NODES!",
                         f"Hello {username},\n\nWelcome to VECTŌ NODES! Your account has been created successfully.\n\n"
                         f"Get started at: https://vecto.nodes/dashboard\n\nThank you for choosing us!")
    
    return jsonify({"success": True, "message": "Registration successful! Please login."})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400
    
    if email not in users:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    user = users[email]
    
    if user.get('banned', False):
        return jsonify({"success": False, "message": "Account has been banned"}), 403
    
    if not verify_password(password, user['password']):
        log_activity(email, "LOGIN_FAILED", "Invalid password attempt")
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    user['last_login'] = datetime.now().isoformat()
    user['login_count'] = user.get('login_count', 0) + 1
    
    session.permanent = remember_me
    session['user_email'] = email
    session['role'] = user.get('role', 'user')
    session['username'] = user.get('username')
    
    log_activity(email, "LOGIN", "User logged in")
    
    redirect_url = "/admin" if session['role'] == 'admin' else "/dashboard"
    
    return jsonify({"success": True, "role": session['role'], "redirect": redirect_url})

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    email = session.get('user_email')
    log_activity(email, "LOGOUT", "User logged out")
    session.clear()
    return jsonify({"success": True, "redirect": "/"})

# ============================================================================
# ᴀᴘɪ ᴇɴᴅᴘᴏɪɴᴛꜱ - ᴘᴀꜱꜱᴡᴏʀᴅ ʀᴇꜱᴇᴛ
# ============================================================================

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.json
    email = data.get('email', '').lower().strip()
    
    if email not in users:
        return jsonify({"success": True, "message": "If email exists, reset instructions will be sent"})
    
    token = generate_reset_token()
    temp_password = generate_temp_password()
    
    reset_tokens[email] = {
        "token": token,
        "temp_password": hash_password(temp_password),
        "expires": (datetime.now() + timedelta(hours=1)).isoformat()
    }
    
    reset_link = f"https://vecto.nodes/reset-password/{token}"
    
    email_body = f"""
Hello {users[email]['username']},

You requested a password reset for your VECTŌ NODES account.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 TEMPORARY PASSWORD: {temp_password}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click the link below to reset your password:
{reset_link}

This link expires in 1 hour.

If you didn't request this, please ignore this email or contact support.

Best regards,
VECTŌ NODES Team
"""
    
    send_email_simulation(email, "Password Reset - VECTŌ NODES", email_body)
    log_activity(email, "PASSWORD_RESET_REQUEST", "Password reset requested")
    
    return jsonify({"success": True, "message": "Reset instructions sent to your email"})

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    data = request.json
    email = data.get('email', '').lower().strip()
    token = data.get('token', '')
    temp_password = data.get('temp_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if email not in reset_tokens:
        return jsonify({"success": False, "message": "Invalid or expired request"}), 400
    
    reset_data = reset_tokens[email]
    
    if reset_data['token'] != token:
        return jsonify({"success": False, "message": "Invalid token"}), 400
    
    if datetime.fromisoformat(reset_data['expires']) < datetime.now():
        del reset_tokens[email]
        return jsonify({"success": False, "message": "Reset token has expired"}), 400
    
    if not verify_password(temp_password, reset_data['temp_password']):
        return jsonify({"success": False, "message": "Invalid temporary password"}), 400
    
    if new_password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400
    
    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
    
    users[email]['password'] = hash_password(new_password)
    del reset_tokens[email]
    
    log_activity(email, "PASSWORD_RESET", "Password successfully reset")
    
    send_email_simulation(email, "Password Changed - VECTŌ NODES",
                         f"Hello {users[email]['username']},\n\nYour password has been successfully changed.\n\n"
                         f"If this wasn't you, please contact support immediately.\n\nVECTŌ NODES Team")
    
    return jsonify({"success": True, "message": "Password reset successful! Please login."})

# ============================================================================
# ᴀᴘɪ ᴇɴᴅᴘᴏɪɴᴛꜱ - ᴜꜱᴇʀ ᴘʀᴏꜰɪʟᴇ & ꜱᴇᴛᴛɪɴɢꜱ
# ============================================================================

@app.route('/api/user/profile', methods=['GET'])
@login_required
def api_get_user_profile():
    user = users.get(session['user_email'], {})
    return jsonify({
        "username": user.get('username'),
        "avatar": user.get('avatar'),
        "email": session['user_email'],
        "joined": user.get('joined'),
        "vps_username": user.get('vps_username'),
        "vps_password": user.get('vps_password'),
        "ptero_username": user.get('ptero_username'),
        "ptero_password": user.get('ptero_password'),
        "api_key": user.get('api_key'),
        "vps_api_key": user.get('vps_api_key'),
        "mc_api_key": user.get('mc_api_key'),
        "bot_api_key": user.get('bot_api_key'),
        "discord_api_key": user.get('discord_api_key')
    })

@app.route('/api/update-profile', methods=['POST'])
@login_required
def api_update_profile():
    data = request.json
    email = session['user_email']
    user = users[email]
    
    if 'username' in data:
        user['username'] = data['username']
    
    if 'avatar' in data:
        user['avatar'] = data['avatar']
    
    if 'current_password' in data and 'new_password' in data:
        if verify_password(data['current_password'], user['password']):
            if len(data['new_password']) >= 6:
                user['password'] = hash_password(data['new_password'])
                log_activity(email, "PASSWORD_CHANGED", "User changed password")
                return jsonify({"success": True, "message": "Password changed successfully!"})
            else:
                return jsonify({"success": False, "message": "New password must be at least 6 characters"}), 400
        else:
            return jsonify({"success": False, "message": "Current password is incorrect"}), 400
    
    log_activity(email, "PROFILE_UPDATED", "User updated profile")
    return jsonify({"success": True, "message": "Profile updated successfully!"})

@app.route('/api/regenerate-api-key', methods=['POST'])
@login_required
def api_regenerate_api_key():
    data = request.json
    key_type = data.get('key_type', 'api_key')
    email = session['user_email']
    
    valid_keys = ['api_key', 'vps_api_key', 'mc_api_key', 'bot_api_key', 'discord_api_key']
    if key_type in valid_keys:
        users[email][key_type] = generate_api_key()
        log_activity(email, "API_KEY_REGENERATED", f"Regenerated {key_type}")
        return jsonify({"success": True, "api_key": users[email][key_type]})
    
    return jsonify({"success": False, "message": "Invalid key type"}), 400

# ============================================================================
# ᴀᴘɪ ᴇɴᴅᴘᴏɪɴᴛꜱ - ᴏʀᴅᴇʀꜱ & ᴄᴀʀᴛ
# ============================================================================

@app.route('/api/create-order', methods=['POST'])
@login_required
def api_create_order():
    if not website_settings.get('cart_system_enabled', True):
        return jsonify({"success": False, "message": "Cart system is currently disabled"}), 400
    
    data = request.json
    global order_counter
    order_counter += 1
    
    plan = None
    for p in all_plans:
        if p['id'] == data.get('plan_id'):
            plan = p
            break
    
    if not plan:
        return jsonify({"success": False, "message": "Plan not found"}), 404
    
    location_price = get_price_for_location(plan)
    
    order = {
        "id": f"ORD-{order_counter}",
        "user_email": session['user_email'],
        "plan_id": plan['id'],
        "plan_name": plan['name'],
        "plan_type": plan.get('type', 'vps'),
        "price": location_price['price'],
        "price_raw": location_price['price_raw'],
        "currency": location_price['currency'],
        "status": "pending",
        "location": data.get('location', 'us_east'),
        "created_at": datetime.now().isoformat()
    }
    orders.append(order)
    
    log_activity(session['user_email'], "ORDER_CREATED", f"Order {order['id']} for {plan['name']}")
    
    return jsonify({
        "success": True,
        "order_id": order['id'],
        "payment_details": payment_details,
        "amount": location_price['price'],
        "currency": location_price['currency']
    })

@app.route('/api/confirm-order/<order_id>', methods=['POST'])
@login_required
def api_confirm_order(order_id):
    for order in orders:
        if order.get('id') == order_id and order.get('user_email') == session['user_email']:
            if order['status'] != 'pending':
                return jsonify({"success": False, "message": f"Order already {order['status']}"}), 400
            
            order['status'] = 'pending_approval'
            order['payment_confirmed'] = True
            order['payment_confirmed_at'] = datetime.now().isoformat()
            
            log_activity(session['user_email'], "ORDER_PAYMENT_CONFIRMED", f"Payment confirmed for {order_id}")
            
            return jsonify({
                "success": True,
                "message": "Payment confirmed! Waiting for admin approval.",
                "order_id": order_id
            })
    
    return jsonify({"success": False, "message": "Order not found"}), 404

@app.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    user_orders = [o for o in orders if o.get('user_email') == session['user_email']]
    return jsonify(user_orders)

@app.route('/api/services', methods=['GET'])
@login_required
def api_get_services():
    services = user_services.get(session['user_email'], [])
    return jsonify(services)

@app.route('/api/service/<service_id>/<action>', methods=['POST'])
@login_required
def api_service_action(service_id, action):
    if action not in ['start', 'stop', 'restart', 'renew', 'cancel']:
        return jsonify({"error": "Invalid action"}), 400
    
    services = user_services.get(session['user_email'], [])
    for service in services:
        if service.get('service_id') == service_id:
            if action == 'start':
                service['status'] = 'active'
            elif action == 'stop':
                service['status'] = 'stopped'
            elif action == 'restart':
                service['status'] = 'restarting'
            elif action == 'renew':
                new_expiry = datetime.fromisoformat(service['expires_at']) + timedelta(days=30)
                service['expires_at'] = new_expiry.isoformat()
            elif action == 'cancel':
                service['status'] = 'cancelled'
            
            log_activity(session['user_email'], f"SERVICE_{action.upper()}", f"Action {action} on {service_id}")
            return jsonify({"success": True, "status": service.get('status', 'active')})
    
    return jsonify({"success": False, "message": "Service not found"}), 404

# ============================================================================
# ᴀᴘɪ ᴇɴᴅᴘᴏɪɴᴛꜱ - ʀᴇᴠɪᴇᴡꜱ
# ============================================================================

@app.route('/api/add-review', methods=['POST'])
@login_required
def api_add_review():
    data = request.json
    product = data.get('product', '')
    rating = data.get('rating', 5)
    comment = data.get('comment', '')
    
    if not comment:
        return jsonify({"success": False, "message": "Please write a review"}), 400
    
    if rating < 1 or rating > 5:
        return jsonify({"success": False, "message": "Rating must be between 1 and 5"}), 400
    
    review = add_review(session['user_email'], product, rating, comment)
    log_activity(session['user_email'], "REVIEW_ADDED", f"Added review for {product}")
    
    return jsonify({"success": True, "review": review})

@app.route('/api/reviews', methods=['GET'])
def api_get_reviews():
    return jsonify([r for r in reviews if r.get('approved', True)])

# ============================================================================
# ᴀᴘɪ ᴇɴᴅᴘᴏɪɴᴛꜱ - ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ
# ============================================================================

@app.route('/api/admin/website-settings', methods=['GET', 'PUT'])
@admin_required
def api_admin_website_settings():
    if request.method == 'GET':
        return jsonify(website_settings)
    
    elif request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            if key in website_settings:
                website_settings[key] = value
        log_activity(session['user_email'], "ADMIN_SETTINGS_UPDATED", "Website settings updated")
        return jsonify({"success": True, "settings": website_settings})

@app.route('/api/admin/payment-details', methods=['GET', 'PUT'])
@admin_required
def api_admin_payment_details():
    if request.method == 'GET':
        return jsonify(payment_details)
    
    elif request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            if key in payment_details:
                if isinstance(value, dict):
                    payment_details[key].update(value)
                else:
                    payment_details[key] = value
        log_activity(session['user_email'], "ADMIN_PAYMENT_UPDATED", "Payment details updated")
        return jsonify({"success": True, "payment_details": payment_details})

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def api_admin_get_users():
    user_list = []
    for email, user in users.items():
        user_list.append({
            "email": email,
            "username": user.get('username'),
            "role": user.get('role'),
            "joined": user.get('joined'),
            "login_count": user.get('login_count', 0),
            "banned": user.get('banned', False),
            "verified": user.get('verified', False),
            "avatar": user.get('avatar', '👤')
        })
    return jsonify(user_list)

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def api_admin_create_user():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    username = data.get('username', '').strip()
    role = data.get('role', 'user')
    
    if email in users:
        return jsonify({"success": False, "message": "Email already exists"}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password too short"}), 400
    
    users[email] = {
        "password": hash_password(password),
        "username": username,
        "role": role,
        "avatar": "👤",
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "verified": True,
        "banned": False,
        "email_verified": True,
        "last_login": None,
        "login_count": 0,
        "api_key": generate_api_key(),
        "vps_api_key": generate_api_key(),
        "mc_api_key": generate_api_key(),
        "bot_api_key": generate_api_key(),
        "discord_api_key": generate_api_key(),
        "nitro_verified": False,
        "two_factor_enabled": False,
        "vps_password": generate_server_password(),
        "ptero_password": generate_server_password(),
        "vps_username": username[:10],
        "ptero_username": username[:10]
    }
    
    log_activity(session['user_email'], "ADMIN_CREATE_USER", f"Created user: {email}")
    return jsonify({"success": True, "message": "User created successfully!", "user": users[email]})

@app.route('/api/admin/users/<email>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_user(email):
    if email not in users:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    if request.method == 'PUT':
        data = request.json
        user = users[email]
        
        if 'role' in data and email != 'admin@vecto.co':
            user['role'] = data['role']
        if 'banned' in data:
            user['banned'] = data['banned']
        if 'username' in data:
            user['username'] = data['username']
        
        log_activity(session['user_email'], "ADMIN_UPDATE_USER", f"Updated user: {email}")
        return jsonify({"success": True})
    
    elif request.method == 'DELETE':
        if email == 'admin@vecto.co':
            return jsonify({"success": False, "message": "Cannot delete main admin"}), 403
        
        del users[email]
        if email in user_services:
            del user_services[email]
        
        log_activity(session['user_email'], "ADMIN_DELETE_USER", f"Deleted user: {email}")
        return jsonify({"success": True})

@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def api_admin_get_orders():
    return jsonify(orders)

@app.route('/api/admin/orders/<order_id>/status', methods=['PUT'])
@admin_required
def api_admin_update_order(order_id):
    data = request.json
    for order in orders:
        if order.get('id') == order_id:
            order['status'] = data.get('status')
            order['updated_at'] = datetime.now().isoformat()
            
            if data.get('status') == 'completed':
                service = {
                    "service_id": str(uuid.uuid4())[:8],
                    "plan_name": order['plan_name'],
                    "plan_type": order['plan_type'],
                    "status": "active",
                    "location": order.get('location', 'us_east'),
                    "created_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
                    "server_password": generate_server_password(),
                    "panel_url": f"https://panel.vecto.nodes/servers/{uuid.uuid4().hex[:8]}"
                }
                
                if order['user_email'] not in user_services:
                    user_services[order['user_email']] = []
                user_services[order['user_email']].append(service)
                
                send_email_simulation(order['user_email'], "Order Approved - VECTŌ NODES",
                                     f"Your order {order_id} has been approved! Your server is now active.\n\n"
                                     f"Server Details:\n"
                                     f"Plan: {order['plan_name']}\n"
                                     f"Location: {order.get('location', 'US East')}\n"
                                     f"Panel URL: {service['panel_url']}\n"
                                     f"Password: {service['server_password']}")
            
            log_activity(session['user_email'], "ADMIN_UPDATE_ORDER", f"Order {order_id} status changed to {order['status']}")
            return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "Order not found"}), 404

@app.route('/api/admin/plans/<plan_type>/<plan_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_plan(plan_type, plan_id):
    plan_lists = {
        'vps_basic': vps_basic_plans,
        'vps_powerful': vps_powerful_plans,
        'vps_elite': vps_elite_plans,
        'mc': mc_plans,
        'bot': bot_plans,
        'discord': discord_plans
    }
    
    if plan_type not in plan_lists:
        return jsonify({"success": False, "message": "Invalid plan type"}), 400
    
    plan_list = plan_lists[plan_type]
    plan_index = next((i for i, p in enumerate(plan_list) if p['id'] == plan_id), None)
    
    if plan_index is None:
        return jsonify({"success": False, "message": "Plan not found"}), 404
    
    if request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            if key in plan_list[plan_index]:
                plan_list[plan_index][key] = value
        log_activity(session['user_email'], "ADMIN_UPDATE_PLAN", f"Updated plan: {plan_list[plan_index]['name']}")
        return jsonify({"success": True, "plan": plan_list[plan_index]})
    
    elif request.method == 'DELETE':
        plan_name = plan_list[plan_index]['name']
        plan_list.pop(plan_index)
        log_activity(session['user_email'], "ADMIN_DELETE_PLAN", f"Deleted plan: {plan_name}")
        return jsonify({"success": True})

@app.route('/api/admin/plans/<plan_type>', methods=['POST'])
@admin_required
def api_admin_add_plan(plan_type):
    plan_lists = {
        'vps_basic': vps_basic_plans,
        'vps_powerful': vps_powerful_plans,
        'vps_elite': vps_elite_plans,
        'mc': mc_plans,
        'bot': bot_plans,
        'discord': discord_plans
    }
    
    if plan_type not in plan_lists:
        return jsonify({"success": False, "message": "Invalid plan type"}), 400
    
    data = request.json
    new_id = f"{plan_type}_{uuid.uuid4().hex[:6]}"
    new_plan = {
        "id": new_id,
        "type": plan_type.split('_')[0] if '_' in plan_type else plan_type,
        "category": plan_type.split('_')[1] if '_' in plan_type and len(plan_type.split('_')) > 1 else 'basic',
        "name": data.get('name'),
        "ram": data.get('ram', ''),
        "cpu": data.get('cpu', ''),
        "storage": data.get('storage', ''),
        "bandwidth": data.get('bandwidth', ''),
        "slots": data.get('slots', ''),
        "servers": data.get('servers', ''),
        "features": data.get('features', ''),
        "duration": data.get('duration', ''),
        "price": data.get('price', '$0'),
        "raw_price_usd": float(data.get('price', '0').replace('$', '')),
        "enabled": data.get('enabled', True),
        "popular": data.get('popular', False),
        "location": data.get('location', 'us_east')
    }
    plan_lists[plan_type].append(new_plan)
    
    log_activity(session['user_email'], "ADMIN_ADD_PLAN", f"Added {plan_type} plan: {new_plan['name']}")
    return jsonify({"success": True, "plan": new_plan})

@app.route('/api/admin/reviews/<review_id>/approve', methods=['PUT'])
@admin_required
def api_admin_approve_review(review_id):
    for review in reviews:
        if review.get('id') == review_id:
            review['approved'] = True
            log_activity(session['user_email'], "ADMIN_APPROVE_REVIEW", f"Approved review from {review.get('user_name')}")
            return jsonify({"success": True})
    return jsonify({"success": False, "message": "Review not found"}), 404

@app.route('/api/admin/reviews/<review_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_review(review_id):
    global reviews
    review_to_delete = next((r for r in reviews if r.get('id') == review_id), None)
    if review_to_delete:
        reviews = [r for r in reviews if r.get('id') != review_id]
        log_activity(session['user_email'], "ADMIN_DELETE_REVIEW", f"Deleted review from {review_to_delete.get('user_name')}")
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Review not found"}), 404

@app.route('/api/admin/vps-settings', methods=['PUT'])
@admin_required
def api_admin_vps_settings():
    data = request.json
    for key, value in data.items():
        if key in vps_settings:
            vps_settings[key] = value
    log_activity(session['user_email'], "ADMIN_VPS_SETTINGS_UPDATED", "VPS settings updated")
    return jsonify({"success": True, "vps_settings": vps_settings})

@app.route('/api/admin/ptero-settings', methods=['PUT'])
@admin_required
def api_admin_ptero_settings():
    data = request.json
    for key, value in data.items():
        if key in ptero_settings:
            ptero_settings[key] = value
    log_activity(session['user_email'], "ADMIN_PTERO_SETTINGS_UPDATED", "Pterodactyl settings updated")
    return jsonify({"success": True, "ptero_settings": ptero_settings})

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def api_admin_stats():
    return jsonify(get_system_stats())

@app.route('/api/admin/logs', methods=['GET'])
@admin_required
def api_admin_logs():
    limit = request.args.get('limit', 100, type=int)
    return jsonify(activity_logs[:limit])

@app.route('/api/admin/cart-toggle', methods=['POST'])
@admin_required
def api_admin_cart_toggle():
    data = request.json
    website_settings['cart_system_enabled'] = data.get('enabled', True)
    log_activity(session['user_email'], "ADMIN_CART_TOGGLE", f"Cart system set to {website_settings['cart_system_enabled']}")
    return jsonify({"success": True, "cart_enabled": website_settings['cart_system_enabled']})

# ============================================================================
# ᴇʀʀᴏʀ ʜᴀɴᴅʟᴇʀꜱ
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', settings=website_settings), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', settings=website_settings), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html', settings=website_settings), 403

# ============================================================================
# ᴍᴀɪɴ ᴀᴘᴘʟɪᴄᴀᴛɪᴏɴ ᴇɴᴛʀʏ ᴘᴏɪɴᴛ
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("╔═════════════════════════════════════════════════════════════════════╗")
    print("║                                                                     ║")
    print("║     ██╗   ██╗███████╗ ██████╗████████╗╗     ███╗   ██╗ ██████╗      ║")
    print("║     ██║   ██║██╔════╝██╔════╝╚══██╔══╝║     ████╗  ██║██╔═══██╗     ║")
    print("║     ██║   ██║█████╗  ██║        ██║   ║     ██╔██╗ ██║██║   ██║     ║")
    print("║     ╚██╗ ██╔╝██╔══╝  ██║        ██║   ║     ██║╚██╗██║██║   ██║     ║")
    print("║      ╚████╔╝ ███████╗╚██████╗   ██║   ║     ██║ ╚████║╚██████╔╝     ║")
    print("║       ╚═══╝  ╚══════╝ ╚═════╝   ╚═╝   ║     ╚═╝  ╚═══╝ ╚═════╝      ║")
    print("║                                                                     ║")
    print("║                    ᴛʜᴇ ꜱᴛʀᴏɴɢᴇꜱᴛ ʜᴏꜱᴛɪɴɢ ᴘʟᴀᴛꜰᴏʀᴍ                ║")
    print("╚═════════════════════════════════════════════════════════════════════╝")
    print("=" * 70)
    print(f"📊 SYSTEM STATUS: ONLINE")
    print(f"👥 TOTAL USERS: {len(users)}")
    print(f"📦 TOTAL PLANS: {len(all_plans)}")
    print(f"🎮 VPS PLANS: {len(vps_basic_plans + vps_powerful_plans + vps_elite_plans)}")
    print(f"🎮 MC PLANS: {len(mc_plans)}")
    print(f"🤖 BOT PLANS: {len(bot_plans)}")
    print(f"💎 DISCORD PLANS: {len(discord_plans)}")
    print("-" * 70)
    print(f"🔑 ADMIN LOGIN: admin@vecto.co / admin123")
    print(f"🌐 SERVER RUNNING AT: http://localhost:5000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
