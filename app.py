<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBT-System | لوحة التحكم</title>
    <style>
        :root {
            --bg-main: #313338;
            --bg-sidebar: #2b2d31;
            --bg-card: #232428;
            --accent: #5865f2;
            --accent-hover: #4752c4;
            --text-main: #f2f3f5;
            --text-muted: #949ba4;
            --border: #1f2023;
            --success: #23a55a;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            direction: rtl;
            text-align: right;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* القائمة الجانبية الثابتة والواضحة */
        .sidebar {
            width: 280px;
            background-color: var(--bg-sidebar);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow-y: auto;
            flex-shrink: 0;
        }

        .sidebar-header {
            padding: 20px;
            font-size: 1.1rem;
            font-weight: bold;
            border-bottom: 1px solid var(--border);
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .bot-logo {
            width: 32px;
            height: 32px;
            background-color: var(--accent);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }

        .menu-category {
            padding: 15px 20px 5px;
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 0.5px;
        }

        .menu-item {
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--text-muted);
            text-decoration: none;
            transition: 0.2s;
            cursor: pointer;
            font-size: 0.9rem;
        }

        .menu-item:hover, .menu-item.active {
            background-color: rgba(255, 255, 255, 0.05);
            color: var(--text-main);
        }

        .menu-item-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: var(--success);
            border-radius: 50%;
        }

        /* المحتوى الرئيسي */
        .main-content {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--bg-card);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }

        .section-title h1 {
            font-size: 1.4rem;
            margin-bottom: 5px;
        }

        .section-title p {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        /* أزرار التفعيل (Switch) */
        .switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 26px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #4e5058;
            transition: .3s;
            border-radius: 26px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            right: 4px;
            bottom: 4px;
            background-color: white;
            transition: .3s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: var(--success);
        }

        input:checked + .slider:before {
            transform: translateX(-24px);
        }

        /* الكروت */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
        }

        .card {
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 15px;
        }

        .card-info h3 {
            font-size: 1.1rem;
            margin-bottom: 5px;
            color: var(--text-main);
            direction: ltr;
            text-align: right;
        }

        .card-info p {
            color: var(--text-muted);
            font-size: 0.85rem;
            line-height: 1.4;
        }

        .card-action {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border);
            padding-top: 15px;
        }

        .btn-edit {
            background-color: var(--bg-sidebar);
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 6px 15px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85rem;
            transition: 0.2s;
        }

        .btn-edit:hover {
            background-color: #35373c;
        }

        /* التجاوب مع الجوال */
        @media (max-width: 768px) {
            body {
                flex-direction: column;
                overflow: auto;
            }
            .sidebar {
                width: 100%;
                height: auto;
                max-height: 220px;
                border-left: none;
                border-bottom: 1px solid var(--border);
            }
            .main-content {
                overflow: visible;
                padding: 15px;
            }
        }
    </style>
</head>
<body>

    <!-- القائمة الجانبية الواضحة -->
    <div class="sidebar">
        <div class="sidebar-header">
            <div class="bot-logo">🤖</div>
            <span>OBT-System</span>
        </div>

        <div class="menu-category">عام</div>
        <a href="/dashboard/settings" class="menu-item">
            <div class="menu-item-content"><span>⚙️</span> إعدادات السيرفر</div>
        </a>
        <a href="/dashboard/logs" class="menu-item">
            <div class="menu-item-content"><span>📋</span> اللوق والتقارير</div>
        </a>

        <div class="menu-category">قائمة الخصائص</div>
        <a href="/dashboard" class="menu-item active">
            <div class="menu-item-content"><span>⚡</span> الأوامر العامة</div>
            <div class="status-dot"></div>
        </a>
        <a href="/dashboard/economy" class="menu-item">
            <div class="menu-item-content"><span>💰</span> الاقتصاد والأموال</div>
            <div class="status-dot"></div>
        </a>
        <a href="/dashboard/tickets" class="menu-item">
            <div class="menu-item-content"><span>🎫</span> التذاكر والدعم</div>
            <div class="status-dot"></div>
        </a>
        <a href="/dashboard/moderation" class="menu-item">
            <div class="menu-item-content"><span>🛡️</span> الإشراف والحماية</div>
            <div class="status-dot"></div>
        </a>
    </div>

    <!-- المحتوى الرئيسي -->
    <div class="main-content">
        
        <div class="section-header">
            <div class="section-title">
                <h1>الأوامر العامة</h1>
                <p>لوحة التحكم الخاصة بـ OBT-System لإدارة الأوامر والخصائص</p>
            </div>
            <label class="switch">
                <input type="checkbox" checked>
                <span class="slider"></span>
            </label>
        </div>

        <div class="cards-grid">
            
            <div class="card">
                <div class="card-info">
                    <h3>/moveme</h3>
                    <p>ينقلك إلى روم صوتي محدد.</p>
                </div>
                <div class="card-action">
                    <button class="btn-edit" onclick="alert('جارٍ تطوير إعدادات أمر moveme');">تعديل</button>
                    <label class="switch" style="width: 40px; height: 22px;">
                        <input type="checkbox" checked>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

            <div class="card">
                <div class="card-info">
                    <h3>/profile</h3>
                    <p>عرض بطاقة التعريف الشخصية المخصصة لك أو لشخص آخر.</p>
                </div>
                <div class="card-action">
                    <button class="btn-edit" onclick="alert('جارٍ تطوير إعدادات أمر profile');">تعديل</button>
                    <label class="switch" style="width: 40px; height: 22px;">
                        <input type="checkbox" checked>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

            <div class="card">
                <div class="card-info">
                    <h3>/user</h3>
                    <p>يعرض معلومات المستخدم، مثل تاريخ دخول السيرفر وتاريخ التسجيل.</p>
                </div>
                <div class="card-action">
                    <button class="btn-edit" onclick="alert('جارٍ تطوير إعدادات أمر user');">تعديل</button>
                    <label class="switch" style="width: 40px; height: 22px;">
                        <input type="checkbox" checked>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

            <div class="card">
                <div class="card-info">
                    <h3>/avatar</h3>
                    <p>الحصول على الصورة الرمزية للمستخدمين بجودة عالية.</p>
                </div>
                <div class="card-action">
                    <button class="btn-edit" onclick="alert('جارٍ تطوير إعدادات أمر avatar');">تعديل</button>
                    <label class="switch" style="width: 40px; height: 22px;">
                        <input type="checkbox" checked>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

        </div>

    </div>

</body>
</html>
