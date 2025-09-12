"""
Premium Card Batch Generation Admin

Django admin interface for bulk generation of Premium Digital Cards.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .premium_card_batch_models import PremiumCardBatchGeneration


@admin.register(PremiumCardBatchGeneration)
class PremiumCardBatchGenerationAdmin(admin.ModelAdmin):
    """Admin interface for Premium Card Batch Generation"""
    
    list_display = [
        'batch_id_display',
        'tier_badge',
        'quantity',
        'price_per_card',
        'total_value_display',
        'status_badge',
        'cards_generated_display',
        'success_rate_display',
        'generated_by',
        'generated_date',
        'actions_display'
    ]
    
    list_filter = [
        'tier',
        'status',
        'generated_date',
        'generated_by'
    ]
    
    search_fields = [
        'batch_id',
        'generated_by__email',
        'distributed_to'
    ]
    
    readonly_fields = [
        'id',
        'batch_id',
        'completed_date',
        'generated_date',
        'distributed_date',
        'cards_generated_display',
        'success_rate_display',
        'total_value_display'
    ]
    
    fieldsets = (
        ('Batch Information', {
            'fields': (
                'id',
                'batch_id',
                'tier',
                'quantity',
                'status'
            )
        }),
        ('Card Configuration', {
            'fields': (
                'price_per_card',
                'validity_months',
                'total_value_display'
            )
        }),
        ('Generation Tracking', {
            'fields': (
                'generated_by',
                'generated_date',
                'completed_date',
                'cards_generated_display',
                'success_rate_display'
            )
        }),
        ('Distribution', {
            'fields': (
                'distributed_to',
                'distributed_date',
                'distribution_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    def get_urls(self):
        """Add custom URLs for batch operations"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-batch/',
                self.admin_site.admin_view(self.generate_batch_view),
                name='accounts_premiumcardbatchgeneration_generate_batch'
            ),
            path(
                'batch-status/<uuid:batch_id>/',
                self.admin_site.admin_view(self.batch_status_view),
                name='accounts_premiumcardbatchgeneration_batch_status'
            ),
        ]
        return custom_urls + urls
    
    def batch_id_display(self, obj):
        """Display batch ID with link"""
        return format_html(
            '<strong><a href="{}">{}</a></strong>',
            reverse('admin:accounts_premiumcardbatchgeneration_change', args=[obj.pk]),
            obj.batch_id
        )
    batch_id_display.short_description = 'Batch ID'
    batch_id_display.admin_order_field = 'batch_id'
    
    def tier_badge(self, obj):
        """Display tier with color coding"""
        colors = {
            'vip': '#FFA500',
            'vip_premium': '#8B0000'
        }
        color = colors.get(obj.tier, '#999')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.tier.upper().replace('_', ' ')
        )
    tier_badge.short_description = 'Tier'
    tier_badge.admin_order_field = 'tier'
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#FFA500',
            'generated': '#28a745',
            'distributed': '#007bff',
            'cancelled': '#dc3545'
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def total_value_display(self, obj):
        """Display total batch value"""
        try:
            # Ensure we have valid values
            if hasattr(obj, 'quantity') and hasattr(obj, 'price_per_card'):
                quantity = obj.quantity or 0
                price = obj.price_per_card or 0
                value = float(quantity * price)
                return format_html('${:,.2f}', value)
            return format_html('<span style="color: orange;">N/A</span>')
        except (ValueError, TypeError, AttributeError) as e:
            return format_html('<span style="color: red;">Error: {}</span>', str(e)[:20])
    total_value_display.short_description = 'Total Value'
    
    def cards_generated_display(self, obj):
        """Display cards generated count"""
        if obj.status in ['generated', 'distributed']:
            try:
                # Use the relationship to get the actual count
                count = obj.generated_cards.count() if hasattr(obj, 'generated_cards') else 0
                quantity = obj.quantity or 0
                return format_html(
                    '<strong>{}</strong> / {}',
                    count,
                    quantity
                )
            except (AttributeError, TypeError) as e:
                return format_html('<span style="color: red;">Error: {}</span>', str(e)[:20])
        return '-'
    cards_generated_display.short_description = 'Cards Generated'
    
    def success_rate_display(self, obj):
        """Display success rate"""
        if obj.status in ['generated', 'distributed']:
            try:
                # Get the actual count using the relationship
                generated_count = obj.generated_cards.count() if hasattr(obj, 'generated_cards') else 0
                quantity = obj.quantity or 1  # Avoid division by zero
                rate = (generated_count / quantity) * 100
                color = '#28a745' if rate >= 100 else '#FFA500' if rate >= 90 else '#dc3545'
                return format_html(
                    '<span style="color: {}; font-weight: bold;">{:.1f}% ({}/{})</span>',
                    color,
                    rate,
                    generated_count,
                    quantity
                )
            except (ValueError, TypeError, AttributeError, ZeroDivisionError) as e:
                return format_html('<span style="color: red;">Error: {}</span>', str(e)[:20])
        return '-'
    success_rate_display.short_description = 'Success Rate'
    
    def actions_display(self, obj):
        """Display available actions"""
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="/admin/accounts/premiumcardbatchgeneration/generate-batch/?batch_id={}">Generate Cards</a>',
                obj.pk
            )
        elif obj.status == 'generated':
            return format_html(
                '<a class="button" href="/admin/accounts/premiumdigitalcard/">View Cards</a>'
            )
        return '-'
    actions_display.short_description = 'Actions'
    
    def generate_batch_view(self, request):
        """Custom view for generating card batches"""
        if request.method == 'POST':
            try:
                tier = request.POST.get('tier')
                quantity = int(request.POST.get('quantity', 0))
                price_per_card = float(request.POST.get('price_per_card', 99.99))
                validity_months = int(request.POST.get('validity_months', 12))
                notes = request.POST.get('notes', '')
                
                if quantity <= 0:
                    messages.error(request, 'Quantity must be greater than 0')
                    return render(request, 'admin/premium_card_batch_generate.html')
                
                if quantity > 1000:
                    messages.error(request, 'Cannot generate more than 1000 cards at once')
                    return render(request, 'admin/premium_card_batch_generate.html')
                
                # Create batch
                batch_id = PremiumCardBatchGeneration.generate_batch_id(tier, quantity)
                batch = PremiumCardBatchGeneration.objects.create(
                    batch_id=batch_id,
                    tier=tier,
                    quantity=quantity,
                    price_per_card=price_per_card,
                    validity_months=validity_months,
                    generated_by=request.user,
                    notes=notes
                )
                
                # Generate cards
                cards = batch.generate_cards()
                
                messages.success(
                    request,
                    f'Successfully generated {len(cards)} Premium Digital Cards (Batch: {batch_id})'
                )
                
                return redirect('admin:accounts_premiumcardbatchgeneration_change', batch.pk)
                
            except Exception as e:
                messages.error(request, f'Error generating cards: {str(e)}')
        
        # Handle GET request with pre-filled batch_id
        batch_id = request.GET.get('batch_id')
        if batch_id:
            try:
                batch = get_object_or_404(PremiumCardBatchGeneration, pk=batch_id)
                return redirect('admin:accounts_premiumcardbatchgeneration_change', batch.pk)
            except:
                pass
        
        context = {
            'title': 'Generate Premium Card Batch',
            'tier_choices': [
                ('vip', 'VIP'),
                ('vip_premium', 'VIP Premium'),
            ],
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
        }
        
        return render(request, 'admin/premium_card_batch_generate.html', context)
    
    def batch_status_view(self, request, batch_id):
        """AJAX view for batch status"""
        try:
            batch = get_object_or_404(PremiumCardBatchGeneration, pk=batch_id)
            return JsonResponse({
                'status': batch.status,
                'cards_generated': batch.cards_generated_count,
                'success_rate': batch.success_rate,
                'total_value': float(batch.total_value)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def save_model(self, request, obj, form, change):
        """Auto-set generated_by on creation"""
        if not change:  # Creating new object
            obj.generated_by = request.user
            if not obj.batch_id:
                obj.batch_id = PremiumCardBatchGeneration.generate_batch_id(obj.tier, obj.quantity)
        super().save_model(request, obj, form, change)
    
    actions = ['mark_distributed', 'cancel_batch']
    
    def mark_distributed(self, request, queryset):
        """Mark selected batches as distributed"""
        count = 0
        for batch in queryset.filter(status='generated'):
            batch.mark_distributed('Admin Panel', 'Marked as distributed via admin action')
            count += 1
        
        self.message_user(request, f'Marked {count} batches as distributed')
    mark_distributed.short_description = "Mark as distributed"
    
    def cancel_batch(self, request, queryset):
        """Cancel selected pending batches"""
        count = 0
        for batch in queryset.filter(status='pending'):
            batch.status = 'cancelled'
            batch.notes = 'Cancelled via admin action'
            batch.save()
            count += 1
        
        self.message_user(request, f'Cancelled {count} batches')
    cancel_batch.short_description = "Cancel pending batches"