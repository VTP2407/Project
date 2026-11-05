import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class AgentExecutionResult(BaseModel):
    agent_id: str
    agent_name: str
    status: str  # SUCCESS, SKIPPED, FAILED
    duration_ms: float
    summary: str
    data: Dict[str, Any] = {}

class BaseAgent:
    agent_id: str = "base_agent"
    agent_name: str = "Base Agent"
    description: str = "Base Agent"

    def execute(self, context: Dict[str, Any]) -> AgentExecutionResult:
        start_time = time.time()
        try:
            res_data, summary = self.run(context)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return AgentExecutionResult(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status="SUCCESS",
                duration_ms=duration_ms,
                summary=summary,
                data=res_data
            )
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return AgentExecutionResult(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status="FAILED",
                duration_ms=duration_ms,
                summary=f"Lỗi thực thi: {str(e)}",
                data={"error": str(e)}
            )

    def run(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        raise NotImplementedError

