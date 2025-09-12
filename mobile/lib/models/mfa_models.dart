class MfaRequirement {
  final bool mfaRequired;
  final List<String> mfaMethods;
  final String? message;
  final String? tempToken;

  MfaRequirement({
    required this.mfaRequired,
    required this.mfaMethods,
    this.message,
    this.tempToken,
  });

  factory MfaRequirement.fromJson(Map<String, dynamic> json) {
    return MfaRequirement(
      mfaRequired:
          json['mfa_required'] == 'True' || json['mfa_required'] == true,
      mfaMethods: List<String>.from(json['mfa_methods'] ?? []),
      message: json['message'],
      tempToken: json['temp_token'],
    );
  }
}

class MfaVerificationRequest {
  final String tempToken;
  final String mfaCode;
  final String mfaMethod;

  MfaVerificationRequest({
    required this.tempToken,
    required this.mfaCode,
    required this.mfaMethod,
  });

  Map<String, dynamic> toJson() {
    return {
      'temp_token': tempToken,
      'mfa_code': mfaCode,
      'mfa_method': mfaMethod,
    };
  }
}

class MfaSetupResponse {
  final String qrCode;
  final String secret;
  final String backupCodes;

  MfaSetupResponse({
    required this.qrCode,
    required this.secret,
    required this.backupCodes,
  });

  factory MfaSetupResponse.fromJson(Map<String, dynamic> json) {
    return MfaSetupResponse(
      qrCode: json['qr_code'] ?? '',
      secret: json['secret'] ?? '',
      backupCodes: json['backup_codes'] ?? '',
    );
  }
}
