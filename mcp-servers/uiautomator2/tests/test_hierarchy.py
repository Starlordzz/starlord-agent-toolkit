"""
Unit tests for UI hierarchy parsing and Set-of-Marks element extraction.
"""
from server.core.hierarchy import HierarchyParser, parse_bounds

SAMPLE_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.example.app" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[0,0][1080,2400]">
    <node index="0" text="欢迎登录" resource-id="com.example.app:id/tv_title" class="android.widget.TextView" package="com.example.app" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[100,200][980,300]" />
    <node index="1" text="" resource-id="com.example.app:id/et_username" class="android.widget.EditText" package="com.example.app" content-desc="用户名输入框" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="true" password="false" selected="false" bounds="[100,350][980,480]" />
    <node index="2" text="登录" resource-id="com.example.app:id/btn_login" class="android.widget.Button" package="com.example.app" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[100,520][980,640]" />
  </node>
</hierarchy>
"""

def test_parse_bounds():
    b = parse_bounds("[100,200][980,300]")
    assert b == (100, 200, 980, 300)

def test_extract_interactive_elements():
    elements = HierarchyParser.extract_interactive_elements(SAMPLE_XML, 1080, 2400)
    assert len(elements) == 3

    # TextView
    assert elements[0]["type"] == "TextView"
    assert elements[0]["text"] == "欢迎登录"
    assert elements[0]["center"] == [540, 250]

    # EditText
    assert elements[1]["type"] == "EditText"
    assert elements[1]["content_desc"] == "用户名输入框"
    assert elements[1]["resource_id"] == "com.example.app:id/et_username"

    # Button
    assert elements[2]["type"] == "Button"
    assert elements[2]["text"] == "登录"
    assert elements[2]["clickable"] is True

def test_format_elements_for_prompt():
    elements = HierarchyParser.extract_interactive_elements(SAMPLE_XML, 1080, 2400)
    prompt = HierarchyParser.format_elements_for_prompt(elements)
    assert "[1] <TextView> text=\"欢迎登录\"" in prompt
    assert "[2] <EditText> desc=\"用户名输入框\"" in prompt
    assert "[3] <Button> text=\"登录\"" in prompt

if __name__ == "__main__":
    test_parse_bounds()
    test_extract_interactive_elements()
    test_format_elements_for_prompt()
    print("All hierarchy tests passed!")

