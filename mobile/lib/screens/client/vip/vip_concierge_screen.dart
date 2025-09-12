import 'package:flutter/material.dart';
import '../../../services/chat_service.dart';
import '../../../models/chat_models.dart';

class VipConciergeScreen extends StatefulWidget {
  const VipConciergeScreen({super.key});

  @override
  State<VipConciergeScreen> createState() => _VipConciergeScreenState();
}

class _VipConciergeScreenState extends State<VipConciergeScreen>
    with TickerProviderStateMixin {
  final ChatService _chatService = ChatService();
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  late AnimationController _typingController;
  late AnimationController _shimmerController;

  List<ChatMessage> _messages = [];
  bool _isLoading = false;
  bool _isTyping = false;
  final bool _isConciergeOnline = true;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _loadChatHistory();
    _simulateConciergeActivity();
  }

  void _initializeAnimations() {
    _typingController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();

    _shimmerController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
  }

  void _simulateConciergeActivity() {
    // Simulate concierge online status
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted && _messages.isEmpty) {
        _addWelcomeMessage();
      }
    });
  }

  void _addWelcomeMessage() {
    final welcomeMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      senderId: 'concierge',
      content:
          'Hello! I\'m Sarah, your dedicated VIP concierge. How may I assist you today? I can help with ride bookings, restaurant reservations, or any special requests.',
      isFromUser: false,
      timestamp: DateTime.now(),
      senderName: 'Sarah - VIP Concierge',
    );

    setState(() {
      _messages.insert(0, welcomeMessage);
    });

    _scrollToBottom();
  }

  Future<void> _loadChatHistory() async {
    setState(() => _isLoading = true);
    try {
      final messages = _chatService
          .getChatHistory(); // Removed await since getChatHistory() returns List, not Future
      setState(() {
        _messages = messages;
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    final messageText = _messageController.text.trim();
    _messageController.clear();

    // Add user message
    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      senderId: 'user',
      content: messageText,
      isFromUser: true,
      timestamp: DateTime.now(),
      senderName: 'You',
    );

    setState(() {
      _messages.insert(0, userMessage);
      _isTyping = true;
    });

    _scrollToBottom();

    // Simulate concierge response
    await Future.delayed(const Duration(seconds: 2));

    final response = _generateConciergeResponse(messageText);
    final conciergeMessage = ChatMessage(
      id: (DateTime.now().millisecondsSinceEpoch + 1).toString(),
      senderId: 'concierge',
      content: response,
      isFromUser: false,
      timestamp: DateTime.now(),
      senderName: 'Sarah - VIP Concierge',
    );

    setState(() {
      _messages.insert(0, conciergeMessage);
      _isTyping = false;
    });

    _scrollToBottom();
  }

  String _generateConciergeResponse(String message) {
    final lowercaseMessage = message.toLowerCase();

    if (lowercaseMessage.contains('book') ||
        lowercaseMessage.contains('ride')) {
      return 'I\'d be happy to help you book a VIP ride! Would you prefer a luxury sedan, SUV, or perhaps something more specific? I can also arrange for your preferred driver if they\'re available.';
    } else if (lowercaseMessage.contains('restaurant') ||
        lowercaseMessage.contains('dinner')) {
      return 'Excellent! I can make reservations at Lagos\' finest restaurants. Do you have a preference for cuisine type? I have partnerships with several Michelin-recommended establishments.';
    } else if (lowercaseMessage.contains('hotel')) {
      return 'I can assist with hotel arrangements and transportation coordination. Our VIP partnerships include The Eko Hotel, Four Points by Sheraton, and other premium properties. What dates are you considering?';
    } else if (lowercaseMessage.contains('airport')) {
      return 'Airport transfers are one of our specialties! I can arrange priority check-in assistance and ensure you have a luxury vehicle waiting. Which airport and what time is your flight?';
    } else if (lowercaseMessage.contains('emergency') ||
        lowercaseMessage.contains('help')) {
      return 'I\'m here to help immediately. For urgent matters, I can escalate to our emergency response team. What assistance do you need right now?';
    } else if (lowercaseMessage.contains('thank')) {
      return 'You\'re very welcome! It\'s my pleasure to serve our VIP members. Is there anything else I can assist you with today?';
    } else {
      return 'I understand your request. Let me check our available options and get back to you with the best VIP solution. Our team prides itself on handling unique requests - nothing is too complex for our VIP service.';
    }
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      Future.delayed(const Duration(milliseconds: 100), () {
        _scrollController.animateTo(
          0,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        backgroundColor: Colors.grey[900],
        elevation: 0,
        title: Row(
          children: [
            Stack(
              children: [
                Container(
                  width: 35,
                  height: 35,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Colors.amber, Colors.orange],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.support_agent,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
                if (_isConciergeOnline)
                  Positioned(
                    right: 0,
                    bottom: 0,
                    child: Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: Colors.green,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.grey[900]!, width: 2),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(width: 12),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'VIP Concierge',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Sarah • Online',
                    style: TextStyle(color: Colors.green, fontSize: 12),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.phone, color: Colors.green),
            onPressed: _callConcierge,
          ),
          IconButton(
            icon: const Icon(Icons.more_vert, color: Colors.white),
            onPressed: _showMenuOptions,
          ),
        ],
      ),
      body: Column(
        children: [
          _buildVipConciergeHeader(),
          Expanded(child: _buildChatArea()),
          _buildMessageInput(),
        ],
      ),
    );
  }

  Widget _buildVipConciergeHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.amber.withOpacity(0.1),
            Colors.orange.withOpacity(0.1),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        border: Border(
          bottom: BorderSide(color: Colors.amber.withOpacity(0.3)),
        ),
      ),
      child: Row(
        children: [
          AnimatedBuilder(
            animation: _shimmerController,
            builder: (context, child) {
              return Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.amber.withOpacity(
                    0.1 + (_shimmerController.value * 0.1),
                  ),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.diamond, color: Colors.amber, size: 20),
              );
            },
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '24/7 Personal Concierge',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'VIP members get priority response within 60 seconds',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.green.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Text(
              'PREMIUM',
              style: TextStyle(
                color: Colors.green,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatArea() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: Colors.amber),
      );
    }

    return ListView.builder(
      controller: _scrollController,
      reverse: true,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length + (_isTyping ? 1 : 0),
      itemBuilder: (context, index) {
        if (_isTyping && index == 0) {
          return _buildTypingIndicator();
        }

        final messageIndex = _isTyping ? index - 1 : index;
        final message = _messages[messageIndex];
        return _buildMessageBubble(message);
      },
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    final isUser = message.isFromUser;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Colors.amber, Colors.orange],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.support_agent,
                color: Colors.white,
                size: 16,
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: isUser ? Colors.amber : Colors.grey[800],
                borderRadius: BorderRadius.circular(18).copyWith(
                  bottomLeft: isUser
                      ? const Radius.circular(18)
                      : const Radius.circular(4),
                  bottomRight: isUser
                      ? const Radius.circular(4)
                      : const Radius.circular(18),
                ),
                boxShadow: [
                  if (!isUser)
                    BoxShadow(
                      color: Colors.amber.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    message.content,
                    style: TextStyle(
                      color: isUser ? Colors.black : Colors.white,
                      fontSize: 14,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${message.timestamp.hour}:${message.timestamp.minute.toString().padLeft(2, '0')}',
                    style: TextStyle(
                      color: isUser ? Colors.black54 : Colors.grey,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: Colors.grey[700],
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.person, color: Colors.white, size: 16),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Container(
            width: 30,
            height: 30,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Colors.amber, Colors.orange],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.support_agent,
              color: Colors.white,
              size: 16,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[800],
              borderRadius: BorderRadius.circular(
                18,
              ).copyWith(bottomLeft: const Radius.circular(4)),
            ),
            child: AnimatedBuilder(
              animation: _typingController,
              builder: (context, child) {
                return Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildTypingDot(0),
                    const SizedBox(width: 4),
                    _buildTypingDot(1),
                    const SizedBox(width: 4),
                    _buildTypingDot(2),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypingDot(int index) {
    final animationValue = (_typingController.value * 3 - index).clamp(
      0.0,
      1.0,
    );
    return Transform.scale(
      scale: 0.5 + (animationValue * 0.5),
      child: Container(
        width: 6,
        height: 6,
        decoration: BoxDecoration(
          color: Colors.amber.withOpacity(0.5 + (animationValue * 0.5)),
          shape: BoxShape.circle,
        ),
      ),
    );
  }

  Widget _buildMessageInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        border: Border(top: BorderSide(color: Colors.grey[700]!)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.grey[800],
                borderRadius: BorderRadius.circular(25),
                border: Border.all(color: Colors.amber.withOpacity(0.3)),
              ),
              child: TextField(
                controller: _messageController,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  hintText: 'Message your VIP concierge...',
                  hintStyle: TextStyle(color: Colors.grey),
                  border: InputBorder.none,
                ),
                maxLines: null,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _sendMessage(),
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _sendMessage,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Colors.amber, Colors.orange],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.amber.withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: const Icon(Icons.send, color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }

  void _callConcierge() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[800],
        title: const Row(
          children: [
            Icon(Icons.phone, color: Colors.green),
            SizedBox(width: 10),
            Text('Call VIP Concierge', style: TextStyle(color: Colors.white)),
          ],
        ),
        content: const Text(
          'Would you like to call your dedicated VIP concierge directly? This will connect you to Sarah within 30 seconds.',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _initiateCall();
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            child: const Text(
              'Call Now',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  void _initiateCall() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Connecting to VIP concierge...'),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _showMenuOptions() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.grey[800],
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Concierge Options',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            ListTile(
              leading: const Icon(Icons.restaurant, color: Colors.amber),
              title: const Text(
                'Restaurant Reservations',
                style: TextStyle(color: Colors.white),
              ),
              onTap: () {
                Navigator.pop(context);
                _requestRestaurantReservation();
              },
            ),
            ListTile(
              leading: const Icon(Icons.local_activity, color: Colors.amber),
              title: const Text(
                'Event Tickets',
                style: TextStyle(color: Colors.white),
              ),
              onTap: () {
                Navigator.pop(context);
                _requestEventTickets();
              },
            ),
            ListTile(
              leading: const Icon(Icons.flight, color: Colors.amber),
              title: const Text(
                'Travel Planning',
                style: TextStyle(color: Colors.white),
              ),
              onTap: () {
                Navigator.pop(context);
                _requestTravelPlanning();
              },
            ),
            ListTile(
              leading: const Icon(Icons.star, color: Colors.amber),
              title: const Text(
                'Special Requests',
                style: TextStyle(color: Colors.white),
              ),
              onTap: () {
                Navigator.pop(context);
                _makeSpecialRequest();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _requestRestaurantReservation() {
    _addAutomatedMessage('I\'d like help with restaurant reservations.');
  }

  void _requestEventTickets() {
    _addAutomatedMessage('Can you help me find event tickets?');
  }

  void _requestTravelPlanning() {
    _addAutomatedMessage('I need assistance with travel planning.');
  }

  void _makeSpecialRequest() {
    _addAutomatedMessage('I have a special request that needs VIP attention.');
  }

  void _addAutomatedMessage(String message) {
    _messageController.text = message;
    _sendMessage();
  }

  @override
  void dispose() {
    _typingController.dispose();
    _shimmerController.dispose();
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}
