"""
OBT Dashboard — لوحة التحكم الويب
Flask + Discord OAuth2
"""

import os
import sys
import sqlite3
import json
import requests
from functools import wraps
from datetime import datetime
from flask import (Flask, render_template, redirect, url_for, request,
                   session, jsonify, flash, g)

# ── App setup ──────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', os.urandom(24))
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ── Config ─────────────────────────────────────────────────────────────────────

DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
BOT_TOKEN = os.getenv('DISCORD_TOKEN', '')

# Database path — same SQLite DB as the bot
DB_PATH = os.getenv('DB_PATH', os.path.join(
    os.path.dirname(__file__), '..', 'obt-system', 'obt_system.db'
))

DISCORD_API = 'https://discord.com/api/v10'
OAUTH_SCOPES = 'identify guilds'

# Redirect URI — auto-detect from Replit env or use env var
def get_redirect_uri():
    base = os.getenv('DASHBOARD_URL', '')
    if not base:
        dev_domain = os.getenv('REPLIT_DEV_DOMAIN', '')
        if dev_domain:
            base = f'https://{dev_domain}'
        else:
            base = 'http://localhost:5000'
    return base.rstrip('/') + '/callback'

# ── Database ───────────────────────────────────────────────────────────────────

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()

def query_db(query, args=(), one=False, commit=False):
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
        return cur.lastrowid
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def ensure_guild(guild_id: int):
    existing = query_db("SELECT guild_id FROM guilds WHERE guild_id = ?", (guild_id,), one=True)
    if not existing:
        query_db("INSERT INTO guilds (guild_id) VALUES (?)", (guild_id,), commit=True)

# ── Discord API helpers ────────────────────────────────────────────────────────

def discord_get(endpoint: str, token: str):
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{DISCORD_API}{endpoint}', headers=headers, timeout=10)
    if r.status_code == 200:
        return r.json()
    return None

def bot_get(endpoint: str):
    headers = {'Authorization': f'Bot {BOT_TOKEN}'}
    r = requests.get(f'{DISCORD_API}{endpoint}', headers=headers, timeout=10)
    if r.status_code == 200:
        return r.json()
    return None

def get_bot_guilds():
    """Get list of guilds the bot is in."""
    if not BOT_TOKEN:
        return []
    data = bot_get('/users/@me/guilds')
    return {str(g['id']): g for g in (data or [])}

def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def requires_guild(f):
    @wraps(f)
    def decorated(guild_id, *args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        # Check user has access to this guild
        user_guilds = session.get('guilds', {})
        if str(guild_id) not in user_guilds:
            flash('ليس لديك وصول لهذا السيرفر.', 'error')
            return redirect(url_for('servers'))
        g.guild_id = int(guild_id)
        g.guild_info = user_guilds[str(guild_id)]
        return f(guild_id, *args, **kwargs)
    return decorated

# ── Auth routes ────────────────────────────────────────────────────────────────

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('servers'))
    return render_template('login.html')

