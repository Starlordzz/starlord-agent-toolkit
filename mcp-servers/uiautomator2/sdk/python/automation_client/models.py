"""
Models and Selectors for Automation Client SDK.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Selector(BaseModel):
    text: Optional[str] = None
    text_contains: Optional[str] = None
    text_matches: Optional[str] = None
    resource_id: Optional[str] = None
    resource_id_matches: Optional[str] = None
    class_name: Optional[str] = None
    description: Optional[str] = None
    description_contains: Optional[str] = None
    xpath: Optional[str] = None
    index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)


class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None

