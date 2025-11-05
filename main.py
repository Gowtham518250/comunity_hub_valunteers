# main.py - ULTRA MODERN COMMUNITY HUB
# main.py - ULTRA MODERN COMMUNITY HUB WITH REAL-TIME ANALYTICS
from fastapi import FastAPI, Request, Form, HTTPException, status, Response, File, UploadFile, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import json
import folium
from folium import plugins
import numpy as np
from scipy.stats import gaussian_kde
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from PIL import Image, ImageOps
import io
import asyncio
from collections import defaultdict
import logging
from typing import Dict, List, Optional, Any
import pandas as pd
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from scipy.stats import gaussian_kde
import folium
from folium import plugins
import json
import asyncio
from datetime import datetime, timedelta
import pytz
import logging
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import jwt
from typing import Optional, Dict, Any, List
import json
import os
import shutil
from collections import defaultdict
import random
import asyncio
import aiofiles
import sys

# ============================================================================
# ENHANCED LOGGING WITH UNICODE SUPPORT
# ============================================================================

def setup_logging():
    """Configure logging with proper Unicode support"""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = logging.FileHandler('communityhub_advanced.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True
    )

setup_logging()
logger = logging.getLogger(__name__)

# Initialize empty databases
users_db = {}
complaints_db = {}
notifications_db = {}
analytics_db = {"hotspots": [], "categories": defaultdict(int), "trends": defaultdict(lambda: defaultdict(int))}

# ============================================================================
# ADVANCED CONFIGURATION
# ============================================================================

class Config:
    SECRET_KEY = "community_hub_ultra_advanced_2024_v3"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 480
    APP_NAME = "CommunityHub AI"
    APP_VERSION = "4.0.0"
    UPLOAD_DIR = "static/uploads/complaints"

config = Config()

# ============================================================================
# FASTAPI APP WITH REAL-TIME ANALYTICS
# ============================================================================

app = FastAPI(
    title=config.APP_NAME,
    description="AI-Powered Community Management Platform with Real-time Analytics",
    version=config.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
            
            

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
Path("static").mkdir(exist_ok=True)
Path("static/css").mkdir(exist_ok=True)
Path("static/js").mkdir(exist_ok=True)
Path("static/uploads/complaints").mkdir(exist_ok=True, parents=True)
Path("templates").mkdir(exist_ok=True)

# Load databases
def load_databases():
    global users_db, complaints_db, notifications_db, analytics_db
    logger.info("Loading databases...")
    
    try:
        def safe_load_json(path: str):
            """Read a file and safely parse JSON, stripping markdown code fences if present."""
            with open(path, "r", encoding="utf-8") as fh:
                raw = fh.read().strip()
            # Remove markdown code fences if the files were saved with them
            if raw.startswith("```"):
                # remove leading ```[json] and trailing ```
                parts = raw.split('\n', 1)
                if len(parts) > 1 and parts[0].startswith("```"):
                    raw = parts[1]
                    if raw.endswith("```"):
                        raw = raw[:-3].strip()
            try:
                return json.loads(raw)
            except Exception:
                # Fallback to empty dict on parse failure
                logger.warning(f"Failed to parse JSON in {path}; returning empty dict")
                return {}

        if os.path.exists("users.json"):
            logger.info("Loading users.json")
            users_db.update(safe_load_json("users.json"))
            logger.info(f"Loaded {len(users_db)} users")
        
        if os.path.exists("complaints.json"):
            logger.info("Loading complaints.json")
            complaints_db.update(safe_load_json("complaints.json"))
            logger.info(f"Loaded {len(complaints_db)} complaints")
        
        if os.path.exists("notifications.json"):
            logger.info("Loading notifications.json")
            notifications_db.update(safe_load_json("notifications.json"))
            logger.info(f"Loaded {len(notifications_db)} notifications")
    except Exception as e:
        logger.error(f"Error loading databases: {str(e)}")
        raise

load_databases()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ============================================================================
# REAL-TIME ANALYTICS AND WEBSOCKET CONNECTIONS
# ============================================================================

@app.websocket("/ws/analytics")
async def websocket_analytics_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "analytics")
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, "analytics")

@app.on_event("startup")
async def start_analytics_broadcast():
    asyncio.create_task(generate_analytics_data())

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.admin_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, user_type: str = "user"):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_type == "admin":
            self.admin_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

    async def broadcast_to_admins(self, message: str):
        for connection in self.admin_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# ============================================================================
# ENHANCED DATABASE WITH ANALYTICS SUPPORT
# ============================================================================

