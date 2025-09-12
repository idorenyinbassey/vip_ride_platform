class ChatMessage {
  final String id;
  final String senderId;
  final String content;
  final DateTime timestamp;
  final String status; // sent, delivered, read
  final List<ChatAttachment> attachments;
  final String? replyToId;
  final bool isSystemMessage;
  final bool isFromUser;
  final String senderName;

  const ChatMessage({
    required this.id,
    required this.senderId,
    required this.content,
    required this.timestamp,
    this.status = 'sent',
    this.attachments = const [],
    this.replyToId,
    this.isSystemMessage = false,
    required this.isFromUser,
    required this.senderName,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    final attachmentsList =
        (json['attachments'] as List?)
            ?.map((attachment) => ChatAttachment.fromJson(attachment))
            .toList() ??
        <ChatAttachment>[];

    return ChatMessage(
      id: json['id'],
      senderId: json['sender_id'],
      content: json['content'],
      timestamp: DateTime.parse(json['timestamp']),
      status: json['status'] ?? 'sent',
      attachments: attachmentsList,
      replyToId: json['reply_to_id'],
      isSystemMessage: json['is_system_message'] ?? false,
      isFromUser: json['is_from_user'] ?? false,
      senderName: json['sender_name'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sender_id': senderId,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'status': status,
      'attachments': attachments.map((a) => a.toJson()).toList(),
      'reply_to_id': replyToId,
      'is_system_message': isSystemMessage,
      'is_from_user': isFromUser,
      'sender_name': senderName,
    };
  }

  ChatMessage copyWith({
    String? id,
    String? senderId,
    String? content,
    DateTime? timestamp,
    String? status,
    List<ChatAttachment>? attachments,
    String? replyToId,
    bool? isSystemMessage,
    bool? isFromUser,
    String? senderName,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      senderId: senderId ?? this.senderId,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      status: status ?? this.status,
      attachments: attachments ?? this.attachments,
      replyToId: replyToId ?? this.replyToId,
      isSystemMessage: isSystemMessage ?? this.isSystemMessage,
      isFromUser: isFromUser ?? this.isFromUser,
      senderName: senderName ?? this.senderName,
    );
  }
}

class ChatAttachment {
  final String id;
  final String name;
  final String type; // image, document, location, voice
  final String url;
  final int? size;
  final Map<String, dynamic>? metadata;

  const ChatAttachment({
    required this.id,
    required this.name,
    required this.type,
    required this.url,
    this.size,
    this.metadata,
  });

  factory ChatAttachment.fromJson(Map<String, dynamic> json) {
    return ChatAttachment(
      id: json['id'],
      name: json['name'],
      type: json['type'],
      url: json['url'],
      size: json['size'],
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'url': url,
      'size': size,
      'metadata': metadata,
    };
  }
}

class ChatRoom {
  final String id;
  final String type; // concierge, support, emergency
  final String name;
  final List<String> participants;
  final ChatMessage? lastMessage;
  final int unreadCount;
  final DateTime createdAt;
  final DateTime? lastActiveAt;
  final bool isActive;
  final Map<String, dynamic>? settings;

  const ChatRoom({
    required this.id,
    required this.type,
    required this.name,
    required this.participants,
    this.lastMessage,
    this.unreadCount = 0,
    required this.createdAt,
    this.lastActiveAt,
    this.isActive = true,
    this.settings,
  });

  factory ChatRoom.fromJson(Map<String, dynamic> json) {
    return ChatRoom(
      id: json['id'],
      type: json['type'],
      name: json['name'],
      participants: List<String>.from(json['participants'] ?? []),
      lastMessage: json['last_message'] != null
          ? ChatMessage.fromJson(json['last_message'])
          : null,
      unreadCount: json['unread_count'] ?? 0,
      createdAt: DateTime.parse(json['created_at']),
      lastActiveAt: json['last_active_at'] != null
          ? DateTime.parse(json['last_active_at'])
          : null,
      isActive: json['is_active'] ?? true,
      settings: json['settings'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'name': name,
      'participants': participants,
      'last_message': lastMessage?.toJson(),
      'unread_count': unreadCount,
      'created_at': createdAt.toIso8601String(),
      'last_active_at': lastActiveAt?.toIso8601String(),
      'is_active': isActive,
      'settings': settings,
    };
  }
}

class ConciergeStatus {
  final bool online;
  final String message;
  final DateTime lastSeen;
  final String agentName;
  final String? agentId;
  final bool isVipAgent;

  const ConciergeStatus({
    required this.online,
    required this.message,
    required this.lastSeen,
    required this.agentName,
    this.agentId,
    this.isVipAgent = false,
  });

  factory ConciergeStatus.fromJson(Map<String, dynamic> json) {
    return ConciergeStatus(
      online: json['online'] ?? false,
      message: json['message'] ?? 'Unavailable',
      lastSeen: DateTime.parse(json['last_seen']),
      agentName: json['agent_name'] ?? 'Concierge',
      agentId: json['agent_id'],
      isVipAgent: json['is_vip_agent'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'online': online,
      'message': message,
      'last_seen': lastSeen.toIso8601String(),
      'agent_name': agentName,
      'agent_id': agentId,
      'is_vip_agent': isVipAgent,
    };
  }
}

class QuickAction {
  final String id;
  final String text;
  final String action;
  final String? icon;
  final bool isVipOnly;
  final Map<String, dynamic>? params;

  const QuickAction({
    required this.id,
    required this.text,
    required this.action,
    this.icon,
    this.isVipOnly = false,
    this.params,
  });

  factory QuickAction.fromJson(Map<String, dynamic> json) {
    return QuickAction(
      id: json['id'],
      text: json['text'],
      action: json['action'],
      icon: json['icon'],
      isVipOnly: json['is_vip_only'] ?? false,
      params: json['params'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'action': action,
      'icon': icon,
      'is_vip_only': isVipOnly,
      'params': params,
    };
  }
}
