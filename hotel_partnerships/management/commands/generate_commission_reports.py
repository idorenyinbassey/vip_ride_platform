from django.core.management.base import BaseCommand
from django.utils import timezone
from hotel_partnerships.signals import create_monthly_commission_reports


class Command(BaseCommand):
    help = 'Generate monthly commission reports for all hotels'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Generate report for specific month (YYYY-MM format)',
        )
        parser.add_argument(
            '--hotel-id',
            type=str,
            help='Generate report for specific hotel UUID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of existing reports',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting commission report generation...')
        )
        
        try:
            if options['month'] or options['hotel_id']:
                self.generate_specific_report(options)
            else:
                # Generate reports for all hotels
                create_monthly_commission_reports()
            
            self.stdout.write(
                self.style.SUCCESS('Commission reports generated successfully!')
            )
            
        except Exception as e:
            from django.core.management import CommandError
            import sys
            
            self.stdout.write(
                self.style.ERROR(f'Error generating reports: {str(e)}')
            )
            raise CommandError(f'Commission report generation failed: {str(e)}')

    def generate_specific_report(self, options):
        """Generate report for specific month/hotel"""
        from hotel_partnerships.models import Hotel, HotelCommissionReport
        from datetime import date
        import uuid
        
        # Parse month if provided
        if options['month']:
            try:
                year, month = map(int, options['month'].split('-'))
                report_month = date(year, month, 1)
            except ValueError:
                raise ValueError("Month must be in YYYY-MM format")
        else:
            # Use last month
            today = date.today()
            if today.month == 1:
                report_month = date(today.year - 1, 12, 1)
            else:
                report_month = date(today.year, today.month - 1, 1)
        
        # Get hotels to process
        if options['hotel_id']:
            try:
                hotel_uuid = uuid.UUID(options['hotel_id'])
                hotels = Hotel.objects.filter(id=hotel_uuid, status='ACTIVE')
            except ValueError:
                raise ValueError("Invalid hotel ID format")
        else:
            hotels = Hotel.objects.filter(status='ACTIVE')
        
        if not hotels.exists():
            self.stdout.write(
                self.style.WARNING('No hotels found matching criteria')
            )
            return
        
        # Generate reports
        for hotel in hotels:
            # Check if report exists
            existing_report = HotelCommissionReport.objects.filter(
                hotel=hotel,
                report_month=report_month
            ).first()
            
            if existing_report and not options['force']:
                self.stdout.write(
                    self.style.WARNING(
                        f'Report already exists for {hotel.name} - '
                        f'{report_month.strftime("%B %Y")}. Use --force to override.'
                    )
                )
                continue
            
            # Delete existing if forcing
            if existing_report and options['force']:
                existing_report.delete()
                self.stdout.write(
                    self.style.WARNING(
                        f'Deleted existing report for {hotel.name}'
                    )
                )
            
            # Generate new report
            self.generate_hotel_report(hotel, report_month)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Generated report for {hotel.name} - '
                    f'{report_month.strftime("%B %Y")}'
                )
            )

    def generate_hotel_report(self, hotel, report_month):
        """Generate commission report for specific hotel and month"""
        from hotel_partnerships.models import HotelBooking, HotelCommissionReport
        from django.db.models import Sum, Count, Avg
        from decimal import Decimal
        
        # Get bookings for the month
        month_bookings = HotelBooking.objects.filter(
            hotel=hotel,
            created_at__year=report_month.year,
            created_at__month=report_month.month
        )
        
        # Calculate metrics
        total_bookings = month_bookings.count()
        completed_bookings = month_bookings.filter(status='COMPLETED').count()
        cancelled_bookings = month_bookings.filter(status='CANCELLED').count()
        
        # Financial calculations
        completed_rides = month_bookings.filter(
            status='COMPLETED',
            final_fare__isnull=False
        )
        
        financial_data = completed_rides.aggregate(
            total_value=Sum('final_fare'),
            total_commission=Sum('hotel_commission'),
            avg_commission_rate=Avg('commission_rate_used')
        )
        
        total_ride_value = financial_data['total_value'] or Decimal('0.00')
        total_commission = financial_data['total_commission'] or Decimal('0.00')
        avg_commission_rate = financial_data['avg_commission_rate'] or Decimal('0.00')
        
        # Create detailed breakdown
        detailed_data = {
            'booking_types': list(
                month_bookings.values('booking_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'vehicle_types': list(
                month_bookings.values('vehicle_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'top_destinations': list(
                completed_rides.values('destination')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
        }
        
        # Create the report
        report = HotelCommissionReport.objects.create(
            hotel=hotel,
            report_month=report_month,
            total_bookings=total_bookings,
            completed_bookings=completed_bookings,
            cancelled_bookings=cancelled_bookings,
            total_ride_value=total_ride_value,
            total_commission_earned=total_commission,
            average_commission_rate=avg_commission_rate,
            detailed_data=detailed_data,
            payment_due_date=self.calculate_payment_due_date(report_month)
        )
        
        return report

    def calculate_payment_due_date(self, report_month):
        """Calculate payment due date (15th of following month)"""
        from datetime import date
        
        if report_month.month == 12:
            return date(report_month.year + 1, 1, 15)
        else:
            return date(report_month.year, report_month.month + 1, 15)
