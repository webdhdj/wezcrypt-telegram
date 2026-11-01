# تعليمات البناء — WezCryptTelegram.ipa

## الحقيقة أولًا: لماذا لا يوجد IPA في هذه الحزمة؟
بيئة الإعداد الحالية: **Linux x86_64، 4 أنوية، 7.7GB RAM، لا Xcode ولا Bazel ولا macOS**. بناء Telegram-iOS مستحيل فيزيائيًا هنا (يتطلب Darwin Toolchain). أي «IPA» يُصنع هنا سيكون ملفًا ميتًا — لذلك لم يُصنع. أقصى مرحلة صادقة وصلنا لها: مشروع + Patch مُختبَر التطبيق + سكربت بناء يتحقق من كل شرط ويفشل بصوت عالٍ بدل إنتاج بناء مكسور. البناء الفعلي = خطوات هذا الملف على Mac (أو Mac مستأجر/GitHub self-hosted runner).

## المتطلبات الدقيقة (من `versions.json` لإصدار release-13.1.2)
| المتطلب | القيمة |
|---|---|
| نظام المضيف | macOS 27 |
| Xcode | **27.1** بالضبط |
| Bazel | 9.2.0 (تديره أدوات Make.py الرسمية) |
| مساحة قرص | ~90GB حرة (تقدير وثيقة Reproducible Builds الرسمية لبيئة بناء iOS) |
| المصدر | `git clone --recursive https://github.com/TelegramMessenger/Telegram-iOS.git` ثم `git checkout release-13.1.2` (commit `279f89e4…`) |
| Minimum iOS | **15.0** (`minimum_os_version` في `Telegram/BUILD`) — Architecture: arm64 (`--configuration=release_arm64`) |
| حسابات | Apple Developer (للتوقيع) + `api_id`/`api_hash` خاصان بك من https://my.telegram.org/apps |

## خطوات البناء (أو ببساطة: `scripts/build-on-mac.sh`)
```bash
export WEZCRYPT_API_ID=<your id> WEZCRYPT_API_HASH=<your hash> WEZCRYPT_TEAM_ID=<your team>
git clone --recursive https://github.com/TelegramMessenger/Telegram-iOS.git
cd Telegram-iOS && git checkout release-13.1.2 && git submodule update --init --recursive

# 1) التخصيص: إما السكربت (يولّد نفس الـ Patch آلياً):
python3 /path/to/wezcrypt-telegram/scripts/customize.py "$PWD"
# أو الـ Patch الجاهز:
# git apply /path/to/wezcrypt-telegram/patches/wezcrypt-telegram-13.1.2.patch
#   (ثم املأ api_id/api_hash/team_id داخل build-system/wezcrypt-configuration.json يدوياً)

# 2) التوقيع: انسخ build-system/fake-codesigning مرجعًا، وجهّز مجلد codesigning
#    بملفات Provisioning خاصة بـ com.wezcrypt.telegram وكل امتداداته
#    (NotificationService, Share, WidgetKit, SiriIntents, BroadcastUpload, Watch)
#    مع App Group بصيغة group.com.wezcrypt.telegram.* كما تولّدها أدوات GenerateProfiles.

# 3) توليد مشروع Xcode:
python3 build-system/Make/Make.py --cacheDir="$HOME/telegram-bazel-cache" \
  generateProject --configurationPath=build-system/wezcrypt-configuration.json \
  --xcodeManagedCodesigning

# 4) بناء Release وإنتاج IPA:
python3 build-system/Make/Make.py --cacheDir="$HOME/telegram-bazel-cache" \
  build --configurationPath=build-system/wezcrypt-configuration.json \
  --codesigningInformationPath=/path/to/codesigning \
  --buildNumber=100001 --configuration=release_arm64

# 5) التسمية والبصمة:
cp <output>/Telegram.ipa WezCryptTelegram.ipa
shasum -a 256 WezCryptTelegram.ipa
```

## ملاحظات تنفيذية موثقة من الـ README الرسمي
- توليد «Organization Identifier» عشوائي + Team ID من شهادة Apple Development في Keychain Access — خطوات README قسم Quick Compilation.
-_codesigning غير مطلوب لبناء Simulator فقط_ (`--disableProvisioningProfiles`) — هذا أسرع فحص Compilation ممكن على Mac قبل عناء الـ Provisioning: **يُنصح به كخطوة أولى** للتحقق أن الـ Patch لا يكسر البناء.
- إن علِق Xcode عند «build-request.json not updated yet» أعد المحاولة (FAQ رسمي).

## CI (GitHub Actions)
`.github/workflows/build-ipa.yml` مرفق كقالب: يتحقق من إصدار Xcode ويفشل إن لم يطابق 27.1. تنبيه صادق: رنّرات GitHub المستضافة قد لا توفر macOS 27 / Xcode 27.1 بعد؛ المسار الموثوق حاليًا Mac فعلي أو Self-hosted runner. لم يُشغَّل هذا الـ Workflow فعليًا.