class AnalyticsDB:
    def __init__(self):
        self.trends = defaultdict(lambda: defaultdict(int))
        self.hotspots = []
        self.category_stats = defaultdict(int)
        self.response_times = defaultdict(list)
    
    def update(self, complaint: Dict[str, Any]):
        date = complaint['created_at'].split('T')[0]
        self.trends[date][complaint['category']] += 1
        self.category_stats[complaint['category']] += 1
        
        if complaint['latitude'] and complaint['longitude']:
            self.update_hotspots(complaint)
    
    def update_hotspots(self, complaint: Dict[str, Any]):
        new_hotspot = {
            'lat': complaint['latitude'],
            'lng': complaint['longitude'],
            'category': complaint['category'],
            'count': 1,
            'complaints': [complaint['id']]
        }
        
        # Merge with existing hotspots if nearby
        merged = False
        for hotspot in self.hotspots:
            if self.is_nearby(hotspot, new_hotspot):
                hotspot['count'] += 1
                hotspot['complaints'].append(complaint['id'])
                merged = True
                break
        
        if not merged:
            self.hotspots.append(new_hotspot)
    
    def is_nearby(self, spot1: Dict[str, Any], spot2: Dict[str, Any], threshold: float = 0.01):
        return (abs(spot1['lat'] - spot2['lat']) < threshold and 
                abs(spot1['lng'] - spot2['lng']) < threshold)
    
    def get_analytics(self) -> Dict[str, Any]:
        return {
            'trends': dict(self.trends),
            'categories': dict(self.category_stats),
            'hotspots': self.hotspots
        }

users_db: Dict[str, Dict[str, Any]] = {}
complaints_db: Dict[str, Dict[str, Any]] = {}
notifications_db: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
analytics_db = AnalyticsDB()

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    return analytics_db.get_analytics()

@app.get("/api/analytics/hotspots")
async def get_hotspots():
    return {"hotspots": analytics_db.hotspots}

@app.get("/api/analytics/trends")
async def get_trends(days: int = 30):
    now = datetime.now()
    start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    
    trends = {}
    for date, categories in analytics_db.trends.items():
        if date >= start_date:
            trends[date] = categories
    
    return {"trends": trends}

# ============================================================================
# AI-POWERED CONSTANTS
# ============================================================================

INDIAN_STATES = {
    "maharashtra": {"name": "Maharashtra", "lat": 19.7515, "lng": 75.7139, "capital": "Mumbai", "zone": "West"},
    "delhi": {"name": "Delhi", "lat": 28.6139, "lng": 77.2090, "capital": "New Delhi", "zone": "North"},
    "karnataka": {"name": "Karnataka", "lat": 15.3173, "lng": 75.7139, "capital": "Bengaluru", "zone": "South"},
    "tamil_nadu": {"name": "Tamil Nadu", "lat": 11.1271, "lng": 78.6569, "capital": "Chennai", "zone": "South"},
    "kerala": {"name": "Kerala", "lat": 10.8505, "lng": 76.2711, "capital": "Thiruvananthapuram", "zone": "South"},
    "andhra_pradesh": {"name": "Andhra Pradesh", "lat": 15.9129, "lng": 79.7400, "capital": "Amaravati", "zone": "South"},
    "telangana": {"name": "Telangana", "lat": 17.1232, "lng": 79.2088, "capital": "Hyderabad", "zone": "South"},
    "west_bengal": {"name": "West Bengal", "lat": 22.9868, "lng": 87.8550, "capital": "Kolkata", "zone": "East"},
    "gujarat": {"name": "Gujarat", "lat": 22.2587, "lng": 71.1924, "capital": "Gandhinagar", "zone": "West"},
    "rajasthan": {"name": "Rajasthan", "lat": 27.0238, "lng": 74.2179, "capital": "Jaipur", "zone": "North"}
}

COMPLAINT_CATEGORIES = {
    "road_damage": {
        "name": "Road Damage", "icon": "🚧", "color": "#e74c3c", 
        "priority": 1, "avg_resolution_days": 7, "department": "Public Works"
    },
    "water_issue": {
        "name": "Water Issue", "icon": "💧", "color": "#3498db", 
        "priority": 2, "avg_resolution_days": 3, "department": "Water Board"
    },
    "electricity": {
        "name": "Electricity Problem", "icon": "⚡", "color": "#f39c12", 
        "priority": 1, "avg_resolution_days": 2, "department": "Electricity Board"
    },
    "waste_management": {
        "name": "Waste Management", "icon": "🗑️", "color": "#2ecc71", 
        "priority": 3, "avg_resolution_days": 1, "department": "Municipal Corporation"
    },
    "public_safety": {
        "name": "Public Safety", "icon": "🚨", "color": "#e67e22", 
        "priority": 1, "avg_resolution_days": 1, "department": "Police Department"
    },
    "parks_greenery": {
        "name": "Parks & Greenery", "icon": "🌳", "color": "#27ae60", 
        "priority": 4, "avg_resolution_days": 14, "department": "Horticulture"
    },
    "noise_pollution": {
        "name": "Noise Pollution", "icon": "🔊", "color": "#9b59b6", 
        "priority": 2, "avg_resolution_days": 2, "department": "Pollution Control"
    },
    "other": {
        "name": "Other Issues", "icon": "📝", "color": "#95a5a6", 
        "priority": 4, "avg_resolution_days": 10, "department": "General Administration"
    }
}

COMPLAINT_SEVERITY = {
    "low": {"name": "Low", "color": "#2ecc71", "priority": 1, "response_time": "48 hours"},
    "medium": {"name": "Medium", "color": "#f39c12", "priority": 2, "response_time": "24 hours"},
    "high": {"name": "High", "color": "#e74c3c", "priority": 3, "response_time": "12 hours"},
    "critical": {"name": "Critical", "color": "#c0392b", "priority": 4, "response_time": "2 hours"}
}

