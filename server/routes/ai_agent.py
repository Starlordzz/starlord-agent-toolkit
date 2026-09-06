"""
AI Agent & Semantic Understanding API Routes.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from server.core.device_manager import device_manager
from server.ai.agent import AIAgent
from server.ai.llm_provider import LLMProvider

router = APIRouter(prefix="/ai", tags=["AI Agent"])


class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


class UnderstandRequest(BaseModel):
    serial: Optional[str] = None
    use_vision: bool = True
    llm: Optional[LLMConfig] = None


class ActRequest(BaseModel):
    serial: Optional[str] = None
    goal: str
    max_steps: int = 8
    use_vision: bool = True
    step_delay: float = 1.0
    llm: Optional[LLMConfig] = None


class DebugRequest(BaseModel):
    serial: Optional[str] = None
    auto_fix: bool = False
    use_vision: bool = True
    llm: Optional[LLMConfig] = None


def get_agent_instance(serial: Optional[str], llm_config: Optional[LLMConfig]) -> AIAgent:
    d = device_manager.get_device(serial)
    provider = None
    if llm_config:
        provider = LLMProvider(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            model=llm_config.model,
        )
    return AIAgent(d, provider)


@router.post("/understand")
async def understand_screen(req: UnderstandRequest = UnderstandRequest()):
    """Understand current screen semantically and detect key elements/modals."""
    try:
        agent = get_agent_instance(req.serial, req.llm)
        res = await agent.understand_screen(use_vision=req.use_vision)
        return {"status": "success", **res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/act")
async def execute_goal(req: ActRequest):
    """Autonomously drive the device with natural language goals."""
    try:
        agent = get_agent_instance(req.serial, req.llm)
        res = await agent.execute_goal(
            goal=req.goal,
            max_steps=req.max_steps,
            use_vision=req.use_vision,
            step_delay=req.step_delay,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug")
async def debug_screen(req: DebugRequest = DebugRequest()):
    """Inspect screen for crashes, ANR, and errors, with optional auto-dismiss/fix."""
    try:
        agent = get_agent_instance(req.serial, req.llm)
        res = await agent.debug_screen(auto_fix=req.auto_fix, use_vision=req.use_vision)
        return {"status": "success", **res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

