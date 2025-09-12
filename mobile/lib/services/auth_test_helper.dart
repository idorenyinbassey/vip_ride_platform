// Test authentication token storage
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthTestHelper {
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  // Store the test token from Django
  static Future<void> storeTestToken() async {
    const testToken =
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU3NDk4NDY3LCJpYXQiOjE3NTc0OTc1NjcsImp0aSI6IjdkN2YzMzc4ZDQ1ODRjNzVhNTJiNTJiNDNhYjUyNGQ2IiwidXNlcl9pZCI6IjgyOTYyMTRkLTczYjAtNDQ1OS05YzgxLWZmNGQ1ZDBhYjA0OCIsImlzcyI6InZpcC1yaWRlLXBsYXRmb3JtIn0.jdSsEGMlrhL0hohNcIpKJukjxrJw7Hbu_6GH5ssgp3c';

    await _storage.write(key: 'access_token', value: testToken);
    debugPrint('✅ Test token stored successfully');
  }

  // Check current stored token
  static Future<void> checkStoredToken() async {
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      debugPrint('✅ Token found: ${token.substring(0, 50)}...');
    } else {
      debugPrint('❌ No token found in storage');
    }
  }

  // Clear stored token
  static Future<void> clearToken() async {
    await _storage.delete(key: 'access_token');
    debugPrint('🗑️ Token cleared from storage');
  }
}
