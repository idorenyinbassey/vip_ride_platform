import 'package:flutter/material.dart';
import '../../../services/api_service.dart';

class LeasedDriverProfileScreen extends StatefulWidget {
  const LeasedDriverProfileScreen({super.key});

  @override
  State<LeasedDriverProfileScreen> createState() =>
      _LeasedDriverProfileScreenState();
}

class _LeasedDriverProfileScreenState extends State<LeasedDriverProfileScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;

  // Driver information
  Map<String, dynamic> _driverInfo = {};
  Map<String, dynamic> _leaseContract = {};
  Map<String, dynamic> _vehicleInfo = {};
  Map<String, dynamic> _documents = {};
  Map<String, dynamic> _paymentInfo = {};

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
          'name': 'Michael Johnson',
          'email': 'michael.johnson@email.com',
          'phone': '+234 802 555 1234',
          'profile_image': null,
          'rating': 4.7,
          'total_rides': 156,
          'member_since': '2024-01-15',
          'status': 'active',
          'address': '78 Surulere Road, Lagos State',
          'emergency_contact': '+234 803 777 8888',
        };

        _leaseContract = {
          'contract_id': 'LC/2024/EVL/001',
          'lessor_name': 'Elite Vehicle Leasing',
          'lessor_contact': '+234 803 555 7777',
          'lessor_email': 'contracts@elitevl.com',
          'start_date': '2024-01-15',
          'end_date': '2024-07-15',
          'duration_months': 6,
          'daily_fee': 15000.0,
          'revenue_split': 70.0, // Driver gets 70%
          'payment_schedule': 'daily',
          'contract_status': 'active',
          'renewal_option': 'available',
          'contract_type': 'vehicle_lease',
        };

        _vehicleInfo = {
          'plate_number': 'GHI-789-XY',
          'make': 'Honda',
          'model': 'Accord',
          'year': 2022,
          'color': 'Black',
          'vin': 'JHMCM56557C404453',
          'lease_start': '2024-01-15',
          'fuel_type': 'Petrol',
          'transmission': 'Automatic',
          'insurance_provider': 'Elite Insurance Co.',
          'insurance_expiry': '2024-12-31',
          'last_maintenance': '2024-02-15',
          'next_maintenance_due': '2024-05-15',
          'condition': 'excellent',
        };

        _documents = {
          'drivers_license': {
            'status': 'valid',
            'expiry_date': '2026-10-20',
            'license_number': 'LOS/2022/MJ456',
          },
          'lease_agreement': {
            'status': 'valid',
            'signed_date': '2024-01-15',
            'document_number': 'LC/2024/EVL/001',
          },
          'vehicle_handover': {
            'status': 'valid',
            'completion_date': '2024-01-15',
            'document_number': 'VH/2024/001',
          },
          'insurance_certificate': {
            'status': 'valid',
            'expiry_date': '2024-12-31',
            'policy_number': 'EIC/2024/789',
          },
          'background_check': {
            'status': 'valid',
            'completion_date': '2024-01-10',
            'certificate_number': 'BC/2024/156',
          },
        };

        _paymentInfo = {
          'bank_name': 'Access Bank',
          'account_number': '0123456789',
          'account_name': 'Michael Johnson',
          'payout_method': 'bank_transfer',
          'last_payout': '2024-03-10',
          'total_payouts': 42850.0,
          'pending_amount': 4950.0,
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

                    // Lease contract information
                    _buildLeaseContractCard(),

                    const SizedBox(height: 24),

                    // Leased vehicle information
                    _buildVehicleInfoCard(),

                    const SizedBox(height: 24),

                    // Payment information
                    _buildPaymentInfoCard(),

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
                      _driverInfo['name']?[0] ?? 'M',
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
                    'Leased Driver',
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

  Widget _buildLeaseContractCard() {
    final daysRemaining = DateTime.parse(
      _leaseContract['end_date'],
    ).difference(DateTime.now()).inDays;
    final isNearExpiry = daysRemaining <= 30;

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
                Icon(Icons.assignment, color: Colors.purple[600]),
                const SizedBox(width: 8),
                const Text(
                  'Lease Contract',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: _leaseContract['contract_status'] == 'active'
                        ? Colors.green[100]
                        : Colors.red[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _leaseContract['contract_status']
                            ?.toString()
                            .toUpperCase() ??
                        'ACTIVE',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: _leaseContract['contract_status'] == 'active'
                          ? Colors.green[600]
                          : Colors.red[600],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Contract ID
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.purple[50],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.confirmation_number,
                    color: Colors.purple[600],
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Contract ID: ${_leaseContract['contract_id']}',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: Colors.purple[600],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Lessor information
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _leaseContract['lessor_name'] ?? 'Unknown Lessor',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  _buildInfoRow(
                    'Contact',
                    _leaseContract['lessor_contact'] ?? 'N/A',
                  ),
                  const SizedBox(height: 4),
                  _buildInfoRow(
                    'Email',
                    _leaseContract['lessor_email'] ?? 'N/A',
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Contract terms
            Row(
              children: [
                Expanded(
                  child: _buildContractMetric(
                    'Daily Fee',
                    '₦${(_leaseContract['daily_fee'] ?? 0).toStringAsFixed(0)}',
                    Icons.money,
                    Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildContractMetric(
                    'Your Share',
                    '${_leaseContract['revenue_split'] ?? 0}%',
                    Icons.pie_chart,
                    Colors.blue,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Contract duration
            Row(
              children: [
                Expanded(
                  child: _buildContractMetric(
                    'Start Date',
                    _leaseContract['start_date'] ?? 'N/A',
                    Icons.calendar_today,
                    Colors.green,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildContractMetric(
                    'End Date',
                    _leaseContract['end_date'] ?? 'N/A',
                    Icons.event,
                    isNearExpiry ? Colors.red : Colors.green,
                  ),
                ),
              ],
            ),

            if (isNearExpiry) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange[300]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.warning, color: Colors.orange[600], size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Contract expires in $daysRemaining days. Contact lessor for renewal.',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.orange[600],
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 16),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _viewContract,
                    icon: const Icon(Icons.description),
                    label: const Text('View Contract'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.purple[600],
                      side: BorderSide(color: Colors.purple[300]!),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _contactLessor,
                    icon: const Icon(Icons.phone),
                    label: const Text('Contact Lessor'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.purple[600],
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
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
                  'Leased Vehicle',
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
                        Text(
                          'VIN: ${_vehicleInfo['vin']}',
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.grey[500],
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Condition badge
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
                      _vehicleInfo['condition']?.toUpperCase() ?? 'GOOD',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: Colors.green[600],
                      ),
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
                    'Lease Start',
                    _vehicleInfo['lease_start'] ?? 'N/A',
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Insurance and maintenance
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
                      Icon(Icons.security, size: 16, color: Colors.blue[600]),
                      const SizedBox(width: 8),
                      Text(
                        'Insurance & Maintenance',
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
                    'Insurance: ${_vehicleInfo['insurance_provider']} (expires ${_vehicleInfo['insurance_expiry']})',
                    style: TextStyle(fontSize: 12, color: Colors.blue[600]),
                  ),
                  Text(
                    'Last Service: ${_vehicleInfo['last_maintenance']}',
                    style: TextStyle(fontSize: 12, color: Colors.blue[600]),
                  ),
                  Text(
                    'Next Service: ${_vehicleInfo['next_maintenance_due']}',
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

  Widget _buildPaymentInfoCard() {
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
                Icon(Icons.account_balance, color: Colors.green[600]),
                const SizedBox(width: 8),
                const Text(
                  'Payment Information',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Bank details
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Payout Account',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.green[600],
                    ),
                  ),
                  const SizedBox(height: 8),
                  _buildInfoRow('Bank', _paymentInfo['bank_name'] ?? 'N/A'),
                  const SizedBox(height: 4),
                  _buildInfoRow(
                    'Account Number',
                    _paymentInfo['account_number'] ?? 'N/A',
                  ),
                  const SizedBox(height: 4),
                  _buildInfoRow(
                    'Account Name',
                    _paymentInfo['account_name'] ?? 'N/A',
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Payment statistics
            Row(
              children: [
                Expanded(
                  child: _buildPaymentMetric(
                    'Total Payouts',
                    '₦${(_paymentInfo['total_payouts'] ?? 0).toStringAsFixed(0)}',
                    Icons.monetization_on,
                    Colors.green,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildPaymentMetric(
                    'Pending',
                    '₦${(_paymentInfo['pending_amount'] ?? 0).toStringAsFixed(0)}',
                    Icons.hourglass_empty,
                    Colors.orange,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Text(
              'Last payout: ${_paymentInfo['last_payout'] ?? 'N/A'}',
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),

            const SizedBox(height: 16),

            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _editPaymentInfo,
                icon: const Icon(Icons.edit),
                label: const Text('Update Payment Info'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.green[600],
                  side: BorderSide(color: Colors.green[300]!),
                ),
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
                Icon(Icons.folder, color: Colors.blue[600]),
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
            }).toList(),

            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _uploadDocuments,
                icon: const Icon(Icons.upload_file),
                label: const Text('Upload Documents'),
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
              'Lease Preferences',
              'Update lease and vehicle preferences',
              Icons.assignment,
              _editLeasePreferences,
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

  // Helper widgets and methods
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

  Widget _buildContractMetric(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
          Text(
            label,
            style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
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

  Widget _buildPaymentMetric(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
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
                if (document['signed_date'] != null)
                  Text(
                    'Signed: ${document['signed_date']}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                if (document['completion_date'] != null)
                  Text(
                    'Completed: ${document['completion_date']}',
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
      case 'lease_agreement':
        return 'Lease Agreement';
      case 'vehicle_handover':
        return 'Vehicle Handover';
      case 'insurance_certificate':
        return 'Insurance Certificate';
      case 'background_check':
        return 'Background Check';
      default:
        return key.replaceAll('_', ' ').toUpperCase();
    }
  }

  // Event handlers
  void _editProfile() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit profile feature coming soon')),
    );
  }

  void _viewContract() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('View contract feature coming soon')),
    );
  }

  void _contactLessor() {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Contacting lessor...')));
  }

  void _editPaymentInfo() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit payment info feature coming soon')),
    );
  }

  void _uploadDocuments() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Document upload feature coming soon')),
    );
  }

  void _editPersonalInfo() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit personal info feature coming soon')),
    );
  }

  void _editNotificationSettings() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Notification settings feature coming soon'),
      ),
    );
  }

  void _editSecuritySettings() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Security settings feature coming soon')),
    );
  }

  void _editLeasePreferences() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Lease preferences feature coming soon')),
    );
  }

  void _openHelpCenter() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Help center feature coming soon')),
    );
  }

  void _contactSupport() {
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
          'This will send an emergency alert to your lessor and emergency services. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
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
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Issue reporting feature coming soon')),
    );
  }
}