COMPLAINT_STATUS = {
    "pending": {"name": "Pending Review", "color": "#95a5a6", "icon": "⏳", "progress": 10},
    "under_review": {"name": "Under Review", "color": "#3498db", "icon": "🔍", "progress": 30},
    "in_progress": {"name": "In Progress", "color": "#f39c12", "icon": "🔄", "progress": 60},
    "resolved": {"name": "Resolved", "color": "#27ae60", "icon": "✅", "progress": 100},
    "rejected": {"name": "Rejected", "color": "#e74c3c", "icon": "❌", "progress": 0}
}

# Template compatibility
CATEGORIES = COMPLAINT_CATEGORIES
SEVERITY_LEVELS = COMPLAINT_SEVERITY
STATUS_TYPES = COMPLAINT_STATUS

# ============================================================================
# AI UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

async def get_current_user(request: Request) -> Optional[Dict]:
    try:
        token = request.cookies.get("access_token")
        if not token:
            return None
        
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username = payload.get("sub")
        
        if not username or username not in users_db:
            return None
        
        return users_db[username]
    except Exception as e:
        return None

async def get_current_admin(request: Request) -> bool:
    user = await get_current_user(request)
    return user and user.get('username') == 'admin'

def generate_ai_insights(analytics: Dict) -> List[Dict]:
    """Generate AI-powered insights based on analytics"""
    insights = []
    
    total_complaints = analytics.get('total_complaints', 0)
    if total_complaints == 0:
        return [
            {
                "type": "info",
                "title": "Welcome to CommunityHub",
                "message": "Start by raising your first complaint to get insights",
                "icon": "⚡",
                "priority": "low"
            }
        ]
    
    resolution_rate = analytics.get('resolution_rate', 0)
    if resolution_rate > 80:
        insights.append({
            "type": "success",
            "title": "Excellent Resolution Rate",
            "message": f"Your resolution rate of {resolution_rate}% is outstanding!",
            "icon": "🎯",
            "priority": "high"
        })
    elif resolution_rate < 50:
        insights.append({
            "type": "warning",
            "title": "Improvement Needed",
            "message": f"Resolution rate of {resolution_rate}% needs attention",
            "icon": "📊",
            "priority": "high"
        })
    
    category_dist = analytics.get('category_distribution', {})
    if category_dist:
        top_category = max(category_dist.items(), key=lambda x: x[1])
        cat_name = COMPLAINT_CATEGORIES.get(top_category[0], {}).get('name', top_category[0])
        insights.append({
            "type": "info",
            "title": "Most Common Issue",
            "message": f"'{cat_name}' accounts for {top_category[1]} complaints",
            "icon": "📈",
            "priority": "medium"
        })
    
    state_dist = analytics.get('state_distribution', {})
    if state_dist:
        top_state = max(state_dist.items(), key=lambda x: x[1])
        if top_state[0] in INDIAN_STATES:
            state_name = INDIAN_STATES[top_state[0]]['name']
            insights.append({
                "type": "info",
                "title": "Regional Focus",
                "message": f"{state_name} has the highest complaints ({top_state[1]})",
                "icon": "📍",
                "priority": "medium"
            })
    
    avg_resolution = analytics.get('avg_resolution_time', 0)
    if avg_resolution > 10:
        insights.append({
            "type": "warning",
            "title": "Slow Resolution",
            "message": f"Average resolution time of {avg_resolution} days needs improvement",
            "icon": "⏰",
            "priority": "high"
        })
    
    return insights[:4]

async def add_notification(user_id: str, title: str, message: str, notification_type: str = "info"):
    """Add real-time notification"""
    notification = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "message": message,
        "type": notification_type,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    notifications_db[user_id].insert(0, notification)
    notifications_db[user_id] = notifications_db[user_id][:50]
    
    await manager.broadcast(json.dumps({
        "type": "notification",
        "user_id": user_id,
        "notification": notification
    }))

# ============================================================================
# DATA PERSISTENCE
# ============================================================================

