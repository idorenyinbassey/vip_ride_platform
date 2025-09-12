import 'package:flutter/material.dart';
import '../../../services/chat_service.dart';
import '../../../models/chat_models.dart';

class ConciergeChatScreen extends StatefulWidget {
  const ConciergeChatScreen({super.key});

  @override
  State<ConciergeChatScreen> createState() => _ConciergeChatScreenState();
}

class _ConciergeChatScreenState extends State<ConciergeChatScreen>
    with TickerProviderStateMixin {
  final ChatService _chatService = ChatService();
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  late AnimationController _typingController;
  late AnimationController _onlineController;

  List<ChatMessage> _messages = [];
  bool _isLoading = true;
  bool _conciergeOnline = true;
  bool _isTyping = false;
  String _conciergeStatus = 'Available 24/7';

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _loadChatHistory();
    _connectToChat();
  }

  void _initializeAnimations() {
    _typingController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();

    _onlineController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();
  }

  Future<void> _loadChatHistory() async {
    try {
      final messages = await _chatService.getConciergeChat();
      setState(() {
        _messages = messages;
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _connectToChat() {
    _chatService.connectToConcierge();

    _chatService.messagesStream.listen((message) {
      setState(() {
        _messages.add(message);
        _isTyping = false;
      });
      _scrollToBottom();
    });

    _chatService.typingStream.listen((typing) {
      setState(() {
        _isTyping = typing;
      });
      if (typing) _scrollToBottom();
    });

    _chatService.statusStream.listen((status) {
      setState(() {
        _conciergeOnline = status.online;
        _conciergeStatus = status.message;
      });
    });
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: _buildAppBar(),
      body: Column(
        children: [
          _buildConciergeHeader(),
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(color: Colors.amber),
                  )
                : _buildChatList(),
          ),
          _buildQuickActions(),
          _buildMessageInput(),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: Colors.black,
      elevation: 0,
      title: Row(
        children: [
          Stack(
            children: [
              const CircleAvatar(
                radius: 18,
                backgroundColor: Colors.amber,
                child: Icon(Icons.support_agent, color: Colors.black, size: 20),
              ),
              if (_conciergeOnline)
                Positioned(
                  right: 0,
                  bottom: 0,
                  child: AnimatedBuilder(
                    animation: _onlineController,
                    builder: (context, child) {
                      return Container(
                        width: 12,
                        height: 12,
                        decoration: BoxDecoration(
                          color: Colors.green.withOpacity(
                            0.7 + (_onlineController.value * 0.3),
                          ),
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.black, width: 2),
                        ),
                      );
                    },
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
                  'Premium Support',
                  style: TextStyle(color: Colors.amber, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.call, color: Colors.amber),
          onPressed: _callConcierge,
        ),
        IconButton(
          icon: const Icon(Icons.video_call, color: Colors.amber),
          onPressed: _videoConcierge,
        ),
      ],
    );
  }

  Widget _buildConciergeHeader() {
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
        border: Border(bottom: BorderSide(color: Colors.grey[800]!, width: 1)),
      ),
      child: Row(
        children: [
          const Icon(Icons.diamond, color: Colors.amber, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'VIP Premium Concierge Service',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  _conciergeStatus,
                  style: TextStyle(
                    color: _conciergeOnline ? Colors.green : Colors.orange,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              'Priority Support',
              style: TextStyle(
                color: Colors.amber,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length + (_isTyping ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == _messages.length && _isTyping) {
          return _buildTypingIndicator();
        }

        final message = _messages[index];
        final isUser = message.senderId != 'concierge';

        return _buildMessageBubble(message, isUser);
      },
    );
  }

  Widget _buildMessageBubble(ChatMessage message, bool isUser) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            const CircleAvatar(
              radius: 16,
              backgroundColor: Colors.amber,
              child: Icon(Icons.support_agent, color: Colors.black, size: 16),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: isUser
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isUser ? Colors.amber : Colors.grey[800],
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(16),
                      topRight: const Radius.circular(16),
                      bottomLeft: Radius.circular(isUser ? 16 : 4),
                      bottomRight: Radius.circular(isUser ? 4 : 16),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (!isUser)
                        const Text(
                          'VIP Concierge',
                          style: TextStyle(
                            color: Colors.amber,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      if (!isUser) const SizedBox(height: 4),
                      Text(
                        message.content,
                        style: TextStyle(
                          color: isUser ? Colors.black : Colors.white,
                          fontSize: 14,
                        ),
                      ),
                      if (message.attachments.isNotEmpty)
                        ...message.attachments.map(
                          (attachment) => _buildAttachment(attachment),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _formatTime(message.timestamp),
                      style: const TextStyle(color: Colors.grey, fontSize: 11),
                    ),
                    if (isUser) ...[
                      const SizedBox(width: 4),
                      Icon(
                        message.status == 'read' ? Icons.done_all : Icons.done,
                        color: message.status == 'read'
                            ? Colors.amber
                            : Colors.grey,
                        size: 12,
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.blue,
              child: Text(
                'VIP',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAttachment(ChatAttachment attachment) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getAttachmentIcon(attachment.type),
            color: Colors.amber,
            size: 16,
          ),
          const SizedBox(width: 8),
          Text(
            attachment.name,
            style: const TextStyle(color: Colors.white, fontSize: 12),
          ),
        ],
      ),
    );
  }

  IconData _getAttachmentIcon(String type) {
    switch (type) {
      case 'image':
        return Icons.image;
      case 'document':
        return Icons.description;
      case 'location':
        return Icons.location_on;
      default:
        return Icons.attach_file;
    }
  }

  Widget _buildTypingIndicator() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          const CircleAvatar(
            radius: 16,
            backgroundColor: Colors.amber,
            child: Icon(Icons.support_agent, color: Colors.black, size: 16),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.grey[800],
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
                bottomRight: Radius.circular(16),
                bottomLeft: Radius.circular(4),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                AnimatedBuilder(
                  animation: _typingController,
                  builder: (context, child) {
                    return Row(
                      children: List.generate(3, (index) {
                        final delay = index * 0.3;
                        final animValue =
                            (_typingController.value + delay) % 1.0;
                        return Container(
                          margin: const EdgeInsets.only(right: 4),
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: Colors.amber.withOpacity(
                              0.5 + (animValue * 0.5),
                            ),
                            shape: BoxShape.circle,
                          ),
                        );
                      }),
                    );
                  },
                ),
                const SizedBox(width: 8),
                const Text(
                  'Concierge is typing...',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    final quickActions = [
      {'text': '🚗 Book Ride', 'action': 'book_ride'},
      {'text': '🏨 Hotel Info', 'action': 'hotel_info'},
      {'text': '📍 Directions', 'action': 'directions'},
      {'text': '🆘 Emergency', 'action': 'emergency'},
    ];

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(
          children: quickActions
              .map(
                (action) => Container(
                  margin: const EdgeInsets.only(right: 8),
                  child: ActionChip(
                    label: Text(
                      action['text']!,
                      style: const TextStyle(color: Colors.white, fontSize: 12),
                    ),
                    backgroundColor: Colors.grey[800],
                    side: BorderSide(color: Colors.amber.withOpacity(0.3)),
                    onPressed: () => _sendQuickAction(action['action']!),
                  ),
                ),
              )
              .toList(),
        ),
      ),
    );
  }

  Widget _buildMessageInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        border: Border(top: BorderSide(color: Colors.grey[800]!, width: 1)),
      ),
      child: SafeArea(
        child: Row(
          children: [
            IconButton(
              icon: const Icon(Icons.attach_file, color: Colors.amber),
              onPressed: _attachFile,
            ),
            Expanded(
              child: TextField(
                controller: _messageController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Type a message to your concierge...',
                  hintStyle: const TextStyle(color: Colors.grey),
                  filled: true,
                  fillColor: Colors.grey[800],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(25),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                ),
                maxLines: null,
                keyboardType: TextInputType.multiline,
                textInputAction: TextInputAction.send,
                onSubmitted: _sendMessage,
              ),
            ),
            const SizedBox(width: 8),
            CircleAvatar(
              backgroundColor: Colors.amber,
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.black, size: 20),
                onPressed: () => _sendMessage(_messageController.text),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _sendMessage(String text) {
    if (text.trim().isEmpty) return;

    final message = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      senderId: 'user',
      content: text.trim(),
      timestamp: DateTime.now(),
      status: 'sent',
      isFromUser: true,
      senderName: 'You',
    );

    setState(() {
      _messages.add(message);
    });

    _messageController.clear();
    _scrollToBottom();

    // Send to service
    _chatService.sendMessage(message);
  }

  void _sendQuickAction(String action) {
    String message;
    switch (action) {
      case 'book_ride':
        message = 'I need to book a ride';
        break;
      case 'hotel_info':
        message = 'I need information about hotel services';
        break;
      case 'directions':
        message = 'I need directions';
        break;
      case 'emergency':
        message = 'This is an emergency situation';
        break;
      default:
        return;
    }
    _sendMessage(message);
  }

  void _attachFile() {
    // TODO: Implement file attachment
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('File attachment coming soon!'),
        backgroundColor: Colors.amber,
      ),
    );
  }

  void _callConcierge() {
    // TODO: Implement voice call
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Connecting to VIP Concierge...'),
        backgroundColor: Colors.amber,
      ),
    );
  }

  void _videoConcierge() {
    // TODO: Implement video call
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Video chat coming soon!'),
        backgroundColor: Colors.amber,
      ),
    );
  }

  String _formatTime(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else {
      return '${timestamp.day}/${timestamp.month}';
    }
  }

  @override
  void dispose() {
    _typingController.dispose();
    _onlineController.dispose();
    _messageController.dispose();
    _scrollController.dispose();
    _chatService.disconnect();
    super.dispose();
  }
}
