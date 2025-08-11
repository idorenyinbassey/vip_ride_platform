# payments/payment_settings.py
"""
Payment system configuration settings
"""

from django.conf import settings
from decimal import Decimal

# Default commission rates by user tier
DEFAULT_COMMISSION_RATES = {
    'normal': Decimal('15.0'),    # 15%
    'premium': Decimal('22.5'),   # 22.5%
    'vip': Decimal('27.5'),       # 27.5%
}

# Payment gateway configurations
PAYSTACK_CONFIG = {
    'public_key': getattr(settings, 'PAYSTACK_PUBLIC_KEY', ''),
    'secret_key': getattr(settings, 'PAYSTACK_SECRET_KEY', ''),
    'webhook_secret': getattr(settings, 'PAYSTACK_WEBHOOK_SECRET', ''),
    'base_url': 'https://api.paystack.co',
    'test_mode': getattr(settings, 'PAYSTACK_TEST_MODE', True),
    'supported_currencies': ['NGN', 'USD', 'GHS', 'ZAR'],
    'default_currency': 'NGN'
}

FLUTTERWAVE_CONFIG = {
    'public_key': getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', ''),
    'secret_key': getattr(settings, 'FLUTTERWAVE_SECRET_KEY', ''),
    'encryption_key': getattr(settings, 'FLUTTERWAVE_ENCRYPTION_KEY', ''),
    'webhook_secret': getattr(settings, 'FLUTTERWAVE_WEBHOOK_SECRET', ''),
    'base_url': 'https://api.flutterwave.com/v3',
    'test_mode': getattr(settings, 'FLUTTERWAVE_TEST_MODE', True),
    'supported_currencies': ['NGN', 'USD', 'GHS', 'KES', 'UGX', 'ZAR'],
    'default_currency': 'NGN'
}

STRIPE_CONFIG = {
    'publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
    'secret_key': getattr(settings, 'STRIPE_SECRET_KEY', ''),
    'webhook_secret': getattr(settings, 'STRIPE_WEBHOOK_SECRET', ''),
    'base_url': 'https://api.stripe.com/v1',
    'test_mode': getattr(settings, 'STRIPE_TEST_MODE', True),
    'supported_currencies': ['USD', 'EUR', 'GBP', 'NGN', 'GHS', 'ZAR'],
    'default_currency': 'USD'
}

# Exchange rate API configurations
EXCHANGE_RATE_CONFIG = {
    'fixer_api_key': getattr(settings, 'FIXER_API_KEY', ''),
    'exchangerate_api_key': getattr(settings, 'EXCHANGERATE_API_KEY', ''),
    'update_interval_hours': getattr(settings, 'EXCHANGE_RATE_UPDATE_INTERVAL', 6),
    'base_currency': 'USD',
    'cache_timeout': 3600,  # 1 hour
}

# Payment processing settings
PAYMENT_CONFIG = {
    'default_gateway': getattr(settings, 'DEFAULT_PAYMENT_GATEWAY', 'paystack'),
    'gateway_priority': getattr(settings, 'PAYMENT_GATEWAY_PRIORITY', [
        'paystack', 'flutterwave', 'stripe'
    ]),
    'max_retry_attempts': getattr(settings, 'PAYMENT_MAX_RETRY_ATTEMPTS', 3),
    'retry_delay_minutes': getattr(settings, 'PAYMENT_RETRY_DELAY_MINUTES', 5),
    'auto_payout_threshold': Decimal(
        str(getattr(settings, 'AUTO_PAYOUT_THRESHOLD', '100.00'))
    ),
    'min_payout_amount': Decimal(
        str(getattr(settings, 'MIN_PAYOUT_AMOUNT', '10.00'))
    ),
    'payout_schedule': getattr(settings, 'PAYOUT_SCHEDULE', 'weekly'),  # daily, weekly, monthly
    'commission_rates': getattr(settings, 'COMMISSION_RATES', DEFAULT_COMMISSION_RATES),
}

# Security settings
SECURITY_CONFIG = {
    'encryption_key': getattr(settings, 'PAYMENT_ENCRYPTION_KEY', ''),
    'encrypt_payment_data': getattr(settings, 'ENCRYPT_PAYMENT_DATA', True),
    'pci_compliance_mode': getattr(settings, 'PCI_COMPLIANCE_MODE', True),
    'audit_all_transactions': getattr(settings, 'AUDIT_ALL_TRANSACTIONS', True),
    'token_expiry_minutes': getattr(settings, 'PAYMENT_TOKEN_EXPIRY_MINUTES', 30),
    'webhook_timeout_seconds': getattr(settings, 'WEBHOOK_TIMEOUT_SECONDS', 30),
}

# Notification settings
NOTIFICATION_CONFIG = {
    'send_payment_confirmations': getattr(settings, 'SEND_PAYMENT_CONFIRMATIONS', True),
    'send_payout_notifications': getattr(settings, 'SEND_PAYOUT_NOTIFICATIONS', True),
    'send_dispute_alerts': getattr(settings, 'SEND_DISPUTE_ALERTS', True),
    'admin_notification_emails': getattr(settings, 'PAYMENT_ADMIN_EMAILS', []),
    'notification_templates': {
        'payment_success': 'payments/email/payment_success.html',
        'payment_failed': 'payments/email/payment_failed.html',
        'payout_processed': 'payments/email/payout_processed.html',
        'dispute_created': 'payments/email/dispute_created.html',
    }
}