def save_data():
    """Save data to JSON files for persistence"""
    try:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users_db, f, indent=2, ensure_ascii=False)
        
        with open('complaints.json', 'w', encoding='utf-8') as f:
            json.dump(complaints_db, f, indent=2, ensure_ascii=False)
            
        with open('notifications.json', 'w', encoding='utf-8') as f:
            json.dump(dict(notifications_db), f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        logger.error(f"Error saving data: {e}")

def load_data():
    """Load data from JSON files on startup"""
    global users_db, complaints_db, notifications_db
    
    try:
        if os.path.exists('users.json'):
            with open('users.json', 'r', encoding='utf-8') as f:
                users_db.update(json.load(f))
    except Exception as e:
        logger.error(f"Error loading users: {e}")
    
    try:
        if os.path.exists('complaints.json'):
            with open('complaints.json', 'r', encoding='utf-8') as f:
                complaints_db.update(json.load(f))
    except Exception as e:
        logger.error(f"Error loading complaints: {e}")
    
    try:
        if os.path.exists('notifications.json'):
            with open('notifications.json', 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                for k, v in loaded.items():
                    notifications_db[k] = v
    except Exception as e:
        logger.error(f"Error loading notifications: {e}")

# ============================================================================
# REAL-TIME ANALYTICS ENGINE
# ============================================================================

def get_complaint_analytics():
    """Generate comprehensive real-time analytics"""
    total_complaints = len(complaints_db)
    
    status_dist = defaultdict(int)
    category_dist = defaultdict(int)
    severity_dist = defaultdict(int)
    state_dist = defaultdict(int)
    zone_dist = defaultdict(int)
    monthly_trend = defaultdict(int)
    weekly_trend = defaultdict(int)
    
    now = datetime.now()
    current_week = now.strftime("%Y-W%W")
    current_month = now.strftime("%Y-%m")
    
    for complaint in complaints_db.values():
        status = complaint.get('status', 'pending')
        category = complaint.get('category', 'other')
        severity = complaint.get('severity', 'medium')
        
        status_dist[status] += 1
        category_dist[category] += 1
        severity_dist[severity] += 1
        
        location = complaint.get('location', '').lower()
        state_found = False
        for state_key, state_data in INDIAN_STATES.items():
            if state_key in location or state_data['name'].lower() in location:
                state_dist[state_key] += 1
                zone_dist[state_data['zone']] += 1
                state_found = True
                break
        if not state_found:
            state_dist['other'] += 1
            zone_dist['unknown'] += 1
        
        created_at = complaint.get('created_at', '')
        if created_at:
            try:
                month = created_at[:7]
                weekly_trend[current_week] += 1
                monthly_trend[month] += 1
            except:
                pass
    
    resolution_times = []
    urgent_complaints = 0
    for complaint in complaints_db.values():
        if complaint.get('severity') in ['high', 'critical']:
            urgent_complaints += 1
            
        if complaint.get('status') == 'resolved':
            try:
                created = datetime.fromisoformat(complaint.get('created_at', datetime.now().isoformat()))
                resolved = datetime.fromisoformat(complaint.get('updated_at', datetime.now().isoformat()))
                days = (resolved - created).days
                resolution_times.append(max(1, days))
            except:
                pass
    
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    resolved_count = status_dist.get('resolved', 0)
    resolution_rate = (resolved_count / total_complaints * 100) if total_complaints > 0 else 0
    
    insights = generate_ai_insights({
        'total_complaints': total_complaints,
        'resolution_rate': resolution_rate,
        'category_distribution': category_dist,
        'state_distribution': state_dist,
        'avg_resolution_time': avg_resolution_time
    })
    
    return {
        "total_complaints": total_complaints,
        "resolved_complaints": resolved_count,
        "pending_complaints": status_dist.get('pending', 0),
        "urgent_complaints": urgent_complaints,
        "status_distribution": dict(status_dist),
        "category_distribution": dict(category_dist),
        "severity_distribution": dict(severity_dist),
        "state_distribution": dict(state_dist),
        "zone_distribution": dict(zone_dist),
        "monthly_trend": dict(monthly_trend),
        "weekly_trend": dict(weekly_trend),
        "resolution_rate": round(resolution_rate, 1),
        "avg_resolution_time": round(avg_resolution_time, 1),
        "total_users": len(users_db),
        "ai_insights": insights,
        "performance_score": calculate_performance_score(resolution_rate, avg_resolution_time, urgent_complaints, total_complaints),
        # Provide extras that are useful for alternate charts
        "category_pie": dict(category_dist),
        "severity_pie": dict(severity_dist)
    }

def calculate_performance_score(resolution_rate: float, avg_resolution: float, urgent_count: int, total_complaints: int = 0) -> int:
    """Calculate overall performance score (0-100).

    Rules:
    - If there are no complaints, return 0 (avoids misleading mid-range scores).
    - Otherwise combine resolution rate, average resolution time and urgency into a 0-100 score.
    """
    # If there are no complaints at all, report 0 so dashboards don't show a misleading score (was 34).
    if total_complaints == 0:
        return 0

    rate_score = min(100, resolution_rate * 1.2)
    time_score = max(0, 100 - (avg_resolution * 5))
    # Use clearer urgent_score mapping instead of boolean arithmetic
    urgent_score = 80 if urgent_count > 0 else 20

    score = (rate_score * 0.5) + (time_score * 0.3) + (urgent_score * 0.2)
    return int(round(score))


async def generate_analytics_data(poll_interval: int = 5):
    """Continuously generate and broadcast analytics data to connected websockets.

    This function rebuilds the lightweight analytics DB from `complaints_db`,
    computes summary metrics using `get_complaint_analytics()` and broadcasts
    the payload to all active websocket clients via `manager.broadcast`.
    """
    global analytics_db
    while True:
        try:
            # Rebuild analytics DB from current complaints
            new_analytics = AnalyticsDB()
            for complaint in complaints_db.values():
                try:
                    new_analytics.update(complaint)
                except Exception:
                    # skip malformed complaint entries
                    continue

            # Replace in-memory analytics store atomically
            analytics_db.trends = new_analytics.trends
            analytics_db.hotspots = new_analytics.hotspots
            analytics_db.category_stats = new_analytics.category_stats
            analytics_db.response_times = new_analytics.response_times

            # Prepare full analytics payload
            payload = get_complaint_analytics()

            # Build websocket-friendly payload expected by analytics.js
            ws_payload = {
                'total_complaints': payload.get('total_complaints', 0),
                'resolved_complaints': payload.get('resolved_complaints', 0),
                'pending_complaints': payload.get('pending_complaints', 0),
                'urgent_complaints': payload.get('urgent_complaints', 0),
                'resolution_rate': payload.get('resolution_rate', 0),
                'total_users': payload.get('total_users', 0),
                'performance_score': payload.get('performance_score', 0),
                # heatmap data uses hotspots
                'heatmap': analytics_db.hotspots,
                # categories as simple mapping
                'categories': dict(analytics_db.category_stats),
                # trend: labels and summed values (keep for backward compatibility)
                'trend': {
                    'labels': list(analytics_db.trends.keys()),
                    'values': [sum(v.values()) for v in analytics_db.trends.values()]
                },
                # Provide alternative chart datasets: category & severity pies, state distribution and monthly bar
                'category_pie': payload.get('category_distribution', {}),
                'severity_pie': payload.get('severity_distribution', {}),
                'state_distribution': payload.get('state_distribution', {}),
                'monthly_bar': payload.get('monthly_trend', {}),
                # markers: reuse hotspots but expose a nicer shape for popups
                'markers': [
                    {
                        'lat': h.get('lat'),
                        'lng': h.get('lng'),
                        'title': f"{h.get('category', '').title()} hotspot",
                        'description': f"{h.get('count', 0)} complaints",
                        'category': h.get('category'),
                        'categoryColor': COMPLAINT_CATEGORIES.get(h.get('category'), {}).get('color', '#4D96FF'),
                        'count': h.get('count', 0)
                    } for h in analytics_db.hotspots
                ]
            }

            # Broadcast the websocket-friendly analytics payload
            try:
                await manager.broadcast(json.dumps(ws_payload))
            except Exception:
                # individual connection errors are handled inside manager
                pass

        except Exception as e:
            logger.error(f"Analytics generation error: {e}")

        await asyncio.sleep(poll_interval)

def generate_sample_complaints():
    """Generate realistic sample complaints"""
    sample_titles = [
        "Potholes on Main Road Causing Accidents",
        "Water Pipeline Leakage in Sector 15",
        "Street Lights Not Working for 3 Days",
        "Garbage Overflow in Park Area",
        "Illegal Construction Noise at Night",
        "Sewage Blockage in Residential Area",
        "Broken Footpath Tiles Near Market",
        "Stray Animal Menace in Colony",
        "Mosquito Breeding in Stagnant Water",
        "Traffic Signal Malfunction at Junction"
    ]
    
    sample_descriptions = [
        "Large potholes have developed on the main road, causing traffic jams and vehicle damage.",
        "Continuous water leakage from main pipeline is wasting water and causing road damage.",
        "Complete blackout in the area due to non-functional street lights, security concern.",
        "Garbage bins overflowing for past 2 days, creating unhygienic conditions.",
        "Illegal construction work continuing beyond permitted hours, causing noise pollution.",
        "Severe sewage blockage causing overflow into residential compounds, health hazard.",
        "Broken footpath tiles causing inconvenience to pedestrians, especially elderly.",
        "Increasing number of stray dogs creating safety concerns for children.",
        "Stagnant water in empty plots leading to mosquito breeding, dengue risk.",
        "Traffic signal not working properly causing traffic chaos during peak hours."
    ]
    
    if len(complaints_db) < 10:
        for i in range(10):
            complaint_id = str(uuid.uuid4())[:8]
            state_key = random.choice(list(INDIAN_STATES.keys()))
            state_data = INDIAN_STATES[state_key]
            
            complaints_db[complaint_id] = {
                'id': complaint_id,
                'user_id': 'sample_user',
                'title': sample_titles[i],
                'description': sample_descriptions[i],
                'category': random.choice(list(COMPLAINT_CATEGORIES.keys())),
                'severity': random.choice(['medium', 'high', 'critical']),
                'location': f"{state_data['capital']}, {state_data['name']}",
                'latitude': state_data['lat'] + random.uniform(-0.3, 0.3),
                'longitude': state_data['lng'] + random.uniform(-0.3, 0.3),
                'image_path': None,
                'status': random.choice(['pending', 'under_review', 'in_progress', 'resolved']),
                'admin_notes': 'Sample complaint for demonstration' if i % 3 == 0 else '',
                'assigned_to': 'admin' if i % 2 == 0 else '',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'priority_score': random.randint(1, 100)
            }

# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    user_type = "admin" if user_id == "admin" else "user"
    await manager.connect(websocket, user_type)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if message_data.get('type') == 'status_update':
                await manager.broadcast_to_admins(json.dumps({
                    'type': 'status_change',
                    'complaint_id': message_data['complaint_id'],
                    'new_status': message_data['status']
                }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = await get_current_user(request)
    analytics = get_complaint_analytics()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "analytics": analytics
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    try:
        user = users_db.get(username)
        
        if not user or not verify_password(password, user.get('hashed_password', '')):
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "Invalid username or password"}
            )
        
        access_token = create_access_token(data={"sub": username})
        response = JSONResponse({"success": True, "message": "Login successful"})
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=86400)
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Server error"}
        )

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...)
):
    try:
        if username in users_db:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Username already exists"}
            )
        
        if len(password) < 6:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Password must be at least 6 characters"}
            )
        
        if "@" not in email or "." not in email:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Invalid email format"}
            )
        
        if len(phone) < 10:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Invalid phone number"}
            )
        
        users_db[username] = {
            'username': username,
            'email': email,
            'phone': phone,
            'hashed_password': hash_password(password),
            'joined_date': datetime.now().isoformat(),
            'role': 'user',
            'preferences': {
                'notifications': True,
                'email_alerts': True,
                'sms_alerts': False
            }
        }
        
        save_data()
        
        access_token = create_access_token(data={"sub": username})
        response = JSONResponse({"success": True, "message": "Account created successfully"})
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=86400)
        
        await add_notification(username, "Welcome to CommunityHub AI", "Your account has been created successfully!", "success")
        
        return response
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Server error"}
        )

