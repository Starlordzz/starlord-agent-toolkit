import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ServerLauncher {
  static Future<bool> isServerAlive(String baseUrl, {Duration timeout = const Duration(seconds: 1)}) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health')).timeout(timeout);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'] == 'ok';
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  static Future<String> ensureServerRunning({
    String host = '127.0.0.1',
    int port = 8765,
    int idleTimeout = 60,
    String? serial,
    String? pythonExecutable,
    String? workingDirectory,
    Duration maxWait = const Duration(seconds: 15),
  }) async {
    final baseUrl = 'http://$host:$port';
    if (await isServerAlive(baseUrl)) {
      return baseUrl;
    }

    final executable = pythonExecutable ?? (Platform.isWindows ? 'python' : 'python3');
    final args = [
      '-m',
      'server.app',
      '--host',
      host,
      '--port',
      port.toString(),
      '--idle-timeout',
      idleTimeout.toString(),
    ];
    if (serial != null && serial.isNotEmpty) {
      args.addAll(['--serial', serial]);
    }

    await Process.start(
      executable,
      args,
      workingDirectory: workingDirectory,
      mode: ProcessStartMode.detached,
    );

    final stopwatch = Stopwatch()..start();
    while (stopwatch.elapsed < maxWait) {
      await Future.delayed(const Duration(milliseconds: 500));
      if (await isServerAlive(baseUrl, timeout: const Duration(milliseconds: 500))) {
        return baseUrl;
      }
    }

    throw TimeoutException('Failed to auto-launch automation server at $baseUrl within ${maxWait.inSeconds}s.');
  }
}

