# VIP Ride-Hailing Platform - Corrected Architecture

## 📋 User Tier Structure

### **Client Tiers:**
1. **Regular/Normal** (`tier: 'normal'`)
   - Standard rides (15-20% commission)
   - Basic features
   - MFA: Optional
   - App: `RegularClientApp()`

2. **Black-Tier** (`tier: 'premium'` OR `tier: 'vip'`)
   - **Premium** (`tier: 'premium'`):
     - Luxury cars + concierge services (hotel booking)
     - 20-25% commission
     - MFA: Required
   - **VIP** (`tier: 'vip'`):
     - Everything Premium + encrypted GPS + SOS + trusted drivers
     - 25-30% commission  
     - MFA: Required
   - App: `BlackTierClientApp()` (handles both Premium and VIP)

## 🎯 Flutter App Navigation Logic

```dart
if (user.isClient) {
  if (user.isBlackTierClient) { // Premium OR VIP
    return BlackTierClientApp(); // Hotel integration, enhanced features
  } else { // Regular
    return RegularClientApp(); // Basic features
  }
}
```

## 🏨 Black-Tier Features

### **Premium Users (within Black-Tier):**
- All regular client features
- Priority ride matching with best-rated drivers
- Luxury vehicle preference
- **Concierge services**: Hotel partnerships, booking integration
- Enhanced customer support
- MFA required for security

### **VIP Users (within Black-Tier):**
- All Premium features PLUS:
- **Encrypted ride tracking** (AES-256-GCM)
- **SOS emergency protocols** with Control Center
- **Trusted driver verification**
- **Discreet booking** mode
- **Biometric MFA** support
- **Control Center monitoring**

## 🔧 Key Implementation Points

1. **Single Black-Tier App**: Handles both Premium and VIP users with role-based feature availability
2. **Hotel Integration**: Core feature of Black-Tier (concierge services)
3. **Security Levels**: Progressive enhancement from Premium → VIP
4. **MFA Requirements**: Both Premium and VIP require MFA (Black-Tier security)
5. **Theme**: Single `blackTierTheme` for Premium and VIP users

## 🚀 Backend Consistency

- Django backend: 3 tiers (`normal`, `premium`, `vip`)
- Flutter frontend: 2 apps (`RegularClientApp`, `BlackTierClientApp`)
- Black-Tier app dynamically shows features based on Premium vs VIP tier
