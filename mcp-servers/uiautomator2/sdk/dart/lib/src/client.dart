import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'launcher.dart';
import 'models.dart';

class AutomationClient {
  final String host;
  final int port;
  String? serial;
  final int idleTimeout;
  final bool autoStartServer;
  final String? pythonExecutable;
  final String? serverWorkingDirectory;
  final LLMConfig? llmConfig;

  final http.Client _httpClient = http.Client();

  AutomationClient({
    this.host = '127.0.0.1',
    this.port = 8765,
    this.serial,
    this.idleTimeout = 60,
    this.autoStartServer = true,
    this.pythonExecutable,
    this.serverWorkingDirectory,
    this.llmConfig,
  });

  String get baseUrl => 'http://$host:$port';

  Future<void> _ensureServer() async {
    if (autoStartServer) {
      await ServerLauncher.ensureServerRunning(
        host: host,
        port: port,
        idleTimeout: idleTimeout,
        serial: serial,
        pythonExecutable: pythonExecutable,
        workingDirectory: serverWorkingDirectory,
      );
    }
  }

  Future<Map<String, dynamic>> _request(String method, String path, [Map<String, dynamic>? body]) async {
    await _ensureServer();
    final uri = Uri.parse('$baseUrl$path');
    final headers = {'Content-Type': 'application/json'};

    http.Response response;
    if (method == 'GET') {
      response = await _httpClient.get(uri, headers: headers);
    } else if (method == 'POST') {
      response = await _httpClient.post(uri, headers: headers, body: body != null ? jsonEncode(body) : null);
    } else {
      throw UnsupportedError('Unsupported HTTP method: $method');
    }

    if (response.statusCode >= 400) {
      throw HttpException('Automation Server error (${response.statusCode}): ${response.body}', uri: uri);
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  /// Connect to Android device
  Future<Map<String, dynamic>> connect([String? deviceSerial]) async {
    final target = deviceSerial ?? serial;
    final res = await _request('POST', '/device/connect', {'serial': target});
    if (res['device'] != null && res['device']['serial'] != null) {
      serial = res['device']['serial'];
    }
    return res;
  }

  /// Get device resolution and foreground app
  Future<Map<String, dynamic>> getDeviceInfo() async {
    return await _request('GET', '/device/info?serial=${serial ?? ""}');
  }

  /// List all ADB devices
  Future<List<dynamic>> listDevices() async {
    final res = await _request('GET', '/device/list');
    return res['devices'] as List<dynamic>? ?? [];
  }

  Map<String, dynamic>? _buildSelector({
    String? text,
    String? textContains,
    String? resourceId,
    String? className,
    String? description,
    String? xpath,
    int? index,
    Selector? selector,
  }) {
    if (selector != null) return selector.toJson();
    final s = Selector(
      text: text,
      textContains: textContains,
      resourceId: resourceId,
      className: className,
      description: description,
      xpath: xpath,
      index: index,
    );
    final json = s.toJson();
    return json.isNotEmpty ? json : null;
  }

  /// Click element or coordinate
  Future<Map<String, dynamic>> click({
    int? x,
    int? y,
    String? text,
    String? textContains,
    String? resourceId,
    String? className,
    String? description,
    String? xpath,
    int? index,
    Selector? selector,
    double timeout = 10.0,
  }) async {
    final sel = _buildSelector(
      text: text,
      textContains: textContains,
      resourceId: resourceId,
      className: className,
      description: description,
      xpath: xpath,
      index: index,
      selector: selector,
    );
    return await _request('POST', '/ui/click', {
      'serial': serial,
      'x': x,
      'y': y,
      'selector': sel,
      'timeout': timeout,
    });
  }

  /// Double click target
  Future<Map<String, dynamic>> doubleClick({
    int? x,
    int? y,
    String? text,
    String? resourceId,
    Selector? selector,
    double duration = 0.1,
  }) async {
    final sel = _buildSelector(text: text, resourceId: resourceId, selector: selector);
    return await _request('POST', '/ui/double_click', {
      'serial': serial,
      'x': x,
      'y': y,
      'selector': sel,
      'duration': duration,
    });
  }

  /// Long click target
  Future<Map<String, dynamic>> longClick({
    int? x,
    int? y,
    String? text,
    String? resourceId,
    Selector? selector,
    double duration = 1.0,
  }) async {
    final sel = _buildSelector(text: text, resourceId: resourceId, selector: selector);
    return await _request('POST', '/ui/long_click', {
      'serial': serial,
      'x': x,
      'y': y,
      'selector': sel,
      'duration': duration,
    });
  }

  /// Input text
  Future<Map<String, dynamic>> input({
    required String text,
    String? targetText,
    String? resourceId,
    Selector? selector,
    bool clear = true,
  }) async {
    final sel = _buildSelector(text: targetText, resourceId: resourceId, selector: selector);
    return await _request('POST', '/ui/input', {
      'serial': serial,
      'text': text,
      'selector': sel,
      'clear': clear,
    });
  }

  /// Clear text in target
  Future<Map<String, dynamic>> clearText({
    String? targetText,
    String? resourceId,
    Selector? selector,
  }) async {
    final sel = _buildSelector(text: targetText, resourceId: resourceId, selector: selector);
    return await _request('POST', '/ui/clear', {
      'serial': serial,
      'selector': sel,
    });
  }

  /// Swipe gesture
  Future<Map<String, dynamic>> swipe({
    required int sx,
    required int sy,
    required int ex,
    required int ey,
    double duration = 0.5,
  }) async {
    return await _request('POST', '/ui/swipe', {
      'serial': serial,
      'sx': sx,
      'sy': sy,
      'ex': ex,
      'ey': ey,
      'duration': duration,
    });
  }

  /// Scroll
  Future<Map<String, dynamic>> scroll({String direction = 'forward'}) async {
    return await _request('POST', '/ui/scroll', {
      'serial': serial,
      'direction': direction,
    });
  }

  /// Press hardware/virtual key
  Future<Map<String, dynamic>> press({String key = 'back'}) async {
    return await _request('POST', '/ui/press', {
      'serial': serial,
      'key': key,
    });
  }

  /// Capture screen as base64 and optionally save to file
  Future<Map<String, dynamic>> screenshot({
    String format = 'PNG',
    int? maxDim,
    bool withSomOverlay = false,
    String? savePath,
  }) async {
    final res = await _request('POST', '/ui/screenshot', {
      'serial': serial,
      'format': format,
      'max_dim': maxDim,
      'with_som_overlay': withSomOverlay,
    });

    if (savePath != null && res['base64'] != null) {
      final bytes = base64Decode(res['base64']);
      await File(savePath).writeAsBytes(bytes);
    }
    return res;
  }

  /// Dump UI hierarchy and simplified interactive elements
  Future<Map<String, dynamic>> dump({bool simplified = true, bool includeXml = false}) async {
    return await _request('POST', '/ui/dump', {
      'serial': serial,
      'simplified': simplified,
      'include_xml': includeXml,
    });
  }

  /// Check if element exists
  Future<bool> exists({String? text, String? resourceId, Selector? selector}) async {
    final sel = _buildSelector(text: text, resourceId: resourceId, selector: selector);
    if (sel == null) return false;
    final res = await _request('POST', '/ui/find', {'serial': serial, 'selector': sel});
    return res['exists'] == true;
  }

  /// Wait for element to appear
  Future<bool> waitFor({String? text, String? resourceId, Selector? selector, double timeout = 10.0}) async {
    final sel = _buildSelector(text: text, resourceId: resourceId, selector: selector);
    if (sel == null) return false;
    final res = await _request('POST', '/ui/wait', {'serial': serial, 'selector': sel, 'timeout': timeout});
    return res['found'] == true;
  }

  /// Start app
  Future<Map<String, dynamic>> startApp({
    required String packageName,
    String? activity,
    bool stopFirst = false,
  }) async {
    return await _request('POST', '/app/start', {
      'serial': serial,
      'package_name': packageName,
      'activity': activity,
      'stop_first': stopFirst,
    });
  }

  /// Stop app
  Future<Map<String, dynamic>> stopApp(String packageName) async {
    return await _request('POST', '/app/stop', {
      'serial': serial,
      'package_name': packageName,
    });
  }

  /// Get current app
  Future<Map<String, dynamic>> currentApp() async {
    final res = await _request('GET', '/app/current?serial=${serial ?? ""}');
    return res['app'] as Map<String, dynamic>? ?? {};
  }

  /// AI Screen Understanding
  Future<Map<String, dynamic>> aiUnderstand({bool useVision = true}) async {
    return await _request('POST', '/ai/understand', {
      'serial': serial,
      'use_vision': useVision,
      'llm': llmConfig?.toJson(),
    });
  }

  /// AI Goal-driven Execution
  Future<Map<String, dynamic>> aiAct({
    required String goal,
    int maxSteps = 8,
    bool useVision = true,
    double stepDelay = 1.0,
  }) async {
    return await _request('POST', '/ai/act', {
      'serial': serial,
      'goal': goal,
      'max_steps': maxSteps,
      'use_vision': useVision,
      'step_delay': stepDelay,
      'llm': llmConfig?.toJson(),
    });
  }

  /// AI Debug & Error Detection
  Future<Map<String, dynamic>> aiDebug({bool autoFix = false, bool useVision = true}) async {
    return await _request('POST', '/ai/debug', {
      'serial': serial,
      'auto_fix': autoFix,
      'use_vision': useVision,
      'llm': llmConfig?.toJson(),
    });
  }

  /// Manually shutdown server
  Future<Map<String, dynamic>> shutdownServer() async {
    return await _request('POST', '/shutdown');
  }

  void close() {
    _httpClient.close();
  }
}

