"""
Web Routes
Flask web application with professional admin dashboard
"""

import os
import json
import logging
from functools import wraps
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for

from config import TELEGRAM_TOKEN, ADMIN_PASSWORD, WEBHOOK_URL, SECRET_KEY, PORT

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ========== Database Simulation ==========
# In production, use a real database (PostgreSQL, MongoDB, etc.)
bot_data = {
    "users": {},
    "content": {
        "year1": {
            "title": "السنة الأولى",
            "subjects": [
                {"id": 1, "title": "أصول الدين", "content": "محتوى السنة الأولى - أصول الدين", "status": "active"},
                {"id": 2, "title": "الفقه", "content": "محتوى السنة الأولى - الفقه", "status": "active"},
            ]
        },
        "year2": {
            "title": "السنة الثانية",
            "subjects": [
                {"id": 1, "title": "أصول الدين", "content": "محتوى السنة الثانية - أصول الدين", "status": "active"},
            ]
        },
        "year3": {
            "title": "السنة الثالثة",
            "subjects": [
                {"id": 1, "title": "أصول الدين", "content": "محتوى السنة الثالثة - أصول الدين", "status": "active"},
            ]
        },
        "year4": {
            "title": "السنة الرابعة",
            "subjects": [
                {"id": 1, "title": "أصول الدين", "content": "محتوى السنة الرابعة - أصول الدين", "status": "active"},
            ]
        }
    },
    "settings": {
        "bot_name": "بوت اصول الدين",
        "welcome_message": "مرحباً بكم في بوت اصول الدين التعليمي",
        "maintenance_mode": False
    }
}

# Global bot statistics
bot_stats = {
    "total_users": 0,
    "total_messages": 0,
    "total_commands": 0,
    "start_date": datetime.now().strftime("%Y-%m-%d"),
    "broadcasts": [],
    "commands_log": []
}


