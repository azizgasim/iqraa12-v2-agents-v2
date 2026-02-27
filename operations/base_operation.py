"""
IQRA-12 BaseOperation v2 — عقد موحد لكل عملية ذرية
44 عملية × 8 فئات (E/L/T/A/C/S/W/V)
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from .models_ref import *

class BaseOperation(ABC):
    """العملية الذرية الأساسية — كل عملية ترث من هنا"""

    operation_id: str = ""
    name_ar: str = ""
    name_en: str = ""
    category: str = ""
    autonomy_level: str = "L1"
    golden_rule: str = ""

    async def execute(self, op_input: 'OperationInput') -> 'OperationOutput':
        """تنفيذ العملية مع الحواجز"""
        start = datetime.utcnow()
        try:
            self.pre_check(op_input)
            result = await self.run(op_input)
            self.post_check(result)
            elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
            return OperationOutput(
                operation_id=self.operation_id,
                run_id=op_input.run_ctx.run_id,
                success=True,
                result=result,
                duration_ms=elapsed,
            )
        except Exception as e:
            elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
            return OperationOutput(
                operation_id=self.operation_id,
                run_id=op_input.run_ctx.run_id,
                success=False,
                errors=[str(e)],
                duration_ms=elapsed,
            )

    def pre_check(self, op_input: 'OperationInput'):
        """حواجز ما قبل التنفيذ"""
        assert op_input.run_ctx.run_id, "لا تشغيل بلا run_id"
        assert op_input.run_ctx.cost_spent_usd < op_input.run_ctx.cost_budget_usd, "تجاوز الميزانية"

    def post_check(self, result: dict):
        """حواجز ما بعد التنفيذ — يُخصصها كل عملية"""
        pass

    @abstractmethod
    async def run(self, op_input: 'OperationInput') -> dict:
        """التنفيذ الفعلي — كل عملية تنفذ هذا"""
        ...
