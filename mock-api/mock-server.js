const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 8000;
const JWT_SECRET = 'mock-jwt-secret-key';

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Mock Database
let users = [
    {
        id: 'user-1',
        email: 'admin@email.com',
        password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // password
        tier: 'regular',
        tier_display: 'Regular',
        first_name: 'Admin',
        last_name: 'User',
        phone: '+1234567890',
        is_active: true,
        premium_cards: [],
        mfa_enabled: false,
        user_type: 'client'
    },
    {
        id: 'user-2',
        email: 'vip@email.com',
        password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // password
        tier: 'vip',
        tier_display: 'VIP',
        first_name: 'VIP',
        last_name: 'User',
        phone: '+1234567891',
        is_active: true,
        premium_cards: [
            {
                id: 'card-1',
                card_number: 'VIP1-2345-6789-0123',
                tier: 'vip',
                status: 'active',
                expires_at: '2025-12-31T23:59:59Z'
            }
        ],
        mfa_enabled: false
    },
    {
        id: 'user-3',
        email: 'premium@email.com',
        password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // password
        tier: 'vip_premium',
        tier_display: 'VIP Premium',
        first_name: 'Premium',
        last_name: 'User',
        phone: '+1234567892',
        is_active: true,
        premium_cards: [
            {
                id: 'card-2',
                card_number: 'VIPR-3456-7890-1234',
                tier: 'vip_premium',
                status: 'active',
                expires_at: '2025-12-31T23:59:59Z'
            }
        ],
        mfa_enabled: false,
        user_type: 'client'
    }
];

let sessions = [];
let trustedDevices = [];
let rides = [];
let digitalCards = [
    {
        id: 'card-test-1',
        card_number: 'TEST-1234-5678-9012',
        verification_code: 'TEST123',
        tier: 'vip',
        status: 'inactive',
        expires_at: '2025-12-31T23:59:59Z',
        created_at: '2025-09-12T10:00:00Z'
    },
    {
        id: 'card-test-2',
        card_number: 'PREM-2345-6789-0123',
        verification_code: 'PREM456',
        tier: 'vip_premium',
        status: 'inactive',
        expires_at: '2025-12-31T23:59:59Z',
        created_at: '2025-09-12T10:00:00Z'
    }
];

// Utility functions
const generateToken = (user) => {
    return jwt.sign(
        { user_id: user.id, email: user.email, tier: user.tier },
        JWT_SECRET,
        { expiresIn: '24h' }
    );
};

const verifyToken = (req, res, next) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'No token provided' });
    }

    const token = authHeader.substring(7);
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = users.find(u => u.id === decoded.user_id);
        if (!req.user) {
            return res.status(401).json({ error: 'Invalid token' });
        }
        next();
    } catch (error) {
        return res.status(401).json({ error: 'Invalid token' });
    }
};

// Auth Endpoints
app.post('/api/v1/accounts/login/', async (req, res) => {
    const { email, password, device_name, device_type, device_os } = req.body;

    const user = users.find(u => u.email === email);
    if (!user) {
        return res.status(400).json({ error: 'Invalid credentials' });
    }

    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
        return res.status(400).json({ error: 'Invalid credentials' });
    }

    // Create session
    const sessionId = uuidv4();
    const session = {
        id: sessionId,
        user_id: user.id,
        device_name: device_name || 'Unknown Device',
        device_type: device_type || 'mobile',
        device_os: device_os || 'unknown',
        created_at: new Date().toISOString(),
        is_active: true
    };
    sessions.push(session);

    // Register trusted device
    const deviceId = uuidv4();
    const trustedDevice = {
        id: deviceId,
        user_id: user.id,
        device_name: device_name || 'Unknown Device',
        device_type: device_type || 'mobile',
        device_os: device_os || 'unknown',
        device_fingerprint: `${device_name}-${device_type}-${Date.now()}`,
        is_trusted: true,
        created_at: new Date().toISOString()
    };
    trustedDevices.push(trustedDevice);

    const token = generateToken(user);

    res.json({
        access_token: token,
        token_type: 'Bearer',
        expires_in: 86400,
        user: {
            id: user.id,
            email: user.email,
            first_name: user.first_name,
            last_name: user.last_name,
            tier: user.tier,
            tier_display: user.tier_display,
            phone: user.phone,
            is_active: user.is_active,
            user_type: user.user_type
        },
        session_id: sessionId,
        device_id: deviceId
    });
});

