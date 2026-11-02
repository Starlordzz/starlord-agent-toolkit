"""
AI Autonomous UI Agent & Debug Engine.
Performs semantic understanding, multi-step goal execution, and visual UI debugging.
"""
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
import uiautomator2 as u2
from server.ai.llm_provider import LLMProvider
from server.core.actions import ActionEngine
from server.core.hierarchy import HierarchyParser
from server.core.screenshot import ScreenshotManager

logger = logging.getLogger("automation.agent")

SYSTEM_UNDERSTAND_PROMPT = """You are an expert Android UI & UX analyzer.
Analyze the provided Android screen state (and screenshot/hierarchy elements).
Return a JSON object with:
{
  "screen_type": "string (e.g. login, home, settings, checkout, error_dialog, form, list, splash)",
  "page_title": "string or null",
  "current_app": "string or null",
  "summary": "Brief explanation of what the user is currently seeing",
  "key_elements": [
    {"index": int, "role": "string", "name": "string", "state": "enabled/disabled/focused/etc"}
  ],
  "has_error_or_modal": true/false,
  "modal_description": "string or null if no modal"
}
"""

SYSTEM_ACT_PROMPT = """You are an autonomous Android UI Agent.
Your goal is to achieve the user's objective by executing actions on the Android device.
You will receive:
1. The user's target goal.
2. The current list of interactive UI elements with their indices [1], [2], etc.
3. Past action history.

Choose the best next action to advance toward the goal.
Respond ONLY with a JSON object in this format:
{
  "thought": "Your step-by-step reasoning about the current screen and what to do next",
  "action": "click | input | swipe | scroll | press_key | wait | finish | fail",
  "target_index": <int index of the element from the list, or null>,
  "x": <optional int x coord>,
  "y": <optional int y coord>,
  "text": <text to type if action is 'input', otherwise null>,
  "key": <key name like 'back', 'home', 'enter' if action is 'press_key'>,
  "scroll_direction": <'down' | 'up' | 'left' | 'right' if action is 'scroll'>,
  "is_finished": <true if goal is completely achieved, false otherwise>,
  "finish_reason": <summary of accomplishment if finished, or failure reason if failed>
}
"""

SYSTEM_DEBUG_PROMPT = """You are an Android crash & UI debugging expert.
Inspect the current screen state and hierarchy.
Determine if the screen exhibits any crashes, ANRs (Application Not Responding), system error dialogs, permission request blockages, blank screens, or layout bugs.
Respond with a JSON object:
{
  "is_abnormal": true/false,
  "issue_type": "crash | anr | error_dialog | permission_block | blank_screen | network_error | none",
  "description": "Detailed explanation of the issue found",
  "suggested_action": "click_dismiss | grant_permission | restart_app | back | none",
  "target_dismiss_index": <int index of button to dismiss/resolve if available, or null>
}
"""