# ============================================================================
# COMPLAINT MANAGEMENT ROUTES
# ============================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    
    user_complaints = [c for c in complaints_db.values() if c.get('user_id') == user['username']]
    is_admin = await get_current_admin(request)
    analytics = get_complaint_analytics()
    user_notifications = notifications_db.get(user['username'], [])[:10]
    
    user_complaints.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    
    stats = {
        "total": len(user_complaints),
        "pending": len([c for c in user_complaints if c.get('status') == 'pending']),
        "resolved": len([c for c in user_complaints if c.get('status') == 'resolved']),
        "in_progress": len([c for c in user_complaints if c.get('status') in ['under_review', 'in_progress']]),
        "urgent": len([c for c in user_complaints if c.get('severity') in ['high', 'critical']])
    }
    
    user_category_dist = defaultdict(int)
    user_status_dist = defaultdict(int)
    for c in user_complaints:
        user_category_dist[c.get('category', 'other')] += 1
        user_status_dist[c.get('status', 'pending')] += 1
    
    user_chart_data = {
        "category": dict(user_category_dist),
        "status": dict(user_status_dist)
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "complaints": user_complaints[:10],
        "categories": COMPLAINT_CATEGORIES,
        "severity_levels": COMPLAINT_SEVERITY,
        "status_types": COMPLAINT_STATUS,
        "is_admin": is_admin,
        "stats": stats,
        "analytics": analytics,
        "notifications": user_notifications,
        "states": INDIAN_STATES,
        "user_chart_data": user_chart_data
    })

