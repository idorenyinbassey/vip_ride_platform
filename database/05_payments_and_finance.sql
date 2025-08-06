-- Payment and Financial Management Tables

-- Exchange Rates for Multi-Currency Support
CREATE TABLE public.exchange_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_currency VARCHAR(3) NOT NULL,
    to_currency VARCHAR(3) NOT NULL,
    rate DECIMAL(15,8) NOT NULL,
    source VARCHAR(50) NOT NULL, -- API source like 'fixer.io', 'currencylayer'
    effective_from TIMESTAMP NOT NULL,
    effective_until TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_active_rate UNIQUE (from_currency, to_currency, is_active)
    DEFERRABLE INITIALLY DEFERRED
);

-- Main Payments Table
CREATE TABLE public.payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Transaction parties
    payer_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    payee_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    
    -- Related entities
    ride_id UUID REFERENCES public.rides(id) ON DELETE SET NULL,
    hotel_booking_id UUID REFERENCES public.hotel_bookings(id) ON DELETE SET NULL,
    vehicle_lease_id UUID REFERENCES public.vehicle_leases(id) ON DELETE SET NULL,
    driver_subscription_id UUID, -- Will reference driver subscriptions
    
    -- Payment details
    payment_type VARCHAR(30) NOT NULL, -- ride_fare, hotel_booking, vehicle_lease, subscription, refund, commission
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'NGN',
    exchange_rate DECIMAL(15,8) DEFAULT 1.0,
    amount_in_base_currency DECIMAL(12,2), -- Converted to platform base currency
    
    -- Fee breakdown
    platform_fee DECIMAL(10,2) DEFAULT 0.00,
    payment_processor_fee DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    tip_amount DECIMAL(10,2) DEFAULT 0.00,
    net_amount DECIMAL(12,2) NOT NULL, -- Amount after all fees
    
    -- Payment processing
    payment_method VARCHAR(30) NOT NULL, -- card, bank_transfer, wallet, cash, crypto
    payment_processor VARCHAR(50), -- stripe, paystack, flutterwave, interswitch
    gateway_transaction_id VARCHAR(255),
    gateway_reference VARCHAR(255),
    merchant_reference VARCHAR(100),
    
    -- Payment status and timing
    status payment_status NOT NULL DEFAULT 'pending',
    initiated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    authorized_at TIMESTAMP,
    captured_at TIMESTAMP,
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,
    
    -- Settlement information
    settlement_date DATE,
    settlement_reference VARCHAR(100),
    settlement_amount DECIMAL(12,2),
    settlement_currency VARCHAR(3),
    
    -- Failure and dispute information
    failure_reason VARCHAR(255),
    failure_code VARCHAR(50),
    dispute_id VARCHAR(100),
    dispute_reason VARCHAR(255),
    dispute_status VARCHAR(20), -- open, under_review, won, lost, accepted
    
    -- Refund information
    refund_reference VARCHAR(100),
    refunded_amount DECIMAL(12,2) DEFAULT 0.00,
    refund_reason VARCHAR(255),
    
    -- Risk and compliance
    risk_score DECIMAL(3,2),
    fraud_check_status VARCHAR(20), -- passed, failed, pending, manual_review
    compliance_status VARCHAR(20), -- compliant, flagged, under_review
    
    -- Metadata
    payment_metadata JSONB DEFAULT '{}',
    gateway_response JSONB DEFAULT '{}',
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Driver Subscriptions
CREATE TABLE public.driver_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id UUID NOT NULL REFERENCES public.drivers(id) ON DELETE CASCADE,
    
    -- Subscription details
    tier subscription_tier NOT NULL DEFAULT 'basic',
    monthly_fee DECIMAL(8,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    
    -- Benefits and limits
    max_daily_rides INTEGER,
    priority_dispatch BOOLEAN DEFAULT FALSE,
    premium_vehicle_access BOOLEAN DEFAULT FALSE,
    vip_customer_access BOOLEAN DEFAULT FALSE,
    reduced_commission_rate DECIMAL(5,2), -- If applicable
    free_background_checks INTEGER DEFAULT 0,
    training_modules_included TEXT[] DEFAULT '{}',
    
    -- Subscription lifecycle
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, cancelled, expired, pending
    started_at TIMESTAMP NOT NULL,
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    next_billing_date DATE NOT NULL,
    
    -- Cancellation
    cancelled_at TIMESTAMP,
    cancellation_reason VARCHAR(100),
    end_date TIMESTAMP, -- When subscription actually ends (may be future date)
    
    -- Payment tracking
    last_payment_date TIMESTAMP,
    next_payment_amount DECIMAL(8,2),
    failed_payment_attempts INTEGER DEFAULT 0,
    
    -- Upgrade/downgrade tracking
    previous_tier subscription_tier,
    tier_changed_at TIMESTAMP,
    tier_change_reason VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_active_subscription UNIQUE (driver_id, status)
    DEFERRABLE INITIALLY DEFERRED
);

