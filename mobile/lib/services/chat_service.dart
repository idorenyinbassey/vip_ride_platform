import 'dart:async';
import '../models/chat_models.dart';

class ChatService {
  static final ChatService _instance = ChatService._internal();
  factory ChatService() => _instance;
  ChatService._internal();

  StreamController<ChatMessage>? _messagesController;
  StreamController<bool>? _typingController;
  StreamController<ConciergeStatus>? _statusController;

  bool _isConnected = false;
  final List<ChatMessage> _chatHistory = [];
  Timer? _typingTimer;

  /// Stream for incoming messages
  Stream<ChatMessage> get messagesStream =>
      _messagesController?.stream ?? const Stream.empty();

  /// Stream for typing indicators
  Stream<bool> get typingStream =>
      _typingController?.stream ?? const Stream.empty();

  /// Stream for concierge status updates
  Stream<ConciergeStatus> get statusStream =>
      _statusController?.stream ?? const Stream.empty();

  /// Connect to concierge chat
  void connectToConcierge() {
    if (_isConnected) return;

    _isConnected = true;
    _messagesController = StreamController<ChatMessage>.broadcast();
    _typingController = StreamController<bool>.broadcast();
    _statusController = StreamController<ConciergeStatus>.broadcast();

    // Initialize with welcome message
    Future.delayed(const Duration(milliseconds: 500), () {
      _addWelcomeMessage();
    });

    // Send initial status
    final status = ConciergeStatus(
      online: true,
      message: 'Available 24/7',
      lastSeen: DateTime.now(),
      agentName: 'Sarah Thompson',
      agentId: 'concierge_001',
      isVipAgent: true,
    );
    _statusController?.add(status);
  }

  /// Disconnect from chat
  void disconnect() {
    _isConnected = false;
    _messagesController?.close();
    _typingController?.close();
    _statusController?.close();
    _typingTimer?.cancel();

    _messagesController = null;
    _typingController = null;
    _statusController = null;
  }

  /// Get chat history
  Future<List<ChatMessage>> getConciergeChat() async {
    await Future.delayed(const Duration(milliseconds: 300));

    // Add some mock history if empty
    if (_chatHistory.isEmpty) {
      _addMockHistory();
    }

    return List.from(_chatHistory);
  }

  /// Send a message
  Future<void> sendMessage(ChatMessage message) async {
    if (!_isConnected) return;

    // Add to history
    _chatHistory.add(message);

    // Simulate concierge response
    _simulateConciergeResponse(message);
  }

  /// Simulate concierge typing and response
  void _simulateConciergeResponse(ChatMessage userMessage) {
    // Start typing indicator
    _typingController?.add(true);

    // Generate response after delay
    Timer(const Duration(seconds: 2), () {
      _typingController?.add(false);

      final response = _generateConciergeResponse(userMessage.content);
      final responseMessage = ChatMessage(
        id: 'msg_${DateTime.now().millisecondsSinceEpoch}',
        senderId: 'concierge',
        content: response,
        timestamp: DateTime.now(),
        status: 'delivered',
        isFromUser: false,
        senderName: 'VIP Concierge',
      );

      _chatHistory.add(responseMessage);
      _messagesController?.add(responseMessage);
    });
  }

  /// Generate contextual concierge responses
  String _generateConciergeResponse(String userMessage) {
    final message = userMessage.toLowerCase();

    if (message.contains('book') && message.contains('ride')) {
      return 'I\'d be happy to help you book a VIP Premium ride! Would you like me to arrange:\n\n'
          '• Executive Sedan (₦15,000)\n'
          '• Luxury SUV (₦25,000)\n'
          '• Armored Vehicle (₦50,000)\n\n'
          'Please let me know your pickup location and destination.';
    }

    if (message.contains('hotel')) {
      return 'Excellent! As a VIP Premium member, you have access to exclusive perks at our partner hotels:\n\n'
          '🏨 Eko Hotel & Suites - Free upgrades, priority check-in\n'
          '🏨 Radisson Blu Anchorage - VIP lounge access\n'
          '🏨 Four Points Sheraton - Welcome drinks, room upgrades\n\n'
          'Which hotel interests you, or would you like me to book a ride to any of these?';
    }

    if (message.contains('emergency')) {
      return '🚨 I understand this is urgent. I\'m immediately:\n\n'
          '• Alerting our emergency response team\n'
          '• Notifying your emergency contacts\n'
          '• Dispatching the nearest VIP security unit\n\n'
          'Please stay on the line. Help is on the way. Can you confirm your current location?';
    }

    if (message.contains('directions') || message.contains('location')) {
      return 'I can help with directions! As your VIP Premium concierge, I have access to:\n\n'
          '• Real-time traffic updates\n'
          '• Optimal route planning\n'
          '• VIP lane information\n'
          '• Hotel and restaurant recommendations\n\n'
          'Where would you like directions to?';
    }

    if (message.contains('cancel')) {
      return 'I can help you cancel any bookings. Let me check your current reservations:\n\n'
          '• Active rides\n'
          '• Hotel bookings\n'
          '• Scheduled pickups\n\n'
          'Which booking would you like to cancel?';
    }

    if (message.contains('payment') || message.contains('billing')) {
      return 'I can assist with your VIP Premium billing:\n\n'
          '• Current subscription: VIP Premium (₦149.99/month)\n'
          '• Next billing: July 2025\n'
          '• Payment method: **** 1234\n\n'
          'Is there a specific billing question I can help with?';
    }

    if (message.contains('thank')) {
      return 'You\'re most welcome! It\'s my pleasure to assist you. As your dedicated VIP Premium concierge, I\'m available 24/7 for any needs you may have.\n\n'
          'Is there anything else I can help you with today?';
    }

    // Default responses
    final defaultResponses = [
      'Thank you for contacting VIP Premium concierge. I\'m here to assist you with any needs you may have. How can I help you today?',
      'As your personal concierge, I can help with ride bookings, hotel arrangements, restaurant reservations, or any other requests. What would you like assistance with?',
      'I understand your request. Let me assist you with that right away. Could you provide me with a few more details?',
      'Certainly! I\'m here to make your VIP Premium experience exceptional. What specific service can I arrange for you?',
      'Thank you for reaching out. As your dedicated concierge, I\'m ready to handle any request, no matter how big or small. How may I serve you?',
    ];

    defaultResponses.shuffle();
    return defaultResponses.first;
  }