@app.get("/raise-complaint", response_class=HTMLResponse)
async def raise_complaint_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    
    return templates.TemplateResponse("raise_complaint.html", {
        "request": request,
        "user": user,
        "categories": COMPLAINT_CATEGORIES,
        "severity_levels": COMPLAINT_SEVERITY,
        "states": INDIAN_STATES
    })
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    
    return templates.TemplateResponse("raise_complaint.html", {
        "request": request,
        "user": user,
        "categories": COMPLAINT_CATEGORIES,
        "severity_levels": COMPLAINT_SEVERITY,
        "states": INDIAN_STATES,
        "is_admin": user.get('username') == 'admin'
    })

@app.post("/raise-complaint")
async def raise_complaint(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    severity: str = Form(...),
    location: str = Form(...),
    state: str = Form(...),
    latitude: float = Form(0.0),
    longitude: float = Form(0.0),
    image: UploadFile = File(None)
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    
    try:
        # Enforce that this community hub only accepts complaints for Tamil Nadu
        if state != 'tamil_nadu':
            # Redirect back with an error indicator; frontend can show a message
            return RedirectResponse("/raise_complaint?error=state_not_supported", status_code=302)

        image_path = None
        if image and image.filename:
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            file_extension = image.filename.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                return RedirectResponse("/raise_complaint?error=invalid_file", status_code=302)
            
            content = await image.read()
            if len(content) > 5 * 1024 * 1024:
                return RedirectResponse("/raise_complaint?error=file_too_large", status_code=302)
            
            filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = f"static/uploads/complaints/{filename}"
            image_path = f"/{file_path}"
            
            async with aiofiles.open(file_path, "wb") as buffer:
                await buffer.write(content)
        
        complaint_id = str(uuid.uuid4())
        
        severity_weight = {
            'low': 1, 'medium': 3, 'high': 6, 'critical': 10
        }.get(severity, 1)
        
        category_weight = COMPLAINT_CATEGORIES.get(category, {}).get('priority', 1)
        priority_score = severity_weight * category_weight
        
        complaints_db[complaint_id] = {
            'id': complaint_id,
            'user_id': user['username'],
            'user_name': user.get('full_name', user['username']),
            'title': title,
            'description': description,
            'category': category,
            'severity': severity,
            'location': location,
            'state': state,
            'latitude': latitude if latitude != 0.0 else INDIAN_STATES.get(state, {}).get('lat', 0.0),
            'longitude': longitude if longitude != 0.0 else INDIAN_STATES.get(state, {}).get('lng', 0.0),
            'image_path': image_path,
            'status': 'pending',
            'admin_notes': '',
            'assigned_to': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'priority_score': priority_score
        }
        
        save_data()
        
        await add_notification(
            user['username'], 
            "Complaint Registered", 
            f"Your complaint '{title}' has been registered successfully.", 
            "success"
        )
        
        await manager.broadcast_to_admins(json.dumps({
            'type': 'new_complaint',
            'complaint_id': complaint_id,
            'title': title,
            'category': category,
            'severity': severity,
            'location': location
        }))
        
        # Immediately update the in-memory analytics DB with the new complaint
        try:
            analytics_db.update(complaints_db[complaint_id])
            # Build the same websocket-friendly payload as the background broadcaster
            ws_payload = {
                'total_complaints': len(complaints_db),
                'resolved_complaints': sum(1 for c in complaints_db.values() if c.get('status') == 'resolved'),
                'pending_complaints': sum(1 for c in complaints_db.values() if c.get('status') == 'pending'),
                'urgent_complaints': sum(1 for c in complaints_db.values() if c.get('severity') in ['high','critical']),
                'resolution_rate': get_complaint_analytics().get('resolution_rate', 0),
                'total_users': len(users_db),
                'performance_score': get_complaint_analytics().get('performance_score', 0),
                'heatmap': analytics_db.hotspots,
                'categories': dict(analytics_db.category_stats),
                'category_pie': get_complaint_analytics().get('category_distribution', {}),
                'severity_pie': get_complaint_analytics().get('severity_distribution', {}),
                'state_distribution': get_complaint_analytics().get('state_distribution', {}),
                'monthly_bar': get_complaint_analytics().get('monthly_trend', {}),
                'trend': {
                    'labels': list(analytics_db.trends.keys()),
                    'values': [sum(v.values()) for v in analytics_db.trends.values()]
                },
                'markers': [
                    {
                        'lat': h.get('lat'),
                        'lng': h.get('lng'),
                        'title': f"{h.get('category', '').title()} hotspot",
                        'description': f"{h.get('count', 0)} complaints",
                        'category': h.get('category'),
                        'categoryColor': COMPLAINT_CATEGORIES.get(h.get('category'), {}).get('color', '#4D96FF'),
                        'count': h.get('count', 0)
                    } for h in analytics_db.hotspots
                ]
            }
            # Broadcast updated analytics to all connected clients so dashboards update instantly
            await manager.broadcast(json.dumps(ws_payload))
        except Exception as e:
            logger.error(f"Immediate analytics broadcast failed: {e}")
        
        logger.info(f"Complaint created: {complaint_id} by {user['username']}")
        
        return RedirectResponse("/dashboard?success=complaint_created", status_code=302)
        
    except Exception as e:
        logger.error(f"Error creating complaint: {e}")
        return RedirectResponse("/raise_complaint?error=server_error", status_code=302)

# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    try:
        user = await get_current_user(request)
        if not user or not await get_current_admin(request):
            logger.warning("Unauthorized access attempt to admin dashboard")
            return RedirectResponse("/dashboard", status_code=302)

        logger.info(f"Authenticated admin user: {user.get('username')}")
        all_complaints = list(complaints_db.values())
        logger.info(f"Fetched {len(all_complaints)} complaints")
        analytics = get_complaint_analytics()
        logger.info("Generated analytics data")

        all_complaints.sort(key=lambda x: (
            -x.get('priority_score', 0),
            0 if x.get('status') in ['pending', 'under_review'] else 1
        ))

        stats = {
            "total": len(all_complaints),
            "pending": len([c for c in all_complaints if c.get('status') == 'pending']),
            "in_progress": len([c for c in all_complaints if c.get('status') in ['under_review', 'in_progress']]),
            "resolved": len([c for c in all_complaints if c.get('status') == 'resolved']),
            "urgent": len([c for c in all_complaints if c.get('severity') in ['high', 'critical']])
        }

        # Sort complaints but don't limit them for the map view
        visible_complaints = all_complaints[:20]  # For table view
        all_geolocated = [c for c in all_complaints if c.get('latitude') and c.get('longitude')]

        response_data = {
            "request": request,
            "user": user,
            "complaints": visible_complaints,  # For table display
            "map_complaints": all_geolocated,  # For map markers
            "analytics": analytics,
            "stats": stats,
            "categories": COMPLAINT_CATEGORIES,
            "severity_levels": COMPLAINT_SEVERITY,
            "status_types": COMPLAINT_STATUS,
            "states": INDIAN_STATES
        }
        logger.info("Rendering admin dashboard template")
        return templates.TemplateResponse("admin_dashboard.html", response_data)
    except Exception as e:
        logger.error(f"Error rendering admin dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/complaints/{complaint_id}/update")
async def update_complaint_status(
    request: Request,
    complaint_id: str,
    status: str = Form(...),
    admin_notes: str = Form(None),
    assigned_to: str = Form(None)
):
    user = await get_current_user(request)
    if not user or not await get_current_admin(request):
        return JSONResponse(
            status_code=403,
            content={"success": False, "message": "Admin access required"}
        )
    
    if complaint_id not in complaints_db:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Complaint not found"}
        )
    
    old_status = complaints_db[complaint_id]['status']
    complaints_db[complaint_id]['status'] = status
    complaints_db[complaint_id]['updated_at'] = datetime.now().isoformat()
    
    if admin_notes:
        complaints_db[complaint_id]['admin_notes'] = admin_notes
    if assigned_to:
        complaints_db[complaint_id]['assigned_to'] = assigned_to
    
    save_data()
    
    complaint = complaints_db[complaint_id]
    await add_notification(complaint['user_id'], "Status Updated", 
                         f"Your complaint '{complaint['title']}' status changed to {COMPLAINT_STATUS[status]['name']}", 
                         "info")
    
    await manager.broadcast(json.dumps({
        'type': 'status_update',
        'complaint_id': complaint_id,
        'old_status': old_status,
        'new_status': status,
        'updated_by': user['username']
    }))
    
    return JSONResponse({"success": True, "message": "Complaint updated successfully"})