# ========== HTML Templates ==========

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - لوحة التحكم</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
        }
        .login-box { 
            background: rgba(255, 255, 255, 0.95); 
            padding: 50px; 
            border-radius: 20px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.3); 
            width: 100%; 
            max-width: 450px; 
        }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 28px;
        }
        h2 { 
            text-align: center; 
            margin-bottom: 30px; 
            color: #333; 
            font-size: 22px;
        }
        .form-group { margin-bottom: 20px; }
        .form-group input { 
            width: 100%; 
            padding: 15px 20px; 
            border: 2px solid #e5e7eb; 
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn { 
            width: 100%; 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            padding: 16px; 
            border: none; 
            border-radius: 12px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: 600; 
            transition: all 0.3s;
        }
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .error { 
            background: #fee2e2; 
            color: #991b1b; 
            padding: 12px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            text-align: center; 
            font-size: 14px;
        }
        .footer { text-align: center; margin-top: 30px; color: #888; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo">
            <h1>🎓 لوحة التحكم</h1>
        </div>
        <h2>🔐 تسجيل الدخول</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <div class="form-group">
                <input type="password" name="password" placeholder="كلمة المرور" required>
            </div>
            <button type="submit" class="btn">دخول</button>
        </form>
        <div class="footer">نظام إدارة بوت اصول الدين</div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - {% if settings %}{{ settings.bot_name }}{% else %}بوت اصول الدين{% endif %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
            font-family: 'Cairo', 'Segoe UI', sans-serif;
        }
        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --info: #3b82f6;
            --dark: #1f2937;
            --light: #f3f4f6;
        }
        body { 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
            min-height: 100vh; 
        }
        
        /* Sidebar */
        .sidebar {
            position: fixed;
            right: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
            padding: 20px;
            overflow-y: auto;
            z-index: 1000;
        }
        .sidebar-header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .sidebar-header h2 {
            color: white;
            font-size: 20px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sidebar-header p {
            color: #9ca3af;
            font-size: 12px;
            margin-top: 5px;
        }
        .nav-menu {
            list-style: none;
        }
        .nav-item {
            margin-bottom: 8px;
        }
        .nav-link {
            display: flex;
            align-items: center;
            padding: 14px 18px;
            color: #d1d5db;
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s;
            cursor: pointer;
        }
        .nav-link:hover, .nav-link.active {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            transform: translateX(-5px);
        }
        .nav-link i {
            width: 24px;
            margin-left: 12px;
        }
        
        /* Main Content */
        .main-content {
            margin-right: 280px;
            padding: 30px;
            min-height: 100vh;
        }
        
        /* Header */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        .page-title {
            color: white;
            font-size: 28px;
            font-weight: 700;
        }
        .header-actions {
            display: flex;
            gap: 15px;
        }
        
        /* Cards */
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f3f4f6;
        }
        .card-title {
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 16px;
            padding: 25px;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }
        .stat-card.success { background: linear-gradient(135deg, #10b981, #059669); }
        .stat-card.warning { background: linear-gradient(135deg, #f59e0b, #d97706); }
        .stat-card.info { background: linear-gradient(135deg, #3b82f6, #2563eb); }
        .stat-card.danger { background: linear-gradient(135deg, #ef4444, #dc2626); }
        
        .stat-icon {
            font-size: 32px;
            margin-bottom: 15px;
        }
        .stat-number {
            font-size: 36px;
            font-weight: 700;
        }
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
            margin-top: 5px;
        }
        
        /* Forms */
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #374151;
        }
        .form-control {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 15px;
            transition: all 0.3s;
        }
        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        textarea.form-control {
            min-height: 120px;
            resize: vertical;
        }
        
        /* Buttons */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, var(--success), #059669);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(135deg, var(--danger), #dc2626);
            color: white;
        }
        .btn-warning {
            background: linear-gradient(135deg, var(--warning), #d97706);
            color: white;
        }
        .btn-info {
            background: linear-gradient(135deg, var(--info), #2563eb);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .btn-sm {
            padding: 8px 16px;
            font-size: 12px;
        }
        
        /* Tables */
        .table-container {
            overflow-x: auto;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        .table th, .table td {
            padding: 14px 16px;
            text-align: right;
            border-bottom: 1px solid #e5e7eb;
        }
        .table th {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            font-weight: 600;
        }
        .table tr:hover {
            background: #f9fafb;
        }
        
        /* Badges */
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-danger { background: #fee2e2; color: #991b1b; }
        .badge-info { background: #dbeafe; color: #1e40af; }
        
        /* Logs */
        .logs-container {
            max-height: 400px;
            overflow-y: auto;
            background: #1f2937;
            border-radius: 12px;
            padding: 15px;
        }
        .log-item {
            color: #10b981;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .log-item.error { color: #ef4444; }
        .log-item.warning { color: #f59e0b; }
        
        /* Content List */
        .content-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f9fafb;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .content-info h4 { color: #1f2937; margin-bottom: 5px; }
        .content-info p { color: #6b7280; font-size: 13px; }
        .content-actions { display: flex; gap: 8px; }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 2000;
            align-items: center;
            justify-content: center;
        }
        .modal.active { display: flex; }
        .modal-content {
            background: white;
            border-radius: 16px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #6b7280;
        }
        
        /* Quick Actions */
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        .action-card {
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            color: white;
            cursor: pointer;
            transition: all 0.3s;
        }
        .action-card:hover {
            transform: translateY(-5px);
        }
        .action-card i { font-size: 28px; margin-bottom: 10px; }
        .action-card.blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
        .action-card.green { background: linear-gradient(135deg, #10b981, #059669); }
        .action-card.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
        .action-card.red { background: linear-gradient(135deg, #ef4444, #dc2626); }
        .action-card.orange { background: linear-gradient(135deg, #f59e0b, #d97706); }
        
        /* Responsive */
        @media (max-width: 992px) {
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
            }
            .main-content {
                margin-right: 0;
            }
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }
        .tab {
            padding: 10px 20px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: #6b7280;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .tab.active {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Settings */
        .settings-group {
            background: #f9fafb;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .settings-group h4 {
            color: #1f2937;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        /* Code Block */
        .code-block {
            background: #1f2937;
            color: #10b981;
            padding: 20px;
            border-radius: 12px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1f2937; }
        ::-webkit-scrollbar-thumb { background: #667eea; border-radius: 4px; }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <h2>🎓 لوحة التحكم</h2>
            <p>{% if settings %}{{ settings.bot_name }}{% else %}بوت اصول الدين{% endif %}</p>
        </div>
        <ul class="nav-menu">
            <li class="nav-item">
                <a class="nav-link active" onclick="showTab('overview')">
                    <i class="fas fa-home"></i>
                    <span>الرئيسية</span>
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" onclick="showTab('content')">
                    <i class="fas fa-book"></i>
                    <span>المحتوى التعليمي</span>
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" onclick="showTab('users')">
                    <i class="fas fa-users"></i>
                    <span>المستخدمين</span>
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" onclick="showTab('broadcast')">
                    <i class="fas fa-bullhorn"></i>
                    <span>الإرسال الجماعي</span>
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" onclick="showTab('settings')">
                    <i class="fas fa-cog"></i>
                    <span>الإعدادات</span>
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" onclick="showTab('logs')">
                    <i class="fas fa-clipboard-list"></i>
                    <span>السجلات</span>
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" onclick="showTab('embed')">
                    <i class="fas fa-code"></i>
                    <span>كود التضمين</span>
                </a>
            </li>
            <li class="nav-item" style="margin-top: 30px;">
                <a class="nav-link" href="/logout" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                    <i class="fas fa-sign-out-alt"></i>
                    <span>تسجيل الخروج</span>
                </a>
            </li>
        </ul>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="page-header">
                <h1 class="page-title">📊 نظرة عامة</h1>
                <span class="badge badge-success">● يعمل</span>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-users"></i></div>
                    <div class="stat-number">{{ stats.total_users }}</div>
                    <div class="stat-label">المستخدمين</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-icon"><i class="fas fa-envelope"></i></div>
                    <div class="stat-number">{{ stats.total_messages }}</div>
                    <div class="stat-label">الرسائل</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-icon"><i class="fas fa-paper-plane"></i></div>
                    <div class="stat-number">{{ stats.broadcasts|length }}</div>
                    <div class="stat-label">الإرسالات</div>
                </div>
                <div class="stat-card info">
                    <div class="stat-icon"><i class="fas fa-calendar"></i></div>
                    <div class="stat-number">{{ stats.start_date }}</div>
                    <div class="stat-label">تاريخ البدء</div>
                </div>
            </div>
            
            <div class="quick-actions">
                <div class="action-card blue" onclick="showTab('broadcast')">
                    <i class="fas fa-bullhorn"></i>
                    <div>إرسال رسالة</div>
                </div>
                <div class="action-card green" onclick="showTab('content')">
                    <i class="fas fa-plus-circle"></i>
                    <div>إضافة محتوى</div>
                </div>
                <div class="action-card purple" onclick="showTab('users')">
                    <i class="fas fa-users-cog"></i>
                    <div>إدارة المستخدمين</div>
                </div>
                <div class="action-card orange" onclick="showTab('settings')">
                    <i class="fas fa-sliders-h"></i>
                    <div>الإعدادات</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📋 آخر الإرسالات</h3>
                </div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>التاريخ</th>
                                <th>الرسالة</th>
                                <th>الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for broadcast in stats.broadcasts[-10:] %}
                            <tr>
                                <td>{{ broadcast.date }}</td>
                                <td>{{ broadcast.message[:50] }}...</td>
                                <td><span class="badge badge-success">{{ broadcast.status }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Content Tab -->
        <div id="content" class="tab-content">
            <div class="page-header">
                <h1 class="page-title">📚 المحتوى التعليمي</h1>
                <button class="btn btn-primary" onclick="openModal('addContentModal')">
                    <i class="fas fa-plus"></i> إضافة محتوى جديد
                </button>
            </div>
            
            <div class="tabs">
                <button class="tab active" onclick="showContentYear('year1')">السنة الأولى</button>
                <button class="tab" onclick="showContentYear('year2')">السنة الثانية</button>
                <button class="tab" onclick="showContentYear('year3')">السنة الثالثة</button>
                <button class="tab" onclick="showContentYear('year4')">السنة الرابعة</button>
            </div>
            
            {% for year_id, year_data in content.items() %}
            <div id="content-{{ year_id }}" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">{{ year_data.title }}</h3>
                        <button class="btn btn-success btn-sm" onclick="addSubject('{{ year_id }}')">
                            <i class="fas fa-plus"></i> إضافة مادة
                        </button>
                    </div>
                    {% for subject in year_data.subjects %}
                    <div class="content-item">
                        <div class="content-info">
                            <h4>{{ subject.title }}</h4>
                            <p>{{ subject.content[:100] }}...</p>
                            <span class="badge badge-{{ 'success' if subject.status == 'active' else 'warning' }}">{{ subject.status }}</span>
                        </div>
                        <div class="content-actions">
                            <button class="btn btn-info btn-sm" onclick="editSubject('{{ year_id }}', {{ subject.id }})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="deleteSubject('{{ year_id }}', {{ subject.id }})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Users Tab -->
        <div id="users" class="tab-content">
            <div class="page-header">
                <h1 class="page-title">👥 المستخدمون</h1>
                <button class="btn btn-primary">
                    <i class="fas fa-file-export"></i> تصدير البيانات
                </button>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">قائمة المستخدمين</h3>
                    <input type="text" class="form-control" style="width: 250px;" placeholder="بحث...">
                </div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>الاسم</th>
                                <th>المعرف</th>
                                <th>تاريخ التسجيل</th>
                                <th>الحالة</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>مستخدم تجريبي</td>
                                <td>@test_user</td>
                                <td>{{ stats.start_date }}</td>
                                <td><span class="badge badge-success">نشط</span></td>
                                <td>
                                    <button class="btn btn-info btn-sm"><i class="fas fa-eye"></i></button>
                                    <button class="btn btn-warning btn-sm"><i class="fas fa-ban"></i></button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Broadcast Tab -->
        <div id="broadcast" class="tab-content">
            <div class="page-header">
                <h1 class="page-title">📢 الإرسال الجماعي</h1>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">إرسال رسالة لجميع المستخدمين</h3>
                </div>
                <form method="POST" action="/broadcast">
                    <div class="form-group">
                        <label>نوع الرسالة</label>
                        <select class="form-control" name="broadcast_type">
                            <option value="all">جميع المستخدمين</option>
                            <option value="active">المستخدمين النشطين</option>
                            <option value="new">المستخدمين الجدد</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>نص الرسالة</label>
                        <textarea class="form-control" name="message" rows="5" placeholder="أدخل نص الرسالة..." required></textarea>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="schedule"> جدولة الرسالة
                        </label>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i> إرسال الآن
                    </button>
                </form>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">سجل الإرسالات</h3>
                </div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>التاريخ</th>
                                <th>النص</th>
                                <th>المستلمين</th>
                                <th>الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for broadcast in stats.broadcasts %}
                            <tr>
                                <td>{{ broadcast.date }}</td>
                                <td>{{ broadcast.message[:50] }}...</td>
                                <td>--</td>
                                <td><span class="badge badge-success">{{ broadcast.status }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Settings Tab -->
        <div id="settings" class="tab-content">
            <div class="page-header">
                <h1 class="page-title">⚙️ الإعدادات</h1>
                <button class="btn btn-success">
                    <i class="fas fa-save"></i> حفظ التغييرات
                </button>
            </div>
            
            <div class="settings-group">
                <h4><i class="fas fa-robot"></i> إعدادات البوت</h4>
                <form method="POST" action="/settings">
                    <div class="form-group">
                        <label>اسم البوت</label>
                        <input type="text" class="form-control" value="{% if settings %}{{ settings.bot_name }}{% else %}بوت اصول الدين{% endif %}">
                    </div>
                    <div class="form-group">
                        <label>رسالة الترحيب</label>
                        <textarea class="form-control" rows="3">{% if settings %}{{ settings.welcome_message }}{% else %}مرحباً بكم في بوت اصول الدين{% endif %}</textarea>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" {% if settings and settings.maintenance_mode %}checked{% endif %}>
                            وضع الصيانة
                        </label>
                    </div>
                </form>
            </div>
            
            <div class="settings-group">
                <h4><i class="fas fa-key"></i> الأمان</h4>
                <div class="form-group">
                    <label>كلمة مرور لوحة التحكم</label>
                    <input type="password" class="form-control" placeholder="أدخل كلمة مرور جديدة">
                </div>
                <div class="form-group">
                    <label>تأكيد كلمة المرور</label>
                    <input type="password" class="form-control" placeholder="أعد إدخال كلمة المرور">
                </div>
            </div>
            
            <div class="settings-group">
                <h4><i class="fas fa-link"></i> الروابط</h4>
                <div class="form-group">
                    <label>رابط الويب هوك</label>
                    <input type="text" class="form-control" value="{{ webhook_url }}/webhook" readonly>
                </div>
                <div class="form-group">
                    <label>رابط التضمين</label>
                    <input type="text" class="form-control" value="{{ webhook_url }}/embed" readonly>
                </div>
            </div>
        </div>
        
        <!-- Logs Tab -->
        <div id="logs" class="tab-content">
            <div class="page-header">
                <h1 class="page-title">📋 السجلات</h1>
                <button class="btn btn-danger">
                    <i class="fas fa-trash"></i> حذف السجلات
                </button>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">سجل الأوامر</h3>
                    <select class="form-control" style="width: 150px;">
                        <option>الكل</option>
                        <option>الأخطاء فقط</option>
                        <option>التحذيرات</option>
                    </select>
                </div>
                <div class="logs-container">
                    {% for log in stats.commands_log[-100:] %}
                    <div class="log-item">{{ log }}</div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <!-- Embed Tab -->
        <div id="embed" class="tab-content">
            <div class="page-header">
                <h1 class="page-title">💻 كود التضمين</h1>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">كود التضمين في بلوجر</h3>
                </div>
                <p style="margin-bottom: 15px; color: #666;">انسخ الكود التالي وضعه في صفحة أو تدوينة على بلوجر:</p>
                <div class="code-block">
<iframe src="{{ webhook_url }}/embed" width="100%" height="800" frameborder="0"></iframe>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">معاينة</h3>
                </div>
                <iframe src="{{ webhook_url }}/embed" width="100%" height="500" frameborder="0" style="border-radius: 12px;"></iframe>
            </div>
        </div>
    </main>
    
    <!-- Add Content Modal -->
    <div id="addContentModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>إضافة محتوى جديد</h3>
                <button class="modal-close" onclick="closeModal('addContentModal')">&times;</button>
            </div>
            <form method="POST" action="/content/add">
                <div class="form-group">
                    <label>السنة الدراسية</label>
                    <select class="form-control" name="year">
                        <option value="year1">السنة الأولى</option>
                        <option value="year2">السنة الثانية</option>
                        <option value="year3">السنة الثالثة</option>
                        <option value="year4">السنة الرابعة</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>عنوان المادة</label>
                    <input type="text" class="form-control" name="title" placeholder="أدخل عنوان المادة" required>
                </div>
                <div class="form-group">
                    <label>المحتوى</label>
                    <textarea class="form-control" name="content" rows="5" placeholder="أدخل المحتوى التعليمي" required></textarea>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">
                    <i class="fas fa-plus"></i> إضافة
                </button>
            </form>
        </div>
    </div>
    
    <script>
        function showTab(tabId) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            // Update nav links
            document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
            event.target.closest('.nav-link').classList.add('active');
        }
        
        function showContentYear(yearId) {
            document.querySelectorAll('#content .tab-content').forEach(tab => tab.classList.remove('active'));
            document.getElementById('content-' + yearId).classList.add('active');
            document.querySelectorAll('#content .tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        function openModal(modalId) {
            document.getElementById(modalId).classList.add('active');
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }
        
        function addSubject(yearId) {
            openModal('addContentModal');
            document.querySelector('select[name="year"]').value = yearId;
        }
        
        function editSubject(yearId, subjectId) {
            alert('سيتم فتح نموذج التعديل للمادة رقم: ' + subjectId);
        }
        
        function deleteSubject(yearId, subjectId) {
            if(confirm('هل أنت متأكد من حذف هذه المادة؟')) {
                // Send delete request
                window.location.href = '/content/delete/' + yearId + '/' + subjectId;
            }
        }
    </script>
</body>
</html>
"""

EMBED_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if settings %}{{ settings.bot_name }}{% else %}بوت اصول الدين{% endif %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
            font-family: 'Cairo', 'Segoe UI', sans-serif;
        }
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            padding: 20px; 
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            padding: 30px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
        }
        .header { 
            text-align: center; 
            padding: 20px 0 30px; 
            border-bottom: 2px solid #f3f4f6; 
            margin-bottom: 25px; 
        }
        h1 { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 28px;
            margin-bottom: 10px;
        }
        .status { 
            display: inline-block;
            text-align: center; 
            padding: 12px 25px; 
            background: #d1fae5; 
            color: #065f46; 
            border-radius: 25px; 
            font-weight: 600;
        }
        .stats { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 15px; 
            margin-bottom: 25px; 
        }
        .stat { 
            background: linear-gradient(135deg, #f3f4f6, #e5e7eb); 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center; 
        }
        .stat-num { font-size: 32px; font-weight: bold; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stat-label { color: #6b7280; font-size: 14px; margin-top: 5px; }
        .link { 
            display: block; 
            text-align: center; 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            padding: 16px; 
            border-radius: 12px; 
            text-decoration: none; 
            font-weight: 700;
            transition: all 0.3s;
        }
        .link:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); 
        }
        .footer {
            text-align: center;
            margin-top: 25px;
            padding-top: 20px;
            border-top: 2px solid #f3f4f6;
            color: #9ca3af;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 {% if settings %}{{ settings.bot_name }}{% else %}بوت اصول الدين{% endif %}</h1>
            <span class="status">● البوت يعمل بنجاح</span>
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-num">{{ stats.total_users }}</div>
                <div class="stat-label">المستخدمين</div>
            </div>
            <div class="stat">
                <div class="stat-num">{{ stats.total_messages }}</div>
                <div class="stat-label">الرسائل</div>
            </div>
        </div>
        <a href="{{ WEBHOOK_URL }}" target="_blank" class="link">🔐 فتح لوحة التحكم</a>
        <div class="footer">
            جميع الحقوق محفوظة © 2024
        </div>
    </div>
</body>
</html>
"""


# ========== Decorators ==========

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ========== Routes ==========

@app.route('/')
def index():
    """Redirect to dashboard"""
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    error = None
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        error = 'كلمة المرور غير صحيحة'
    return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route('/logout')
def logout():
    """Logout and redirect to login"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    return render_template_string(
        DASHBOARD_TEMPLATE, 
        stats=bot_stats, 
        content=bot_data["content"],
        settings=bot_data["settings"],
        webhook_url=WEBHOOK_URL or "https://your-app.onrender.com"
    )


@app.route('/embed')
def embed_dashboard():
    """Embeddable dashboard for Blogger"""
    return render_template_string(
        EMBED_TEMPLATE, 
        stats=bot_stats,
        settings=bot_data["settings"],
        WEBHOOK_URL=WEBHOOK_URL or "https://your-app.onrender.com"
    )


@app.route('/broadcast', methods=['POST'])
@login_required
def broadcast():
    """Broadcast message to all users"""
    message = request.form.get('message')
    broadcast_type = request.form.get('broadcast_type', 'all')
    
    if message:
        broadcast_data = {
            "message": message,
            "type": broadcast_type,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "sent"
        }
        bot_stats['broadcasts'].append(broadcast_data)
        bot_stats['commands_log'].append(f"[{datetime.now()}] Broadcast ({broadcast_type}): {message[:50]}...")
        return jsonify({"status": "success", "message": "تم الإرسال بنجاح"})
    return jsonify({"status": "error", "message": "الرجاء إدخال نص الرسالة"}), 400


@app.route('/settings', methods=['POST'])
@login_required
def update_settings():
    """Update bot settings"""
    bot_data['settings']['bot_name'] = request.form.get('bot_name', 'بوت اصول الدين')
    bot_data['settings']['welcome_message'] = request.form.get('welcome_message', '')
    bot_data['settings']['maintenance_mode'] = 'maintenance_mode' in request.form
    
    bot_stats['commands_log'].append(f"[{datetime.now()}] Settings updated")
    return jsonify({"status": "success", "message": "تم حفظ الإعدادات"})


@app.route('/content/add', methods=['POST'])
@login_required
def add_content():
    """Add new educational content"""
    year = request.form.get('year')
    title = request.form.get('title')
    content = request.form.get('content')
    
    if year and title and content:
        if year not in bot_data['content']:
            bot_data['content'][year] = {"title": f"السنة {year[-1]}", "subjects": []}
        
        new_id = len(bot_data['content'][year]['subjects']) + 1
        bot_data['content'][year]['subjects'].append({
            "id": new_id,
            "title": title,
            "content": content,
            "status": "active"
        })
        
        bot_stats['commands_log'].append(f"[{datetime.now()}] Content added: {title} ({year})")
        return jsonify({"status": "success", "message": "تم إضافة المحتوى"})
    
    return jsonify({"status": "error", "message": "حدث خطأ"}), 400


@app.route('/content/delete/<year>/<int:subject_id>')
@login_required
def delete_content(year, subject_id):
    """Delete educational content"""
    if year in bot_data['content']:
        bot_data['content'][year]['subjects'] = [
            s for s in bot_data['content'][year]['subjects'] 
            if s['id'] != subject_id
        ]
        bot_stats['commands_log'].append(f"[{datetime.now()}] Content deleted: {year}/{subject_id}")
    return redirect(url_for('dashboard'))


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Telegram webhook endpoint"""
    if request.method == 'POST':
        try:
            from telegram import Update
            from telegram.ext import Application
            
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            bot = application.bot
            
            update_data = request.get_json(force=True)
            update = Update.de_json(update_data, bot)
            
            # Process update (simplified for webhook)
            logger.info(f"Webhook received: {update}")
            
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    return "Bot is running! Use POST method.", 200


@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy", 
        "bot": "running",
        "settings": bot_data['settings']
    }), 200


@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for statistics"""
    return jsonify({
        "stats": bot_stats,
        "content": bot_data['content'],
        "settings": bot_data['settings']
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True)
