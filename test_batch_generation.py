#!/usr/bin/env python
"""
Test script for Premium Card Batch Generation
This script demonstrates the bulk generation functionality
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

def test_batch_generation():
    """Test the batch generation functionality"""
    
    print("🧪 Testing Premium Card Batch Generation System")
    print("=" * 60)
    
    # Get or create a test admin user
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
    
    # Test batch creation
    batch = PremiumCardBatchGeneration.objects.create(
        name="Test Production Batch #1",
        description="Testing bulk generation for production efficiency",
        tier="VIP",
        quantity=25,
        price=Decimal('499.99'),
        validity_months=12,
        requested_by=admin_user
    )
    
    print(f"✅ Created batch: {batch.name}")
    print(f"   - Batch ID: {batch.id}")
    print(f"   - Tier: {batch.tier}")
    print(f"   - Quantity: {batch.quantity}")
    print(f"   - Price per card: ${batch.price}")
    print(f"   - Status: {batch.status}")
    
    # Generate the cards
    print("\n🔄 Generating cards...")
    batch.generate_cards()
    
    # Refresh from database
    batch.refresh_from_db()
    
    print(f"✅ Cards generated successfully!")
    print(f"   - Generated: {batch.cards_generated}")
    print(f"   - Status: {batch.status}")
    print(f"   - Completed at: {batch.completed_at}")
    
    # Show some sample cards
    sample_cards = PremiumDigitalCard.objects.filter(
        premium_card_batch_generation=batch
    )[:5]
    
    print(f"\n📋 Sample Generated Cards:")
    for i, card in enumerate(sample_cards, 1):
        print(f"   {i}. Card: {card.card_number}")
        print(f"      - Verification: {card.verification_code}")
        print(f"      - Price: ${card.price}")
        print(f"      - Status: {card.status}")
    
    # Test batch statistics
    print(f"\n📊 Batch Statistics:")
    stats = batch.get_stats()
    for key, value in stats.items():
        print(f"   - {key.replace('_', ' ').title()}: {value}")
    
    # Test distribution marking
    print(f"\n📦 Testing distribution marking...")
    distributed_cards = sample_cards[:3]
    batch.mark_distributed(list(distributed_cards))
    
    batch.refresh_from_db()
    print(f"   - Distributed: {batch.cards_distributed}")
    print(f"   - Remaining: {batch.cards_generated - batch.cards_distributed}")
    
    print(f"\n🎉 Batch generation test completed successfully!")
    print(f"   Total batches in system: {PremiumCardBatchGeneration.objects.count()}")
    print(f"   Total generated cards: {PremiumDigitalCard.objects.count()}")

if __name__ == "__main__":
    test_batch_generation()