app.post('/api/v1/accounts/register/', async (req, res) => {
    const { email, password, first_name, last_name, phone } = req.body;

    if (users.find(u => u.email === email)) {
        return res.status(400).json({ error: 'Email already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = {
        id: uuidv4(),
        email,
        password: hashedPassword,
        first_name,
        last_name,
        phone,
        tier: 'regular',
        tier_display: 'Regular',
        is_active: true,
        premium_cards: [],
        mfa_enabled: false,
        user_type: 'client'
    };

    users.push(newUser);

    const token = generateToken(newUser);

    res.status(201).json({
        access_token: token,
        user: {
            id: newUser.id,
            email: newUser.email,
            first_name: newUser.first_name,
            last_name: newUser.last_name,
            tier: newUser.tier,
            tier_display: newUser.tier_display,
            phone: newUser.phone,
            is_active: newUser.is_active,
            user_type: newUser.user_type
        }
    });
});

// Profile Endpoints
// Device Registration Endpoint
app.post('/api/v1/accounts/devices/', verifyToken, (req, res) => {
    const { action, device_name, device_type, device_os } = req.body;
    if (action !== 'register') {
        return res.status(400).json({ error: 'Invalid action' });
    }
    const deviceId = uuidv4();
    const trustedDevice = {
        id: deviceId,
        user_id: req.user.id,
        device_name: device_name || 'Unknown Device',
        device_type: device_type || 'mobile',
        device_os: device_os || 'unknown',
        device_fingerprint: `${device_name}-${device_type}-${Date.now()}`,
        is_trusted: true,
        created_at: new Date().toISOString()
    };
    trustedDevices.push(trustedDevice);
    res.status(201).json({
        message: 'Device registered',
        device_id: deviceId
    });
});
app.get('/api/v1/accounts/profile/', verifyToken, (req, res) => {
    res.json({
        id: req.user.id,
        email: req.user.email,
        first_name: req.user.first_name,
        last_name: req.user.last_name,
        tier: req.user.tier,
        tier_display: req.user.tier_display,
        phone: req.user.phone,
        is_active: req.user.is_active,
        premium_cards: req.user.premium_cards
    });
});

// Flutter-specific Tier Status Endpoint
app.get('/api/v1/accounts/flutter/tier-status/', verifyToken, (req, res) => {
    const userSessions = sessions.filter(s => s.user_id === req.user.id && s.is_active);
    const userDevices = trustedDevices.filter(d => d.user_id === req.user.id);

    res.json({
        user: {
            id: req.user.id,
            tier: req.user.tier,
            tier_display: req.user.tier_display,
            email: req.user.email,
            first_name: req.user.first_name,
            last_name: req.user.last_name
        },
        tier_info: {
            benefits: req.user.tier === 'vip_premium' ? [
                'Priority ride matching',
                'Luxury vehicle access',
                'Hotel partnerships',
                'Encrypted GPS tracking',
                'Concierge support',
                'SOS alerts'
            ] : req.user.tier === 'vip' ? [
                'Priority ride matching',
                'Premium vehicles',
                'Enhanced support'
            ] : [
                'Standard ride booking',
                'Basic support'
            ],
            features: req.user.tier === 'vip_premium' ? [
                'hotel_booking',
                'encrypted_tracking',
                'vip_support',
                'luxury_vehicles',
                'priority_matching'
            ] : req.user.tier === 'vip' ? [
                'premium_vehicles',
                'priority_matching',
                'enhanced_support'
            ] : [
                'standard_booking'
            ]
        },
        premium_cards: req.user.premium_cards,
        device_status: {
            device_id: userDevices[0]?.id || null,
            is_registered: userDevices.length > 0,
            device_count: userDevices.length
        },
        session_status: {
            session_id: userSessions[0]?.id || null,
            is_active: userSessions.length > 0,
            session_count: userSessions.length
        }
    });
});

// Card Activation Endpoints
app.post('/api/v1/accounts/flutter/activate-card/', verifyToken, (req, res) => {
    const { card_number, verification_code, device_name } = req.body;

    const card = digitalCards.find(c =>
        c.card_number === card_number &&
        c.verification_code === verification_code &&
        c.status === 'inactive'
    );

    if (!card) {
        return res.status(400).json({
            success: false,
            error: 'Invalid card number or verification code',
            error_code: 'INVALID_CARD'
        });
    }

    // Activate card and upgrade user tier
    card.status = 'active';
    card.activated_at = new Date().toISOString();
    card.activated_by = req.user.id;

    // Upgrade user tier
    const oldTier = req.user.tier;
    if (card.tier === 'vip' && req.user.tier === 'regular') {
        req.user.tier = 'vip';
        req.user.tier_display = 'VIP';
    } else if (card.tier === 'vip_premium') {
        req.user.tier = 'vip_premium';
        req.user.tier_display = 'VIP Premium';
    }

    // Add card to user's premium cards
    req.user.premium_cards.push({
        id: card.id,
        card_number: card.card_number,
        tier: card.tier,
        status: card.status,
        expires_at: card.expires_at
    });

    res.json({
        success: true,
        message: `Card activated successfully! Upgraded from ${oldTier} to ${req.user.tier}`,
        card: {
            id: card.id,
            card_number: card.card_number,
            tier: card.tier,
            status: card.status,
            expires_at: card.expires_at
        },
        user: {
            id: req.user.id,
            tier: req.user.tier,
            tier_display: req.user.tier_display
        },
        next_steps: {
            requires_mfa_setup: req.user.tier === 'vip_premium' && !req.user.mfa_enabled,
            should_refresh_session: true,
            redirect_to: req.user.tier === 'vip_premium' ? 'vip_premium_dashboard' : 'vip_dashboard'
        }
    });
});

// Ride Endpoints
app.post('/api/v1/rides/workflow/request/', verifyToken, (req, res) => {
    const { pickup_location, destination, vehicle_type } = req.body;

    const ride = {
        id: uuidv4(),
        user_id: req.user.id,
        pickup_location,
        destination,
        vehicle_type: vehicle_type || 'standard',
        status: 'requested',
        created_at: new Date().toISOString(),
        estimated_fare: Math.floor(Math.random() * 5000) + 1000, // Random fare 1000-6000
        estimated_duration: Math.floor(Math.random() * 30) + 10, // 10-40 minutes
        priority: req.user.tier !== 'regular' ? 'high' : 'normal'
    };

    rides.push(ride);

    res.json({
        ride_id: ride.id,
        status: ride.status,
        estimated_fare: ride.estimated_fare,
        estimated_duration: ride.estimated_duration,
        priority: ride.priority,
        message: 'Ride request submitted successfully'
    });
});

app.get('/api/v1/rides/workflow/active/', verifyToken, (req, res) => {
    const userRides = rides.filter(r =>
        r.user_id === req.user.id &&
        ['requested', 'accepted', 'in_progress'].includes(r.status)
    );

    res.json({
        rides: userRides,
        count: userRides.length
    });
});

// Hotel Endpoints (for VIP Premium users)
app.get('/api/v1/hotel-partnerships/hotels/nearby/', verifyToken, (req, res) => {
    if (req.user.tier !== 'vip_premium') {
        return res.status(403).json({ error: 'VIP Premium access required' });
    }

    const mockHotels = [
        {
            id: 'hotel-1',
            name: 'Grand Luxury Hotel',
            address: '123 VIP Street, Premium City',
            rating: 4.8,
            distance: 2.5,
            amenities: ['spa', 'pool', 'restaurant', 'vip_lounge'],
            vip_perks: ['priority_check_in', 'room_upgrade', 'free_breakfast']
        },
        {
            id: 'hotel-2',
            name: 'Executive Plaza',
            address: '456 Business Ave, Premium City',
            rating: 4.6,
            distance: 3.2,
            amenities: ['gym', 'restaurant', 'meeting_rooms'],
            vip_perks: ['late_checkout', 'welcome_drink']
        }
    ];

    res.json({
        hotels: mockHotels,
        count: mockHotels.length
    });
});

// MFA Endpoints
app.post('/api/v1/accounts/auth/mfa/setup/', verifyToken, (req, res) => {
    // Mock MFA setup
    const secret = 'MOCK_MFA_SECRET_123456';
    const qr_code = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';

    res.json({
        secret,
        qr_code,
        backup_codes: ['123456', '789012', '345678', '901234', '567890']
    });
});

app.post('/api/v1/accounts/auth/mfa/verify/', verifyToken, (req, res) => {
    const { token } = req.body;

    // Mock verification - accept any 6-digit code
    if (token && token.length === 6 && /^\d+$/.test(token)) {
        req.user.mfa_enabled = true;
        res.json({
            success: true,
            message: 'MFA enabled successfully'
        });
    } else {
        res.status(400).json({
            success: false,
            error: 'Invalid MFA token'
        });
    }
});

// Health Check
app.get('/health/', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        mock: true
    });
});