@app.post("/admin/clear-complaints")
async def clear_all_complaints(request: Request):
    """Admin-only endpoint to clear all complaints immediately.

    This clears the in-memory `complaints_db`, resets the lightweight analytics
    store, persists the empty state to disk, and broadcasts an empty analytics
    payload so connected dashboards update.
    """
    user = await get_current_user(request)
    if not user or not await get_current_admin(request):
        return JSONResponse(
            status_code=403,
            content={"success": False, "message": "Admin access required"}
        )

    # Clear in-memory complaints
    try:
        complaints_db.clear()
    except Exception:
        # Ensure variable exists and is empty
        globals()['complaints_db'] = {}

    # Reset analytics DB
    try:
        analytics_db.trends.clear()
        analytics_db.hotspots.clear()
        analytics_db.category_stats.clear()
        analytics_db.response_times.clear()
    except Exception:
        # reinstantiate if something odd
        globals()['analytics_db'] = AnalyticsDB()

    # Persist changes
    save_data()

    # Broadcast an updated empty analytics payload so clients refresh
    try:
        payload = get_complaint_analytics()
        await manager.broadcast(json.dumps(payload))
    except Exception as e:
        logger.warning(f"Failed to broadcast analytics after clearing complaints: {e}")

    logger.info(f"Admin {user.get('username')} cleared all complaints")
    return JSONResponse({"success": True, "message": "All complaints cleared"})

