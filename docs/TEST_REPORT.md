# تقرير الاختبار — ما تم التحقق منه فعلًا وما لم يتم

## مُتحقق (أدلة قابلة لإعادة الإنتاج في هذه البيئة)
| # | الاختبار | النتيجة |
|---|---|---|
| 1 | هوية المستودع والإصدار | `git ls-remote`: ‏HEAD ‏= `279f89e4d4f63f17227bf877dc3d8990f22ecd58` ‏= Tag ‏`release-13.1.2` بالضبط؛ `versions.json`: app 13.1.2 / Xcode 27.1 / Bazel 9.2.0 / macOS 27 |
| 2 | قراءة كود الإعلانات مصدريًا | `AdMessages.swift` (711 سطرًا) قُرئ بالكامل + نقاط الاستهلاك في `ChatControllerNode.swift` و`ChatHistoryListNode.swift` و`ChatController.swift` |
| 3 | شروط API | نص §3.3 و§2.3 و§4.2 مقروء من الصفحة الرسمية مباشرة |
| 4 | تشغيل `scripts/customize.py` على نسخة Sparse حقيقية من المستودع | نجح: عدّل 19 ملف InfoPlist.strings + أنشأ ملف الإعداد بـ `bundle_id=com.wezcrypt.telegram` |
| 5 | الـ Patch على شجرة نظيفة | `git apply --check` ✅ ثم تطبيق فعلي ✅ ثم Revert نظيف (working tree = 0 تغييرات) |
| 6 | سلامة الـ Patch الأمنية | `verify-no-forbidden-changes.sh` ✅ — لا ملفات إعلانات/MTProto/تشفير/شبكات، لا Endpoints مضافة |
| 7 | Syntax السكربتات | `python3 -m py_compile customize.py` ✅ — `bash -n build-on-mac.sh` ✅ |

## غير مُتحقق — صراحة كاملة
- **Compilation: لم يُجرَ.** لا Xcode/Bazel/macOS هنا؛ أول فحص حقيقي يكون على Mac ببناء Simulator (`--disableProvisioningProfiles`) ثم Release.
- **اختبارات Upstream (`Tests/`، Unit/UI): لم تُشغَّل** — تتطلب نفس بيئة Mac.
- **IPA: غير موجود.** لا SHA-256 له لأنه لم يُبنَ (SHA256SUMS المرفق يغطي ملفات التسليم الموجودة فقط).
- **تسجيل الدخول، المكالمات، الإشعارات، Secret Chats على جهاز: لم تُختبر** — كلها بانتظار بناء + جهاز.
- **CI Workflow: مكتوب ولم يُشغَّل.**

## قائمة الوظائف الأساسية — حالة الحفاظ عليها تصميميًا
كل الوظائف التالية **لم تُحذف ولم تُعدَّل** (الـ Patch لا يلمس أي كود وظيفي): محادثات/مجموعات/قنوات، مكالمات صوتية ومرئية (WebRTC/tgcalls)، رسائل صوتية وفيديو، ملفات وصور، Push (بقيد INSTALL.md)، Secret Chats، 2FA، تسجيل دخول بالهاتف، مزامنة، بحث وملصقات وبوتات، Dark/Light، العربية والإنجليزية (حزم `.lproj` سليمة — عُدّل فيها سطر اسم العرض فقط).
تأكيدها عمليًا = اختبار جهاز بعد البناء، وهو البند المفتوح التالي في المشروع.
