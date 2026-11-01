# تقرير الأمان — WezCrypt Telegram

## النطاق والمنهجية
مراجعة مصدرية (Source audit) لإصدار `release-13.1.2` (commit `279f89e4d4f63f17227bf877dc3d8990f22ecd58`) ولفروقات هذا المشروع فقط. لا توجد مراجعة ثنائية (Binary audit) لأنه لا يوجد IPA مبني بعد.

## التعديلات الأمنية لهذا المشروع — وما لم يتغير
| المجال | الحالة |
|---|---|
| MTProto / التشفير / Secret Chats | **لم يُمسّ** — صفر أسطر معدّلة |
| Certificate Validation / TLS | **لم يُمسّ** — لا Pinning مُعطّل، لا استثناءات |
| إضافة Analytics / Trackers / خوادم خارجية | **لا شيء** — يتحقق `verify-no-forbidden-changes.sh` أن الـ Patch لا يضيف أي Endpoint |
| تخزين الجلسات | كما هو Upstream: Postbox + iOS Keychain عبر طبقات Telegram الرسمية (`MtProtoKit`/`Postbox`) — لم نضف أي Logging؛ الـ Patch لا يلمس أي كود Logging |
| ملفات معدّلة فعليًا | 19 ملف `InfoPlist.strings` (سطر `CFBundleDisplayName` فقط) + ملف إعداد بناء جديد — قائمة كاملة في الـ Patch |
| Backdoors / مراقبة | لا يوجد أي كود مضاف أصلًا باستثناء إعداد البناء — الـ Diff كامل وقابل للقراءة (195 سطرًا) |

## كيفية الحصول على Telegram API credentials رسمية (إلزامي §2.1)
1. سجّل دخولك برقم هاتفك في https://my.telegram.org/apps
2. أنشئ Application (اسم/منصة iOS) — ستحصل على `api_id` (رقم) و`api_hash` (32 hex).
3. **لا تستخدم `api_id=8` الظاهر في `build-system/appstore-configuration.json`** — ذاك خاص ببناء Telegram الرسمي (`ph.telegra.Telegraph`)؛ استخدامه في تطبيقك مخالفة ويعرّضك للحظر.
4. مرّر القيم عبر متغيرات بيئة فقط (`WEZCRYPT_API_ID` / `WEZCRYPT_API_HASH`) — سكربت التخصيص لا يكتبها في أي ملف يُرفع إلى Git، ولا تضعها في لقطات/تقارير.

## التبعيات (Dependencies) — من `.gitmodules` الرسمي
`rules_apple`/`rules_swift`/`apple_support`/`rules_xcodeproj` (Bazel)، `webrtc` (مكالمات)، `tgcalls`، `tdlib/td`، `mtproto-engine`، `rlottie`/`tlottie`، `libvpx`، `dav1d`، `wallet-engine`، Swift Packages داخل `submodules/*/Package.swift` (مثل TelegramCore/TelegramApi).
- السلامة: البناء يثبّت كل Submodule على Commit الـ Tag الرسمي (`git submodule update --init --recursive` بعد Checkout الـ Tag) — لا تبعيات عائمة.
- لم تُجرَ مراجعة CVE مستقلة لكل تبعية في هذه الجولة؛ قبل أي توزيع عام يُنصح بتشغيل فحص تبعيات ومطابقة SHA للـ Submodules مع الـ Tag.

## مخاطر وقيود صريحة
1. **التوقيع هو حد الأمان الفعلي**: IPA موقّع بشهادة مسرّبة أو Enterprise مُساء استخدامها = مرفوض أخلاقيًا وتقنيًا هنا؛ المسارات الشرعية فقط (انظر INSTALL.md).
2. **Push Notifications**: بناء بBundle ID مختلف (`com.wezcrypt.telegram`) يحتاج Provisioning خاصًا به وApp Groups مطابقة؛ استقبال APNs عبر خوادم Telegram لعميل خارجي بـ `api_id` خاص غير مضمون — يُوثَّق كقيد غير مُتحقق حتى تجربة جهاز حقيقية.
3. **GPLv2-or-later**: أي توزيع للـ IPA يلزمك بنشر كودك المعدّل كاملًا (README الرسمي يذكّر بذلك صراحة).
4. البناء لم يُنفَّذ بعد (لا macOS/Xcode في بيئة الإعداد) — كل ما أعلاه عن الكود المصدري، لا عن منتج نهائي.
