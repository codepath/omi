// InstabugManager temporarily disabled due to dependency issues
// This is a stub implementation to allow the app to compile

import 'package:flutter/material.dart';

/// Platform-aware manager for Instabug
/// Handles macOS compatibility internally without exposing platform checks
class InstabugManager {
  static final InstabugManager _instance = InstabugManager._internal();
  static InstabugManager get instance => _instance;

  InstabugManager._internal();

  factory InstabugManager() {
    return _instance;
  }

  /// Initialize Instabug with the provided token and settings
  static Future<void> init({
    required String token,
    List<dynamic> invocationEvents = const [],
  }) async {
    // Stub implementation
  }

  /// Set welcome message mode
  Future<void> setWelcomeMessageMode(dynamic mode) async {
    // Stub implementation
  }

  /// Identify user with email, name, and user ID
  void identifyUser(String email, String name, String userId) {
    // Stub implementation
  }

  /// Set color theme
  void setColorTheme(dynamic theme) {
    // Stub implementation
  }

  /// Log info message
  void logInfo(String message) {
    // Stub implementation
  }

  /// Log error message
  void logError(String message) {
    // Stub implementation
  }

  /// Log warning message
  void logWarn(String message) {
    // Stub implementation
  }

  /// Log debug message
  void logDebug(String message) {
    // Stub implementation
  }

  /// Log verbose message
  void logVerbose(String message) {
    // Stub implementation
  }

  /// Show bug reporting screen
  void show() {
    // Stub implementation
  }

  /// Set user attribute
  void setUserAttribute(String key, String value) {
    // Stub implementation
  }

  /// Set enabled state
  void setEnabled(bool isEnabled) {
    // Stub implementation
  }

  Future<void> reportCrash(Object exception, StackTrace stackTrace, {Map<String, String>? userAttributes}) async {
    // Stub implementation
  }

  /// Get navigator observer for navigation tracking
  /// Returns null on unsupported platforms
  NavigatorObserver? getNavigatorObserver() {
    return null;
  }

  /// Check if platform supports Instabug
  bool get isSupported => false;
}