  /// Add welcome message
  void _addWelcomeMessage() {
    final welcomeMessage = ChatMessage(
      id: 'welcome_msg',
      senderId: 'concierge',
      content:
          'Welcome to VIP Premium Concierge! 👋\n\n'
          'I\'m Sarah, your dedicated personal assistant. I\'m available 24/7 to help with:\n\n'
          '🚗 Premium ride bookings\n'
          '🏨 Hotel arrangements & perks\n'
          '🍽️ Restaurant reservations\n'
          '🆘 Emergency assistance\n'
          '📍 Travel planning & directions\n\n'
          'How may I assist you today?',
      timestamp: DateTime.now(),
      status: 'delivered',
      isSystemMessage: true,
      isFromUser: false,
      senderName: 'VIP Concierge',
    );

    _chatHistory.add(welcomeMessage);
    _messagesController?.add(welcomeMessage);
  }

  /// Add mock chat history
  void _addMockHistory() {
    final mockMessages = [
      ChatMessage(
        id: 'history_1',
        senderId: 'user',
        content: 'Hi, I need a ride to the airport',
        timestamp: DateTime.now().subtract(const Duration(hours: 2)),
        status: 'read',
        isFromUser: true,
        senderName: 'You',
      ),
      ChatMessage(
        id: 'history_2',
        senderId: 'concierge',
        content:
            'Good afternoon! I\'d be happy to arrange an airport transfer for you. I can book an Executive Sedan for ₦15,000 or a Luxury SUV for ₦25,000. Which would you prefer?',
        timestamp: DateTime.now().subtract(
          const Duration(hours: 2, minutes: -1),
        ),
        status: 'read',
        isFromUser: false,
        senderName: 'VIP Concierge',
      ),
      ChatMessage(
        id: 'history_3',
        senderId: 'user',
        content: 'The luxury SUV sounds perfect',
        timestamp: DateTime.now().subtract(
          const Duration(hours: 2, minutes: -2),
        ),
        status: 'read',
        isFromUser: true,
        senderName: 'You',
      ),
      ChatMessage(
        id: 'history_4',
        senderId: 'concierge',
        content:
            'Excellent choice! I\'ve booked a Range Rover Evoque for your airport transfer. The driver will arrive in 15 minutes. You\'ll receive a text with vehicle details shortly.',
        timestamp: DateTime.now().subtract(
          const Duration(hours: 2, minutes: -3),
        ),
        status: 'read',
        isFromUser: false,
        senderName: 'VIP Concierge',
      ),
    ];

    _chatHistory.addAll(mockMessages);
  }

  /// Get quick action suggestions
  Future<List<QuickAction>> getQuickActions() async {
    await Future.delayed(const Duration(milliseconds: 200));

    return [
      const QuickAction(
        id: 'book_ride',
        text: '🚗 Book Ride',
        action: 'book_ride',
        icon: 'directions_car',
      ),
      const QuickAction(
        id: 'hotel_info',
        text: '🏨 Hotel Info',
        action: 'hotel_info',
        icon: 'hotel',
      ),
      const QuickAction(
        id: 'directions',
        text: '📍 Directions',
        action: 'directions',
        icon: 'navigation',
      ),
      const QuickAction(
        id: 'emergency',
        text: '🆘 Emergency',
        action: 'emergency',
        icon: 'emergency',
        isVipOnly: true,
      ),
    ];
  }

  /// Mark messages as read
  Future<void> markAsRead(List<String> messageIds) async {
    await Future.delayed(const Duration(milliseconds: 100));

    for (final messageId in messageIds) {
      final messageIndex = _chatHistory.indexWhere(
        (msg) => msg.id == messageId,
      );
      if (messageIndex != -1) {
        _chatHistory[messageIndex] = _chatHistory[messageIndex].copyWith(
          status: 'read',
        );
      }
    }
  }

  /// Get chat history
  List<ChatMessage> getChatHistory() {
    return List.unmodifiable(_chatHistory);
  }

  /// Get unread message count
  int getUnreadCount() {
    return _chatHistory
        .where((msg) => msg.senderId == 'concierge' && msg.status != 'read')
        .length;
  }

  /// Check if concierge is currently online
  bool get isOnline => _isConnected;

  /// Get chat history count
  int get messageCount => _chatHistory.length;
}
