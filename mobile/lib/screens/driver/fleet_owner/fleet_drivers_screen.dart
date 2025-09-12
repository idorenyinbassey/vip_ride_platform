import 'package:flutter/material.dart';
import '../../../services/api_service.dart';

class FleetDriversScreen extends StatefulWidget {
  const FleetDriversScreen({super.key});

  @override
  State<FleetDriversScreen> createState() => _FleetDriversScreenState();
}

class _FleetDriversScreenState extends State<FleetDriversScreen> {
  final ApiService _apiService = ApiService();

  List<Map<String, dynamic>> _drivers = [];
  bool _isLoading = false;
  String _searchQuery = '';
  String _filterStatus = 'all'; // all, online, offline, pending

  @override
  void initState() {
    super.initState();
    _loadDrivers();
  }

  Future<void> _loadDrivers() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real driver data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _drivers = [
          {
            'id': '1',
            'name': 'James Okafor',
            'email': 'james.okafor@email.com',
            'phone': '+234 802 123 4567',
            'status': 'online',
            'rating': 4.9,
            'total_rides': 245,
            'earnings_today': 15200,
            'earnings_month': 285000,
            'vehicle': {
              'plate_number': 'ABC-123-XY',
              'make': 'Honda',
              'model': 'Accord',
            },
            'location': {
              'lat': 6.5244,
              'lng': 3.3792,
              'address': 'Victoria Island, Lagos',
            },
            'joined_date': '2023-06-15',
            'last_active': '2024-03-10T14:30:00Z',
            'documents': {
              'license': 'valid',
              'permit': 'valid',
              'background_check': 'valid',
            },
            'profile_image': null,
          },
          {
            'id': '2',
            'name': 'Sarah Ahmed',
            'email': 'sarah.ahmed@email.com',
            'phone': '+234 703 987 6543',
            'status': 'online',
            'rating': 4.8,
            'total_rides': 189,
            'earnings_today': 12800,
            'earnings_month': 262000,
            'vehicle': {
              'plate_number': 'DEF-456-ZW',
              'make': 'Toyota',
              'model': 'Camry',
            },
            'location': {
              'lat': 6.4524,
              'lng': 3.3842,
              'address': 'Ikeja, Lagos',
            },
            'joined_date': '2023-08-22',
            'last_active': '2024-03-10T15:45:00Z',
            'documents': {
              'license': 'valid',
              'permit': 'valid',
              'background_check': 'valid',
            },
            'profile_image': null,
          },
          {
            'id': '3',
            'name': 'Peter Eze',
            'email': 'peter.eze@email.com',
            'phone': '+234 806 555 7890',
            'status': 'offline',
            'rating': 4.7,
            'total_rides': 156,
            'earnings_today': 8500,
            'earnings_month': 248000,
            'vehicle': {
              'plate_number': 'JKL-012-ST',
              'make': 'Nissan',
              'model': 'Altima',
            },
            'location': {
              'lat': 6.4698,
              'lng': 3.5852,
              'address': 'Lekki, Lagos',
            },
            'joined_date': '2023-09-10',
            'last_active': '2024-03-10T12:20:00Z',
            'documents': {
              'license': 'valid',
              'permit': 'expired',
              'background_check': 'valid',
            },
            'profile_image': null,
          },
          {
            'id': '4',
            'name': 'Fatima Hassan',
            'email': 'fatima.hassan@email.com',
            'phone': '+234 701 234 5678',
            'status': 'pending',
            'rating': 0.0,
            'total_rides': 0,
            'earnings_today': 0,
            'earnings_month': 0,
            'vehicle': null,
            'location': null,
            'joined_date': '2024-03-08',
            'last_active': null,
            'documents': {
              'license': 'pending',
              'permit': 'pending',
              'background_check': 'pending',
            },
            'profile_image': null,
          },
        ];
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading drivers: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  List<Map<String, dynamic>> get _filteredDrivers {
    return _drivers.where((driver) {
      final matchesSearch =
          driver['name'].toLowerCase().contains(_searchQuery.toLowerCase()) ||
          driver['email'].toLowerCase().contains(_searchQuery.toLowerCase()) ||
          driver['phone'].contains(_searchQuery) ||
          (driver['vehicle']?['plate_number'] ?? '').toLowerCase().contains(
            _searchQuery.toLowerCase(),
          );

      final matchesFilter =
          _filterStatus == 'all' || driver['status'] == _filterStatus;

      return matchesSearch && matchesFilter;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Fleet Drivers'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: const Icon(Icons.person_add),
            onPressed: _inviteNewDriver,
          ),
        ],
      ),
      body: Column(
        children: [
          // Search and filter bar
          Container(
            color: Colors.white,
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Search bar
                TextField(
                  decoration: InputDecoration(
                    hintText: 'Search drivers, emails, or plates...',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey[300]!),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey[300]!),
                    ),
                    filled: true,
                    fillColor: Colors.grey[50],
                  ),
                  onChanged: (value) {
                    setState(() => _searchQuery = value);
                  },
                ),

