# VIP Digital Card Django Admin Configuration
"""
Admin interface for VIP Digital Card management with batch generation
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.forms import ModelForm, IntegerField, CharField, ChoiceField
from .vip_card_models import VIPDigitalCard, CardActivationHistory, CardBatchGeneration
import csv
from django.http import HttpResponse


class VIPCardBatchGenerationForm(ModelForm):
    """Form for generating VIP card batches"""
    quantity = IntegerField(
        min_value=1, 
        max_value=1000,
        help_text="Number of cards to generate (1-1000)"
    )
    tier = ChoiceField(
        choices=VIPDigitalCard.TIER_CHOICES,
        help_text="Select tier type for the cards"
    )
    notes = CharField(
        required=False,
        widget=admin.widgets.AdminTextareaWidget,
        help_text="Optional notes about this batch"
    )
    
    class Meta:
        model = CardBatchGeneration
        fields = ['tier', 'quantity', 'notes']


class VIPDigitalCardAdmin(admin.ModelAdmin):
    """Admin interface for VIP Digital Cards"""
    
    list_display = [
        'serial_number_display',
        'tier_badge',
        'status_badge', 
        'activated_by_display',
        'activated_date',
        'expiry_status',
        'admin_actions'
    ]
    
    list_filter = [
        'tier',
        'status',
        'issued_date',
        'activated_date',
        ('activated_by', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'serial_number',
        'activation_code',
        'activated_by__email',
        'activated_by__first_name',
        'activated_by__last_name',
    ]
    
    readonly_fields = [
        'id',
        'serial_number',
        'activation_code',
        'issued_date',
        'activated_date',
        'activation_ip',
        'card_preview'
    ]
    
    fieldsets = [
        ('Card Information', {
            'fields': [
                'id',
                'serial_number',
                'activation_code',
                'tier',
                'status',
            ]
        }),
        ('Card Design', {
            'fields': [
                'primary_color',
                'secondary_color',
                'background_image',
                'hologram_pattern',
                'logo_url',
                'card_preview',
            ],
            'classes': ['collapse']
        }),
        ('Activation Details', {
            'fields': [
                'activated_by',
                'issued_date',
                'activated_date',
                'expiry_date',
                'activation_ip',
            ]
        }),
        ('Features & Metadata', {
            'fields': [
                'card_features',
                'encrypted_metadata',
            ],
            'classes': ['collapse']
        }),
    ]
    
    actions = [
        'export_cards_csv',
        'deactivate_selected_cards',
        'extend_expiry_date',
    ]
    
    def get_urls(self):
        """Add custom admin URLs"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-batch/',
                self.admin_site.admin_view(self.generate_batch_view),
                name='accounts_vipdigitalcard_generate_batch'
            ),
            path(
                'batch-status/<uuid:batch_id>/',
                self.admin_site.admin_view(self.batch_status_view),
                name='accounts_vipdigitalcard_batch_status'
            ),
        ]
        return custom_urls + urls
    
    def serial_number_display(self, obj):
        """Display formatted serial number"""
        if obj.status == 'active':
            return format_html(
                '<strong style="color: green;">{}</strong>',
                obj.serial_number
            )
        return obj.serial_number
    serial_number_display.short_description = 'Serial Number'
    
    def tier_badge(self, obj):
        """Display tier as colored badge"""
        colors = {
            'vip': '#FFD700',
            'vip_premium': '#9932CC'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.tier, '#666'),
            obj.tier.upper().replace('_', ' ')
        )
    tier_badge.short_description = 'Tier'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'inactive': '#6c757d',
            'active': '#28a745',
            'suspended': '#ffc107',
            'expired': '#dc3545',
            'revoked': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#666'),
            obj.status.title()
        )
    status_badge.short_description = 'Status'
    
    def activated_by_display(self, obj):
        """Display user who activated the card"""
        if obj.activated_by:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                reverse('admin:accounts_user_change', args=[obj.activated_by.id]),
                obj.activated_by.get_full_name() or obj.activated_by.email
            )
        return '-'
    activated_by_display.short_description = 'Activated By'
    
    def expiry_status(self, obj):
        """Display expiry status"""
        if not obj.expiry_date:
            return '-'
        
        days_left = obj.days_until_expiry
        if days_left is None:
            return '-'
        elif days_left <= 0:
            return format_html('<span style="color: red; font-weight: bold;">EXPIRED</span>')
        elif days_left <= 30:
            return format_html('<span style="color: orange; font-weight: bold;">{} days left</span>', days_left)
        else:
            return f"{days_left} days left"
    expiry_status.short_description = 'Expiry Status'
    
    def admin_actions(self, obj):
        """Display admin action buttons"""
        buttons = []
        
        if obj.status == 'active':
            buttons.append(
                f'<a href="#" onclick="deactivateCard(\'{obj.id}\')" '
                f'style="color: red; text-decoration: none;">🔒 Deactivate</a>'
            )
        
        if obj.activated_by:
            buttons.append(
                f'<a href="{reverse("admin:accounts_user_change", args=[obj.activated_by.id])}" '
                f'target="_blank" style="color: blue; text-decoration: none;">👤 View User</a>'
            )
        
        return format_html(' | '.join(buttons))
    admin_actions.short_description = 'Actions'
    
    def card_preview(self, obj):
        """Display card preview"""
        if obj.tier:
            return format_html(
                '<div style="background: linear-gradient(45deg, {}, {}); '
                'color: white; padding: 15px; border-radius: 10px; '
                'font-family: monospace; max-width: 300px;">'
                '<div style="font-size: 12px; opacity: 0.8;">VIP DIGITAL CARD</div>'
                '<div style="font-size: 16px; font-weight: bold; margin: 5px 0;">{}</div>'
                '<div style="font-size: 14px; margin: 5px 0;">{}</div>'
                '<div style="font-size: 10px; opacity: 0.8;">Status: {}</div>'
                '</div>',
                obj.primary_color,
                obj.secondary_color,
                obj.serial_number,
                obj.tier.upper().replace('_', ' '),
                obj.status.title()
            )
        return "No preview available"
    card_preview.short_description = 'Card Preview'
    
    def generate_batch_view(self, request):
        """View for generating card batches"""
        if request.method == 'POST':
            form = VIPCardBatchGenerationForm(request.POST)
            if form.is_valid():
                try:
                    # Create batch record
                    batch = CardBatchGeneration.objects.create(
                        batch_id=CardBatchGeneration.generate_batch_id(
                            form.cleaned_data['tier'],
                            form.cleaned_data['quantity']
                        ),
                        tier=form.cleaned_data['tier'],
                        quantity=form.cleaned_data['quantity'],
                        generated_by=request.user,
                        notes=form.cleaned_data.get('notes', '')
                    )
                    
                    # Generate the cards
                    cards = batch.generate_cards()
                    
                    messages.success(
                        request,
                        f'Successfully generated {len(cards)} {batch.tier.upper()} cards in batch {batch.batch_id}'
                    )
                    
                    return redirect(
                        reverse('admin:accounts_vipdigitalcard_batch_status', args=[batch.id])
                    )
                    
                except Exception as e:
                    messages.error(request, f'Failed to generate cards: {str(e)}')
        else:
            form = VIPCardBatchGenerationForm()
        
        context = {
            'form': form,
            'title': 'Generate VIP Card Batch',
            'opts': self.model._meta,
        }
        return render(request, 'admin/vip_cards/generate_batch.html', context)
    
    def batch_status_view(self, request, batch_id):
        """View batch generation status and cards"""
        try:
            batch = CardBatchGeneration.objects.get(id=batch_id)
            cards = batch.cards.all()
            
            context = {
                'batch': batch,
                'cards': cards,
                'title': f'Batch {batch.batch_id} Status',
                'opts': self.model._meta,
            }
            return render(request, 'admin/vip_cards/batch_status.html', context)
            
        except CardBatchGeneration.DoesNotExist:
            messages.error(request, 'Batch not found')
            return redirect('admin:accounts_vipdigitalcard_changelist')
    
    def export_cards_csv(self, request, queryset):
        """Export selected cards to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vip_cards.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Serial Number', 'Activation Code', 'Tier', 'Status',
            'Activated By', 'Activated Date', 'Expiry Date'
        ])
        
        for card in queryset:
            writer.writerow([
                card.serial_number,
                card.activation_code,
                card.tier,
                card.status,
                card.activated_by.email if card.activated_by else '',
                card.activated_date.strftime('%Y-%m-%d %H:%M') if card.activated_date else '',
                card.expiry_date.strftime('%Y-%m-%d') if card.expiry_date else ''
            ])
        
        return response
    export_cards_csv.short_description = "Export selected cards to CSV"
    
    def deactivate_selected_cards(self, request, queryset):
        """Deactivate selected cards"""
        active_cards = queryset.filter(status='active')
        count = 0
        
        for card in active_cards:
            try:
                card.deactivate_card("Admin bulk deactivation")
                count += 1
            except ValueError:
                pass
        
        self.message_user(request, f'Deactivated {count} cards')
    deactivate_selected_cards.short_description = "Deactivate selected cards"
    
    def extend_expiry_date(self, request, queryset):
        """Extend expiry date by 6 months"""
        count = 0
        for card in queryset.filter(status='active'):
            if card.expiry_date:
                card.expiry_date = card.expiry_date + timezone.timedelta(days=180)
                card.save()
                count += 1
        
        self.message_user(request, f'Extended expiry date for {count} cards')
    extend_expiry_date.short_description = "Extend expiry by 6 months"
    
    # Add inlines for activation history
    inlines = []
    
    def get_inlines(self, request, obj):
        """Add activation history inline for existing cards"""
        inlines = []
        if obj and obj.pk:  # Only show for existing cards
            from .activation_history_admin import CardActivationHistoryInline, CardUsageLogInline
            
            # Filter inlines to show only VIP card history
            class VIPCardActivationHistoryInline(CardActivationHistoryInline):
                def get_queryset(self, request):
                    qs = super().get_queryset(request)
                    return qs.filter(card_type='vip')
            
            class VIPCardUsageLogInline(CardUsageLogInline):
                def get_queryset(self, request):
                    qs = super().get_queryset(request)
                    return qs.filter(vip_card__isnull=False)
            
            inlines.extend([VIPCardActivationHistoryInline, VIPCardUsageLogInline])
        return inlines


class CardActivationHistoryAdmin(admin.ModelAdmin):
    """Admin interface for card activation history"""
    
    list_display = [
        'card_serial',
        'user_email',
        'tier_change',
        'activation_date',
        'client_ip',
        'notes_preview'
    ]
    
    list_filter = [
        'activation_date',
        'previous_tier',
        'new_tier',
        'card__tier',
    ]
    
    search_fields = [
        'card__serial_number',
        'user__email',
        'user__first_name',
        'user__last_name',
        'notes',
    ]
    
    readonly_fields = [
        'id',
        'card',
        'user',
        'activation_date',
        'client_ip',
        'previous_tier',
        'new_tier',
    ]
    
    def card_serial(self, obj):
        return obj.card.serial_number
    card_serial.short_description = 'Card Serial'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def tier_change(self, obj):
        return format_html(
            '<span style="color: {};">{}</span> → <span style="color: {};">{}</span>',
            '#dc3545' if obj.previous_tier == 'regular' else '#28a745',
            obj.previous_tier.upper(),
            '#28a745',
            obj.new_tier.upper()
        )
    tier_change.short_description = 'Tier Change'
    
    def notes_preview(self, obj):
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = 'Notes'


class CardBatchGenerationAdmin(admin.ModelAdmin):
    """Admin interface for card batch generation"""
    
    list_display = [
        'batch_id',
        'tier_badge',
        'quantity',
        'status_badge',
        'generated_by',
        'generated_date',
        'cards_count',
        'admin_actions'
    ]
    
    list_filter = [
        'tier',
        'status',
        'generated_date',
        'generated_by',
    ]
    
    search_fields = [
        'batch_id',
        'notes',
        'generated_by__email',
    ]
    
    readonly_fields = [
        'id',
        'batch_id',
        'generated_date',
        'cards_preview'
    ]
    
    def tier_badge(self, obj):
        colors = {'vip': '#FFD700', 'vip_premium': '#9932CC'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.tier, '#666'),
            obj.tier.upper().replace('_', ' ')
        )
    tier_badge.short_description = 'Tier'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#6c757d',
            'generated': '#28a745',
            'distributed': '#17a2b8',
            'cancelled': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#666'),
            obj.status.title()
        )
    status_badge.short_description = 'Status'
    
    def cards_count(self, obj):
        return obj.cards.count()
    cards_count.short_description = 'Cards Generated'
    
    def admin_actions(self, obj):
        return format_html(
            '<a href="{}" style="color: blue; text-decoration: none;">📋 View Cards</a>',
            reverse('admin:accounts_vipdigitalcard_batch_status', args=[obj.id])
        )
    admin_actions.short_description = 'Actions'
    
    def cards_preview(self, obj):
        """Show preview of generated cards"""
        cards = obj.cards.all()[:5]  # Show first 5 cards
        if cards:
            preview = '<br>'.join([f"{card.serial_number} - {card.activation_code}" for card in cards])
            if obj.cards.count() > 5:
                preview += f'<br><em>... and {obj.cards.count() - 5} more cards</em>'
            return format_html(preview)
        return "No cards generated yet"
    cards_preview.short_description = 'Generated Cards Preview'