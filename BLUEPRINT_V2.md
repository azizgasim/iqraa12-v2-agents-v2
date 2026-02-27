# البلوبرنت التفصيلي - منظومة وكلاء اقرا-12 v2
# التاريخ: 2026-02-28
# المصدر: 47 درس + 15 نمط + 85 اب + 44 عملية + 7 اجيال نوهاو

## 1. الفلسفة: الوكيل = تركيبة ديناميكية تتشكل من السؤال
## 2. المبادئ الخمسة غير القابلة للتفاوض
- لا claim بلا evidence (Claim.evidence_ids min_length=1)
- لا evidence بلا offsets (TextSpan: doc_id, char_start, char_end)
- لا تشغيل بلا run_id + recipe (RunContext اجباري)
- لا ربط كيانات تلقائي (L1 = suggest فقط)
- لا نشر بلا بوابات (V1+V2+V4 الزامية)

## 3. هيكل v2_build/
- core/ : models.py(DONE) base_agent.py(DONE) config.py exceptions.py
- operations/ : base_operation.py(DONE) registry.py + extract/ link/ trace/ analyze/ construct/ synthesize/ write/ verify/
- engine/ : pipeline_builder.py pipeline_executor.py recipe_library.py question_parser.py
- gates/ : base_gate.py g0_input.py g1_evidence.py g4_theory.py g5_export.py
- agents/ : orchestrator.py cost_guardian.py semantic_searcher.py entity_extractor.py claim_crafter.py evidence_bundler.py publish_gate_agent.py identity_resolver.py
- infra/ : bq_client.py vertex_client.py logging.py
- tests/ : test_models.py test_base_agent.py test_pipeline.py test_gates.py test_e2e.py

## 4. Phase 1 - الهيكل العظمي (الجلسة 9) ~880 سطر
1. config.py - اعدادات مركزية (~40)
2. exceptions.py - اخطاء موحدة (~30)
3. registry.py - سجل العمليات register/get/list/filter (~60)
4. pipeline_builder.py - تجميع عمليات من سؤال (~80)
5. pipeline_executor.py - تنفيذ تسلسلي/متوازي (~100)
6. base_gate.py - بوابة اساسية check>pass/fail (~50)
7. g1_evidence.py - بوابة الادلة (~40)
8. g5_export.py - بوابة مكافحة الهلوسة (~50)
9. orchestrator.py - المنسق parse>build>execute>gate (~120)
10. cost_guardian.py - حارس التكلفة (~60)
11. bq_client.py - عميل BigQuery stub (~50)
12. vertex_client.py - عميل Vertex AI stub (~50)
13. tests (models+agent+pipeline) (~150)

## 5. Phase 2 - العمليات الاساسية (الجلسة 10)
- E1 TextSearch + E2 SemanticSearch + E3 EntityExtraction
- V1 CitationAudit + V2 ConsistencyAudit + V4 ProvenanceAudit
- G0 InputGate + G4 TheoryGate
- question_parser + recipe_library
- semantic_searcher + entity_extractor + publish_gate agents

## 6. Phase 3 - الوكلاء المتقدمون (الجلسة 11)
- L1-L5 Link + C1-C6 Construct operations
- claim_crafter + evidence_bundler + identity_resolver
- test_e2e.py (سؤال > مسودة موثقة)

## 7. Phase 4 - التطهير والمستشارون (مؤجل)
- عائلة التطهير pkg7 + المستشارون pkg8 + الادوات pkg9

## 8. خريطة الاعتماديات
config.py < كل شيء
models.py < كل شيء
base_operation.py < registry.py < pipeline_builder.py
base_agent.py < orchestrator.py
base_gate.py < g1, g5
bq_client.py < E1, E2
vertex_client.py < E2, ClaimCrafter
pipeline_builder + executor < orchestrator
cost_guardian < orchestrator

## 9. تدفق البيانات
سؤال > QuestionParser > PipelineBuilder > G0_Input > PipelineExecutor(E>L>T>A>C>S>W) > CostGuardian > G1_Evidence > G5_Export(V1+V2+V4) > مسودة موثقة

## 10. التقنيات
Python 3.11+ | Pydantic v2 | asyncio | BigQuery | Vertex AI (Gemini 1.5 Pro + Claude fallback) | structlog | pytest

## 11. معايير قبول Phase 1
- 13 ملف مكتوبة ومتصلة
- 3 اختبارات تمر (models + agent + pipeline)
- Orchestrator يستقبل سؤال ويعيد pipeline
- CostGuardian يوقف عند تجاوز الميزانية
- G1 + G5 تفحص وترفض/تقبل
- كل شيء مدفوع ل GitHub