@app.route('/auth')
def auth():
    redirect_uri = get_redirect_uri()
    url = (
        f'https://discord.com/api/oauth2/authorize'
        f'?client_id={DISCORD_CLIENT_ID}'
        f'&redirect_uri={requests.utils.quote(redirect_uri)}'
        f'&response_type=code'
        f'&scope={requests.utils.quote(OAUTH_SCOPES)}'
    )
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        flash('فشل تسجيل الدخول.', 'error')
        return redirect(url_for('login'))

    redirect_uri = get_redirect_uri()

    # Exchange code for token
    r = requests.post(f'{DISCORD_API}/oauth2/token', data={
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }, timeout=10)

    if r.status_code != 200:
        flash('فشل الحصول على التوكن.', 'error')
        return redirect(url_for('login'))

    token_data = r.json()
    access_token = token_data.get('access_token')

    # Get user info
    user = discord_get('/users/@me', access_token)
    if not user:
        flash('فشل الحصول على معلومات المستخدم.', 'error')
        return redirect(url_for('login'))

    # Get user guilds
    guilds_list = discord_get('/users/@me/guilds', access_token)
    MANAGE_GUILD = 0x20

    # Filter: user has Manage Server permission
    admin_guilds = {
        str(g['id']): g for g in (guilds_list or [])
        if (int(g.get('permissions', 0)) & MANAGE_GUILD) or g.get('owner')
    }

    # Also filter: bot must be in the guild
    bot_guilds = get_bot_guilds()
    shared_guilds = {
        gid: ginfo for gid, ginfo in admin_guilds.items()
        if gid in bot_guilds
    }

    session['user'] = user
    session['access_token'] = access_token
    session['guilds'] = shared_guilds

    return redirect(url_for('servers'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Server selection ───────────────────────────────────────────────────────────

@app.route('/')
@requires_login
def servers():
    guilds = session.get('guilds', {})
    return render_template('servers.html', guilds=guilds, user=session['user'])

# ── Dashboard overview ─────────────────────────────────────────────────────────

@app.route('/dashboard/<int:guild_id>')
@requires_login
@requires_guild
def dashboard(guild_id):
    ensure_guild(guild_id)
    guild_data = query_db("SELECT * FROM guilds WHERE guild_id = ?", (guild_id,), one=True)
    
    # Stats
    member_count = len(query_db("SELECT DISTINCT user_id FROM points WHERE guild_id = ?", (guild_id,)))
    total_tickets = query_db("SELECT COUNT(*) as c FROM tickets WHERE guild_id = ?", (guild_id,), one=True)
    open_tickets = query_db("SELECT COUNT(*) as c FROM tickets WHERE guild_id = ? AND status = 'open'", (guild_id,), one=True)
    total_warnings = query_db("SELECT COUNT(*) as c FROM warnings WHERE guild_id = ?", (guild_id,), one=True)
    total_clans = query_db("SELECT COUNT(*) as c FROM clans WHERE guild_id = ?", (guild_id,), one=True)
    recent_actions = query_db(
        "SELECT * FROM action_logs WHERE guild_id = ? ORDER BY timestamp DESC LIMIT 8", (guild_id,))

    stats = {
        'members_with_points': member_count,
        'total_tickets': total_tickets['c'] if total_tickets else 0,
        'open_tickets': open_tickets['c'] if open_tickets else 0,
        'total_warnings': total_warnings['c'] if total_warnings else 0,
        'total_clans': total_clans['c'] if total_clans else 0,
    }

    return render_template('dashboard.html',
        guild_id=guild_id,
        guild_info=g.guild_info,
        guild_data=guild_data,
        stats=stats,
        recent_actions=recent_actions,
        user=session['user']
    )

# ── Administration & Protection ────────────────────────────────────────────────

@app.route('/dashboard/<int:guild_id>/admin', methods=['GET', 'POST'])
@requires_login
@requires_guild
def admin(guild_id):
    ensure_guild(guild_id)
    if request.method == 'POST':
        data = request.form

        # Guild settings
        guild_kwargs = {}
        if 'prefix' in data:
            guild_kwargs['prefix'] = data['prefix'] or '!'
        if 'log_channel' in data:
            ch = data['log_channel']
            guild_kwargs['log_channel'] = int(ch) if ch else None
        if 'mute_role' in data:
            r = data['mute_role']
            guild_kwargs['mute_role'] = int(r) if r else None

        if guild_kwargs:
            sets = ', '.join(f"{k} = ?" for k in guild_kwargs)
            vals = list(guild_kwargs.values()) + [guild_id]
            query_db(f"UPDATE guilds SET {sets} WHERE guild_id = ?", vals, commit=True)

        # Logs config — individual log channel fields
        log_fields = ['ban_log', 'kick_log', 'delete_log', 'edit_log', 'channel_log',
                      'role_log', 'member_log', 'name_log', 'mute_log', 'ticket_log',
                      'command_log', 'invite_log']
        log_kwargs = {}
        for field in log_fields:
            if field in data:
                val = data[field]
                log_kwargs[field] = int(val) if val else None

        if log_kwargs:
            existing_log = query_db("SELECT guild_id FROM logs_config WHERE guild_id = ?", (guild_id,), one=True)
            if existing_log:
                sets = ', '.join(f"{k} = ?" for k in log_kwargs)
                vals = list(log_kwargs.values()) + [guild_id]
                query_db(f"UPDATE logs_config SET {sets} WHERE guild_id = ?", vals, commit=True)
            else:
                log_kwargs['guild_id'] = guild_id
                cols = ', '.join(log_kwargs.keys())
                placeholders = ', '.join('?' for _ in log_kwargs)
                query_db(f"INSERT INTO logs_config ({cols}) VALUES ({placeholders})",
                         list(log_kwargs.values()), commit=True)

        # Protection settings
        prot_kwargs = {}
        bool_fields = ['anti_spam', 'anti_links', 'anti_mention', 'anti_invites',
                       'anti_bots', 'anti_channel_create', 'anti_role_create',
                       'anti_channel_delete', 'anti_role_delete']
        for field in bool_fields:
            prot_kwargs[field] = 1 if field in data else 0

        if 'spam_limit' in data and data['spam_limit']:
            prot_kwargs['spam_limit'] = int(data['spam_limit'])
        if 'mention_limit' in data and data['mention_limit']:
            prot_kwargs['mention_limit'] = int(data['mention_limit'])
        if 'warn_limit' in data and data['warn_limit']:
            prot_kwargs['warn_limit'] = int(data['warn_limit'])
        if 'warn_action' in data:
            prot_kwargs['warn_action'] = data['warn_action']

        # Upsert protection
        existing = query_db("SELECT guild_id FROM protection_config WHERE guild_id = ?", (guild_id,), one=True)
        if existing:
            sets = ', '.join(f"{k} = ?" for k in prot_kwargs)
            vals = list(prot_kwargs.values()) + [guild_id]
            query_db(f"UPDATE protection_config SET {sets} WHERE guild_id = ?", vals, commit=True)
        else:
            prot_kwargs['guild_id'] = guild_id
            cols = ', '.join(prot_kwargs.keys())
            placeholders = ', '.join('?' for _ in prot_kwargs)
            query_db(f"INSERT INTO protection_config ({cols}) VALUES ({placeholders})",
                     list(prot_kwargs.values()), commit=True)

        flash('✅ تم حفظ الإعدادات بنجاح!', 'success')
        return redirect(url_for('admin', guild_id=guild_id))

    guild_data = query_db("SELECT * FROM guilds WHERE guild_id = ?", (guild_id,), one=True)
    protection = query_db("SELECT * FROM protection_config WHERE guild_id = ?", (guild_id,), one=True)

    # Log config
    log_config = query_db("SELECT * FROM logs_config WHERE guild_id = ?", (guild_id,), one=True)

    # Recent warnings
    warnings = query_db(
        "SELECT * FROM warnings WHERE guild_id = ? ORDER BY timestamp DESC LIMIT 20", (guild_id,))

    return render_template('admin.html',
        guild_id=guild_id,
        guild_info=g.guild_info,
        guild_data=guild_data,
        protection=protection,
        log_config=log_config,
        warnings=warnings,
        user=session['user']
    )

# ── Ticket System ──────────────────────────────────────────────────────────────

@app.route('/dashboard/<int:guild_id>/tickets', methods=['GET', 'POST'])
@requires_login
@requires_guild
def tickets(guild_id):
    ensure_guild(guild_id)
    if request.method == 'POST':
        data = request.form
        action = data.get('action')

        if action == 'save_config':
            kwargs = {}
            if data.get('support_role'):
                kwargs['support_role'] = int(data['support_role'])
            if data.get('log_channel'):
                kwargs['log_channel'] = int(data['log_channel'])
            if data.get('category_id'):
                kwargs['category_id'] = int(data['category_id'])
            kwargs['rating_enabled'] = 1 if 'rating_enabled' in data else 0
            kwargs['auto_close'] = 1 if 'auto_close' in data else 0

            # Departments
            depts = [d.strip() for d in data.get('departments', '').split(',') if d.strip()]
            if depts:
                kwargs['departments'] = json.dumps(depts, ensure_ascii=False)

            existing = query_db("SELECT guild_id FROM ticket_config WHERE guild_id = ?", (guild_id,), one=True)
            if existing:
                sets = ', '.join(f"{k} = ?" for k in kwargs)
                vals = list(kwargs.values()) + [guild_id]
                query_db(f"UPDATE ticket_config SET {sets} WHERE guild_id = ?", vals, commit=True)
            else:
                kwargs['guild_id'] = guild_id
                cols = ', '.join(kwargs.keys())
                placeholders = ', '.join('?' for _ in kwargs)
                query_db(f"INSERT INTO ticket_config ({cols}) VALUES ({placeholders})",
                         list(kwargs.values()), commit=True)
            flash('✅ تم حفظ إعدادات التذاكر!', 'success')

        elif action == 'close_ticket':
            ticket_channel = data.get('channel_id')
            if ticket_channel:
                query_db("UPDATE tickets SET status = 'closed', closed_at = ? WHERE channel_id = ? AND guild_id = ?",
                         (datetime.utcnow().isoformat(), int(ticket_channel), guild_id), commit=True)
                flash('✅ تم إغلاق التذكرة.', 'success')

        return redirect(url_for('tickets', guild_id=guild_id))

    config = query_db("SELECT * FROM ticket_config WHERE guild_id = ?", (guild_id,), one=True)
    all_tickets = query_db(
        "SELECT * FROM tickets WHERE guild_id = ? ORDER BY timestamp DESC LIMIT 50", (guild_id,))
    open_count = query_db(
        "SELECT COUNT(*) as c FROM tickets WHERE guild_id = ? AND status = 'open'", (guild_id,), one=True)
    closed_count = query_db(
        "SELECT COUNT(*) as c FROM tickets WHERE guild_id = ? AND status = 'closed'", (guild_id,), one=True)

    departments = ['عام', 'فني', 'إداري', 'شكاوى']
    if config and config['departments']:
        try:
            departments = json.loads(config['departments'])
        except Exception:
            pass

    return render_template('tickets.html',
        guild_id=guild_id,
        guild_info=g.guild_info,
        config=config,
        tickets=all_tickets,
        open_count=open_count['c'] if open_count else 0,
        closed_count=closed_count['c'] if closed_count else 0,
        departments=departments,
        user=session['user']
    )

# ── Points & Clans ─────────────────────────────────────────────────────────────

@app.route('/dashboard/<int:guild_id>/points', methods=['GET', 'POST'])
@requires_login
@requires_guild
def points(guild_id):
    ensure_guild(guild_id)
    if request.method == 'POST':
        data = request.form
        action = data.get('action')

        if action == 'modify_points':
            user_id = data.get('user_id')
            amount = int(data.get('amount', 0))
            point_type = data.get('point_type', 'member')
            operation = data.get('operation', 'add')

            if user_id and amount:
                if operation == 'add':
                    existing = query_db(
                        "SELECT points FROM points WHERE guild_id = ? AND user_id = ? AND point_type = ?",
                        (guild_id, int(user_id), point_type), one=True)
                    if existing:
                        query_db(
                            "UPDATE points SET points = points + ? WHERE guild_id = ? AND user_id = ? AND point_type = ?",
                            (amount, guild_id, int(user_id), point_type), commit=True)
                    else:
                        query_db(
                            "INSERT INTO points (guild_id, user_id, points, point_type) VALUES (?, ?, ?, ?)",
                            (guild_id, int(user_id), amount, point_type), commit=True)
                    flash(f'✅ تمت إضافة {amount} نقطة.', 'success')
                else:
                    query_db(
                        "UPDATE points SET points = MAX(0, points - ?) WHERE guild_id = ? AND user_id = ? AND point_type = ?",
                        (amount, guild_id, int(user_id), point_type), commit=True)
                    flash(f'✅ تم خصم {amount} نقطة.', 'success')

        elif action == 'add_clan_points':
            clan_id = data.get('clan_id')
            amount = int(data.get('clan_amount', 0))
            if clan_id and amount:
                query_db("UPDATE clans SET points = points + ? WHERE id = ? AND guild_id = ?",
                         (amount, int(clan_id), guild_id), commit=True)
                flash(f'✅ تمت إضافة {amount} نقطة للكلان.', 'success')

        elif action == 'delete_clan':
            clan_id = data.get('clan_id')
            if clan_id:
                query_db("DELETE FROM clan_members WHERE clan_id = ?", (int(clan_id),), commit=True)
                query_db("DELETE FROM clans WHERE id = ? AND guild_id = ?",
                         (int(clan_id), guild_id), commit=True)
                flash('✅ تم حذف الكلان.', 'success')

        return redirect(url_for('points', guild_id=guild_id))

    # Leaderboards
    member_lb = query_db(
        "SELECT user_id, points FROM points WHERE guild_id = ? AND point_type = 'member' ORDER BY points DESC LIMIT 20",
        (guild_id,))
    admin_lb = query_db(
        "SELECT user_id, points FROM points WHERE guild_id = ? AND point_type = 'admin' ORDER BY points DESC LIMIT 20",
        (guild_id,))
    clan_lb = query_db(
        "SELECT user_id, points FROM points WHERE guild_id = ? AND point_type = 'clan' ORDER BY points DESC LIMIT 20",
        (guild_id,))

    clans = query_db(
        "SELECT c.*, COUNT(cm.user_id) as member_count FROM clans c "
        "LEFT JOIN clan_members cm ON c.id = cm.clan_id "
        "WHERE c.guild_id = ? GROUP BY c.id ORDER BY c.points DESC",
        (guild_id,))

    rewards = query_db(
        "SELECT * FROM point_rewards WHERE guild_id = ? ORDER BY required_points ASC", (guild_id,))

    return render_template('points.html',
        guild_id=guild_id,
        guild_info=g.guild_info,
        member_lb=member_lb,
        admin_lb=admin_lb,
        clan_lb=clan_lb,
        clans=clans,
        rewards=rewards,
        user=session['user']
    )

# ── Content Creators & Interactions ───────────────────────────────────────────

@app.route('/dashboard/<int:guild_id>/content', methods=['GET', 'POST'])
@requires_login
@requires_guild
def content(guild_id):
    ensure_guild(guild_id)
    if request.method == 'POST':
        data = request.form
        action = data.get('action')

        if action == 'save_welcome':
            kwargs = {}
            if data.get('welcome_channel'):
                kwargs['welcome_channel'] = int(data['welcome_channel'])
            if data.get('goodbye_channel'):
                kwargs['goodbye_channel'] = int(data['goodbye_channel'])
            if 'welcome_message' in data:
                kwargs['welcome_message'] = data['welcome_message']
            if 'goodbye_message' in data:
                kwargs['goodbye_message'] = data['goodbye_message']
            if data.get('verify_channel'):
                kwargs['verify_channel'] = int(data['verify_channel'])
            if data.get('verify_role'):
                kwargs['verify_role'] = int(data['verify_role'])
            if data.get('auto_role'):
                kwargs['auto_role'] = int(data['auto_role'])

            if kwargs:
                sets = ', '.join(f"{k} = ?" for k in kwargs)
                vals = list(kwargs.values()) + [guild_id]
                query_db(f"UPDATE guilds SET {sets} WHERE guild_id = ?", vals, commit=True)
            flash('✅ تم حفظ إعدادات التفاعل!', 'success')

        elif action == 'remove_creator':
            user_id = data.get('creator_user_id')
            if user_id:
                query_db("DELETE FROM content_creators WHERE guild_id = ? AND user_id = ?",
                         (guild_id, int(user_id)), commit=True)
                flash('✅ تم إزالة صانع المحتوى.', 'success')

        elif action == 'add_creator':
            user_id = data.get('new_user_id')
            yt_id = data.get('youtube_channel_id')
            yt_name = data.get('youtube_name')
            announce_ch = data.get('announce_channel')
            if user_id and yt_id and yt_name:
                query_db(
                    """INSERT INTO content_creators (guild_id, user_id, youtube_channel_id, youtube_name, announce_channel)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(guild_id, user_id) DO UPDATE SET
                       youtube_channel_id = excluded.youtube_channel_id,
                       youtube_name = excluded.youtube_name,
                       announce_channel = excluded.announce_channel""",
                    (guild_id, int(user_id), yt_id, yt_name,
                     int(announce_ch) if announce_ch else None), commit=True)
                flash('✅ تم إضافة صانع المحتوى.', 'success')

        return redirect(url_for('content', guild_id=guild_id))

    guild_data = query_db("SELECT * FROM guilds WHERE guild_id = ?", (guild_id,), one=True)
    creators = query_db(
        "SELECT * FROM content_creators WHERE guild_id = ?", (guild_id,))
    
    # Reaction roles
    reaction_roles = query_db(
        "SELECT * FROM reaction_roles WHERE guild_id = ?", (guild_id,))

    return render_template('content.html',
        guild_id=guild_id,
        guild_info=g.guild_info,
        guild_data=guild_data,
        creators=creators,
        reaction_roles=reaction_roles,
        user=session['user']
    )

# ── API endpoints (JSON) ───────────────────────────────────────────────────────

@app.route('/api/<int:guild_id>/stats')
@requires_login
@requires_guild
def api_stats(guild_id):
    member_lb = query_db(
        "SELECT user_id, points FROM points WHERE guild_id = ? AND point_type = 'member' ORDER BY points DESC LIMIT 10",
        (guild_id,))
    return jsonify([dict(row) for row in member_lb])

@app.route('/api/<int:guild_id>/warnings/<int:user_id>', methods=['DELETE'])
@requires_login
@requires_guild
def api_delete_warning(guild_id, user_id):
    warning_id = request.json.get('warning_id') if request.json else None
    if warning_id:
        query_db("DELETE FROM warnings WHERE id = ? AND guild_id = ?", (warning_id, guild_id), commit=True)
    return jsonify({'success': True})

# ── Template context ───────────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    return {
        'now': datetime.utcnow(),
        'bot_name': 'OBT System',
    }

@app.template_filter('datetime_fmt')
def datetime_fmt(value):
    if not value:
        return '—'
    try:
        dt = datetime.fromisoformat(str(value)[:19])
        return dt.strftime('%Y/%m/%d %H:%M')
    except Exception:
        return str(value)[:16]

@app.template_filter('user_mention')
def user_mention(user_id):
    return f'<@{user_id}>'

# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