// Admin data endpoints (for testing)
app.get('/mock/admin/sessions', (req, res) => {
    res.json({
        sessions: sessions.map(s => ({
            ...s,
            user_email: users.find(u => u.id === s.user_id)?.email
        }))
    });
});

app.get('/mock/admin/devices', (req, res) => {
    res.json({
        devices: trustedDevices.map(d => ({
            ...d,
            user_email: users.find(u => u.id === d.user_id)?.email
        }))
    });
});

app.get('/mock/admin/users', (req, res) => {
    res.json({
        users: users.map(u => ({
            id: u.id,
            email: u.email,
            tier: u.tier,
            tier_display: u.tier_display,
            premium_cards_count: u.premium_cards.length,
            mfa_enabled: u.mfa_enabled
        }))
    });
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

app.listen(PORT, () => {
    console.log(`🚀 VIP Ride Mock API Server running on http://localhost:${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health/`);
    console.log(`👤 Test users:`);
    console.log(`   Regular: admin@email.com / password`);
    console.log(`   VIP: vip@email.com / password`);
    console.log(`   VIP Premium: premium@email.com / password`);
    console.log(`🃏 Test cards:`);
    console.log(`   VIP: TEST-1234-5678-9012 / TEST123`);
    console.log(`   VIP Premium: PREM-2345-6789-0123 / PREM456`);
    console.log(`📋 Admin endpoints:`);
    console.log(`   Sessions: http://localhost:${PORT}/mock/admin/sessions`);
    console.log(`   Devices: http://localhost:${PORT}/mock/admin/devices`);
    console.log(`   Users: http://localhost:${PORT}/mock/admin/users`);
});