# ============================================================================
# ANALYTICS & API ROUTES
# ============================================================================

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    try:
        analytics = get_complaint_analytics() or {}

        # Normalize commonly used keys so the template can access them safely
        analytics.setdefault('monthly_trend', analytics.get('monthly_trend', {}))
        analytics.setdefault('category_distribution', analytics.get('category_distribution', {}))
        analytics.setdefault('status_distribution', analytics.get('status_distribution', {}))
        analytics.setdefault('severity_distribution', analytics.get('severity_distribution', {}))
        analytics.setdefault('total_complaints', analytics.get('total_complaints', 0))
        analytics.setdefault('performance_score', analytics.get('performance_score', 0))
        analytics.setdefault('resolved_complaints', analytics.get('resolved_complaints', 0))
        analytics.setdefault('pending_complaints', analytics.get('pending_complaints', 0))
        analytics.setdefault('urgent_complaints', analytics.get('urgent_complaints', 0))
        analytics.setdefault('total_users', analytics.get('total_users', 0))

        # Provide a hotspots/heatmap key for templates that expect it
        if 'hotspots' not in analytics:
            analytics['hotspots'] = []

        return templates.TemplateResponse("analytics.html", {
            "request": request,
            "user": user,
            "analytics": analytics,
            "states": INDIAN_STATES,
            "categories": COMPLAINT_CATEGORIES,
            "status_types": COMPLAINT_STATUS,
            "severity_levels": COMPLAINT_SEVERITY
        })
    except Exception as e:
        logger.error(f"Error rendering analytics page: {e}")
        # Return a simple error response so the server doesn't return a 500 with no details
        return HTMLResponse(f"<h1>Analytics Error</h1><pre>{str(e)}</pre>", status_code=500)

@app.get("/api/analytics")
async def get_analytics_api():
    analytics = get_complaint_analytics()
    return {"success": True, "analytics": analytics}

@app.get("/api/notifications/{username}")
async def get_notifications_api(username: str):
    user_notifications = notifications_db.get(username, [])
    return {"success": True, "notifications": user_notifications}

@app.post("/api/notifications/{username}/read/{notification_id}")
async def mark_notification_read(username: str, notification_id: str):
    for notification in notifications_db.get(username, []):
        if notification['id'] == notification_id:
            notification['read'] = True
            break
    save_data()
    return {"success": True}

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    return response

# ============================================================================
# STARTUP AND INITIALIZATION
# ============================================================================

@app.on_event("startup")
async def startup_event():
    # Load any existing files into memory first (safe-read)
    load_data()

    logger.info(f"-> Starting {config.APP_NAME} v{config.APP_VERSION}")

    # As requested: remove all existing database files so the app starts with a fresh store.
    global users_db, complaints_db, notifications_db
    for fname in ('users.json', 'complaints.json', 'notifications.json'):
        try:
            if os.path.exists(fname):
                os.remove(fname)
                logger.info(f"Removed existing database file: {fname}")
        except Exception as e:
            logger.warning(f"Could not remove {fname}: {e}")

    # Clear in-memory stores to ensure a clean slate
    try:
        users_db.clear()
    except Exception:
        users_db = {}
    try:
        complaints_db.clear()
    except Exception:
        complaints_db = {}
    try:
        notifications_db.clear()
    except Exception:
        notifications_db = defaultdict(list)

    # Create a minimal admin account so the site remains administrable
    admin_username = "admin"
    users_db[admin_username] = {
        'username': admin_username,
        'email': 'admin@communityhub.ai',
        'phone': '+91-9876543210',
        'hashed_password': hash_password("admin123"),
        'joined_date': datetime.now().isoformat(),
        'role': 'admin',
        'preferences': {
            'notifications': True,
            'email_alerts': True,
            'sms_alerts': True
        }
    }
    save_data()
    logger.info("[Admin] Admin user created; data files cleared to enforce fresh start")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
