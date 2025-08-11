import requests
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import Hotel, HotelGuest, HotelBooking, PMSIntegrationLog

logger = logging.getLogger(__name__)


class PMSIntegrationService:
    """Service for integrating with Property Management Systems"""
    
    def __init__(self, hotel):
        self.hotel = hotel
        self.timeout = 30  # seconds
    
    def sync_guest_data(self, pms_guest_id=None):
        """Sync guest data from PMS"""
        if self.hotel.pms_type == 'NONE':
            return {'success': False, 'message': 'No PMS integration configured'}
        
        try:
            start_time = timezone.now()
            
            if self.hotel.pms_type == 'ORACLE_OPERA':
                result = self._sync_oracle_opera_guests(pms_guest_id)
            elif self.hotel.pms_type == 'FIDELIO':
                result = self._sync_fidelio_guests(pms_guest_id)
            elif self.hotel.pms_type == 'CLOUDBEDS':
                result = self._sync_cloudbeds_guests(pms_guest_id)
            else:
                result = self._sync_generic_pms_guests(pms_guest_id)
            
            processing_time = timezone.now() - start_time
            
            # Log the integration attempt
            PMSIntegrationLog.objects.create(
                hotel=self.hotel,
                action_type='GUEST_SYNC',
                success=result['success'],
                request_data={'pms_guest_id': pms_guest_id},
                response_data=result.get('data', {}),
                error_message=result.get('error', ''),
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            logger.error(f"PMS guest sync error for {self.hotel.name}: {str(e)}")
            
            PMSIntegrationLog.objects.create(
                hotel=self.hotel,
                action_type='GUEST_SYNC',
                success=False,
                error_message=str(e),
                processing_time=timezone.now() - start_time
            )
            
            return {'success': False, 'error': str(e)}
    
    def create_booking_in_pms(self, booking):
        """Create or update booking in PMS"""
        if self.hotel.pms_type == 'NONE':
            return {'success': True, 'message': 'No PMS integration needed'}
        
        try:
            start_time = timezone.now()
            
            booking_data = {
                'booking_reference': booking.booking_reference,
                'guest_name': booking.guest_name,
                'guest_phone': booking.guest_phone,
                'room_number': booking.guest_room_number,
                'pickup_datetime': booking.pickup_datetime.isoformat(),
                'destination': booking.destination,
                'vehicle_type': booking.vehicle_type,
                'passenger_count': booking.passenger_count,
                'special_instructions': booking.special_instructions,
                'status': booking.status
            }
            
            if self.hotel.pms_type == 'ORACLE_OPERA':
                result = self._create_oracle_opera_booking(booking_data)
            elif self.hotel.pms_type == 'FIDELIO':
                result = self._create_fidelio_booking(booking_data)
            elif self.hotel.pms_type == 'CLOUDBEDS':
                result = self._create_cloudbeds_booking(booking_data)
            else:
                result = self._create_generic_pms_booking(booking_data)
            
            processing_time = timezone.now() - start_time
            
            # Log the integration attempt
            PMSIntegrationLog.objects.create(
                hotel=self.hotel,
                action_type='BOOKING_CREATE',
                success=result['success'],
                booking_reference=booking.booking_reference,
                request_data=booking_data,
                response_data=result.get('data', {}),
                error_message=result.get('error', ''),
                pms_reference=result.get('pms_reference', ''),
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            logger.error(f"PMS booking creation error for {self.hotel.name}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_status_update(self, booking, status_data):
        """Send booking status update to PMS"""
        if self.hotel.pms_type == 'NONE' or not self.hotel.send_real_time_updates:
            return {'success': True, 'message': 'No PMS updates needed'}
        
        try:
            update_data = {
                'booking_reference': booking.booking_reference,
                'status': booking.status,
                'timestamp': timezone.now().isoformat(),
                **status_data
            }
            
            if self.hotel.pms_type == 'ORACLE_OPERA':
                result = self._send_oracle_opera_update(update_data)
            elif self.hotel.pms_type == 'FIDELIO':
                result = self._send_fidelio_update(update_data)
            elif self.hotel.pms_type == 'CLOUDBEDS':
                result = self._send_cloudbeds_update(update_data)
            else:
                result = self._send_generic_pms_update(update_data)
            
            # Log the update
            PMSIntegrationLog.objects.create(
                hotel=self.hotel,
                action_type='STATUS_UPDATE',
                success=result['success'],
                booking_reference=booking.booking_reference,
                request_data=update_data,
                response_data=result.get('data', {}),
                error_message=result.get('error', '')
            )
            
            return result
            
        except Exception as e:
            logger.error(f"PMS status update error for {self.hotel.name}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _make_pms_request(self, method, endpoint, data=None):
        """Make HTTP request to PMS API"""
        url = f"{self.hotel.pms_endpoint.rstrip('/')}/{endpoint.lstrip('/')}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.hotel.pms_api_key}',
            'User-Agent': 'VIP-Ride-Platform/1.0'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=data, 
                    timeout=self.timeout
                )
            elif method.upper() == 'PUT':
                response = requests.put(
                    url, 
                    headers=headers, 
                    json=data, 
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json() if response.text else {},
                'status_code': response.status_code
            }
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'PMS request timeout'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'PMS connection failed'}
        except requests.exceptions.HTTPError as e:
            return {
                'success': False, 
                'error': f'PMS HTTP error: {e.response.status_code}'
            }
        except Exception as e:
            return {'success': False, 'error': f'PMS request error: {str(e)}'}
    
    # Oracle Opera PMS Integration
    def _sync_oracle_opera_guests(self, guest_id=None):
        """Sync guests from Oracle Opera PMS"""
        endpoint = f"/guests/{guest_id}" if guest_id else "/guests/current"
        result = self._make_pms_request('GET', endpoint)
        
        if result['success']:
            guests_data = result['data'].get('guests', [])
            synced_count = 0
            
            for guest_data in guests_data:
                self._create_or_update_guest_from_pms(guest_data, 'ORACLE_OPERA')
                synced_count += 1
            
            return {
                'success': True,
                'message': f'Synced {synced_count} guests from Oracle Opera',
                'data': {'synced_count': synced_count}
            }
        
        return result
    
    def _create_oracle_opera_booking(self, booking_data):
        """Create booking in Oracle Opera PMS"""
        opera_data = {
            'reservation_id': booking_data['booking_reference'],
            'guest_name': booking_data['guest_name'],
            'contact_phone': booking_data['guest_phone'],
            'room_number': booking_data['room_number'],
            'transport_details': {
                'pickup_time': booking_data['pickup_datetime'],
                'destination': booking_data['destination'],
                'vehicle_type': booking_data['vehicle_type'],
                'passenger_count': booking_data['passenger_count']
            },
            'special_requests': booking_data['special_instructions'],
            'status': 'CONFIRMED'
        }
        
        result = self._make_pms_request('POST', '/transport/bookings', opera_data)
        
        if result['success']:
            pms_reference = result['data'].get('booking_id', '')
            return {
                'success': True,
                'pms_reference': pms_reference,
                'data': result['data']
            }
        
        return result
    
    def _send_oracle_opera_update(self, update_data):
        """Send status update to Oracle Opera PMS"""
        endpoint = f"/transport/bookings/{update_data['booking_reference']}/status"
        
        opera_update = {
            'status': update_data['status'],
            'timestamp': update_data['timestamp'],
            'driver_details': update_data.get('driver_details', {}),
            'current_location': update_data.get('current_location', {})
        }
        
        return self._make_pms_request('PUT', endpoint, opera_update)
    
    # Fidelio PMS Integration
    def _sync_fidelio_guests(self, guest_id=None):
        """Sync guests from Fidelio PMS"""
        # Fidelio-specific implementation
        endpoint = "/api/guests/inhouse"
        result = self._make_pms_request('GET', endpoint)
        
        if result['success']:
            guests = result['data'].get('guests', [])
            synced_count = len(guests)
            
            for guest_data in guests:
                self._create_or_update_guest_from_pms(guest_data, 'FIDELIO')
            
            return {
                'success': True,
                'message': f'Synced {synced_count} guests from Fidelio',
                'data': {'synced_count': synced_count}
            }
        
        return result
    
    def _create_fidelio_booking(self, booking_data):
        """Create booking in Fidelio PMS"""
        # Fidelio-specific booking creation
        fidelio_data = {
            'guest_name': booking_data['guest_name'],
            'room': booking_data['room_number'],
            'transport_request': {
                'pickup_time': booking_data['pickup_datetime'],
                'destination': booking_data['destination'],
                'vehicle': booking_data['vehicle_type'],
                'passengers': booking_data['passenger_count']
            }
        }
        
        return self._make_pms_request('POST', '/api/transport', fidelio_data)
    
    def _send_fidelio_update(self, update_data):
        """Send update to Fidelio PMS"""
        endpoint = f"/api/transport/{update_data['booking_reference']}"
        return self._make_pms_request('PUT', endpoint, update_data)
    
    # CloudBeds PMS Integration
    def _sync_cloudbeds_guests(self, guest_id=None):
        """Sync guests from CloudBeds PMS"""
        endpoint = "/api/v1.1/getReservations"
        params = {
            'checkin_from': timezone.now().date().isoformat(),
            'checkin_to': (timezone.now().date() + timedelta(days=1)).isoformat(),
            'status': 'checked_in'
        }
        
        result = self._make_pms_request('GET', f"{endpoint}?{self._build_query_string(params)}")
        
        if result['success']:
            reservations = result['data'].get('data', [])
            synced_count = len(reservations)
            
            for reservation in reservations:
                guest_data = self._parse_cloudbeds_guest(reservation)
                self._create_or_update_guest_from_pms(guest_data, 'CLOUDBEDS')
            
            return {
                'success': True,
                'message': f'Synced {synced_count} guests from CloudBeds',
                'data': {'synced_count': synced_count}
            }
        
        return result
    
    def _create_cloudbeds_booking(self, booking_data):
        """Create note/request in CloudBeds PMS"""
        note_data = {
            'reservation_id': booking_data.get('pms_reservation_id'),
            'note': f"Transport Request: {booking_data['destination']} at {booking_data['pickup_datetime']}",
            'category': 'transport'
        }
        
        return self._make_pms_request('POST', '/api/v1.1/postReservationNote', note_data)
    
    def _send_cloudbeds_update(self, update_data):
        """Send update to CloudBeds PMS"""
        # CloudBeds doesn't have direct transport booking updates
        # We'll add a note to the reservation
        note_data = {
            'note': f"Transport Status: {update_data['status']} - {update_data.get('message', '')}",
            'category': 'transport'
        }
        
        return self._make_pms_request('POST', '/api/v1.1/postReservationNote', note_data)
    
    # Generic PMS Integration
    def _sync_generic_pms_guests(self, guest_id=None):
        """Generic PMS guest sync"""
        endpoint = "/guests" if not guest_id else f"/guests/{guest_id}"
        return self._make_pms_request('GET', endpoint)
    
    def _create_generic_pms_booking(self, booking_data):
        """Generic PMS booking creation"""
        return self._make_pms_request('POST', '/bookings', booking_data)
    
    def _send_generic_pms_update(self, update_data):
        """Generic PMS status update"""
        endpoint = f"/bookings/{update_data['booking_reference']}/status"
        return self._make_pms_request('PUT', endpoint, update_data)
    
    # Helper methods
    def _create_or_update_guest_from_pms(self, guest_data, pms_type):
        """Create or update guest from PMS data"""
        try:
            # Normalize guest data based on PMS type
            normalized_data = self._normalize_guest_data(guest_data, pms_type)
            
            # Find existing guest or create new one
            guest, created = HotelGuest.objects.update_or_create(
                hotel=self.hotel,
                pms_guest_id=normalized_data['pms_guest_id'],
                defaults=normalized_data
            )
            
            return guest
            
        except Exception as e:
            logger.error(f"Error creating/updating guest from PMS: {str(e)}")
            return None
    
    def _normalize_guest_data(self, guest_data, pms_type):
        """Normalize guest data from different PMS formats"""
        if pms_type == 'ORACLE_OPERA':
            return {
                'pms_guest_id': guest_data.get('guest_id', ''),
                'first_name': guest_data.get('first_name', ''),
                'last_name': guest_data.get('last_name', ''),
                'email': guest_data.get('email', ''),
                'phone': guest_data.get('phone', ''),
                'check_in_date': datetime.fromisoformat(guest_data.get('check_in')).date(),
                'check_out_date': datetime.fromisoformat(guest_data.get('check_out')).date(),
                'is_checked_in': guest_data.get('status') == 'checked_in',
                'pms_reservation_id': guest_data.get('reservation_id', '')
            }
        elif pms_type == 'FIDELIO':
            return {
                'pms_guest_id': str(guest_data.get('guest_id', '')),
                'first_name': guest_data.get('first_name', ''),
                'last_name': guest_data.get('surname', ''),
                'email': guest_data.get('email_address', ''),
                'phone': guest_data.get('phone_number', ''),
                'check_in_date': datetime.strptime(guest_data.get('arrival'), '%Y-%m-%d').date(),
                'check_out_date': datetime.strptime(guest_data.get('departure'), '%Y-%m-%d').date(),
                'is_checked_in': True,  # Fidelio sync only returns in-house guests
                'pms_reservation_id': guest_data.get('reservation_number', '')
            }
        elif pms_type == 'CLOUDBEDS':
            return self._parse_cloudbeds_guest(guest_data)
        else:
            # Generic format
            return {
                'pms_guest_id': str(guest_data.get('id', '')),
                'first_name': guest_data.get('first_name', ''),
                'last_name': guest_data.get('last_name', ''),
                'email': guest_data.get('email', ''),
                'phone': guest_data.get('phone', ''),
                'check_in_date': datetime.fromisoformat(guest_data.get('check_in')).date(),
                'check_out_date': datetime.fromisoformat(guest_data.get('check_out')).date(),
                'is_checked_in': guest_data.get('is_checked_in', False),
                'pms_reservation_id': guest_data.get('reservation_id', '')
            }
    
    def _parse_cloudbeds_guest(self, reservation_data):
        """Parse CloudBeds reservation data to guest format"""
        guest_info = reservation_data.get('guest', {})
        
        return {
            'pms_guest_id': str(reservation_data.get('reservationID', '')),
            'first_name': guest_info.get('guestFirstName', ''),
            'last_name': guest_info.get('guestLastName', ''),
            'email': guest_info.get('guestEmail', ''),
            'phone': guest_info.get('guestPhone', ''),
            'check_in_date': datetime.strptime(
                reservation_data.get('startDate'), '%Y-%m-%d'
            ).date(),
            'check_out_date': datetime.strptime(
                reservation_data.get('endDate'), '%Y-%m-%d'
            ).date(),
            'is_checked_in': reservation_data.get('status') == 'checked_in',
            'pms_reservation_id': str(reservation_data.get('reservationID', ''))
        }
    
    def _build_query_string(self, params):
        """Build query string from parameters"""
        return '&'.join([f"{key}={value}" for key, value in params.items()])


# Service factory function
def get_pms_service(hotel):
    """Get PMS integration service for hotel"""
    return PMSIntegrationService(hotel)
