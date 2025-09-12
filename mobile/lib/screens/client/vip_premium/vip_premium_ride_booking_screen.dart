import 'package:flutter/material.dart';
import '../../../models/ride_models.dart';
import '../../../services/ride_service.dart';

class VipPremiumRideBookingScreen extends StatefulWidget {
  const VipPremiumRideBookingScreen({super.key});

  @override
  State<VipPremiumRideBookingScreen> createState() =>
      _VipPremiumRideBookingScreenState();
}

class _VipPremiumRideBookingScreenState
    extends State<VipPremiumRideBookingScreen> {
  final RideService _rideService = RideService();
  final TextEditingController _pickupController = TextEditingController();
  final TextEditingController _destinationController = TextEditingController();
  final TextEditingController _specialRequestsController =
      TextEditingController();

  String _selectedVehicleType = 'luxury_sedan';
  String _selectedTimeSlot = 'now';
  bool _discreetMode = false;
  bool _encryptedTracking = true;
  bool _conciergeAssistance = false;
  bool _isLoading = false;

  final List<Map<String, dynamic>> _vehicleTypes = [
    {
      'id': 'luxury_sedan',
      'name': 'Executive Sedan',
      'description': 'BMW 7 Series, Mercedes S-Class',
      'icon': Icons.directions_car,
      'price': '₦15,000',
      'features': ['Leather Interior', 'WiFi', 'Privacy Glass'],
    },
    {
      'id': 'luxury_suv',
      'name': 'Luxury SUV',
      'description': 'Range Rover, Cadillac Escalade',
      'icon': Icons.directions_car_filled,
      'price': '₦25,000',
      'features': ['Spacious Interior', 'Enhanced Security', 'Premium Sound'],
    },
    {
      'id': 'armored_vehicle',
      'name': 'Armored Vehicle',
      'description': 'High-security transport',
      'icon': Icons.security,
      'price': '₦50,000',
      'features': [
        'Bulletproof Glass',
        'Armored Body',
        'Emergency Communication',
      ],
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Row(
          children: [
            Icon(Icons.diamond, color: Colors.amber),
            SizedBox(width: 10),
            Text(
              'VIP Premium Booking',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildVipPremiumHeader(),
            const SizedBox(height: 20),
            _buildLocationSection(),
            const SizedBox(height: 20),
            _buildVehicleSelection(),
            const SizedBox(height: 20),
            _buildTimeSelection(),
            const SizedBox(height: 20),
            _buildVipPremiumFeatures(),
            const SizedBox(height: 20),
            _buildSpecialRequests(),
            const SizedBox(height: 30),
            _buildBookingButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildVipPremiumHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Colors.amber, Colors.orange],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Row(
        children: [
          Icon(Icons.diamond, color: Colors.white, size: 24),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'VIP Premium Service',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Priority matching • Enhanced security • Discreet service',
                  style: TextStyle(color: Colors.white, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLocationSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Trip Details',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _pickupController,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              labelText: 'Pickup Location',
              labelStyle: const TextStyle(color: Colors.grey),
              prefixIcon: const Icon(Icons.my_location, color: Colors.amber),
              filled: true,
              fillColor: Colors.grey[700],
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _destinationController,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              labelText: 'Destination',
              labelStyle: const TextStyle(color: Colors.grey),
              prefixIcon: const Icon(Icons.location_on, color: Colors.amber),
              filled: true,
              fillColor: Colors.grey[700],
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVehicleSelection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Select Vehicle',
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ..._vehicleTypes.map((vehicle) => _buildVehicleCard(vehicle)),
      ],
    );
  }

  Widget _buildVehicleCard(Map<String, dynamic> vehicle) {
    final isSelected = _selectedVehicleType == vehicle['id'];

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: isSelected ? Colors.amber.withOpacity(0.1) : Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isSelected ? Colors.amber : Colors.transparent,
          width: 2,
        ),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: isSelected ? Colors.amber : Colors.grey[700],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            vehicle['icon'],
            color: isSelected ? Colors.black : Colors.white,
            size: 24,
          ),
        ),
        title: Text(
          vehicle['name'],
          style: TextStyle(
            color: isSelected ? Colors.amber : Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              vehicle['description'],
              style: const TextStyle(color: Colors.grey, fontSize: 14),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: (vehicle['features'] as List<String>)
                  .map(
                    (feature) => Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.grey[600],
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        feature,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              vehicle['price'],
              style: TextStyle(
                color: isSelected ? Colors.amber : Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Text(
              'Base fare',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
        onTap: () {
          setState(() {
            _selectedVehicleType = vehicle['id'];
          });
        },
      ),
    );
  }

  Widget _buildTimeSelection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'When do you need the ride?',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(child: _buildTimeOption('now', 'Now', Icons.flash_on)),
              const SizedBox(width: 12),
              Expanded(
                child: _buildTimeOption('schedule', 'Schedule', Icons.schedule),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTimeOption(String value, String label, IconData icon) {
    final isSelected = _selectedTimeSlot == value;

    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedTimeSlot = value;
        });
      },
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? Colors.amber.withOpacity(0.1) : Colors.grey[700],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? Colors.amber : Colors.transparent,
            width: 2,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.amber : Colors.white,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.amber : Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVipPremiumFeatures() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'VIP Premium Features',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          _buildFeatureToggle(
            title: 'Discreet Mode',
            subtitle: 'Minimal client details shared with driver',
            value: _discreetMode,
            onChanged: (value) => setState(() => _discreetMode = value),
            icon: Icons.visibility_off,
          ),
          const SizedBox(height: 12),
          _buildFeatureToggle(
            title: 'Encrypted Tracking',
            subtitle: 'Secure GPS monitoring for enhanced safety',
            value: _encryptedTracking,
            onChanged: (value) => setState(() => _encryptedTracking = value),
            icon: Icons.lock,
          ),
          const SizedBox(height: 12),
          _buildFeatureToggle(
            title: 'Concierge Assistance',
            subtitle: 'Personal assistant for trip coordination',
            value: _conciergeAssistance,
            onChanged: (value) => setState(() => _conciergeAssistance = value),
            icon: Icons.support_agent,
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureToggle({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
    required IconData icon,
  }) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.amber.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: Colors.amber, size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                subtitle,
                style: const TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ],
          ),
        ),
        Switch(
          value: value,
          onChanged: onChanged,
          activeThumbColor: Colors.amber,
          inactiveThumbColor: Colors.grey,
          inactiveTrackColor: Colors.grey[700],
        ),
      ],
    );
  }

  Widget _buildSpecialRequests() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Special Requests',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _specialRequestsController,
            style: const TextStyle(color: Colors.white),
            maxLines: 3,
            decoration: InputDecoration(
              hintText: 'Additional requirements or preferences...',
              hintStyle: const TextStyle(color: Colors.grey),
              filled: true,
              fillColor: Colors.grey[700],
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBookingButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _bookRide,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.amber,
          foregroundColor: Colors.black,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isLoading
            ? const SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.black),
                ),
              )
            : const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.diamond, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Book VIP Premium Ride',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
      ),
    );
  }

  Future<void> _bookRide() async {
    if (_pickupController.text.isEmpty || _destinationController.text.isEmpty) {
      _showErrorDialog('Please fill in pickup and destination locations');
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final rideRequest = RideRequest(
        pickup: LocationData(
          latitude: 0.0, // TODO: Use actual coordinates
          longitude: 0.0,
          address: _pickupController.text,
        ),
        destination: LocationData(
          latitude: 0.0, // TODO: Use actual coordinates
          longitude: 0.0,
          address: _destinationController.text,
        ),
        vehicleType: _selectedVehicleType,
        paymentMethod: 'card', // Default payment method
        isScheduled: _selectedTimeSlot == 'schedule',
        encryptedTracking: _encryptedTracking,
        specialRequests: _specialRequestsController.text,
        serviceLevel: 'vip_premium',
      );

      final response = await _rideService.bookRide(rideRequest);

      if (response.success) {
        _showSuccessDialog('VIP Premium ride booked successfully!');
      } else {
        _showErrorDialog(response.message ?? 'Failed to book ride');
      }
    } catch (e) {
      _showErrorDialog('An error occurred while booking the ride');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[800],
        title: const Text('Error', style: TextStyle(color: Colors.red)),
        content: Text(message, style: const TextStyle(color: Colors.white)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK', style: TextStyle(color: Colors.amber)),
          ),
        ],
      ),
    );
  }

  void _showSuccessDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[800],
        title: const Text('Success', style: TextStyle(color: Colors.green)),
        content: Text(message, style: const TextStyle(color: Colors.white)),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context); // Return to previous screen
            },
            child: const Text('OK', style: TextStyle(color: Colors.amber)),
          ),
        ],
      ),
    );
  }
}
