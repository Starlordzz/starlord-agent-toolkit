"""
LLM Provider module supporting OpenAI-compatible APIs (OpenAI, Gemini, DeepSeek, Local LLMs).
"""
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from server.config import settings

logger = logging.getLogger("automation.llm")


class LLMProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.llm_api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or settings.llm_base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model or settings.llm_model or "gpt-4o-mini"
        self._client: Optional[AsyncOpenAI] = None

    def get_client(self) -> AsyncOpenAI:
        if not self.api_key:
            raise ValueError(
                "LLM API Key is not configured. Please set OPENAI_API_KEY or LLM_API_KEY in environment or pass it in request."
            )
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    async def chat_completion_json(
        self,
        system_prompt: str,
        user_prompt: str,
        image_base64: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Request JSON completion with optional multimodal screenshot."""
        client = self.get_client()

        user_content: List[Dict[str, Any]] = []
        if image_base64:
            # Add base64 image
            data_url = (
                image_base64
                if image_base64.startswith("data:")
                else f"data:image/png;base64,{image_base64}"
            )
            user_content.append({
                "type": "image_url",
                "image_url": {"url": data_url, "detail": "high"}
            })

        user_content.append({"type": "text", "text": user_prompt})

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content if image_base64 else user_prompt},
        ]

        logger.info(f"Calling LLM ({self.model}) for reasoning...")
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback regex extraction in case of surrounding markers
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Failed to parse LLM response as JSON: {content}")

