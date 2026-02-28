"""
AGT-04: Synthesis Agent — وكيل التوليف
========================================
يستقبل claims + entities + cross_refs → يولّف ملخصاً بحثياً مهيكلاً.

Thin Slice: توليف rule-based بسيط (تجميع + ترتيب).
التوسع: توليف عبر LLM مع citations دقيقة.

ملاحظة: AGT-04 الأصلي قُسّم إلى متخصصين (قرار الجلسة 9).
هذا هو الـ Synthesizer الأساسي.
"""
from __future__ import annotations

from typing import Any
from core.base_agent import BaseAgent, AgentCard, AgentResult
from core.models import Evidence, AutonomyLevel, RiskTier
from core.run_context import UnifiedRunContext


def _build_card() -> AgentCard:
    return AgentCard(
        agent_id="AGT-04",
        name="Synthesis Agent",
        name_ar="وكيل التوليف",
        version="2.0.0",
        description="Synthesizes verified claims, entities, and cross-refs into structured research output",
        category="synthesize",
        autonomy_level=AutonomyLevel.L1_SUGGEST,
        risk_tier=RiskTier.MEDIUM,
        operations=["synthesize_report", "build_outline", "cite_evidence"],
        non_use_cases=["text_extraction", "verification"],
        owner="iqraa-12",
    )


class SynthesisAgent(BaseAgent):
    """AGT-04: يجمع النتائج في تقرير بحثي مهيكل"""

    def __init__(self):
        super().__init__(_build_card())

    async def perceive(self, params: dict[str, Any]) -> dict[str, Any]:
        claims = params.get("claims", [])
        entities = params.get("entities", [])
        cross_refs = params.get("cross_refs", [])
        source_id = params.get("source_id", "unknown")
        if not claims:
            raise ValueError("AGT-04: no claims to synthesize")
        return {
            "claims": claims,
            "entities": entities,
            "cross_refs": cross_refs,
            "source_id": source_id,
        }

    async def think(self, perceived: dict, run_ctx: UnifiedRunContext) -> dict[str, Any]:
        claims = perceived["claims"]
        sections = []
        main_claims = [c for c in claims if self._get_conf(c) >= 0.7]
        supporting = [c for c in claims if 0.4 <= self._get_conf(c) < 0.7]
        weak = [c for c in claims if self._get_conf(c) < 0.4]
        if main_claims:
            sections.append({"title": "core_findings", "claims": main_claims})
        if supporting:
            sections.append({"title": "supporting_evidence", "claims": supporting})
        if weak:
            sections.append({"title": "needs_verification", "claims": weak})
        return {
            "sections": sections,
            "entities": perceived["entities"],
            "cross_refs": perceived["cross_refs"],
            "source_id": perceived["source_id"],
            "total_claims": len(claims),
        }

    async def act(self, plan: dict, run_ctx: UnifiedRunContext) -> dict[str, Any]:
        report_sections = []
        for section in plan["sections"]:
            items = []
            for c in section["claims"]:
                text = c.get("text", "") if isinstance(c, dict) else c.text
                conf = self._get_conf(c)
                ev_ids = c.get("evidence_ids", []) if isinstance(c, dict) else c.evidence_ids
                items.append({
                    "claim_text": text,
                    "confidence": conf,
                    "evidence_count": len(ev_ids),
                    "citations": ev_ids,
                })
            report_sections.append({
                "section": section["title"],
                "items": items,
                "count": len(items),
            })

        entity_summary = []
        for e in plan.get("entities", []):
            if isinstance(e, dict):
                entity_summary.append({
                    "text": e.get("text", ""),
                    "type": e.get("entity_type", "unknown"),
                })

        report = {
            "source_id": plan["source_id"],
            "total_claims": plan["total_claims"],
            "sections": report_sections,
            "entity_summary": entity_summary,
            "cross_ref_count": len(plan.get("cross_refs", [])),
        }

        run_ctx.record_audit("synthesis_complete", "AGT-04", {
            "sections": len(report_sections),
            "total_claims": plan["total_claims"],
        })

        return {
            "output": report,
            "evidence": [],
            "cost_usd": 0.0,
        }

    def _get_conf(self, claim) -> float:
        if isinstance(claim, dict):
            return claim.get("confidence", 0.5)
        return getattr(claim, "confidence", 0.5)
