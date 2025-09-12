import 'package:flutter/material.dart';
import '../../../services/api_service.dart';

class VipRidesHistoryScreen extends StatefulWidget {
  const VipRidesHistoryScreen({super.key});

  @override
  State<VipRidesHistoryScreen> createState() => _VipRidesHistoryScreenState();
}

class _VipRidesHistoryScreenState extends State<VipRidesHistoryScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  String _selectedFilter = 'all';
  List<Map<String, dynamic>> _rides = [];
  List<Map<String, dynamic>> _filteredRides = [];

  final List<String> _filterOptions = [
    'all',
    'completed',
    'cancelled',
    'scheduled',
    'discrete',
  ];

  @override
  void initState() {
    super.initState();
    _loadRidesHistory();
  }

  Future<void> _loadRidesHistory() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real rides data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _rides = [
          {
            'id': 'vip_ride_001',
            'date': '2024-01-15',
            'time': '14:30',
            'status': 'completed',
            'pickup_address': 'Victoria Island, Lagos',
            'dropoff_address': 'Ikoyi, Lagos',
            'distance': '12.5 km',
            'duration': '25 mins',
            'fare': 12500.0,
            'vehicle_type': 'Executive Sedan',
            'vehicle_model': '2023 Mercedes E-Class',
            'driver': {
              'id': 'vip_driver_001',
              'name': 'James Okafor',
              'rating': 4.9,
              'photo': null,
            },
            'discrete_mode': true,
            'priority_booking': true,
            'booking_type': 'now',
            'payment_method': 'Wallet',
            'concierge_used': false,
            'loyalty_points_earned': 125,
            'trip_notes': '',
            'rating_given': 5,
            'review_text':
                'Excellent service as always. Very professional driver.',
          },
          {
            'id': 'vip_ride_002',
            'date': '2024-01-12',
            'time': '09:15',
            'status': 'completed',
            'pickup_address': 'Lekki Phase 1, Lagos',
            'dropoff_address': 'Murtala Muhammed Airport',
            'distance': '28.3 km',
            'duration': '45 mins',
            'fare': 18500.0,
            'vehicle_type': 'Luxury SUV',
            'vehicle_model': '2022 BMW X5',
            'driver': {
              'id': 'vip_driver_002',
              'name': 'David Adebayo',
              'rating': 4.8,
              'photo': null,
            },
            'discrete_mode': false,
            'priority_booking': true,
            'booking_type': 'scheduled',
            'scheduled_time': '2024-01-12 09:15',
            'payment_method': 'Card',
            'concierge_used': true,
            'concierge_request': 'Airport VIP lounge access arranged',
            'loyalty_points_earned': 185,
            'trip_notes': 'Flight: BA 083, Terminal 2',
            'rating_given': 5,
            'review_text': 'Perfect timing and smooth ride to airport.',
          },
          {
            'id': 'vip_ride_003',
            'date': '2024-01-10',
            'time': '19:45',
            'status': 'completed',
            'pickup_address': 'Eko Hotel & Suites',
            'dropoff_address': 'National Theatre, Lagos',
            'distance': '15.7 km',
            'duration': '32 mins',
            'fare': 15200.0,
            'vehicle_type': 'Premium Van',
            'vehicle_model': 'Mercedes V-Class',
            'driver': {
              'id': 'vip_driver_003',
              'name': 'Samuel Adeola',
              'rating': 4.9,
              'photo': null,
            },
            'discrete_mode': true,
            'priority_booking': true,
            'booking_type': 'now',
            'payment_method': 'Wallet',
            'concierge_used': true,
            'concierge_request': 'Event tickets and VIP seating arranged',
            'loyalty_points_earned': 152,
            'trip_notes': 'Group of 6 for cultural event',
            'rating_given': 5,
            'review_text': 'Spacious vehicle perfect for our group.',
          },
          {
            'id': 'vip_ride_004',
            'date': '2024-01-08',
            'time': '16:20',
            'status': 'cancelled',
            'pickup_address': 'Ikeja GRA, Lagos',
            'dropoff_address': 'Lagos Island',
            'distance': '22.1 km',
            'duration': 'N/A',
            'fare': 0.0,
            'vehicle_type': 'Executive Sedan',
            'vehicle_model': 'N/A',
            'driver': null,
            'discrete_mode': false,
            'priority_booking': true,
            'booking_type': 'scheduled',
            'scheduled_time': '2024-01-08 16:20',
            'payment_method': 'N/A',
            'concierge_used': false,
            'cancellation_reason': 'Meeting rescheduled',
            'cancellation_time': '2024-01-08 15:45',
            'loyalty_points_earned': 0,
          },
          {
            'id': 'vip_ride_005',
            'date': '2024-01-20',
            'time': '11:00',
            'status': 'scheduled',
            'pickup_address': 'Banana Island, Lagos',
            'dropoff_address': 'Four Points by Sheraton',
            'distance': '18.5 km',
            'duration': '35 mins (estimated)',
            'fare': 16800.0,
            'vehicle_type': 'Luxury Coupe',
            'vehicle_model': '2023 BMW 8 Series',
            'driver': {
              'id': 'vip_driver_004',
              'name': 'Ibrahim Yusuf',
              'rating': 4.9,
              'photo': null,
            },
            'discrete_mode': true,
            'priority_booking': true,
            'booking_type': 'scheduled',
            'scheduled_time': '2024-01-20 11:00',
            'payment_method': 'Wallet',
            'concierge_used': true,
            'concierge_request': 'Restaurant reservation for 2 at hotel',
            'loyalty_points_earned': 0,
            'trip_notes': 'Business lunch meeting',
          },
        ];

        _applyFilter();
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading rides: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _applyFilter() {
    setState(() {
      switch (_selectedFilter) {
        case 'completed':
          _filteredRides = _rides
              .where((ride) => ride['status'] == 'completed')
              .toList();
          break;
        case 'cancelled':
          _filteredRides = _rides
              .where((ride) => ride['status'] == 'cancelled')
              .toList();
          break;
        case 'scheduled':
          _filteredRides = _rides
              .where((ride) => ride['status'] == 'scheduled')
              .toList();
          break;
        case 'discrete':
          _filteredRides = _rides
              .where((ride) => ride['discrete_mode'] == true)
              .toList();
          break;
        default:
          _filteredRides = _rides;
      }
    });
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
                  Icon(Icons.history, color: Colors.white, size: 14),
                  const SizedBox(width: 4),
                  Text(
                    'VIP',
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
            const Text('Ride History'),
          ],
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: Icon(Icons.search, color: Colors.grey[600]),
            onPressed: _showSearchDialog,
          ),
          IconButton(
            icon: Icon(Icons.filter_list, color: Colors.grey[600]),
            onPressed: _showFilterDialog,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Filter chips
                _buildFilterChips(),

                // Stats summary
                _buildStatsCard(),

                // Rides list
                Expanded(
                  child: _filteredRides.isEmpty
                      ? _buildEmptyState()
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _filteredRides.length,
                          itemBuilder: (context, index) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 12),
                              child: _buildRideCard(_filteredRides[index]),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }

  Widget _buildFilterChips() {
    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _filterOptions.length,
        itemBuilder: (context, index) {
          final filter = _filterOptions[index];
          final isSelected = _selectedFilter == filter;

          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: FilterChip(
              label: Text(_getFilterLabel(filter)),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  _selectedFilter = filter;
                  _applyFilter();
                });
              },
              selectedColor: Colors.amber[100],
              checkmarkColor: Colors.amber[600],
              backgroundColor: Colors.grey[100],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildStatsCard() {
    final completedRides = _rides
        .where((ride) => ride['status'] == 'completed')
        .length;
    final totalSpent = _rides
        .where((ride) => ride['status'] == 'completed')
        .fold(0.0, (sum, ride) => sum + (ride['fare'] as double));
    final totalPoints = _rides.fold(
      0,
      (sum, ride) => sum + (ride['loyalty_points_earned'] as int),
    );

    return Container(
      margin: const EdgeInsets.all(16),
      child: Card(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'VIP Ride Summary',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[800],
                ),
              ),

              const SizedBox(height: 16),

              Row(
                children: [
                  _buildStatItem(
                    'Total Rides',
                    completedRides.toString(),
                    Icons.car_rental,
                    Colors.blue[600]!,
                  ),
                  _buildStatItem(
                    'Amount Spent',
                    '₦${totalSpent.toStringAsFixed(0)}',
                    Icons.payment,
                    Colors.green[600]!,
                  ),
                  _buildStatItem(
                    'Points Earned',
                    totalPoints.toString(),
                    Icons.stars,
                    Colors.amber[600]!,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Expanded(
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
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

  Widget _buildRideCard(Map<String, dynamic> ride) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () => _showRideDetails(ride),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                children: [
                  _buildStatusChip(ride['status']),
                  const Spacer(),
                  if (ride['discrete_mode'] == true)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.purple[100],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.visibility_off,
                            size: 12,
                            color: Colors.purple[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'DISCRETE',
                            style: TextStyle(
                              fontSize: 8,
                              fontWeight: FontWeight.bold,
                              color: Colors.purple[600],
                            ),
                          ),
                        ],
                      ),
                    ),
                  const SizedBox(width: 8),
                  Text(
                    '${ride['date']} • ${ride['time']}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // Route info
              Row(
                children: [
                  Column(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: Colors.green[600],
                          shape: BoxShape.circle,
                        ),
                      ),
                      Container(width: 2, height: 20, color: Colors.grey[300]),
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: Colors.red[600],
                          shape: BoxShape.circle,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          ride['pickup_address'],
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          ride['dropoff_address'],
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Trip details
              Row(
                children: [
                  if (ride['vehicle_type'] != null) ...[
                    Icon(
                      Icons.directions_car,
                      size: 16,
                      color: Colors.grey[600],
                    ),
                    const SizedBox(width: 4),
                    Text(
                      ride['vehicle_type'],
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                    ),
                    const SizedBox(width: 16),
                  ],
                  Icon(Icons.route, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    '${ride['distance']} • ${ride['duration']}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  const Spacer(),
                  if (ride['fare'] > 0)
                    Text(
                      '₦${ride['fare'].toStringAsFixed(0)}',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: ride['status'] == 'completed'
                            ? Colors.green[600]
                            : Colors.grey[600],
                      ),
                    ),
                ],
              ),

              // Driver info (if available)
              if (ride['driver'] != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[50],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 16,
                        backgroundColor: Colors.grey[300],
                        child: Text(
                          ride['driver']['name'][0],
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              ride['driver']['name'],
                              style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            if (ride['vehicle_model'] != null)
                              Text(
                                ride['vehicle_model'],
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Colors.grey[600],
                                ),
                              ),
                          ],
                        ),
                      ),
                      if (ride['driver']['rating'] != null)
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              ride['driver']['rating'].toString(),
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Icon(
                              Icons.star,
                              size: 12,
                              color: Colors.amber[600],
                            ),
                          ],
                        ),
                    ],
                  ),
                ),
              ],

              // Special features
              if (ride['concierge_used'] == true ||
                  ride['priority_booking'] == true) ...[
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: [
                    if (ride['priority_booking'] == true)
                      _buildFeatureChip(
                        'Priority Booking',
                        Icons.flash_on,
                        Colors.amber[600]!,
                      ),
                    if (ride['concierge_used'] == true)
                      _buildFeatureChip(
                        'Concierge',
                        Icons.support_agent,
                        Colors.blue[600]!,
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
    IconData icon;

    switch (status) {
      case 'completed':
        color = Colors.green[600]!;
        icon = Icons.check_circle;
        break;
      case 'cancelled':
        color = Colors.red[600]!;
        icon = Icons.cancel;
        break;
      case 'scheduled':
        color = Colors.blue[600]!;
        icon = Icons.schedule;
        break;
      default:
        color = Colors.grey[600]!;
        icon = Icons.help;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            status.toUpperCase(),
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureChip(String label, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 10, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 8,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.history, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'No rides found',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Your VIP ride history will appear here',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  String _getFilterLabel(String filter) {
    switch (filter) {
      case 'all':
        return 'All';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      case 'scheduled':
        return 'Scheduled';
      case 'discrete':
        return 'Discrete';
      default:
        return filter;
    }
  }

  void _showSearchDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Search Rides'),
        content: const TextField(
          decoration: InputDecoration(
            hintText: 'Search by location, driver, or date...',
            prefixIcon: Icon(Icons.search),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Search'),
          ),
        ],
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter Options'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: _filterOptions.map((filter) {
            return RadioListTile<String>(
              title: Text(_getFilterLabel(filter)),
              value: filter,
              groupValue: _selectedFilter,
              onChanged: (value) {
                setState(() {
                  _selectedFilter = value!;
                  _applyFilter();
                });
                Navigator.pop(context);
              },
            );
          }).toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showRideDetails(Map<String, dynamic> ride) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        maxChildSize: 0.9,
        minChildSize: 0.5,
        builder: (context, scrollController) {
          return Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Column(
              children: [
                // Handle
                Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),

                // Header
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      const Text(
                        'Ride Details',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Spacer(),
                      _buildStatusChip(ride['status']),
                    ],
                  ),
                ),

                // Content
                Expanded(
                  child: SingleChildScrollView(
                    controller: scrollController,
                    padding: const EdgeInsets.all(16),
                    child: _buildRideDetailsContent(ride),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildRideDetailsContent(Map<String, dynamic> ride) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Trip info
        _buildDetailSection('Trip Information', [
          _buildDetailRow('Date & Time', '${ride['date']} at ${ride['time']}'),
          _buildDetailRow('Distance', ride['distance']),
          _buildDetailRow('Duration', ride['duration']),
          if (ride['booking_type'] == 'scheduled' &&
              ride['scheduled_time'] != null)
            _buildDetailRow('Scheduled Time', ride['scheduled_time']),
        ]),

        const SizedBox(height: 20),

        // Route
        _buildDetailSection('Route', [
          Row(
            children: [
              Column(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: Colors.green[600],
                      shape: BoxShape.circle,
                    ),
                  ),
                  Container(width: 2, height: 30, color: Colors.grey[300]),
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: Colors.red[600],
                      shape: BoxShape.circle,
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Pickup',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey[600],
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      ride['pickup_address'],
                      style: const TextStyle(fontSize: 14),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Destination',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey[600],
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      ride['dropoff_address'],
                      style: const TextStyle(fontSize: 14),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ]),

        const SizedBox(height: 20),

        // Vehicle & Driver
        if (ride['driver'] != null)
          _buildDetailSection('Driver & Vehicle', [
            Row(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor: Colors.grey[300],
                  child: Text(
                    ride['driver']['name'][0],
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ride['driver']['name'],
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (ride['vehicle_model'] != null)
                        Text(
                          ride['vehicle_model'],
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      if (ride['driver']['rating'] != null)
                        Row(
                          children: [
                            Text(
                              ride['driver']['rating'].toString(),
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Icon(
                              Icons.star,
                              size: 12,
                              color: Colors.amber[600],
                            ),
                            const SizedBox(width: 4),
                            Text(
                              'rating',
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ]),

        const SizedBox(height: 20),

        // Payment & Fare
        if (ride['fare'] > 0)
          _buildDetailSection('Payment', [
            _buildDetailRow(
              'Total Fare',
              '₦${ride['fare'].toStringAsFixed(0)}',
            ),
            if (ride['payment_method'] != null)
              _buildDetailRow('Payment Method', ride['payment_method']),
            if (ride['loyalty_points_earned'] > 0)
              _buildDetailRow(
                'Points Earned',
                '${ride['loyalty_points_earned']} points',
              ),
          ]),

        const SizedBox(height: 20),

        // VIP Features
        _buildDetailSection('VIP Features', [
          if (ride['discrete_mode'] == true)
            _buildFeatureItem(
              'Discrete Mode',
              'Your identity was hidden from driver',
              Icons.visibility_off,
            ),
          if (ride['priority_booking'] == true)
            _buildFeatureItem(
              'Priority Booking',
              'Matched with top-rated driver',
              Icons.flash_on,
            ),
          if (ride['concierge_used'] == true) ...[
            _buildFeatureItem(
              'Concierge Service',
              'Used concierge assistance',
              Icons.support_agent,
            ),
            if (ride['concierge_request'] != null)
              Padding(
                padding: const EdgeInsets.only(left: 32, top: 4),
                child: Text(
                  ride['concierge_request'],
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
          ],
        ]),

        // Trip notes
        if (ride['trip_notes']?.isNotEmpty == true) ...[
          const SizedBox(height: 20),
          _buildDetailSection('Trip Notes', [
            Text(ride['trip_notes'], style: const TextStyle(fontSize: 14)),
          ]),
        ],

        // Review
        if (ride['review_text']?.isNotEmpty == true) ...[
          const SizedBox(height: 20),
          _buildDetailSection('Your Review', [
            Row(
              children: [
                ...List.generate(5, (index) {
                  return Icon(
                    index < (ride['rating_given'] ?? 0)
                        ? Icons.star
                        : Icons.star_border,
                    size: 16,
                    color: Colors.amber[600],
                  );
                }),
                const SizedBox(width: 8),
                Text(
                  '${ride['rating_given']}/5',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(ride['review_text'], style: const TextStyle(fontSize: 14)),
          ]),
        ],

        // Cancellation info
        if (ride['status'] == 'cancelled') ...[
          const SizedBox(height: 20),
          _buildDetailSection('Cancellation', [
            if (ride['cancellation_reason'] != null)
              _buildDetailRow('Reason', ride['cancellation_reason']),
            if (ride['cancellation_time'] != null)
              _buildDetailRow('Cancelled At', ride['cancellation_time']),
          ]),
        ],
      ],
    );
  }

  Widget _buildDetailSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.grey[800],
          ),
        ),
        const SizedBox(height: 8),
        ...children,
      ],
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 12))),
        ],
      ),
    );
  }

  Widget _buildFeatureItem(String title, String description, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 16, color: Colors.amber[600]),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  description,
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
