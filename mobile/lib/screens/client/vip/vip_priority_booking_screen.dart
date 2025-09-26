import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';
import '../../../services/api_service.dart';
import '../../../widgets/map/live_map_widget.dart';

class VipPriorityBookingScreen extends StatefulWidget {
  const VipPriorityBookingScreen({super.key});

  @override
  State<VipPriorityBookingScreen> createState() =>
      _VipPriorityBookingScreenState();
}

class _VipPriorityBookingScreenState extends State<VipPriorityBookingScreen> {
  final ApiService _apiService = ApiService();

  final TextEditingController _pickupController = TextEditingController();
  final TextEditingController _dropoffController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();

  bool _isLoading = false;
  bool _discreteMode = false;
  bool _priorityMatching = true;
  bool _premiumVehiclesOnly = true;

  String _selectedVehicleType = 'executive_sedan';
  String _selectedBookingType = 'now';
  DateTime? _scheduledDateTime;

  // Available premium vehicles
  List<Map<String, dynamic>> _vehicleTypes = [];
  List<Map<String, dynamic>> _availableDrivers = [];
  Map<String, dynamic>? _selectedDriver;
  Map<String, dynamic> _fareEstimate = {};

  @override
  void initState() {
    super.initState();
    _loadBookingData();
  }

  Future<void> _loadBookingData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real booking data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _vehicleTypes = [
          {
            'id': 'executive_sedan',
            'name': 'Executive Sedan',
            'description': 'Luxury sedan for business',
            'models': ['Mercedes E-Class', 'BMW 5 Series', 'Audi A6'],
            'capacity': 4,
            'price_multiplier': 1.5,
            'features': ['Wi-Fi', 'Premium Sound', 'Climate Control'],
            'image': 'sedan.png',
          },
          {
            'id': 'luxury_suv',
            'name': 'Luxury SUV',
            'description': 'Spacious premium SUV',
            'models': ['Mercedes GLE', 'BMW X5', 'Audi Q7'],
            'capacity': 6,
            'price_multiplier': 2.0,
            'features': ['Wi-Fi', 'Premium Sound', 'Privacy Glass'],
            'image': 'suv.png',
          },
          {
            'id': 'premium_van',
            'name': 'Premium Van',
            'description': 'Executive transport for groups',
            'models': ['Mercedes V-Class', 'Toyota Hiace Executive'],
            'capacity': 8,
            'price_multiplier': 2.5,
            'features': ['Wi-Fi', 'Conference Setup', 'Refreshments'],
            'image': 'van.png',
          },
          {
            'id': 'luxury_coupe',
            'name': 'Luxury Coupe',
            'description': 'High-end sports luxury',
            'models': ['Mercedes S-Coupe', 'BMW 8 Series'],
            'capacity': 2,
            'price_multiplier': 3.0,
            'features': ['Premium Sound', 'Heated Seats', 'Champagne Service'],
            'image': 'coupe.png',
          },
        ];

        _availableDrivers = [
          {
            'id': 'vip_driver_001',
            'name': 'James Okafor',
            'rating': 4.9,
            'experience_years': 8,
            'vip_rides': 1250,
            'vehicle_type': 'executive_sedan',
            'vehicle_model': '2023 Mercedes E-Class',
            'specialties': [
              'Business meetings',
              'Airport transfers',
              'Discrete service',
            ],
            'languages': ['English', 'Yoruba'],
            'available': true,
            'eta_minutes': 5,
            'location': {'lat': 6.5244, 'lng': 3.3792},
          },
          {
            'id': 'vip_driver_002',
            'name': 'David Adebayo',
            'rating': 4.8,
            'experience_years': 6,
            'vip_rides': 890,
            'vehicle_type': 'luxury_suv',
            'vehicle_model': '2022 BMW X5',
            'specialties': [
              'Evening events',
              'Family transport',
              'Long distance',
            ],
            'languages': ['English', 'Hausa'],
            'available': true,
            'eta_minutes': 8,
            'location': {'lat': 6.5300, 'lng': 3.3850},
          },
        ];

