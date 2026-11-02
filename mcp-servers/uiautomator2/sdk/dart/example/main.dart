import 'package:automation_client/automation_client.dart';

void main() async {
  print('=== 1. Initialize Dart Automation Client ===');
  // Auto-spawns server if not running, with 60s idle timeout
  final client = AutomationClient(
    host: '127.0.0.1',
    port: 8765,
    idleTimeout: 60,
    autoStartServer: true,
  );

  print('=== 2. Connect to Android Device ===');
  final conn = await client.connect();
  print('Connected: $conn');

  final info = await client.getDeviceInfo();
  print('Device Info: $info');

  print('=== 3. Take Screenshot ===');
  await client.screenshot(savePath: 'dart_screen.png');
  print('Saved dart_screen.png');

  print('=== 4. Dump Hierarchy ===');
  final dump = await client.dump();
  print('Detected ${dump["element_count"]} interactive UI elements.');

  print('=== 5. Perform Actions ===');
  // Click button by text
  // await client.click(text: '登录');

  // Input text
  // await client.input(text: 'my_username', resourceId: 'com.example:id/username');

  // Press home key
  await client.press(key: 'home');

  print('=== 6. AI Agent Example ===');
  /*
  final aiResult = await client.aiAct(
    goal: '打开系统设置并进入关于手机',
    maxSteps: 5,
  );
  print('AI Result: $aiResult');
  */

  print('Done! Automation server will automatically shut down after 60s idle.');
  client.close();
}