-- Add foreign key reference from payments to driver subscriptions
ALTER TABLE public.payments ADD CONSTRAINT fk_payments_driver_subscription
    FOREIGN KEY (driver_subscription_id) REFERENCES public.driver_subscriptions(id) ON DELETE SET NULL;

-- Commission Tracking
CREATE TABLE public.commission_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Commission source
    ride_id UUID REFERENCES public.rides(id) ON DELETE CASCADE,
    hotel_booking_id UUID REFERENCES public.hotel_bookings(id) ON DELETE CASCADE,
    
    -- Commission parties
    fleet_company_id UUID REFERENCES public.fleet_companies(id) ON DELETE SET NULL,
    driver_id UUID REFERENCES public.drivers(id) ON DELETE SET NULL,
    hotel_partner_id UUID REFERENCES public.hotel_partners(id) ON DELETE SET NULL,
    
    -- Commission calculation
    base_amount DECIMAL(12,2) NOT NULL, -- Amount commission is calculated on
    commission_rate DECIMAL(5,2) NOT NULL, -- Percentage rate
    commission_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    
    -- Commission type and tier
    commission_type VARCHAR(30) NOT NULL, -- ride_commission, hotel_commission, bonus, penalty
    customer_tier user_tier NOT NULL,
    
    -- Timing
    earned_date DATE NOT NULL,
    payment_period_start DATE NOT NULL,
    payment_period_end DATE NOT NULL,
    
    -- Payout information
    payout_status VARCHAR(20) DEFAULT 'pending', -- pending, paid, withheld, disputed
    payout_date DATE,
    payout_reference VARCHAR(100),
    payout_amount DECIMAL(10,2), -- May differ from commission_amount due to adjustments
    
    -- Adjustments
    adjustment_amount DECIMAL(10,2) DEFAULT 0.00,
    adjustment_reason VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Lease Payments (for vehicle leasing)
CREATE TABLE public.lease_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lease_id UUID NOT NULL REFERENCES public.vehicle_leases(id) ON DELETE CASCADE,
    
    -- Payment period
    payment_period_start DATE NOT NULL,
    payment_period_end DATE NOT NULL,
    payment_type VARCHAR(20) NOT NULL, -- fixed_rent, revenue_share, excess_mileage, penalty
    
    -- Payment calculation
    base_amount DECIMAL(10,2) NOT NULL,
    revenue_share_percentage DECIMAL(5,2),
    total_revenue_period DECIMAL(12,2), -- Total revenue for revenue share calculation
    calculated_amount DECIMAL(10,2) NOT NULL,
    
    -- Adjustments
    mileage_adjustment DECIMAL(8,2) DEFAULT 0.00,
    damage_deduction DECIMAL(8,2) DEFAULT 0.00,
    bonus_amount DECIMAL(8,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL,
    
    -- Payment details
    currency VARCHAR(3) DEFAULT 'NGN',
    due_date DATE NOT NULL,
    payment_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, overdue, waived, disputed
    
    -- Payment method
    payment_method VARCHAR(30),
    payment_reference VARCHAR(100),
    
    -- Late payment
    days_overdue INTEGER DEFAULT 0,
    late_fee_amount DECIMAL(8,2) DEFAULT 0.00,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_lease_payment_period UNIQUE (lease_id, payment_period_start, payment_period_end, payment_type)
);

