"""
AI-Driven UI Understanding and Goal Execution Demo.
Demonstrates using the AI agent to understand screen layout and achieve goals with natural language.
"""
from automation_client import AutomationClient
from automation_client.models import LLMConfig

def main():
    # Optional LLM Config (can also be read from OPENAI_API_KEY environment variable)
    llm_cfg = LLMConfig(
        model="gpt-4o-mini",
        # api_key="sk-...",
        # base_url="https://api.openai.com/v1"
    )

    client = AutomationClient(
        auto_start_server=True,
        idle_timeout=60,
        llm_config=llm_cfg,
    )
    client.connect()

    print("=== 1. AI Screen Understanding ===")
    analysis = client.ai_understand(use_vision=True)
    print("Page Analysis:", analysis.get("analysis"))

    print("\n=== 2. AI Screen Debugging / Error Detection ===")
    debug_report = client.ai_debug(auto_fix=True)
    print("Debug Report:", debug_report.get("debug_analysis"))

    print("\n=== 3. AI Natural Language Goal Execution ===")
    # Instruct AI to perform a task
    goal_res = client.ai_act(
        goal="点击屏幕上的设置图标进入系统设置",
        max_steps=5,
        use_vision=True,
    )
    print("Execution Result:", goal_res)

if __name__ == "__main__":
    main()

