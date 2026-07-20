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
التفاعل!', 'success')

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
