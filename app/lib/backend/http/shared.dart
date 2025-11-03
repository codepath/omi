import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:omi/backend/auth.dart';
import 'package:omi/backend/preferences.dart';
import 'package:omi/env/env.dart';
import 'package:omi/utils/logger.dart';
import 'package:http/http.dart' as http;
import 'package:omi/utils/platform/platform_manager.dart';

Future<String> getAuthHeader() async {
  debugPrint('DEBUG: getAuthHeader called');
  DateTime? expiry = DateTime.fromMillisecondsSinceEpoch(SharedPreferencesUtil().tokenExpirationTime);
  bool hasAuthToken = SharedPreferencesUtil().authToken.isNotEmpty;
  
  debugPrint('DEBUG: hasAuthToken: $hasAuthToken');
  debugPrint('DEBUG: tokenExpirationTime: ${SharedPreferencesUtil().tokenExpirationTime}');
  debugPrint('DEBUG: expiry: $expiry');

  bool isExpirationDateValid = !(expiry.isBefore(DateTime.now()) ||
      expiry.isAtSameMomentAs(DateTime.fromMillisecondsSinceEpoch(0)) ||
      (expiry.isBefore(DateTime.now().add(const Duration(minutes: 5))) && expiry.isAfter(DateTime.now())));

  debugPrint('DEBUG: isExpirationDateValid: $isExpirationDateValid');

  if (!hasAuthToken || !isExpirationDateValid) {
    debugPrint('DEBUG: Token refresh needed, calling getIdToken()...');
    SharedPreferencesUtil().authToken = await getIdToken() ?? '';
    debugPrint('DEBUG: Token refresh result: ${SharedPreferencesUtil().authToken.isNotEmpty ? "SUCCESS" : "FAILED"}');
  }

  hasAuthToken = SharedPreferencesUtil().authToken.isNotEmpty;
  
  if (!hasAuthToken) {
    debugPrint('DEBUG: No auth token available');
    if (isSignedIn()) {
      // should only throw if the user is signed in but the token is not found
      // if the user is not signed in, the token will always be empty
      debugPrint('DEBUG: User is signed in but no token found - throwing exception');
      throw Exception('No auth token found');
    }
  }
  
  String header = 'Bearer ${SharedPreferencesUtil().authToken}';
  debugPrint('DEBUG: Returning auth header, length: ${header.length}');
  return header;
}

Future<http.Response?> makeApiCall({
  required String url,
  required Map<String, String> headers,
  required String body,
  required String method,
}) async {
  try {
    debugPrint('DEBUG: ========== API CALL ==========');
    debugPrint('DEBUG: Request URL: $url');
    debugPrint('DEBUG: API Base URL: ${Env.apiBaseUrl}');
    debugPrint('DEBUG: Stored token exists: ${SharedPreferencesUtil().authToken.isNotEmpty}');
    debugPrint('DEBUG: Stored token length: ${SharedPreferencesUtil().authToken.length}');
    
    if (url.contains(Env.apiBaseUrl!)) {
      headers['Authorization'] = await getAuthHeader();
      debugPrint('DEBUG: Auth header added, token length: ${headers['Authorization']?.length ?? 0}');
      // headers['Authorization'] = ''; // set admin key + uid here for testing
    }

    final client = http.Client();

    http.Response? response = await _performRequest(client, url, headers, body, method);
    debugPrint('DEBUG: Initial response status: ${response.statusCode}');
    
    if (response.statusCode == 401) {
      Logger.log('Token expired on 1st attempt');
      debugPrint('DEBUG: 401 received, attempting token refresh...');
      
      // Refresh the token
      SharedPreferencesUtil().authToken = await getIdToken() ?? '';
      debugPrint('DEBUG: New token obtained: ${SharedPreferencesUtil().authToken.isNotEmpty ? "SUCCESS" : "FAILED"}');
      debugPrint('DEBUG: Token length: ${SharedPreferencesUtil().authToken.length}');
      
      if (SharedPreferencesUtil().authToken.isNotEmpty) {
        // Update the header with the new token
        headers['Authorization'] = 'Bearer ${SharedPreferencesUtil().authToken}';
        // Retry the request with the new token
        response = await _performRequest(client, url, headers, body, method);
        Logger.log('Token refreshed and request retried');
        if (response.statusCode == 401) {
          // Only sign out if user is actually signed in
          if (isSignedIn()) {
            await signOut();
          }
          Logger.handle(Exception('Authentication failed. Please sign in again.'), StackTrace.current,
              message: 'Authentication failed. Please sign in again.');
        }
      } else {
        // Only sign out if user is actually signed in
        if (isSignedIn()) {
          await signOut();
        }
        Logger.handle(Exception('Authentication failed. Please sign in again.'), StackTrace.current,
            message: 'Authentication failed. Please sign in again.');
      }
    }

    return response;
  } catch (e, stackTrace) {
    debugPrint('HTTP request failed: $e, $stackTrace');
    PlatformManager.instance.instabug.reportCrash(e, stackTrace, userAttributes: {'url': url, 'method': method});
    return null;
  } finally {}
}

Future<http.Response> _performRequest(
  http.Client client,
  String url,
  Map<String, String> headers,
  String body,
  String method,
) async {
  switch (method) {
    case 'POST':
      headers['Content-Type'] = 'application/json';
      return await client.post(Uri.parse(url), headers: headers, body: body);
    case 'GET':
      return await client.get(Uri.parse(url), headers: headers);
    case 'DELETE':
      headers['Content-Type'] = 'application/json';
      return await client.delete(Uri.parse(url), headers: headers, body: body);
    case 'PATCH':
      headers['Content-Type'] = 'application/json';
      return await client.patch(Uri.parse(url), headers: headers, body: body);
    case 'PUT':
      headers['Content-Type'] = 'application/json';
      return await client.put(Uri.parse(url), headers: headers, body: body);
    default:
      throw Exception('Unsupported HTTP method: $method');
  }
}

// Function to extract content from the API response.
dynamic extractContentFromResponse(
  http.Response? response, {
  bool isEmbedding = false,
  bool isFunctionCalling = false,
}) {
  if (response != null && response.statusCode == 200) {
    var data = jsonDecode(response.body);
    if (isEmbedding) {
      var embedding = data['data'][0]['embedding'];
      return embedding;
    }
    var message = data['choices'][0]['message'];
    if (isFunctionCalling && message['tool_calls'] != null) {
      debugPrint('message $message');
      debugPrint('message ${message['tool_calls'].runtimeType}');
      return message['tool_calls'];
    }
    return data['choices'][0]['message']['content'];
  } else {
    debugPrint('Error fetching data: ${response?.statusCode}');
    // TODO: handle error, better specially for script migration
    PlatformManager.instance.instabug
        .reportCrash(Exception('Error fetching data: ${response?.statusCode}'), StackTrace.current, userAttributes: {
      'response_null': (response == null).toString(),
      'response_status_code': response?.statusCode.toString() ?? '',
      'is_embedding': isEmbedding.toString(),
      'is_function_calling': isFunctionCalling.toString(),
    });
    return null;
  }
}
