# تحليل Sponsored Messages — الآلية، الشروط، والقرار

## 1) كيف يعرض العميل الرسمي الإعلانات؟ (مُتحقق من كود 13.1.2)

الإعلانات ليست WebView ولا وحدات خارجية؛ هي رسائل Synthetic يبنيها العميل محليًا:

| المرحلة | الملف (release-13.1.2) | ماذا يحدث |
|---|---|---|
| إنشاء السياق | `submodules/TelegramUI/Sources/ChatControllerNode.swift` (~L805) | عند فتح أي Peer (غير Preview) يُنشأ `AdMessagesHistoryContext` |
| الجلب | `submodules/TelegramCore/Sources/TelegramEngine/Messages/AdMessages.swift` — `AdMessagesHistoryContextImpl.activate()` | طلب MTProto: `messages.getSponsoredMessages(peer, msg_id?)`؛ النتيجة تُخزَّن Cache لمدة **5 دقائق** في Postbox (`Namespaces.CachedItemCollection.cachedAdMessageStates`) ثم تُحوَّل إلى `Message` محلية بـ `AdMessageAttribute` وTimestamp = `Int32.max - 1` |
| العرض | `submodules/TelegramUI/Sources/ChatHistoryListNode.swift` — `beginAdMessageManagement` | تُدمج الإعلانات في قائمة المحادثة: أول إعلان Fixed + إعلانات Opportunistic بفاصل `posts_between`؛ بدون مساحات فارغة عند غيابها (القائمة فارغة أصلًا) |
| القياس | نفس `AdMessages.swift` | عند الظهور: `messages.viewSponsoredMessage(random_id)`؛ عند النقر: `messages.clickSponsoredMessage` |
| أسطح أخرى | `TelegramEngine/Peers/AdPeers.swift`، `ReportAds.swift` | إعلانات بحث (`contacts.getSponsoredPeers`)، إعلانات فيديو القنوات (نفس السياق مع `messageId`)، وإبلاغ عن إعلان |

لا توجد أي مكتبة إعلانات خارجية، ولا يُبنى أي ملف تعريف من محتوى المحادثات الخاصة.

## 2) هل تعطيل العرض محليًا متوافق مع شروط Telegram API؟ — لا

**Telegram API Terms of Service — §3.3** (نص رسمي، core.telegram.org/api/terms):

> "If your app allows accessing content from Telegram channels, you must include support for official sponsored messages in Telegram channels and **may not interfere with this functionality**."

**§4.2**: عند المخالفة يُنذَر الحساب المسؤول، وإن لم يُصلَح خلال **10 أيام** تُقطع إمكانية الوصول إلى Telegram API ويُخاطَب متجر التطبيقات للإزالة.
ووثيقة Sponsored Messages الرسمية تضيف أن العملاء الخارجيين مُلزمون بدعم الإعلانات وعرضها بشكل صحيح منذ 2022-01-01، وأن التطبيقات التي لا تعرضها «will have to be disconnected».

إذن: أي Patch يحذف/يحجب `getSponsoredMessages` أو يصفّي `AdMessageAttribute` من العرض لحسابات غير Premium هو **مخالفة صريحة لـ §3.3** تعرّض الـ `api_id` الخاص بالتطبيق للقطع. لذلك لم يُضمَّن مثل هذا الـ Patch في هذا المشروع — بناءً على شرطك أنت في المهمة: «إذا لم يكن مسموحًا، اشرح القيد واقترح بديلًا مشروعًا».

## 3) البدائل المشروعة (مدمجة أصلًا في البروتوكول والعميل)

1. **Telegram Premium — `no_ads` (الرسمي والكامل):** حساب Premium لا تصله إعلانات خادميًا (الخادم يرد `sponsoredMessagesEmpty`)، والعميل الرسمي يحتوي أصلًا زر «إخفاء الإعلان»: في `ChatController.swift` (~L5305) عند `context.isPremium` يستدعي `updateAdMessagesEnabled(enabled: false)` — أي MTProto `account.toggleSponsoredMessages(false)` — ويحذف الإعلان من الواجهة؛ لغير المشتركين يعرض شاشة Premium. **النتيجة: مستخدم WezCrypt Telegram بحساب Premium يحصل على تجربة خالية تمامًا من الإعلانات، صفر تعديلات، صفر مخالفة.**
2. **مالك القناة:** `channels.restrictSponsoredMessages` (موجود في `ChannelAds.swift`) يتيح لمالك قناة تقييد الإعلانات في قناته ضمن إعدادات Monetization الرسمية.
3. **ما فعله هذا المشروع فعليًا:** ترك خط الإعلانات سليمًا بالكامل (يتحقق منه `scripts/verify-no-forbidden-changes.sh`)، فلا يُعرَّض الـ `api_id` للقطع، وتبقى التجربة «بلا إعلانات» متاحة بالطريق الرسمي الوحيد.

> ملاحظة صريحة: لو قررت لاحقًا — لاستخدام شخصي بحت وعلى مسؤوليتك — تجربة حجب محلي، فنقطة التدخل التقنية موثقة أعلاه (`AdMessagesHistoryContextImpl.activate()` / `ChatHistoryListNode`)، لكن أي توزيع لمثل هذا البناء يخالف §3.3. هذا المشروع لا يوزّعه.

## 4) قيد ثانٍ اكتُشف أثناء الفحص — اسم التطبيق (§2.3)

> "To avoid confusion, the title of your app must not include the word “Telegram”. An exception can be made if the word “Telegram” is preceded with the word “Unofficial”."

- الاسم المطلوب «WezCrypt Telegram» كـ **عنوان تطبيق** يخالف §2.3.
- الحل المعتمد هنا: اسم المشروع/الـ Codename يبقى **WezCrypt Telegram**، واسم العرض على الشاشة الرئيسية (CFBundleDisplayName) هو **"WezCrypt"**، مع إلزام §2.2 بأن يذكر وصف التطبيق بوضوح أنه عميل غير رسمي يستخدم Telegram API.
- README الرسمي يضيف: لا تستخدم شعار Telegram القياسي (الطائرة الورقية) أيقونةً لتطبيقك — يجب تصميم أيقونة WezCrypt خاصة قبل البناء التوزيعي.