-- Wallet/Account Balances
CREATE TABLE public.user_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Balance information
    currency VARCHAR(3) NOT NULL DEFAULT 'NGN',
    available_balance DECIMAL(12,2) DEFAULT 0.00,
    pending_balance DECIMAL(12,2) DEFAULT 0.00, -- Funds on hold
    total_balance DECIMAL(12,2) GENERATED ALWAYS AS (available_balance + pending_balance) STORED,
    
    -- Limits
    daily_spend_limit DECIMAL(10,2),
    monthly_spend_limit DECIMAL(10,2),
    minimum_balance DECIMAL(8,2) DEFAULT 0.00,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_frozen BOOLEAN DEFAULT FALSE,
    freeze_reason VARCHAR(100),
    
    -- Tracking
    last_transaction_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_user_currency_wallet UNIQUE (user_id, currency)
);

-- Wallet Transactions
CREATE TABLE public.wallet_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES public.user_wallets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Transaction details
    transaction_type VARCHAR(30) NOT NULL, -- credit, debit, hold, release, refund
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    
    -- Related entities
    payment_id UUID REFERENCES public.payments(id) ON DELETE SET NULL,
    ride_id UUID REFERENCES public.rides(id) ON DELETE SET NULL,
    
    -- Balance tracking
    balance_before DECIMAL(12,2) NOT NULL,
    balance_after DECIMAL(12,2) NOT NULL,
    
    -- Transaction metadata
    description TEXT NOT NULL,
    reference VARCHAR(100),
    external_reference VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'completed', -- pending, completed, failed, reversed
    processed_at TIMESTAMP DEFAULT NOW(),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for payment tables
CREATE INDEX idx_payments_payer_id ON public.payments(payer_id);
CREATE INDEX idx_payments_payee_id ON public.payments(payee_id);
CREATE INDEX idx_payments_ride_id ON public.payments(ride_id);
CREATE INDEX idx_payments_hotel_booking_id ON public.payments(hotel_booking_id);
CREATE INDEX idx_payments_vehicle_lease_id ON public.payments(vehicle_lease_id);
CREATE INDEX idx_payments_payment_type ON public.payments(payment_type);
CREATE INDEX idx_payments_status ON public.payments(status);
CREATE INDEX idx_payments_currency ON public.payments(currency);
CREATE INDEX idx_payments_payment_method ON public.payments(payment_method);
CREATE INDEX idx_payments_gateway_transaction_id ON public.payments(gateway_transaction_id);
CREATE INDEX idx_payments_initiated_at ON public.payments(initiated_at DESC);
CREATE INDEX idx_payments_completed_at ON public.payments(completed_at DESC);

CREATE INDEX idx_driver_subscriptions_driver_id ON public.driver_subscriptions(driver_id);
CREATE INDEX idx_driver_subscriptions_tier ON public.driver_subscriptions(tier);
CREATE INDEX idx_driver_subscriptions_status ON public.driver_subscriptions(status);
CREATE INDEX idx_driver_subscriptions_next_billing_date ON public.driver_subscriptions(next_billing_date);
CREATE INDEX idx_driver_subscriptions_end_date ON public.driver_subscriptions(end_date);

CREATE INDEX idx_commission_records_ride_id ON public.commission_records(ride_id);
CREATE INDEX idx_commission_records_hotel_booking_id ON public.commission_records(hotel_booking_id);
CREATE INDEX idx_commission_records_fleet_company_id ON public.commission_records(fleet_company_id);
CREATE INDEX idx_commission_records_driver_id ON public.commission_records(driver_id);
CREATE INDEX idx_commission_records_earned_date ON public.commission_records(earned_date DESC);
CREATE INDEX idx_commission_records_payout_status ON public.commission_records(payout_status);

