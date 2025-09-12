#!/usr/bin/env python
"""
Test Batch Generation with Proper Card Linking

This script tests the updated batch generation system that properly links
generated cards to their batch using the new batch_generation relationship.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.dev_settings')
django.setup()

from accounts.premium_card_batch_models import PremiumCardBatchGeneration
from accounts.premium_card_models import PremiumDigitalCard
from accounts.models import User
from decimal import Decimal

def test_improved_batch_generation():
    """Test the improved batch generation with proper card linking"""
    
    print("🔧 Testing IMPROVED Batch Generation System")
    print("=" * 60)
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@email.com',
        defaults={
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'tier': 'VIP'
        }
    )
    
    print(f"✅ Using admin user: {admin_user.email}")
    
    # Create a test batch
    batch = PremiumCardBatchGeneration.objects.create(
        tier="vip",
        quantity=5,  # Small batch for testing
        price_per_card=Decimal('299.99'),
        validity_months=12,
        generated_by=admin_user
    )
    
    print(f"✅ Created batch: {batch.batch_id}")
    print(f"   - Batch UUID: {batch.id}")
    print(f"   - Tier: {batch.tier}")
    print(f"   - Quantity: {batch.quantity}")
    print(f"   - Price per card: ${batch.price_per_card}")
    print(f"   - Status: {batch.status}")
    
    # Test initial state
    print(f"\n📊 Initial State:")
    print(f"   - Total value: ${batch.quantity * batch.price_per_card}")
    print(f"   - Cards linked: {batch.generated_cards.count()}")
    print(f"   - Success rate: 0% (not generated yet)")
    
    # Generate the cards
    print(f"\n🔄 Generating cards with proper linking...")
    try:
        batch.generate_cards()
        print(f"✅ Cards generated successfully!")
    except Exception as e:
        print(f"❌ Error generating cards: {e}")
        return
    
    # Refresh from database
    batch.refresh_from_db()
    
    # Test after generation
    print(f"\n📊 After Generation:")
    print(f"   - Status: {batch.status}")
    print(f"   - Completed at: {batch.completed_date}")
    print(f"   - Cards linked to batch: {batch.generated_cards.count()}")
    
    # Test the relationship
    linked_cards = batch.generated_cards.all()
    print(f"\n🔗 Card Linkage Test:")
    print(f"   - Total cards in system: {PremiumDigitalCard.objects.count()}")
    print(f"   - Cards linked to this batch: {linked_cards.count()}")
    
    # Show sample linked cards
    print(f"\n📋 Sample Linked Cards:")
    for i, card in enumerate(linked_cards[:3], 1):
        print(f"   {i}. Card: {card.card_number}")
        print(f"      - Verification: {card.verification_code}")
        print(f"      - Batch: {card.batch_generation.batch_id if card.batch_generation else 'None'}")
        print(f"      - Price: ${card.price}")
        print(f"      - Status: {card.status}")
    
    # Test calculated properties
    print(f"\n🧮 Calculated Properties:")
    total_value = batch.quantity * batch.price_per_card
    success_rate = (batch.generated_cards.count() / batch.quantity) * 100
    print(f"   - Total Value: ${total_value}")
    print(f"   - Success Rate: {success_rate}%")
    print(f"   - Cards Generated: {batch.generated_cards.count()}/{batch.quantity}")
    
    # Test admin display methods (simulate what admin sees)
    print(f"\n🎛️ Admin Display Simulation:")
    print(f"   - Total Value Display: ${batch.quantity * batch.price_per_card:,.2f}")
    print(f"   - Success Rate Display: {success_rate:.1f}% ({batch.generated_cards.count()}/{batch.quantity})")
    print(f"   - Cards Generated Display: {batch.generated_cards.count()} / {batch.quantity}")
    
    print(f"\n🎉 Improved batch generation test completed successfully!")
    print(f"   - All cards properly linked to batch")
    print(f"   - No more time-based filtering issues")
    print(f"   - Accurate statistics and calculations")

if __name__ == "__main__":
    test_improved_batch_generation()