        _fareEstimate = {
          'base_fare': 3500.0,
          'vip_premium': 1500.0,
          'vehicle_premium': 2000.0,
          'priority_fee': 500.0,
          'total_estimate': 7500.0,
          'currency': 'NGN',
        };
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading booking data: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.amber[600]!, Colors.amber[800]!],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.flash_on, color: Colors.white, size: 14),
                  const SizedBox(width: 4),
                  Text(
                    'PRIORITY',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            const Text('VIP Booking'),
          ],
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: Icon(
              _discreteMode ? Icons.visibility_off : Icons.visibility,
              color: _discreteMode ? Colors.amber[600] : Colors.grey[600],
            ),
            onPressed: () {
              setState(() {
                _discreteMode = !_discreteMode;
              });
            },
            tooltip: 'Discrete Mode',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // VIP Settings Card
                  _buildVipSettingsCard(),

                  const SizedBox(height: 20),

                  // Location inputs
                  _buildLocationInputsCard(),

                  const SizedBox(height: 20),

                  // Booking type selection
                  _buildBookingTypeCard(),

                  const SizedBox(height: 20),

                  // Vehicle selection
                  _buildVehicleSelectionCard(),

                  const SizedBox(height: 20),

                  // Available VIP drivers
                  _buildAvailableDriversCard(),

                  const SizedBox(height: 20),

                  // Live map
                  _buildLiveMapCard(),

                  const SizedBox(height: 20),

                  // Fare estimate
                  _buildFareEstimateCard(),

                  const SizedBox(height: 20),

                  // Additional preferences
                  _buildAdditionalPreferencesCard(),

                  const SizedBox(height: 20),

                  // Book button
                  _buildBookingButton(),
                ],
              ),
            ),
    );
  }

  Widget _buildVipSettingsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.settings, color: Colors.amber[600]),
                const SizedBox(width: 8),
                Text(
                  'VIP Preferences',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Discrete mode
            _buildPreferenceToggle(
              'Discrete Mode',
              'Hide your identity from driver until pickup',
              _discreteMode,
              Icons.visibility_off,
              (value) => setState(() => _discreteMode = value),
            ),

            const SizedBox(height: 12),

            // Priority matching
            _buildPreferenceToggle(
              'Priority Matching',
              'Get matched with top-rated VIP drivers',
              _priorityMatching,
              Icons.flash_on,
              (value) => setState(() => _priorityMatching = value),
            ),

            const SizedBox(height: 12),

            // Premium vehicles only
            _buildPreferenceToggle(
              'Premium Vehicles Only',
              'Only show luxury vehicles',
              _premiumVehiclesOnly,
              Icons.diamond,
              (value) => setState(() => _premiumVehiclesOnly = value),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationInputsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.location_on, color: Colors.blue[600]),
                const SizedBox(width: 8),
                Text(
                  'Trip Details',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Pickup location
            Container(
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.green[200]!),
              ),
              child: TextField(
                controller: _pickupController,
                decoration: InputDecoration(
                  hintText: 'Pickup location',
                  prefixIcon: Icon(
                    Icons.radio_button_checked,
                    color: Colors.green[600],
                  ),
                  suffixIcon: IconButton(
                    icon: Icon(Icons.my_location, color: Colors.green[600]),
                    onPressed: _useCurrentLocation,
                  ),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.all(16),
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Dropoff location
            Container(
              decoration: BoxDecoration(
                color: Colors.red[50],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.red[200]!),
              ),
              child: TextField(
                controller: _dropoffController,
                decoration: InputDecoration(
                  hintText: 'Destination',
                  prefixIcon: Icon(Icons.location_on, color: Colors.red[600]),
                  suffixIcon: IconButton(
                    icon: Icon(Icons.search, color: Colors.red[600]),
                    onPressed: _searchDestination,
                  ),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.all(16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBookingTypeCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'When do you need the ride?',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: _buildBookingTypeOption(
                    'now',
                    'Now',
                    'Get a ride immediately',
                    Icons.flash_on,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildBookingTypeOption(
                    'scheduled',
                    'Schedule',
                    'Book for later',
                    Icons.schedule,
                  ),
                ),
              ],
            ),

            if (_selectedBookingType == 'scheduled') ...[
              const SizedBox(height: 16),
              _buildDateTimeSelector(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildVehicleSelectionCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Select Vehicle Type',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),

            const SizedBox(height: 16),

            ...(_premiumVehiclesOnly ? _vehicleTypes : _vehicleTypes.take(2))
                .map((vehicle) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _buildVehicleOption(vehicle),
                  );
                }),
          ],
        ),
      ),
    );
  }

  Widget _buildAvailableDriversCard() {
    if (!_priorityMatching) return const SizedBox.shrink();

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.person_pin, color: Colors.green[600]),
                const SizedBox(width: 8),
                Text(
                  'Available VIP Drivers',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            ..._availableDrivers
                .where((driver) {
                  return _premiumVehiclesOnly
                      ? driver['vehicle_type'] == _selectedVehicleType
                      : true;
                })
                .map((driver) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _buildDriverOption(driver),
                  );
                }),
          ],
        ),
      ),
    );
  }

  Widget _buildLiveMapCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(Icons.map, color: Colors.blue[600]),
                const SizedBox(width: 8),
                Text(
                  'VIP Drivers Near You',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
              ],
            ),
          ),
          Container(
            height: 200,
            margin: const EdgeInsets.only(left: 16, right: 16, bottom: 16),
            decoration: BoxDecoration(borderRadius: BorderRadius.circular(12)),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: const LiveMapWidget(
                showNearbyDrivers: true,
                currentLocation: LatLng(6.5244, 3.3792),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFareEstimateCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Fare Estimate',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),

            const SizedBox(height: 16),

            _buildFareBreakdownItem('Base Fare', _fareEstimate['base_fare']),
            _buildFareBreakdownItem(
              'VIP Premium',
              _fareEstimate['vip_premium'],
            ),
            _buildFareBreakdownItem(
              'Vehicle Premium',
              _fareEstimate['vehicle_premium'],
            ),
            if (_priorityMatching)
              _buildFareBreakdownItem(
                'Priority Fee',
                _fareEstimate['priority_fee'],
              ),

            const Divider(height: 20),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Total Estimate',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  '₦${_fareEstimate['total_estimate']?.toStringAsFixed(0) ?? '0'}',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.green[600],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 8),

            Text(
              'Final fare may vary based on actual distance and time',
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAdditionalPreferencesCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Additional Notes',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),

            const SizedBox(height: 16),

            TextField(
              controller: _notesController,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Special requests, preferred route, etc.',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.grey[300]!),
                ),
                contentPadding: const EdgeInsets.all(16),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBookingButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _bookVipRide,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.amber[600],
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 3,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.flash_on, size: 20),
            const SizedBox(width: 8),
            Text(
              _selectedBookingType == 'now'
                  ? 'Book VIP Ride Now'
                  : 'Schedule VIP Ride',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }

  // Helper widgets
  Widget _buildPreferenceToggle(
    String title,
    String subtitle,
    bool value,
    IconData icon,
    Function(bool) onChanged,
  ) {
    return Row(
      children: [
        Icon(
          icon,
          color: value ? Colors.amber[600] : Colors.grey[600],
          size: 20,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                subtitle,
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
        Switch(
          value: value,
          onChanged: onChanged,
          activeThumbColor: Colors.amber[600],
        ),
      ],
    );
  }

  Widget _buildBookingTypeOption(
    String type,
    String title,
    String subtitle,
    IconData icon,
  ) {
    final isSelected = _selectedBookingType == type;

    return GestureDetector(
      onTap: () => setState(() => _selectedBookingType = type),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue[50] : Colors.grey[50],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? Colors.blue[300]! : Colors.grey[300]!,
            width: 2,
          ),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.blue[600] : Colors.grey[600],
              size: 24,
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: isSelected ? Colors.blue[600] : Colors.grey[600],
              ),
            ),
            Text(
              subtitle,
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDateTimeSelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Row(
        children: [
          Icon(Icons.access_time, color: Colors.blue[600]),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _scheduledDateTime != null
                  ? '${_scheduledDateTime!.day}/${_scheduledDateTime!.month}/${_scheduledDateTime!.year} at ${_scheduledDateTime!.hour}:${_scheduledDateTime!.minute.toString().padLeft(2, '0')}'
                  : 'Select date and time',
              style: TextStyle(fontSize: 14, color: Colors.blue[600]),
            ),
          ),
          TextButton(onPressed: _selectDateTime, child: const Text('Select')),
        ],
      ),
    );
  }

  Widget _buildVehicleOption(Map<String, dynamic> vehicle) {
    final isSelected = _selectedVehicleType == vehicle['id'];

    return GestureDetector(
      onTap: () => setState(() => _selectedVehicleType = vehicle['id']),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.purple[50] : Colors.grey[50],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? Colors.purple[300]! : Colors.grey[300]!,
            width: 2,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                color: isSelected ? Colors.purple[100] : Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.directions_car,
                color: isSelected ? Colors.purple[600] : Colors.grey[600],
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    vehicle['name'],
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: isSelected ? Colors.purple[600] : Colors.grey[800],
                    ),
                  ),
                  Text(
                    vehicle['description'],
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  Text(
                    '${vehicle['capacity']} passengers • ${vehicle['models'].join(', ')}',
                    style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '+${((vehicle['price_multiplier'] - 1) * 100).toInt()}%',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: isSelected ? Colors.purple[600] : Colors.grey[600],
                  ),
                ),
                Text(
                  'premium',
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDriverOption(Map<String, dynamic> driver) {
    final isSelected = _selectedDriver?['id'] == driver['id'];

    return GestureDetector(
      onTap: () => setState(() => _selectedDriver = isSelected ? null : driver),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.green[50] : Colors.grey[50],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? Colors.green[300]! : Colors.grey[300]!,
            width: 2,
          ),
        ),
        child: Row(
          children: [
            CircleAvatar(
              radius: 25,
              backgroundColor: isSelected
                  ? Colors.green[100]
                  : Colors.grey[200],
              child: Text(
                driver['name'][0],
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: isSelected ? Colors.green[600] : Colors.grey[600],
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    driver['name'],
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: isSelected ? Colors.green[600] : Colors.grey[800],
                    ),
                  ),
                  Text(
                    '${driver['rating']}⭐ • ${driver['vip_rides']} VIP rides',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  Text(
                    driver['vehicle_model'],
                    style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.green[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${driver['eta_minutes']} min',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: Colors.green[600],
                    ),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'ETA',
                  style: TextStyle(fontSize: 8, color: Colors.grey[600]),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFareBreakdownItem(String label, double? amount) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontSize: 14, color: Colors.grey[600])),
          Text(
            '₦${amount?.toStringAsFixed(0) ?? '0'}',
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  // Event handlers
  void _useCurrentLocation() {
    // TODO: Get current location
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Getting current location...')),
    );
  }

  void _searchDestination() {
    // TODO: Open destination search
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Search destination feature coming soon')),
    );
  }

  void _selectDateTime() async {
    final date = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(hours: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 30)),
    );

    if (date != null) {
      final time = await showTimePicker(
        context: context,
        initialTime: TimeOfDay.now(),
      );

      if (time != null) {
        setState(() {
          _scheduledDateTime = DateTime(
            date.year,
            date.month,
            date.day,
            time.hour,
            time.minute,
          );
        });
      }
    }
  }

  void _bookVipRide() {
    if (_pickupController.text.isEmpty || _dropoffController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter pickup and destination')),
      );
      return;
    }

    // TODO: Process VIP booking
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green[600]),
            const SizedBox(width: 8),
            const Text('VIP Booking Confirmed'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Your VIP ride has been ${_selectedBookingType == 'now' ? 'booked' : 'scheduled'}.',
            ),
            const SizedBox(height: 8),
            if (_selectedDriver != null)
              Text('Driver: ${_selectedDriver!['name']}'),
            Text(
              'Vehicle: ${_vehicleTypes.firstWhere((v) => v['id'] == _selectedVehicleType)['name']}',
            ),
            if (_discreteMode) Text('Mode: Discrete booking enabled'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}
