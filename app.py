from flask import Flask, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from database import Base, GuildSettings, Ticket, ModerationCase, Clan, EconomyPoint

app = Flask(__name__)

# إعداد قاعدة البيانات باستخدام ملف SQLite الموجود في المشروع
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obt_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ربط SQLAlchemy بقاعدة البيانات ونماذج جداول البوت
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# إنشاء الجداول تلقائياً في حال لم تكن موجودة
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """عرض صفحة لوحة التحكم الرئيسية"""
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    """مسار برمجي (API) لجلب إحصائيات البوت الحقيقية من قاعدة البيانات وعرضها في الداشبورد"""
    try:
        guilds_count = GuildSettings.query.count()
        tickets_count = Ticket.query.filter_by(status='open').count()
        clans_count = Clan.query.count()
        
        return jsonify({
            "status": "success",
            "guilds": guilds_count,
            "active_tickets": tickets_count,
            "clans": clans_count
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
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
