# payments/management/commands/update_exchange_rates.py
"""
Management command to update currency exchange rates
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import requests
import logging
from decimal import Decimal
from payments.payment_models import Currency, ExchangeRate

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update currency exchange rates from external API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--api-source',
            type=str,
            default='fixer',
            help='Exchange rate API source (fixer, exchangerate-api, etc.)'
        )
        parser.add_argument(
            '--base-currency',
            type=str,
            default='USD',
            help='Base currency for exchange rates'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if rates were recently updated'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting exchange rate update...')
        )
        
        api_source = options['api_source']
        base_currency = options['base_currency']
        force_update = options['force']
        
        try:
            # Get active currencies
            currencies = Currency.objects.filter(is_active=True)
            
            if not currencies.exists():
                self.stdout.write(
                    self.style.WARNING('No active currencies found')
                )
                return
            
            # Update rates based on API source
            if api_source == 'fixer':
                self.update_from_fixer_api(currencies, base_currency, force_update)
            elif api_source == 'exchangerate-api':
                self.update_from_exchangerate_api(currencies, base_currency, force_update)
            else:
                self.stdout.write(
                    self.style.ERROR(f'Unsupported API source: {api_source}')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS('Exchange rate update completed successfully')
            )
            
        except Exception as e:
            logger.error(f"Exchange rate update failed: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Exchange rate update failed: {str(e)}')
            )
    
    def update_from_fixer_api(self, currencies, base_currency, force_update):
        """Update rates from Fixer.io API"""
        from django.conf import settings
        
        api_key = getattr(settings, 'FIXER_API_KEY', None)
        if not api_key:
            self.stdout.write(
                self.style.WARNING('FIXER_API_KEY not configured, skipping Fixer.io update')
            )
            return
        
        # Check if update is needed (unless forced)
        if not force_update:
            from datetime import timedelta
            recent_cutoff = timezone.now() - timedelta(hours=1)
            recent_updates = currencies.filter(last_rate_update__gte=recent_cutoff)
            if recent_updates.exists():
                self.stdout.write(
                    self.style.WARNING('Rates updated recently, use --force to override')
                )
                return
        
        # Get currency codes
        currency_codes = ','.join([c.code for c in currencies if c.code != base_currency])
        
        url = f'http://data.fixer.io/api/latest'
        params = {
            'access_key': api_key,
            'symbols': currency_codes
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                raise Exception(f"Fixer API error: {data.get('error', {}).get('info', 'Unknown error')}")
            
            rates = data.get('rates', {})
            self.update_currency_rates(currencies, rates, base_currency, 'fixer.io')
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch rates from Fixer.io: {str(e)}")
    
    def update_from_exchangerate_api(self, currencies, base_currency, force_update):
        """Update rates from ExchangeRate-API"""
        url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            rates = data.get('rates', {})
            self.update_currency_rates(currencies, rates, base_currency, 'exchangerate-api.com')
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch rates from ExchangeRate-API: {str(e)}")
    
    def update_currency_rates(self, currencies, rates, base_currency, source):
        """Update currency rates in database"""
        updated_count = 0
        
        # Get base currency object
        try:
            base_curr = Currency.objects.get(code=base_currency)
        except Currency.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Base currency {base_currency} not found in database')
            )
            return
        
        for currency in currencies:
            if currency.code == base_currency:
                # Base currency rate is always 1.0
                if currency.usd_exchange_rate != Decimal('1.0'):
                    currency.usd_exchange_rate = Decimal('1.0')
                    currency.last_rate_update = timezone.now()
                    currency.save()
                    updated_count += 1
                continue
            
            rate = rates.get(currency.code)
            if rate:
                try:
                    rate_decimal = Decimal(str(rate))
                    
                    # Convert to USD rate if base currency is not USD
                    if base_currency == 'USD':
                        usd_rate = rate_decimal
                    else:
                        # If base is EUR and rate is 1.2 for USD, then 1 USD = 1/1.2 EUR
                        # If base is EUR and rate is 120 for JPY, then 1 USD = 120 * (EUR/USD) JPY
                        base_to_usd_rate = rates.get('USD', 1) if base_currency != 'USD' else 1
                        usd_rate = rate_decimal / Decimal(str(base_to_usd_rate)) if base_to_usd_rate else rate_decimal
                    
                    # Update currency
                    currency.usd_exchange_rate = usd_rate
                    currency.last_rate_update = timezone.now()
                    currency.save()
                    
                    # Create exchange rate record
                    ExchangeRate.objects.create(
                        base_currency=base_curr,
                        target_currency=currency,
                        rate=rate_decimal,
                        rate_source=source,
                        effective_date=timezone.now()
                    )
                    
                    updated_count += 1
                    self.stdout.write(
                        f'Updated {currency.code}: USD rate = {usd_rate}'
                    )
                    
                except (ValueError, Exception) as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Failed to update {currency.code}: {str(e)}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'No rate found for {currency.code}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Updated {updated_count} currencies')
        )