                const SizedBox(height: 12),

                // Filter chips
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _buildFilterChip('All', 'all'),
                      const SizedBox(width: 8),
                      _buildFilterChip('Online', 'online'),
                      const SizedBox(width: 8),
                      _buildFilterChip('Offline', 'offline'),
                      const SizedBox(width: 8),
                      _buildFilterChip('Pending', 'pending'),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Drivers list
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _loadDrivers,
                    child: _filteredDrivers.isEmpty
                        ? _buildEmptyState()
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: _filteredDrivers.length,
                            itemBuilder: (context, index) {
                              return _buildDriverCard(_filteredDrivers[index]);
                            },
                          ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, String value) {
    final isSelected = _filterStatus == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() => _filterStatus = value);
      },
      backgroundColor: Colors.grey[200],
      selectedColor: Colors.orange[100],
      checkmarkColor: Colors.orange[600],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.people_outline, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'No drivers found',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Invite drivers to join your fleet',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _inviteNewDriver,
            icon: const Icon(Icons.person_add),
            label: const Text('Invite Driver'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange[600],
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDriverCard(Map<String, dynamic> driver) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => _viewDriverDetails(driver),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row with name and status
              Row(
                children: [
                  // Profile picture
                  CircleAvatar(
                    radius: 24,
                    backgroundColor: Colors.blue[100],
                    child: driver['profile_image'] != null
                        ? Image.network(driver['profile_image'])
                        : Text(
                            driver['name'][0],
                            style: TextStyle(
                              color: Colors.blue[600],
                              fontWeight: FontWeight.bold,
                              fontSize: 18,
                            ),
                          ),
                  ),

                  const SizedBox(width: 12),

                  // Name and contact
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          driver['name'],
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          driver['phone'],
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Status and actions
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      _buildStatusChip(driver['status']),
                      const SizedBox(height: 4),
                      IconButton(
                        onPressed: () => _showDriverActions(driver),
                        icon: const Icon(Icons.more_vert),
                        constraints: const BoxConstraints(),
                        padding: EdgeInsets.zero,
                      ),
                    ],
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Rating and rides (if active driver)
              if (driver['status'] != 'pending') ...[
                Row(
                  children: [
                    // Rating
                    Row(
                      children: [
                        Icon(Icons.star, size: 16, color: Colors.amber[600]),
                        const SizedBox(width: 4),
                        Text(
                          '${driver['rating']}',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(width: 16),

                    // Total rides
                    Row(
                      children: [
                        Icon(
                          Icons.local_taxi,
                          size: 16,
                          color: Colors.blue[600],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${driver['total_rides']} rides',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Vehicle info
                if (driver['vehicle'] != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.grey[200]!),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.directions_car, color: Colors.grey[600]),
                        const SizedBox(width: 8),
                        Text(
                          '${driver['vehicle']['plate_number']} • ${driver['vehicle']['make']} ${driver['vehicle']['model']}',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[700],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Earnings
                Row(
                  children: [
                    Expanded(
                      child: _buildEarningsItem(
                        'Today',
                        '₦${driver['earnings_today']}',
                        Colors.green,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildEarningsItem(
                        'This Month',
                        '₦${driver['earnings_month']}',
                        Colors.blue,
                      ),
                    ),
                  ],
                ),
              ] else ...[
                // Pending driver info
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.orange[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.orange[200]!),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.pending,
                            size: 16,
                            color: Colors.orange[600],
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Pending Verification',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.orange[600],
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Documents under review',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.orange[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              // Document status warnings
              if (driver['documents'] != null) ...[
                const SizedBox(height: 12),
                ..._buildDocumentWarnings(driver['documents']),
              ],

              // Location (if available)
              if (driver['location'] != null) ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(Icons.location_on, size: 16, color: Colors.grey[500]),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        driver['location']['address'],
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    Color color;
    String label;
    IconData icon;

    switch (status) {
      case 'online':
        color = Colors.green;
        label = 'Online';
        icon = Icons.online_prediction;
        break;
      case 'offline':
        color = Colors.grey;
        label = 'Offline';
        icon = Icons.offline_bolt;
        break;
      case 'pending':
        color = Colors.orange;
        label = 'Pending';
        icon = Icons.pending;
        break;
      default:
        color = Colors.grey;
        label = status;
        icon = Icons.help;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEarningsItem(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  List<Widget> _buildDocumentWarnings(Map<String, dynamic> documents) {
    List<Widget> warnings = [];

    documents.forEach((docType, status) {
      if (status == 'expired' || status == 'pending') {
        warnings.add(
          Container(
            margin: const EdgeInsets.only(bottom: 4),
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: status == 'expired' ? Colors.red[50] : Colors.orange[50],
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: status == 'expired'
                    ? Colors.red[200]!
                    : Colors.orange[200]!,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  status == 'expired' ? Icons.error : Icons.pending,
                  size: 14,
                  color: status == 'expired'
                      ? Colors.red[600]
                      : Colors.orange[600],
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    '${docType.replaceAll('_', ' ').toUpperCase()} ${status}',
                    style: TextStyle(
                      fontSize: 11,
                      color: status == 'expired'
                          ? Colors.red[600]
                          : Colors.orange[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      }
    });

    return warnings;
  }

  void _inviteNewDriver() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _buildInviteDriverForm(),
    );
  }

  Widget _buildInviteDriverForm() {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // Handle bar
          Container(
            margin: const EdgeInsets.only(top: 8),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Header
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Invite New Driver',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
          ),

          // Form content
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Column(
                children: [
                  TextField(
                    decoration: const InputDecoration(
                      labelText: 'Driver Name',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    decoration: const InputDecoration(
                      labelText: 'Email Address',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.emailAddress,
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    decoration: const InputDecoration(
                      labelText: 'Phone Number',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.phone,
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _sendInvitation,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange[600],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text('Send Invitation'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _sendInvitation() {
    // TODO: Send invitation via API
    Navigator.pop(context);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Invitation sent successfully')),
    );
  }

  void _viewDriverDetails(Map<String, dynamic> driver) {
    // TODO: Navigate to driver details screen
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('View details for ${driver['name']}')),
    );
  }

  void _showDriverActions(Map<String, dynamic> driver) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.visibility),
              title: const Text('View Details'),
              onTap: () {
                Navigator.pop(context);
                _viewDriverDetails(driver);
              },
            ),
            if (driver['status'] != 'pending') ...[
              ListTile(
                leading: const Icon(Icons.message),
                title: const Text('Send Message'),
                onTap: () {
                  Navigator.pop(context);
                  _messageDriver(driver);
                },
              ),
              ListTile(
                leading: const Icon(Icons.directions_car),
                title: const Text('Assign Vehicle'),
                onTap: () {
                  Navigator.pop(context);
                  _assignVehicle(driver);
                },
              ),
            ],
            if (driver['status'] == 'pending') ...[
              ListTile(
                leading: const Icon(Icons.check_circle, color: Colors.green),
                title: const Text(
                  'Approve Driver',
                  style: TextStyle(color: Colors.green),
                ),
                onTap: () {
                  Navigator.pop(context);
                  _approveDriver(driver);
                },
              ),
              ListTile(
                leading: const Icon(Icons.cancel, color: Colors.red),
                title: const Text(
                  'Reject Driver',
                  style: TextStyle(color: Colors.red),
                ),
                onTap: () {
                  Navigator.pop(context);
                  _rejectDriver(driver);
                },
              ),
            ] else ...[
              ListTile(
                leading: const Icon(Icons.remove_circle, color: Colors.red),
                title: const Text(
                  'Remove Driver',
                  style: TextStyle(color: Colors.red),
                ),
                onTap: () {
                  Navigator.pop(context);
                  _removeDriver(driver);
                },
              ),
            ],
          ],
        ),
      ),
    );
  }

  void _messageDriver(Map<String, dynamic> driver) {
    // TODO: Open messaging with driver
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Messaging feature coming soon')),
    );
  }

  void _assignVehicle(Map<String, dynamic> driver) {
    // TODO: Show vehicle assignment dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Vehicle assignment feature coming soon')),
    );
  }

  void _approveDriver(Map<String, dynamic> driver) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Approve Driver'),
        content: Text('Approve ${driver['name']} to join your fleet?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Approve driver via API
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Driver approved successfully')),
              );
            },
            child: const Text('Approve', style: TextStyle(color: Colors.green)),
          ),
        ],
      ),
    );
  }

  void _rejectDriver(Map<String, dynamic> driver) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reject Driver'),
        content: Text('Reject ${driver['name']}\'s application?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Reject driver via API
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Driver application rejected')),
              );
            },
            child: const Text('Reject', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _removeDriver(Map<String, dynamic> driver) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Remove Driver'),
        content: Text('Remove ${driver['name']} from your fleet?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Remove driver via API
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Driver removed successfully')),
              );
            },
            child: const Text('Remove', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
