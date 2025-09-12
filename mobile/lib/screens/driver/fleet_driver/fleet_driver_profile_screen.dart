import 'package:flutter/material.dart';
import '../../../services/api_service.dart';

class FleetDriverProfileScreen extends StatefulWidget {
  const FleetDriverProfileScreen({super.key});

  @override
  State<FleetDriverProfileScreen> createState() =>
      _FleetDriverProfileScreenState();
}

class _FleetDriverProfileScreenState extends State<FleetDriverProfileScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;

  // Driver information
  Map<String, dynamic> _driverInfo = {};
  Map<String, dynamic> _fleetInfo = {};
  Map<String, dynamic> _vehicleInfo = {};
  Map<String, dynamic> _documents = {};

  @override
  void initState() {
    super.initState();
    _loadProfileData();
  }

  Future<void> _loadProfileData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real profile data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _driverInfo = {
          'name': 'Sarah Ahmed',
          'email': 'sarah.ahmed@email.com',
          'phone': '+234 703 987 6543',
          'profile_image': null,
          'rating': 4.8,
          'total_rides': 189,
          'member_since': '2023-08-22',
          'status': 'active',
          'address': '45 Lagos Island, Lagos State',
          'emergency_contact': '+234 803 111 2222',
        };

        _fleetInfo = {
          'name': 'Lagos Premier Fleet',
          'manager': 'John Doe',
          'contact': '+234 803 456 7890',
          'email': 'manager@lagospremier.com',
          'commission_rate': 20.0,
          'contract_start': '2023-08-22',
          'contract_type': 'Fleet Driver',
        };

        _vehicleInfo = {
          'plate_number': 'DEF-456-ZW',
          'make': 'Toyota',
          'model': 'Camry',
          'year': 2021,
          'color': 'Silver',
          'assigned_date': '2023-08-22',
          'fuel_type': 'Petrol',
          'transmission': 'Automatic',
          'insurance_expiry': '2024-11-30',
          'last_maintenance': '2024-02-01',
          'next_maintenance_due': '2024-05-01',
        };

        _documents = {
          'drivers_license': {
            'status': 'valid',
            'expiry_date': '2026-12-15',
            'license_number': 'LOS/2021/ABC123',
          },
          'vehicle_permit': {
            'status': 'valid',
            'expiry_date': '2024-08-30',
            'permit_number': 'VP/2023/DEF456',
          },
          'background_check': {
            'status': 'valid',
            'completion_date': '2023-08-15',
            'certificate_number': 'BC/2023/789',
          },
          'medical_certificate': {
            'status': 'valid',
            'expiry_date': '2024-08-22',
            'certificate_number': 'MC/2023/456',
          },
        };
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading profile: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(icon: const Icon(Icons.edit), onPressed: _editProfile),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadProfileData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Profile header
                    _buildProfileHeader(),

                    const SizedBox(height: 24),

                    // Fleet information
                    _buildFleetInfoCard(),

                    const SizedBox(height: 24),

                    // Vehicle information
                    _buildVehicleInfoCard(),

                    const SizedBox(height: 24),

                    // Documents
                    _buildDocumentsCard(),

                    const SizedBox(height: 24),

                    // Account settings
                    _buildAccountSettingsCard(),

                    const SizedBox(height: 24),

                    // Support and help
                    _buildSupportCard(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildProfileHeader() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            // Profile picture
            CircleAvatar(
              radius: 40,
              backgroundColor: Colors.blue[100],
              child: _driverInfo['profile_image'] != null
                  ? Image.network(_driverInfo['profile_image'])
                  : Text(
                      _driverInfo['name']?[0] ?? 'S',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue[600],
                      ),
                    ),
            ),

            const SizedBox(width: 20),

            // Profile info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _driverInfo['name'] ?? 'Unknown',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Fleet Driver',
                    style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.star, color: Colors.amber[600], size: 20),
                      const SizedBox(width: 4),
                      Text(
                        '${_driverInfo['rating'] ?? 0.0}',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Text(
                        '${_driverInfo['total_rides'] ?? 0} rides',
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Status badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.green[100],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _driverInfo['status']?.toUpperCase() ?? 'ACTIVE',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.green[600],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFleetInfoCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.business, color: Colors.blue[600]),
                const SizedBox(width: 8),
                const Text(
                  'Fleet Information',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('Fleet Name', _fleetInfo['name'] ?? 'N/A'),
            const SizedBox(height: 8),
            _buildInfoRow('Manager', _fleetInfo['manager'] ?? 'N/A'),
            const SizedBox(height: 8),
            _buildInfoRow('Contact', _fleetInfo['contact'] ?? 'N/A'),
            const SizedBox(height: 8),
            _buildInfoRow('Email', _fleetInfo['email'] ?? 'N/A'),
            const SizedBox(height: 8),
            _buildInfoRow(
              'Commission Rate',
              '${_fleetInfo['commission_rate'] ?? 0}%',
            ),
            const SizedBox(height: 8),
            _buildInfoRow(
              'Contract Start',
              _fleetInfo['contract_start'] ?? 'N/A',
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _contactFleetManager,
                icon: const Icon(Icons.phone),
                label: const Text('Contact Fleet Manager'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.blue[600],
                  side: BorderSide(color: Colors.blue[300]!),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVehicleInfoCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.directions_car, color: Colors.orange[600]),
                const SizedBox(width: 8),
                const Text(
                  'Assigned Vehicle',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Vehicle header
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.directions_car,
                    size: 40,
                    color: Colors.orange[600],
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _vehicleInfo['plate_number'] ?? 'N/A',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '${_vehicleInfo['year']} ${_vehicleInfo['make']} ${_vehicleInfo['model']}',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Vehicle details
            Row(
              children: [
                Expanded(
                  child: _buildVehicleDetail(
                    'Color',
                    _vehicleInfo['color'] ?? 'N/A',
                  ),
                ),
                Expanded(
                  child: _buildVehicleDetail(
                    'Fuel Type',
                    _vehicleInfo['fuel_type'] ?? 'N/A',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildVehicleDetail(
                    'Transmission',
                    _vehicleInfo['transmission'] ?? 'N/A',
                  ),
                ),
                Expanded(
                  child: _buildVehicleDetail(
                    'Assigned',
                    _vehicleInfo['assigned_date'] ?? 'N/A',
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Maintenance info
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue[200]!),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.build, size: 16, color: Colors.blue[600]),
                      const SizedBox(width: 8),
                      Text(
                        'Maintenance Schedule',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Colors.blue[600],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Last Service: ${_vehicleInfo['last_maintenance'] ?? 'N/A'}',
                    style: TextStyle(fontSize: 12, color: Colors.blue[600]),
                  ),
                  Text(
                    'Next Service: ${_vehicleInfo['next_maintenance_due'] ?? 'N/A'}',
                    style: TextStyle(fontSize: 12, color: Colors.blue[600]),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDocumentsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.folder, color: Colors.purple[600]),
                const SizedBox(width: 8),
                const Text(
                  'Documents',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            ..._documents.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildDocumentItem(
                  _getDocumentDisplayName(entry.key),
                  entry.value,
                ),
              );
            }),

            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _uploadDocuments,
                icon: const Icon(Icons.upload_file),
                label: const Text('Upload Documents'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.purple[600],
                  side: BorderSide(color: Colors.purple[300]!),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAccountSettingsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.settings, color: Colors.grey[600]),
                const SizedBox(width: 8),
                const Text(
                  'Account Settings',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            _buildSettingItem(
              'Personal Information',
              'Update your profile details',
              Icons.person,
              _editPersonalInfo,
            ),
            const SizedBox(height: 12),
            _buildSettingItem(
              'Notification Settings',
              'Manage your notification preferences',
              Icons.notifications,
              _editNotificationSettings,
            ),
            const SizedBox(height: 12),
            _buildSettingItem(
              'Security Settings',
              'Change password and security options',
              Icons.security,
              _editSecuritySettings,
            ),
            const SizedBox(height: 12),
            _buildSettingItem(
              'Banking Information',
              'Update payout account details',
              Icons.account_balance,
              _editBankingInfo,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSupportCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.help, color: Colors.green[600]),
                const SizedBox(width: 8),
                const Text(
                  'Support & Help',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: _buildSupportButton(
                    'Help Center',
                    Icons.help_center,
                    Colors.blue,
                    _openHelpCenter,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildSupportButton(
                    'Contact Support',
                    Icons.support_agent,
                    Colors.green,
                    _contactSupport,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildSupportButton(
                    'Emergency',
                    Icons.emergency,
                    Colors.red,
                    _triggerEmergency,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildSupportButton(
                    'Report Issue',
                    Icons.report_problem,
                    Colors.orange,
                    _reportIssue,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(fontSize: 14, color: Colors.grey[600])),
        Flexible(
          child: Text(
            value,
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }

  Widget _buildVehicleDetail(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }

  Widget _buildDocumentItem(String name, Map<String, dynamic> document) {
    final status = document['status'] as String;
    final isValid = status == 'valid';
    final color = isValid ? Colors.green : Colors.red;

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(
            isValid ? Icons.check_circle : Icons.error,
            color: color,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (document['expiry_date'] != null)
                  Text(
                    'Expires: ${document['expiry_date']}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
              ],
            ),
          ),
          Text(
            status.toUpperCase(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingItem(
    String title,
    String subtitle,
    IconData icon,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Row(
          children: [
            Icon(icon, color: Colors.grey[600]),
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
            Icon(Icons.chevron_right, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  Widget _buildSupportButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onPressed,
  ) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      child: Column(
        children: [
          Icon(icon, size: 20),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  String _getDocumentDisplayName(String key) {
    switch (key) {
      case 'drivers_license':
        return 'Driver\'s License';
      case 'vehicle_permit':
        return 'Vehicle Permit';
      case 'background_check':
        return 'Background Check';
      case 'medical_certificate':
        return 'Medical Certificate';
      default:
        return key.replaceAll('_', ' ').toUpperCase();
    }
  }

  void _editProfile() {
    // TODO: Navigate to edit profile screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit profile feature coming soon')),
    );
  }

  void _contactFleetManager() {
    // TODO: Contact fleet manager
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Contacting fleet manager...')),
    );
  }

  void _uploadDocuments() {
    // TODO: Upload documents
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Document upload feature coming soon')),
    );
  }

  void _editPersonalInfo() {
    // TODO: Edit personal information
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit personal info feature coming soon')),
    );
  }

  void _editNotificationSettings() {
    // TODO: Edit notification settings
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Notification settings feature coming soon'),
      ),
    );
  }

  void _editSecuritySettings() {
    // TODO: Edit security settings
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Security settings feature coming soon')),
    );
  }

  void _editBankingInfo() {
    // TODO: Edit banking information
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Banking info feature coming soon')),
    );
  }

  void _openHelpCenter() {
    // TODO: Open help center
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Help center feature coming soon')),
    );
  }

  void _contactSupport() {
    // TODO: Contact support
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Contacting support...')));
  }

  void _triggerEmergency() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Emergency Alert'),
        content: const Text(
          'This will send an emergency alert to your fleet manager and emergency services. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Trigger emergency alert
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Emergency alert sent'),
                  backgroundColor: Colors.red,
                ),
              );
            },
            child: const Text(
              'Send Alert',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

  void _reportIssue() {
    // TODO: Report issue
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Issue reporting feature coming soon')),
    );
  }
}
