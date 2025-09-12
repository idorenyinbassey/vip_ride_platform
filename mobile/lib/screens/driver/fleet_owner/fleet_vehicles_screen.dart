import 'package:flutter/material.dart';
import '../../../services/api_service.dart';

class FleetVehiclesScreen extends StatefulWidget {
  const FleetVehiclesScreen({super.key});

  @override
  State<FleetVehiclesScreen> createState() => _FleetVehiclesScreenState();
}

class _FleetVehiclesScreenState extends State<FleetVehiclesScreen> {
  final ApiService _apiService = ApiService();

  List<Map<String, dynamic>> _vehicles = [];
  bool _isLoading = false;
  String _searchQuery = '';
  String _filterStatus = 'all'; // all, online, offline, maintenance

  @override
  void initState() {
    super.initState();
    _loadVehicles();
  }

  Future<void> _loadVehicles() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real vehicle data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _vehicles = [
          {
            'id': '1',
            'plate_number': 'ABC-123-XY',
            'make': 'Honda',
            'model': 'Accord',
            'year': 2020,
            'color': 'Black',
            'status': 'online',
            'driver': {
              'name': 'James Okafor',
              'phone': '+234 802 123 4567',
              'rating': 4.9,
            },
            'location': {
              'lat': 6.5244,
              'lng': 3.3792,
              'address': 'Victoria Island, Lagos',
            },
            'earnings_today': 15200,
            'trips_today': 8,
            'last_maintenance': '2024-01-15',
            'next_maintenance_due': '2024-04-15',
            'insurance_expiry': '2024-12-31',
            'documents_status': 'valid',
          },
          {
            'id': '2',
            'plate_number': 'DEF-456-ZW',
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2021,
            'color': 'Silver',
            'status': 'online',
            'driver': {
              'name': 'Sarah Ahmed',
              'phone': '+234 703 987 6543',
              'rating': 4.8,
            },
            'location': {
              'lat': 6.4524,
              'lng': 3.3842,
              'address': 'Ikeja, Lagos',
            },
            'earnings_today': 12800,
            'trips_today': 6,
            'last_maintenance': '2024-02-01',
            'next_maintenance_due': '2024-05-01',
            'insurance_expiry': '2024-11-30',
            'documents_status': 'valid',
          },
          {
            'id': '3',
            'plate_number': 'GHI-789-UV',
            'make': 'Hyundai',
            'model': 'Elantra',
            'year': 2019,
            'color': 'White',
            'status': 'maintenance',
            'driver': null,
            'location': {
              'lat': 6.5955,
              'lng': 3.3087,
              'address': 'Auto Service Center, Lagos',
            },
            'earnings_today': 0,
            'trips_today': 0,
            'last_maintenance': '2024-03-01',
            'next_maintenance_due': '2024-03-05',
            'insurance_expiry': '2024-10-15',
            'documents_status': 'expired',
          },
          {
            'id': '4',
            'plate_number': 'JKL-012-ST',
            'make': 'Nissan',
            'model': 'Altima',
            'year': 2022,
            'color': 'Blue',
            'status': 'offline',
            'driver': {
              'name': 'Peter Eze',
              'phone': '+234 806 555 7890',
              'rating': 4.7,
            },
            'location': {
              'lat': 6.4698,
              'lng': 3.5852,
              'address': 'Lekki, Lagos',
            },
            'earnings_today': 8500,
            'trips_today': 4,
            'last_maintenance': '2024-01-20',
            'next_maintenance_due': '2024-04-20',
            'insurance_expiry': '2025-01-15',
            'documents_status': 'valid',
          },
        ];
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading vehicles: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  List<Map<String, dynamic>> get _filteredVehicles {
    return _vehicles.where((vehicle) {
      final matchesSearch =
          vehicle['plate_number'].toLowerCase().contains(
            _searchQuery.toLowerCase(),
          ) ||
          '${vehicle['make']} ${vehicle['model']}'.toLowerCase().contains(
            _searchQuery.toLowerCase(),
          ) ||
          (vehicle['driver']?['name'] ?? '').toLowerCase().contains(
            _searchQuery.toLowerCase(),
          );

      final matchesFilter =
          _filterStatus == 'all' || vehicle['status'] == _filterStatus;

      return matchesSearch && matchesFilter;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Fleet Vehicles'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: _addNewVehicle),
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
                    hintText: 'Search vehicles, plates, or drivers...',
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
                      _buildFilterChip('Maintenance', 'maintenance'),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Vehicles list
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _loadVehicles,
                    child: _filteredVehicles.isEmpty
                        ? _buildEmptyState()
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: _filteredVehicles.length,
                            itemBuilder: (context, index) {
                              return _buildVehicleCard(
                                _filteredVehicles[index],
                              );
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
          Icon(
            Icons.directions_car_outlined,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No vehicles found',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Add your first vehicle to get started',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _addNewVehicle,
            icon: const Icon(Icons.add),
            label: const Text('Add Vehicle'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange[600],
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVehicleCard(Map<String, dynamic> vehicle) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => _viewVehicleDetails(vehicle),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row with plate and status
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          vehicle['plate_number'],
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '${vehicle['year']} ${vehicle['make']} ${vehicle['model']}',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  _buildStatusChip(vehicle['status']),
                ],
              ),

              const SizedBox(height: 16),

              // Driver info (if assigned)
              if (vehicle['driver'] != null) ...[
                Row(
                  children: [
                    CircleAvatar(
                      radius: 16,
                      backgroundColor: Colors.blue[100],
                      child: Text(
                        vehicle['driver']['name'][0],
                        style: TextStyle(
                          color: Colors.blue[600],
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            vehicle['driver']['name'],
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          Row(
                            children: [
                              Icon(
                                Icons.star,
                                size: 14,
                                color: Colors.amber[600],
                              ),
                              const SizedBox(width: 4),
                              Text(
                                '${vehicle['driver']['rating']}',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Icon(Icons.phone, size: 16, color: Colors.grey[500]),
                  ],
                ),
                const SizedBox(height: 16),
              ] else ...[
                Container(
                  padding: const EdgeInsets.symmetric(
                    vertical: 8,
                    horizontal: 12,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.orange[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.orange[200]!),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.person_off,
                        size: 16,
                        color: Colors.orange[600],
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'No driver assigned',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.orange[600],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Performance metrics
              Row(
                children: [
                  Expanded(
                    child: _buildMetricItem(
                      'Today Earnings',
                      '₦${vehicle['earnings_today']}',
                      Icons.monetization_on,
                      Colors.green,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildMetricItem(
                      'Trips Today',
                      '${vehicle['trips_today']}',
                      Icons.local_taxi,
                      Colors.blue,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Location and actions
              Row(
                children: [
                  Icon(Icons.location_on, size: 16, color: Colors.grey[500]),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      vehicle['location']['address'],
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  IconButton(
                    onPressed: () => _showVehicleActions(vehicle),
                    icon: const Icon(Icons.more_vert),
                    constraints: const BoxConstraints(),
                    padding: EdgeInsets.zero,
                  ),
                ],
              ),

              // Document status warning
              if (vehicle['documents_status'] != 'valid') ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.red[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red[200]!),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.warning, size: 16, color: Colors.red[600]),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Documents need renewal',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.red[600],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      TextButton(
                        onPressed: () => _renewDocuments(vehicle),
                        child: Text(
                          'Renew',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.red[600],
                          ),
                        ),
                      ),
                    ],
                  ),
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
      case 'maintenance':
        color = Colors.orange;
        label = 'Maintenance';
        icon = Icons.build;
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

  Widget _buildMetricItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 6),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              label,
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            ),
          ],
        ),
      ],
    );
  }

  void _addNewVehicle() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _buildAddVehicleForm(),
    );
  }

  Widget _buildAddVehicleForm() {
    return Container(
      height: MediaQuery.of(context).size.height * 0.9,
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
                  'Add New Vehicle',
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
                      labelText: 'Plate Number',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          decoration: const InputDecoration(
                            labelText: 'Make',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextField(
                          decoration: const InputDecoration(
                            labelText: 'Model',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          decoration: const InputDecoration(
                            labelText: 'Year',
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextField(
                          decoration: const InputDecoration(
                            labelText: 'Color',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _saveNewVehicle,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange[600],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text('Add Vehicle'),
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

  void _saveNewVehicle() {
    // TODO: Save new vehicle to API
    Navigator.pop(context);
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Vehicle added successfully')));
  }

  void _viewVehicleDetails(Map<String, dynamic> vehicle) {
    // TODO: Navigate to vehicle details screen
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('View details for ${vehicle['plate_number']}')),
    );
  }

  void _showVehicleActions(Map<String, dynamic> vehicle) {
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
                _viewVehicleDetails(vehicle);
              },
            ),
            ListTile(
              leading: const Icon(Icons.edit),
              title: const Text('Edit Vehicle'),
              onTap: () {
                Navigator.pop(context);
                _editVehicle(vehicle);
              },
            ),
            ListTile(
              leading: const Icon(Icons.person_add),
              title: const Text('Assign Driver'),
              onTap: () {
                Navigator.pop(context);
                _assignDriver(vehicle);
              },
            ),
            ListTile(
              leading: const Icon(Icons.build),
              title: const Text('Schedule Maintenance'),
              onTap: () {
                Navigator.pop(context);
                _scheduleMaintenance(vehicle);
              },
            ),
            ListTile(
              leading: const Icon(Icons.delete, color: Colors.red),
              title: const Text(
                'Remove Vehicle',
                style: TextStyle(color: Colors.red),
              ),
              onTap: () {
                Navigator.pop(context);
                _removeVehicle(vehicle);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _editVehicle(Map<String, dynamic> vehicle) {
    // TODO: Open edit vehicle form
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit vehicle feature coming soon')),
    );
  }

  void _assignDriver(Map<String, dynamic> vehicle) {
    // TODO: Show driver assignment dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Assign driver feature coming soon')),
    );
  }

  void _scheduleMaintenance(Map<String, dynamic> vehicle) {
    // TODO: Open maintenance scheduling
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Schedule maintenance feature coming soon')),
    );
  }

  void _removeVehicle(Map<String, dynamic> vehicle) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Remove Vehicle'),
        content: Text(
          'Are you sure you want to remove ${vehicle['plate_number']} from your fleet?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Remove vehicle from API
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Vehicle removed successfully')),
              );
            },
            child: const Text('Remove', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _renewDocuments(Map<String, dynamic> vehicle) {
    // TODO: Open document renewal flow
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Document renewal feature coming soon')),
    );
  }
}
