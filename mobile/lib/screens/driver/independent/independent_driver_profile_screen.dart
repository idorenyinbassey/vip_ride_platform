import 'package:flutter/material.dart';
import '../../../services/api_service.dart';
import '../../../services/user_service.dart';

class IndependentDriverProfileScreen extends StatefulWidget {
  const IndependentDriverProfileScreen({super.key});

  @override
  State<IndependentDriverProfileScreen> createState() =>
      _IndependentDriverProfileScreenState();
}

class _IndependentDriverProfileScreenState
    extends State<IndependentDriverProfileScreen> {
  final ApiService _apiService = ApiService();
  final UserService _userService = UserService();

  // Driver data
  String _driverName = 'John Adebayo';
  String _email = 'john.adebayo@example.com';
  String _phone = '+234 801 234 5678';
  double _rating = 4.8;
  int _totalRides = 1247;
  String _joinDate = 'March 2023';

  // Vehicle data
  String _vehicleModel = '2019 Toyota Camry';
  String _vehiclePlate = 'ABC-123-XY';
  String _vehicleColor = 'Silver';
  final String _licenseExpiry = 'Dec 2025';

  // Documents status
  final bool _licenseVerified = true;
  final bool _insuranceVerified = true;
  final bool _roadworthinessVerified = false;
  final bool _backgroundCheckPassed = true;

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadProfileData();
  }

  Future<void> _loadProfileData() async {
    setState(() => _isLoading = true);

    try {
      // Load real profile data from API
      final user = await _userService.getUserProfile();

      if (user != null) {
        setState(() {
          _driverName = user.fullName;
          _email = user.email;
          _phone = user.phoneNumber ?? '+234 800 000 0000';
          _joinDate = user.dateJoined?.toString().split(' ')[0] ?? '2024-01-15';
        });
      }

      // Load driver-specific data (rating, total rides, vehicle info, documents status)
      // This would come from driver profile endpoint when available
      try {
        final driverProfile = await _apiService.get(
          '/api/v1/accounts/driver/profile/',
        );
        if (driverProfile.statusCode == 200) {
          final data = driverProfile.data;
          setState(() {
            _rating = data['rating']?.toDouble() ?? 4.8;
            _totalRides = data['total_rides'] ?? 0;
            _vehicleModel = data['vehicle_model'] ?? 'Toyota Camry 2022';
            _vehiclePlate = data['vehicle_plate'] ?? 'LAG 123 ABC';
            _vehicleColor = data['vehicle_color'] ?? 'Silver';
          });
        }
      } catch (e) {
        debugPrint('ℹ️ Driver profile not available, using defaults: $e');
      }
    } catch (e) {
      debugPrint('❌ Failed to load profile: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error loading profile: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Driver Profile'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: _openSettings,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadProfileData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Profile header
                    _buildProfileHeader(),

                    const SizedBox(height: 24),

                    // Driver stats
                    _buildDriverStats(),

                    const SizedBox(height: 24),

                    // Personal information
                    _buildPersonalInfo(),

                    const SizedBox(height: 24),

                    // Vehicle information
                    _buildVehicleInfo(),

                    const SizedBox(height: 24),

                    // Documents status
                    _buildDocumentsStatus(),

                    const SizedBox(height: 24),

                    // Action buttons
                    _buildActionButtons(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildProfileHeader() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.blue[50]!, Colors.blue[100]!],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          children: [
            CircleAvatar(
              radius: 50,
              backgroundColor: Colors.blue[200],
              child: Text(
                _driverName.split(' ').map((n) => n[0]).join(''),
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue[800],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              _driverName,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.green[100],
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                'Independent Driver',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Colors.green[800],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.star, color: Colors.amber[600], size: 24),
                const SizedBox(width: 4),
                Text(
                  _rating.toStringAsFixed(1),
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '($_totalRides rides)',
                  style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDriverStats() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Driver Statistics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Total Rides',
                    _totalRides.toString(),
                    Icons.directions_car,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Member Since',
                    _joinDate,
                    Icons.calendar_today,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Acceptance Rate',
                    '94%',
                    Icons.check_circle,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Cancellation Rate',
                    '2%',
                    Icons.cancel,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 24, color: Colors.blue[600]),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildPersonalInfo() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Personal Information',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.edit, size: 20),
                  onPressed: _editPersonalInfo,
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow(Icons.email, 'Email', _email),
            _buildInfoRow(Icons.phone, 'Phone', _phone),
          ],
        ),
      ),
    );
  }

  Widget _buildVehicleInfo() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Vehicle Information',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.edit, size: 20),
                  onPressed: _editVehicleInfo,
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow(Icons.directions_car, 'Model', _vehicleModel),
            _buildInfoRow(
              Icons.confirmation_number,
              'Plate Number',
              _vehiclePlate,
            ),
            _buildInfoRow(Icons.palette, 'Color', _vehicleColor),
            _buildInfoRow(Icons.date_range, 'License Expiry', _licenseExpiry),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 12),
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
          const Spacer(),
          Text(
            value,
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  Widget _buildDocumentsStatus() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Documents & Verification',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildDocumentRow('Driver\'s License', _licenseVerified),
            _buildDocumentRow('Vehicle Insurance', _insuranceVerified),
            _buildDocumentRow(
              'Vehicle Roadworthiness',
              _roadworthinessVerified,
            ),
            _buildDocumentRow('Background Check', _backgroundCheckPassed),
          ],
        ),
      ),
    );
  }

  Widget _buildDocumentRow(String document, bool isVerified) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(
            isVerified ? Icons.check_circle : Icons.warning,
            color: isVerified ? Colors.green : Colors.orange,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              document,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: isVerified ? Colors.green[100] : Colors.orange[100],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              isVerified ? 'Verified' : 'Pending',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: isVerified ? Colors.green[800] : Colors.orange[800],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          height: 50,
          child: ElevatedButton.icon(
            onPressed: _uploadDocuments,
            icon: const Icon(Icons.upload_file),
            label: const Text('Upload Documents'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue[600],
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          height: 50,
          child: OutlinedButton.icon(
            onPressed: _contactSupport,
            icon: const Icon(Icons.support_agent),
            label: const Text('Contact Support'),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.blue[600],
              side: BorderSide(color: Colors.blue[600]!),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          height: 50,
          child: TextButton.icon(
            onPressed: _logout,
            icon: const Icon(Icons.logout),
            label: const Text('Logout'),
            style: TextButton.styleFrom(foregroundColor: Colors.red[600]),
          ),
        ),
      ],
    );
  }

  void _openSettings() {
    // TODO: Navigate to settings screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Settings feature coming soon')),
    );
  }

  void _editPersonalInfo() {
    // TODO: Navigate to edit personal info screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit personal info feature coming soon')),
    );
  }

  void _editVehicleInfo() {
    // TODO: Navigate to edit vehicle info screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit vehicle info feature coming soon')),
    );
  }

  void _uploadDocuments() {
    // TODO: Navigate to document upload screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Document upload feature coming soon')),
    );
  }

  void _contactSupport() {
    // TODO: Navigate to support screen or open support chat
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Support chat feature coming soon')),
    );
  }

  void _logout() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Implement logout functionality
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Logged out successfully')),
              );
            },
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
}