# Reporting and analytics settings
REPORTING_CONFIG = {
    'generate_daily_reports': getattr(settings, 'GENERATE_DAILY_PAYMENT_REPORTS', True),
    'generate_weekly_reports': getattr(settings, 'GENERATE_WEEKLY_PAYMENT_REPORTS', True),
    'report_recipients': getattr(settings, 'PAYMENT_REPORT_RECIPIENTS', []),
    'dashboard_cache_timeout': getattr(settings, 'PAYMENT_DASHBOARD_CACHE_TIMEOUT', 300),
    'enable_real_time_metrics': getattr(settings, 'ENABLE_REAL_TIME_PAYMENT_METRICS', False),
}

# Development and testing settings
DEVELOPMENT_CONFIG = {
    'use_sandbox_gateways': getattr(settings, 'USE_SANDBOX_PAYMENT_GATEWAYS', settings.DEBUG),
    'log_payment_requests': getattr(settings, 'LOG_PAYMENT_REQUESTS', settings.DEBUG),
    'mock_external_apis': getattr(settings, 'MOCK_PAYMENT_APIS', False),
    'test_card_numbers': {
        'visa_success': '4084084084084081',
        'visa_declined': '4084084084084099',
        'mastercard_success': '5060990580000217',
        'verve_success': '5061020000000000003',
    }
}

# Compliance and regulatory settings
COMPLIANCE_CONFIG = {
    'ndpr_compliance': getattr(settings, 'NDPR_COMPLIANCE_ENABLED', True),
    'data_retention_days': getattr(settings, 'PAYMENT_DATA_RETENTION_DAYS', 2555),  # 7 years
    'anonymize_old_data': getattr(settings, 'ANONYMIZE_OLD_PAYMENT_DATA', True),
    'gdpr_compliance': getattr(settings, 'GDPR_COMPLIANCE_ENABLED', False),
    'pci_dss_level': getattr(settings, 'PCI_DSS_COMPLIANCE_LEVEL', 4),
    'audit_log_retention_days': getattr(settings, 'AUDIT_LOG_RETENTION_DAYS', 2555),
}

# Feature flags
FEATURE_FLAGS = {
    'enable_multi_currency': getattr(settings, 'ENABLE_MULTI_CURRENCY_PAYMENTS', True),
    'enable_driver_payouts': getattr(settings, 'ENABLE_DRIVER_PAYOUTS', True),
    'enable_dispute_management': getattr(settings, 'ENABLE_DISPUTE_MANAGEMENT', True),
    'enable_subscription_billing': getattr(settings, 'ENABLE_SUBSCRIPTION_BILLING', False),
    'enable_payment_analytics': getattr(settings, 'ENABLE_PAYMENT_ANALYTICS', True),
    'enable_fraud_detection': getattr(settings, 'ENABLE_FRAUD_DETECTION', False),
}

# Performance settings
PERFORMANCE_CONFIG = {
    'use_redis_cache': getattr(settings, 'USE_REDIS_FOR_PAYMENTS', True),
    'cache_exchange_rates': getattr(settings, 'CACHE_EXCHANGE_RATES', True),
    'async_webhook_processing': getattr(settings, 'ASYNC_WEBHOOK_PROCESSING', True),
    'batch_payout_processing': getattr(settings, 'BATCH_PAYOUT_PROCESSING', True),
    'max_concurrent_payments': getattr(settings, 'MAX_CONCURRENT_PAYMENTS', 50),
}


def get_gateway_config(gateway_type):
    """Get configuration for a specific gateway"""
    configs = {
        'paystack': PAYSTACK_CONFIG,
        'flutterwave': FLUTTERWAVE_CONFIG,
        'stripe': STRIPE_CONFIG,
    }
    return configs.get(gateway_type, {})


def get_commission_rate(user_tier):
    """Get commission rate for a user tier"""
    rates = PAYMENT_CONFIG['commission_rates']
    return rates.get(user_tier.lower(), rates['normal'])


def is_gateway_enabled(gateway_type):
    """Check if a gateway is properly configured and enabled"""
    config = get_gateway_config(gateway_type)
    if not config:
        return False
    
    required_keys = {
        'paystack': ['public_key', 'secret_key'],
        'flutterwave': ['public_key', 'secret_key', 'encryption_key'],
        'stripe': ['publishable_key', 'secret_key'],
    }
    
    required = required_keys.get(gateway_type, [])
    return all(config.get(key) for key in required)


def get_enabled_gateways():
    """Get list of enabled payment gateways"""
    all_gateways = ['paystack', 'flutterwave', 'stripe']
    return [gateway for gateway in all_gateways if is_gateway_enabled(gateway)]


def validate_payment_config():
    """Validate payment system configuration"""
    errors = []
    
    # Check if at least one gateway is enabled
    enabled_gateways = get_enabled_gateways()
    if not enabled_gateways:
        errors.append("No payment gateways are properly configured")
    
    # Check encryption key for PCI compliance
    if SECURITY_CONFIG['pci_compliance_mode'] and not SECURITY_CONFIG['encryption_key']:
        errors.append("Encryption key is required for PCI compliance mode")
    
    # Check commission rates
    for tier, rate in PAYMENT_CONFIG['commission_rates'].items():
        if not (0 <= rate <= 100):
            errors.append(f"Invalid commission rate for {tier}: {rate}%")
    
    return errors
