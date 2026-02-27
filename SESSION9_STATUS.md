# تقرير الحالة المعمارية - الجلسة 9
# التاريخ: 2026-02-28
# الحالة: نقل G4 + قرار استراتيجي محوري

## القرارات الاستراتيجية المتخذة
1. تبني نهج "استكمال أنضج جيل" بدل البناء من الصفر
2. G4 هو الأنضج (حوكمة + gates + cost + lifecycle + orchestrator)
3. تبني توصيات الاستشاريين: LangGraph + Thin Slice + Canonical Policy
4. رفع هدف التكلفة من $0.50 إلى $0.80-1.00/سؤال
5. تقسيم AGT-04 إلى متخصصين منفصلين

## إنجازات الجلسة 9
1. استحضار سياق 8 جلسات سابقة
2. كتابة البلوبرنت الشامل (IQRAA12_AGENTS_V2_BLUEPRINT.docx - 12 قسم)
3. كتابة برومبت الاستشارة (IQRAA12_CONSULTATION_REQUEST.docx - 8 أقسام)
4. استلام وتحليل تقرير الاستشارة (C1-C10 + D1-D5 + 10 مخاطر)
5. جرد G4 الكامل: 61 ملف Python في 11 مجلد (1721 سطر)
6. قراءة عميقة لـ 13 ملف حرج في G4
7. نقل G4 الناضج إلى v2_build: 54 ملف / 1625 سطر
8. إنشاء ريبو Git مستقل في v2_build + أول commit
9. محاولة push (فشل - التوكن منتهي)

## ما تم بناؤه (v2_build/) - 54 ملف / 1625 سطر
### من v2 الجديد:
- core/models.py (93 سطر - TextSpan, Evidence, Claim, RunContext)
- core/base_agent.py (97 سطر - Brain-Perception-Action)
- operations/base_operation.py (58 سطر - pre>run>post)
- BLUEPRINT_V2.md, BUILD_LOG.md

### من G4 (منقول):
- core/g4_context.py (52 سطر - ExecutionContext ناضج)
- core/g4_orchestrator.py (~150 سطر - lifecycle كامل 6 مراحل)
- core/lifecycle.py (22 سطر - 7 phases enum)
- core/decision.py (25 سطر - ALLOW/DENY/DEFER/SOFT_DENY)
- core/exceptions.py (12 سطر - 4 exceptions)
- governance/gates/base.py + gate0-5 (7 ملفات - 6 بوابات كاملة)
- governance/audit_engine.py (35 سطر)
- governance/budget_engine.py (40 سطر)
- governance/policy_engine.py (50 سطر)
- governance/gate_registry.py (18 سطر)
- cost/cost_guardian.py (28 سطر)
- execution/model_router.py (18 سطر - stub)
- tests/ (14 ملف اختبار من G4)
- schemas/ (4 JSON schemas)
- configs/ (3 YAML recipes)

## توصيات الاستشاريين الحرجة (P0)
1. LangGraph للـ L5/L7 (توفير 3-4 أشهر)
2. Canonical Text Policy + CTS URNs (قبل أي وكيل)
3. Thin Slice أولا: نص → AGT-01 → G1 → AGT-05 → نتيجة
4. TDD من اليوم الأول (80%+ تغطية)
5. تقسيم AGT-04 إلى متخصصين
6. إضافة وكيل المراجعة البشرية AGT-00

## مهام الجلسة 10
1. توليد PAT جديد لـ GitHub + push
2. كتابة Canonical Text Policy (canonical_policy.py)
3. دمج g4_context.py مع v2 RunContext (إضافة canonical fields)
4. إصلاح imports في الملفات المنقولة
5. تثبيت LangGraph + تصميم StateGraph
6. بناء Thin Slice MVP:
   - AGT-01 الورّاق (extract + offset_calc)
   - G1 Evidence Gate (التحقق من offsets)
   - AGT-05 المراجع (faithfulness_score)
7. كتابة 50 unit test أساسي
8. قياس التكلفة الفعلية على 100 مقطع

## المسارات المرجعية
- البناء: ~/iqraa-12/iqraa-v3/agents/v2_build/
- ريبو Git: v2_build/.git/ (محلي - يحتاج push)
- GitHub: https://github.com/azizgasim/iqraa-v3-agents-v2 (يحتاج توكن)
- النوهاو: ~/iqraa-12/iqraa-v3/agents/v2_design/knowhow/
- تقرير الاستشارة: (في محادثة الجلسة 9)

## المبادئ غير القابلة للتفاوض
1. لا claim بلا evidence
2. لا evidence بلا offsets وسياق + Canonical Policy
3. لا تشغيل بلا run_id + recipe
4. لا ربط كيانات بلا Suggest>Approve
5. لا نشر بلا بوابات الثقة (G1+G4+G5)
6. لا كود بلا اختبارات (TDD - 80%+)
7. Thin Slice قبل التوسع