CREATE INDEX idx_lease_payments_lease_id ON public.lease_payments(lease_id);
CREATE INDEX idx_lease_payments_payment_period ON public.lease_payments(payment_period_start, payment_period_end);
CREATE INDEX idx_lease_payments_status ON public.lease_payments(status);
CREATE INDEX idx_lease_payments_payment_date ON public.lease_payments(payment_date);
CREATE INDEX idx_lease_payments_due_date ON public.lease_payments(due_date);

CREATE INDEX idx_user_wallets_user_id ON public.user_wallets(user_id);
CREATE INDEX idx_user_wallets_currency ON public.user_wallets(currency);
CREATE INDEX idx_user_wallets_active ON public.user_wallets(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_wallet_transactions_wallet_id ON public.wallet_transactions(wallet_id);
CREATE INDEX idx_wallet_transactions_user_id ON public.wallet_transactions(user_id);
CREATE INDEX idx_wallet_transactions_payment_id ON public.wallet_transactions(payment_id);
CREATE INDEX idx_wallet_transactions_processed_at ON public.wallet_transactions(processed_at DESC);

CREATE INDEX idx_exchange_rates_currencies ON public.exchange_rates(from_currency, to_currency);
CREATE INDEX idx_exchange_rates_active ON public.exchange_rates(is_active) WHERE is_active = TRUE;

-- Row Level Security
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.driver_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallet_transactions ENABLE ROW LEVEL SECURITY;

-- Audit triggers
CREATE TRIGGER audit_payments_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.payments
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_driver_subscriptions_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.driver_subscriptions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_wallet_transactions_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.wallet_transactions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Financial calculations and utilities
CREATE OR REPLACE FUNCTION calculate_commission(
    base_amount DECIMAL(12,2),
    tier user_tier,
    service_type VARCHAR(20)
) RETURNS DECIMAL(5,2) AS $$
BEGIN
    RETURN CASE 
        WHEN tier = 'normal' AND service_type = 'ride' THEN 15.00
        WHEN tier = 'normal' AND service_type = 'hotel' THEN 10.00
        WHEN tier = 'premium' AND service_type = 'ride' THEN 20.00
        WHEN tier = 'premium' AND service_type = 'hotel' THEN 15.00
        WHEN tier = 'vip' AND service_type = 'ride' THEN 25.00
        WHEN tier = 'vip' AND service_type = 'hotel' THEN 20.00
        ELSE 15.00
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get current exchange rate
CREATE OR REPLACE FUNCTION get_exchange_rate(
    from_curr VARCHAR(3),
    to_curr VARCHAR(3)
) RETURNS DECIMAL(15,8) AS $$
DECLARE
    rate DECIMAL(15,8);
BEGIN
    IF from_curr = to_curr THEN
        RETURN 1.0;
    END IF;
    
    SELECT er.rate INTO rate
    FROM public.exchange_rates er
    WHERE er.from_currency = from_curr 
      AND er.to_currency = to_curr 
      AND er.is_active = TRUE
      AND er.effective_from <= NOW()
      AND (er.effective_until IS NULL OR er.effective_until > NOW())
    ORDER BY er.effective_from DESC
    LIMIT 1;
    
    RETURN COALESCE(rate, 1.0);
END;
$$ LANGUAGE plpgsql STABLE;

-- Comments
COMMENT ON TABLE public.payments IS 'Main payment processing and transaction records';
COMMENT ON TABLE public.driver_subscriptions IS 'Driver subscription management and billing';
COMMENT ON TABLE public.commission_records IS 'Commission tracking for all parties';
COMMENT ON TABLE public.lease_payments IS 'Vehicle lease payment tracking and calculation';
COMMENT ON TABLE public.user_wallets IS 'User wallet and balance management';
COMMENT ON TABLE public.wallet_transactions IS 'Wallet transaction history and tracking';
COMMENT ON TABLE public.exchange_rates IS 'Multi-currency exchange rate management';
