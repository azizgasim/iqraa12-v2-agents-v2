"""
IQRAA V2 — Extended Pipeline (LangGraph)
==========================================
AGT-01 (تحليل) → G1 (جودة) → AGT-02 (كيانات) → AGT-05 (تحقق) → AGT-04 (توليف)
"""
from __future__ import annotations
import asyncio
from typing import Any, TypedDict
from langgraph.graph import StateGraph, END
from core.run_context import UnifiedRunContext
from core.canonical_policy import canonicalize
from agents.agt01_text_analysis import TextAnalysisAgent
from agents.agt02_entity_linking import EntityLinkingAgent
from agents.agt05_verification import VerificationAgent
from agents.agt04_synthesis import SynthesisAgent
from governance.g1_quality_gate import run_g1_gate

class ExtPipelineState(TypedDict, total=False):
    text: str
    source_id: str
    run_ctx_dict: dict
    claims: list
    evidences: list
    canonical_text: str
    agt01_success: bool
    g1_passed: bool
    g1_score: float
    g1_issues: list
    entities: list
    verification_passed: bool
    verified_count: int
    synthesis: dict
    pipeline_success: bool
    errors: list

async def node_agt01(state: ExtPipelineState) -> dict:
    agent = TextAnalysisAgent()
    ctx = UnifiedRunContext(**state.get("run_ctx_dict", {}))
    r = await agent.run(ctx, {"text": state["text"], "source_id": state.get("source_id", "unknown")})
    if not r.success:
        return {"agt01_success": False, "errors": r.errors, "pipeline_success": False}
    return {"claims": r.output.get("claims", []), "evidences": [e.model_dump() for e in r.evidence], "canonical_text": canonicalize(state["text"]), "agt01_success": True, "run_ctx_dict": ctx.model_dump(mode="json")}

async def node_g1(state: ExtPipelineState) -> dict:
    from core.models import Evidence
    evs = [Evidence(**e) if isinstance(e, dict) else e for e in state.get("evidences", [])]
    r = run_g1_gate(state.get("claims", []), evs)
    return {"g1_passed": r.passed, "g1_score": r.score, "g1_issues": r.issues}

def route_g1(state: ExtPipelineState) -> str:
    return "agt02_entities" if state.get("g1_passed") else "fail_end"

async def node_agt02(state: ExtPipelineState) -> dict:
    agent = EntityLinkingAgent()
    ctx = UnifiedRunContext(**state.get("run_ctx_dict", {}))
    r = await agent.run(ctx, {"text": state.get("canonical_text", ""), "source_id": state.get("source_id", "unknown")})
    return {"entities": r.output.get("entities", []) if r.success else [], "run_ctx_dict": ctx.model_dump(mode="json")}

async def node_agt05(state: ExtPipelineState) -> dict:
    from core.models import Evidence
    agent = VerificationAgent()
    ctx = UnifiedRunContext(**state.get("run_ctx_dict", {}))
    evs = [Evidence(**e) if isinstance(e, dict) else e for e in state.get("evidences", [])]
    r = await agent.run(ctx, {"claims": state.get("claims", []), "evidences": evs, "canonical_text": state.get("canonical_text", ""), "source_id": state.get("source_id", "unknown")})
    return {"verification_passed": r.output.get("all_passed", False), "verified_count": r.output.get("verified_count", 0), "run_ctx_dict": ctx.model_dump(mode="json")}

async def node_agt04(state: ExtPipelineState) -> dict:
    agent = SynthesisAgent()
    ctx = UnifiedRunContext(**state.get("run_ctx_dict", {}))
    r = await agent.run(ctx, {"claims": state.get("claims", []), "entities": state.get("entities", []), "cross_refs": [], "source_id": state.get("source_id", "unknown")})
    return {"synthesis": r.output if r.success else {}, "pipeline_success": True, "run_ctx_dict": ctx.model_dump(mode="json")}

async def node_fail(state: ExtPipelineState) -> dict:
    return {"pipeline_success": False, "errors": state.get("g1_issues", []) + state.get("errors", [])}

def build_extended_pipeline() -> StateGraph:
    g = StateGraph(ExtPipelineState)
    g.add_node("agt01_analyze", node_agt01)
    g.add_node("g1_quality", node_g1)
    g.add_node("agt02_entities", node_agt02)
    g.add_node("agt05_verify", node_agt05)
    g.add_node("agt04_synthesize", node_agt04)
    g.add_node("fail_end", node_fail)
    g.set_entry_point("agt01_analyze")
    g.add_edge("agt01_analyze", "g1_quality")
    g.add_conditional_edges("g1_quality", route_g1, {"agt02_entities": "agt02_entities", "fail_end": "fail_end"})
    g.add_edge("agt02_entities", "agt05_verify")
    g.add_edge("agt05_verify", "agt04_synthesize")
    g.add_edge("agt04_synthesize", END)
    g.add_edge("fail_end", END)
    return g

async def run_extended(text: str, source_id: str = "source") -> dict:
    app = build_extended_pipeline().compile()
    return await app.ainvoke({"text": text, "source_id": source_id, "run_ctx_dict": {}, "errors": []})