class AIAgent:
    def __init__(self, device: u2.Device, llm_provider: Optional[LLMProvider] = None):
        self.d = device
        self.engine = ActionEngine(device)
        self.llm = llm_provider or LLMProvider()

    async def understand_screen(self, use_vision: bool = True) -> Dict[str, Any]:
        """Analyze current screen and return semantic structure."""
        w, h = self.d.window_size()
        xml = self.d.dump_hierarchy()
        elements = HierarchyParser.extract_interactive_elements(xml, w, h)
        elements_text = HierarchyParser.format_elements_for_prompt(elements)

        app_info = self.d.app_current()
        user_prompt = f"Current App: {app_info.get('package')} / {app_info.get('activity')}\nScreen Size: {w}x{h}\n\n{elements_text}"

        img_b64 = None
        if use_vision:
            try:
                # Capture and overlay marks for maximum accuracy
                raw_img = ScreenshotManager.capture_image(self.d)
                som_img = ScreenshotManager.draw_som_overlay(raw_img, elements)
                img_b64 = ScreenshotManager.image_to_base64(som_img, format="JPEG", quality=80)
            except Exception as e:
                logger.warning(f"Failed to process vision screenshot for understand: {e}")

        result = await self.llm.chat_completion_json(
            system_prompt=SYSTEM_UNDERSTAND_PROMPT,
            user_prompt=user_prompt,
            image_base64=img_b64,
        )
        return {
            "analysis": result,
            "element_count": len(elements),
            "elements": elements,
            "current_app": app_info,
        }

    async def execute_goal(
        self,
        goal: str,
        max_steps: int = 8,
        use_vision: bool = True,
        step_delay: float = 1.0,
    ) -> Dict[str, Any]:
        """Autonomously drive the device to achieve a given goal."""
        history: List[Dict[str, Any]] = []

        logger.info(f"Starting AI Goal Execution: '{goal}' (max_steps={max_steps})")

        for step in range(1, max_steps + 1):
            w, h = self.d.window_size()
            xml = self.d.dump_hierarchy()
            elements = HierarchyParser.extract_interactive_elements(xml, w, h)
            elements_text = HierarchyParser.format_elements_for_prompt(elements)
            app_info = self.d.app_current()

            history_str = (
                "\n".join([f"Step {h['step']}: Action={h['action']} -> Result={h['result']}" for h in history])
                if history
                else "No previous actions taken yet."
            )

            user_prompt = (
                f"GOAL: {goal}\n"
                f"Current App: {app_info.get('package')} / {app_info.get('activity')}\n"
                f"Action History:\n{history_str}\n\n"
                f"Current Step: {step}/{max_steps}\n"
                f"{elements_text}\n"
                "What is the next action to take?"
            )

            img_b64 = None
            if use_vision:
                try:
                    raw_img = ScreenshotManager.capture_image(self.d)
                    som_img = ScreenshotManager.draw_som_overlay(raw_img, elements)
                    img_b64 = ScreenshotManager.image_to_base64(som_img, format="JPEG", quality=80)
                except Exception as e:
                    logger.warning(f"Failed to capture SoM screenshot: {e}")

            decision = await self.llm.chat_completion_json(
                system_prompt=SYSTEM_ACT_PROMPT,
                user_prompt=user_prompt,
                image_base64=img_b64,
            )

            action = decision.get("action", "").lower()
            thought = decision.get("thought", "")
            target_idx = decision.get("target_index")
            is_finished = decision.get("is_finished", False)
            finish_reason = decision.get("finish_reason", "")

            step_record = {
                "step": step,
                "thought": thought,
                "action": action,
                "target_index": target_idx,
                "decision": decision,
            }

            logger.info(f"[Step {step}] Thought: {thought} | Action: {action} (idx: {target_idx})")

            if is_finished or action == "finish":
                step_record["result"] = f"Finished: {finish_reason or 'Goal completed.'}"
                history.append(step_record)
                return {
                    "status": "success",
                    "goal": goal,
                    "completed": True,
                    "steps_taken": step,
                    "finish_reason": finish_reason or thought,
                    "history": history,
                }

            if action == "fail":
                step_record["result"] = f"Failed: {finish_reason or 'Could not complete goal.'}"
                history.append(step_record)
                return {
                    "status": "failed",
                    "goal": goal,
                    "completed": False,
                    "steps_taken": step,
                    "error": finish_reason or thought,
                    "history": history,
                }

            # Execute the action
            try:
                if action == "click":
                    if target_idx is not None:
                        res = self.engine.click(selector_params={"index": target_idx})
                    elif decision.get("x") is not None and decision.get("y") is not None:
                        res = self.engine.click(x=decision["x"], y=decision["y"])
                    else:
                        res = "Click target missing."
                    step_record["result"] = str(res)

                elif action == "input":
                    text = decision.get("text", "")
                    if target_idx is not None:
                        res = self.engine.input_text(text=text, selector_params={"index": target_idx})
                    else:
                        res = self.engine.input_text(text=text)
                    step_record["result"] = str(res)

                elif action == "scroll":
                    direction = decision.get("scroll_direction", "down")
                    res = self.engine.scroll(direction=direction)
                    step_record["result"] = str(res)

                elif action == "press_key":
                    key = decision.get("key", "back")
                    res = self.engine.press_key(key=key)
                    step_record["result"] = str(res)

                elif action == "wait":
                    await asyncio.sleep(2.0)
                    step_record["result"] = "Waited 2.0s"

                else:
                    step_record["result"] = f"Unknown action: {action}"

            except Exception as e:
                step_record["result"] = f"Error executing action: {e}"
                logger.warning(f"Step {step} execution error: {e}")

            history.append(step_record)
            await asyncio.sleep(step_delay)

        return {
            "status": "timeout",
            "goal": goal,
            "completed": False,
            "steps_taken": max_steps,
            "error": f"Reached maximum allowed steps ({max_steps}) without completing goal.",
            "history": history,
        }

    async def debug_screen(self, auto_fix: bool = False, use_vision: bool = True) -> Dict[str, Any]:
        """Inspect screen for crashes, ANRs, or error dialogs."""
        w, h = self.d.window_size()
        xml = self.d.dump_hierarchy()
        elements = HierarchyParser.extract_interactive_elements(xml, w, h)
        elements_text = HierarchyParser.format_elements_for_prompt(elements)
        app_info = self.d.app_current()

        user_prompt = f"App: {app_info.get('package')} / {app_info.get('activity')}\n{elements_text}"

        img_b64 = None
        if use_vision:
            try:
                raw_img = ScreenshotManager.capture_image(self.d)
                som_img = ScreenshotManager.draw_som_overlay(raw_img, elements)
                img_b64 = ScreenshotManager.image_to_base64(som_img, format="JPEG", quality=80)
            except Exception as e:
                logger.warning(f"Failed to capture debug screenshot: {e}")

        result = await self.llm.chat_completion_json(
            system_prompt=SYSTEM_DEBUG_PROMPT,
            user_prompt=user_prompt,
            image_base64=img_b64,
        )

        fix_result = None
        if auto_fix and result.get("is_abnormal"):
            dismiss_idx = result.get("target_dismiss_index")
            suggested = result.get("suggested_action")
            if dismiss_idx is not None:
                try:
                    fix_result = self.engine.click(selector_params={"index": dismiss_idx})
                except Exception as e:
                    fix_result = f"Failed to click dismiss button [{dismiss_idx}]: {e}"
            elif suggested == "back":
                fix_result = self.engine.press_key("back")

        return {
            "debug_analysis": result,
            "auto_fixed": fix_result is not None,
            "fix_result": fix_result,
            "current_app": app_info,
        }

