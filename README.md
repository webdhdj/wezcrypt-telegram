# WezCrypt Telegram — عميل Telegram iOS مخصص (مشروع + Patch + بناء)

مبني على المصدر الرسمي: https://github.com/TelegramMessenger/Telegram-iOS
الإصدار المثبّت: **release-13.1.2** (commit `279f89e4d4f63f17227bf877dc3d8990f22ecd58`) — ترخيص العميل: GNU GPLv2 or later (نشر كودك المعدّل إلزامي عند أي توزيع).

## الخلاصة الصادقة (اقرأها أولًا)
1. **لا يوجد IPA في هذه الحزمة، ولم يُدَّعَ غير ذلك.** بيئة الإعداد Linux بلا macOS/Xcode، وبناء Telegram-iOS مستحيل هنا. البناء الفعلي يحتاج Mac بـ macOS 27 + Xcode 27.1 — `scripts/build-on-mac.sh` ينفذه كاملًا ويفشل بصوت عالٍ عند أي شرط ناقص.
2. **إزالة Sponsored Messages لجميع المستخدمين تخالف Telegram API Terms §3.3** («must include support for official sponsored messages… may not interfere») وعقوبتها قطع الـ API عن تطبيقك (§4.2). لذلك هذا المشروع **لا يحجب الإعلانات قسرًا**. تجربة «بلا إعلانات» تتحقق بالطريق الرسمي المدمج أصلًا في العميل: **حساب Telegram Premium** (استحقاق `no_ads` خادمي + زر الإخفاء الرسمي `account.toggleSponsoredMessages`). التحليل الكامل بالأدلة من الكود: `docs/ADS_AND_TERMS_ANALYSIS.md`.
3. **الاسم**: «WezCrypt Telegram» اسم المشروع؛ اسم العرض على الشاشة **WezCrypt** التزامًا بـ §2.3 (حظر كلمة Telegram في عنوان التطبيق ما لم تسبقها Unofficial).

## ما تحتويه الحزمة
```
patches/wezcrypt-telegram-13.1.2.patch   # الـ Diff الحقيقي الكامل (195 سطرًا) — مُختبَر التطبيق على شجرة نظيفة
scripts/customize.py                     # يولّد نفس التخصيص آليًا + يقرأ API credentials من البيئة فقط
scripts/build-on-mac.sh                  # بناء كامل على Mac مع فحوص شروط صارمة
scripts/verify-no-forbidden-changes.sh   # يثبت أن الـ Patch لا يمس الإعلانات/MTProto/التشفير/الشبكات
config/wezcrypt-telegram-configuration.template.json  # bundle com.wezcrypt.telegram + scheme wezcrypttg
.github/workflows/build-ipa.yml          # قالب CI (يتطلب macOS 27/Xcode 27.1 — غالبًا Self-hosted)
docs/ADS_AND_TERMS_ANALYSIS.md           # آلية الإعلانات في الكود + نصوص الشروط + البدائل المشروعة
docs/BUILD_INSTRUCTIONS.md               # متطلبات وخطوات البناء وإنتاج IPA + SHA-256
docs/SECURITY_REPORT.md                  # تقرير الأمان والتبعيات وكيفية api_id الرسمي
docs/INSTALL.md                          # التثبيت (Developer/AltStore/SideStore/Sideloadly) + القيود
docs/TEST_REPORT.md                      # ما تُحقق منه فعلًا وما لم يُتحقق — بلا اختراع
```

## الإعدادات المعتمدة
- الاسم (مشروع): WezCrypt Telegram — اسم العرض: WezCrypt
- Bundle ID: `com.wezcrypt.telegram`
- Minimum iOS: **15.0** — Architecture: arm64
- Output المطلوب بعد البناء: `WezCryptTelegram.ipa`

## البدء السريع (على Mac)
```bash
export WEZCRYPT_API_ID=... WEZCRYPT_API_HASH=... WEZCRYPT_TEAM_ID=...
./scripts/build-on-mac.sh
```
