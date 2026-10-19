# مدير الكمبيوتر Kimo PC Manager

هذه صفحة تعريف عربية للمشروع. [افتح README الرئيسي](README.md#العربية) لقراءة وصف المميزات وفوائدها، وطريقة التنزيل والتشغيل، ومعلومات الخصوصية والترخيص.

![معاينة Kimo PC Manager](assets/social-preview.png)

## تنزيل نسخة Windows

حمّل أحدث إصدار **Windows x64** من [صفحة الإصدارات](https://github.com/qkraim723-code/kimo-pc-manager/releases/latest). فك ضغط الحزمة كاملة ثم شغّل `KimoPCManager.exe`؛ لا تنقل الملف التنفيذي وحده خارج مجلده.

## التشغيل من السورس

يتطلب المشروع Windows 10 أو 11 (64 بت) وPython 3.11 أو أحدث:

```powershell
python -m pip install -r requirements.txt
python main.py
```

لبناء حزمة Windows، شغّل `build.bat` من مجلد المشروع. المشروع مرخص بموجب [MIT](LICENSE).
