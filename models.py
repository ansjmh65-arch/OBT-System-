<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم النظام - ProBot Style</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --probot-dark: #1e1f22;
            --probot-darker: #111214;
            --probot-card: #2b2d31;
            --probot-accent: #5865f2;
            --probot-green: #23a55a;
            --probot-text: #dbdee1;
            --probot-muted: #949ba4;
        }
        body {
            background-color: var(--probot-darker);
            color: var(--probot-text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        /* Sidebar */
        .sidebar {
            width: 280px;
            background-color: var(--probot-dark);
            display: flex;
            flex-direction: column;
            border-left: 1px solid #3f4147;
            height: 100%;
        }
        .server-header {
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            border-bottom: 1px solid #3f4147;
            background-color: rgba(0,0,0,0.1);
        }
        .server-icon {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: var(--probot-accent);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: #fff;
        }
        .nav-sections {
            flex: 1;
            overflow-y: auto;
            padding: 15px 10px;
        }
        .nav-item-custom {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 15px;
            color: var(--probot-muted);
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 5px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        .nav-item-custom:hover, .nav-item-custom.active {
            background-color: var(--probot-card);
            color: #fff;
        }
        .nav-item-custom i {
            font-size: 18px;
            width: 25px;
            text-align: center;
        }
        /* Main Content */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow-y: auto;
        }
        .top-navbar {
            height: 70px;
            background-color: var(--probot-dark);
            border-bottom: 1px solid #3f4147;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
        }
        .content-body {
            padding: 30px;
            flex: 1;
        }
        .probot-card {
            background-color: var(--probot-card);
            border: 1px solid #3f4147;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
        }
        .btn-probot {
            background-color: var(--probot-accent);
            color: #fff;
            border: none;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.2s;
        }
        .btn-probot:hover {
            background-color: #4752c4;
            color: #fff;
        }
        .form-control, .form-select {
            background-color: var(--probot-darker) !important;
            border: 1px solid #222327 !important;
            color: #fff !important;
            border-radius: 8px;
            padding: 12px;
        }
        .form-control:focus, .form-select:focus {
            border-color: var(--probot-accent) !important;
            box-shadow: 0 0 0 0.25rem rgba(88, 101, 242, 0.25);
        }
        .section-pane {
            display: none;
        }
        .section-pane.active {
            display: block;
        }
    </style>
</head>
<body>

    <!-- الشريط الجانبي (يشمل الـ 11 أقسام الكاملة تماماً مثل بروبوت) -->
    <div class="sidebar">
        <div class="server-header">
            <div class="server-icon"><i class="fa-solid fa-server"></i></div>
            <div>
                <h6 class="mb-0 fw-bold text-white">{{ guild_name }}</h6>
                <small class="text-muted">معرف: {{ guild_id }}</small>
            </div>
        </div>
        <div class="nav-sections">
            {% for section in sections %}
            <a href="#" class="nav-item-custom {% if loop.first %}active{% endif %}" onclick="switchSection('section-{{ section.route }}', this); return false;">
                <span>{{ section.icon }}</span>
                <span>{{ section.name }}</span>
            </a>
            {% endfor %}
        </div>
    </div>

    <!-- المحتوى الرئيسي للداشبورد -->
    <div class="main-content">
        <div class="top-navbar">
            <h4 class="mb-0 text-white"><i class="fa-solid fa-sliders me-2"></i> لوحة التحكم المركزية</h4>
            <div class="d-flex align-items-center gap-3">
                <span class="badge bg-success p-2 px-3 rounded-pill"><i class="fa-solid fa-circle-check me-1"></i> متصل بنجاح</span>
            </div>
        </div>

        <div class="content-body">
            <!-- 1. الإعدادات العامة -->
            <div id="section-general" class="section-pane active">
                <div class="probot-card">
                    <h3 class="text-white mb-3">⚙️ الإعدادات العامة</h3>
                    <p class="text-muted">تحكم في البادئة العامة وإعدادات البوت الأساسية للسيرفر.</p>
                    <hr class="border-secondary">
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label text-white fw-bold">بادئة الأوامر (Prefix)</label>
                            <input type="text" class="form-control" value="!">
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-white fw-bold">لغة البوت المفضلة</label>
                            <select class="form-select">
                                <option value="ar" selected>العربية</option>
                                <option value="en">English</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-probot">حفظ التغييرات</button>
                    </form>
                </div>
            </div>

            <!-- 2. الحماية (Protection) -->
            <div id="section-protection" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">🛡️ نظام الحماية المتقدمة</h3>
                    <p class="text-muted">حماية السيرفر ضد السبام، الروابط الضارة، والتخريب.</p>
                    <hr class="border-secondary">
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="antiSpam" checked>
                        <label class="form-check-label text-white fw-bold" for="antiSpam">تفعيل نظام منع السبام التلقائي</label>
                    </div>
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="antiLinks" checked>
                        <label class="form-check-label text-white fw-bold" for="antiLinks">منع نشر الروابط الخارجية والدعوات</label>
                    </div>
                    <button type="button" class="btn btn-probot">تحديث إعدادات الحماية</button>
                </div>
            </div>

            <!-- 3. الترحيب والمغادرة -->
            <div id="section-welcomer" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">👋 نظام الترحيب والمغادرة</h3>
                    <p class="text-muted">خصص رسائل ترحيب الأعضاء الجدد بشكل احترافي مع صور وبطاقات.</p>
                    <hr class="border-secondary">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">روم الترحيب</label>
                        <select class="form-select">
                            <option>#الترحيب-welcomes</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">نص رسالة الترحيب</label>
                        <textarea class="form-control" rows="4">أهلاً بك يا {user} في سيرفرنا! نورتنا 🌹</textarea>
                    </div>
                    <button type="button" class="btn btn-probot">حفظ رسالة الترحيب</button>
                </div>
            </div>

            <!-- 4. الردود التلقائية -->
            <div id="section-auto_responder" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">🤖 الردود التلقائية</h3>
                    <p class="text-muted">برمج ردود تلقائية لكلمات مفتاحية محددة يرسلها الأعضاء.</p>
                    <hr class="border-secondary">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">الكلمة المفتاحية</label>
                        <input type="text" class="form-control" placeholder="مثال: السلام عليكم">
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">رد البوت</label>
                        <input type="text" class="form-control" placeholder="مثال: وعليكم السلام ورحمة الله وبركاته ❤️">
                    </div>
                    <button type="button" class="btn btn-probot">إضافة الرد التلقائي</button>
                </div>
            </div>

            <!-- 5. نظام التذاكر -->
            <div id="section-tickets" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">🎫 نظام التذاكر والدعم الفني</h3>
                    <p class="text-muted">أنشئ لوحة تذاكر تفاعلية لخدمة الأعضاء وحل مشاكلهم.</p>
                    <hr class="border-secondary">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">روم إرسال بانل التذاكر</label>
                        <select class="form-select">
                            <option>#الدعم-الفني-tickets</option>
                        </select>
                    </div>
                    <button type="button" class="btn btn-probot">إرسال لوحة التذاكر الآن</button>
                </div>
            </div>

            <!-- 6. سجل الأحداث (Logs) -->
            <div id="section-logs" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">📜 سجل الأحداث والرقابة (Logs)</h3>
                    <p class="text-muted">راقب تعديل الرسائل، الحذف، دخول وخروج الأعضاء بدقة عالية.</p>
                    <hr class="border-secondary">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">روم السجلات العامة</label>
                        <select class="form-select">
                            <option>#سجل-السيرفر-logs</option>
                        </select>
                    </div>
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="logMessages" checked>
                        <label class="form-check-label text-white fw-bold" for="logMessages">تسجيل تعديل وحذف الرسائل</label>
                    </div>
                    <button type="button" class="btn btn-probot">حفظ إعدادات السجلات</button>
                </div>
            </div>

            <!-- 7. الأدوار التلقائية -->
            <div id="section-auto_roles" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">🎭 الأدوار التلقائية (Auto Roles)</h3>
                    <p class="text-muted">منح رتبة تلقائية فور دخول أي عضو جديد للسيرفر.</p>
                    <hr class="border-secondary">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">الرتبة التلقائية للأعضاء الجدد</label>
                        <select class="form-select">
                            <option>@Member</option>
                        </select>
                    </div>
                    <button type="button" class="btn btn-probot">حفظ الرتبة التلقائية</button>
                </div>
            </div>

            <!-- 8. نظام المستويات -->
            <div id="section-leveling" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">⭐ نظام المستويات والتفاعل (Leveling)</h3>
                    <p class="text-muted">امنح خبرة (XP) للأعضاء بناءً على تفاعلهم وكتابتهم للرسائل.</p>
                    <hr class="border-secondary">
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="enableLeveling" checked>
                        <label class="form-check-label text-white fw-bold" for="enableLeveling">تفعيل نظام المستويات في السيرفر</label>
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">روم إرسال إعلانات لفل أب (Level Up)</label>
                        <select class="form-select">
                            <option>في نفس الروم الحالي</option>
                        </select>
                    </div>
                    <button type="button" class="btn btn-probot">حفظ إعدادات المستويات</button>
                </div>
            </div>

            <!-- 9. الاقتصاد (Economy) -->
            <div id="section-economy" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">💰 نظام الاقتصاد والأموال</h3>
                    <p class="text-muted">تحكم بعملة السيرفر، الأرباح، الرواتب اليومية، والمتاجر.</p>
                    <hr class="border-secondary">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">قيمة الراتب اليومي (Daily Reward)</label>
                        <input type="number" class="form-control" value="500">
                    </div>
                    <button type="button" class="btn btn-probot">حفظ الإعدادات الاقتصادية</button>
                </div>
            </div>

            <!-- 10. الرومات الصوتية المؤقتة -->
            <div id="section-voice" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">🎙️ الرومات الصوتية المؤقتة</h3>
                    <p class="text-muted">دع الأعضاء ينشئون رومات صوتية خاصة بهم تلقائياً بمجرد دخول روم الإنشاء.</p>
                    <hr class="border-secondary">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">روم إنشاء الرومات الصوتية</label>
                        <select class="form-select">
                            <option>➕ انضم لإنشاء روم</option>
                        </select>
                    </div>
                    <button type="button" class="btn btn-probot">حفظ إعدادات الرومات الصوتية</button>
                </div>
            </div>

            <!-- 11. أوامر الإدارة (Moderation) -->
            <div id="section-moderation" class="section-pane">
                <div class="probot-card">
                    <h3 class="text-white mb-3">🔨 أوامر الإدارة والصلاحيات</h3>
                    <p class="text-muted">تخصيص رتب المشرفين وصلاحيات الحظر، الطرد، والكتم.</p>
                    <hr class="border-secondary">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">رتبة المشرفين المخولة (Moderator Role)</label>
                        <select class="form-select">
                            <option>@Moderator</option>
                        </select>
                    </div>
                    <button type="button" class="btn btn-probot">حفظ صلاحيات الإدارة</button>
                </div>
            </div>

        </div>
    </div>

    <!-- جافاسكريبت لتبديل الأقسام بسلاسة تامة بدون إعادة تحميل -->
    <script>
        function switchSection(sectionId, element) {
            // إزالة الكلاس active من كل الأزرار
            document.querySelectorAll('.nav-item-custom').forEach(item => {
                item.classList.remove('active');
            });
            // إضافة الكلاس active للزر المضغوط
            element.classList.add('active');

            // إخفاء كل أقسام المحتوى
            document.querySelectorAll('.section-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            // إظهار القسم المطلوب فقط
            document.getElementById(sectionId).classList.add('active');
        }
    </script>
</body>
</html>
