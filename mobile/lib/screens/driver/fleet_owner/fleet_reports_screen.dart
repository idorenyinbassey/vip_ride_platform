import 'package:flutter/material.dart';
import '../../../services/api_service.dart';

class FleetReportsScreen extends StatefulWidget {
  const FleetReportsScreen({super.key});

  @override
  State<FleetReportsScreen> createState() => _FleetReportsScreenState();
}

class _FleetReportsScreenState extends State<FleetReportsScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  String _selectedReportType =
      'overview'; // overview, drivers, vehicles, earnings
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 30));
  DateTime _endDate = DateTime.now();

  // Report data
  Map<String, dynamic> _reportData = {};

  @override
  void initState() {
    super.initState();
    _loadReportData();
  }

  Future<void> _loadReportData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real report data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _reportData = {
          'overview': {
            'total_rides': 1245,
            'total_earnings': 5892400.0,
            'active_drivers': 18,
            'active_vehicles': 25,
            'avg_rating': 4.7,
            'completion_rate': 96.5,
            'cancellation_rate': 3.5,
            'peak_hours': '8:00 AM - 10:00 AM, 5:00 PM - 8:00 PM',
            'busiest_day': 'Friday',
            'top_location': 'Victoria Island, Lagos',
          },
          'drivers': [
            {
              'name': 'James Okafor',
              'total_rides': 245,
              'earnings': 285000,
              'rating': 4.9,
              'completion_rate': 98.2,
              'online_hours': 156,
              'avg_trip_duration': 25,
            },
            {
              'name': 'Sarah Ahmed',
              'total_rides': 189,
              'earnings': 262000,
              'rating': 4.8,
              'completion_rate': 97.1,
              'online_hours': 142,
              'avg_trip_duration': 28,
            },
            {
              'name': 'Peter Eze',
              'total_rides': 156,
              'earnings': 248000,
              'rating': 4.7,
              'completion_rate': 95.8,
              'online_hours': 138,
              'avg_trip_duration': 30,
            },
          ],
          'vehicles': [
            {
              'plate': 'ABC-123-XY',
              'model': '2020 Honda Accord',
              'total_trips': 65,
              'earnings': 350000,
              'utilization': 78.5,
              'maintenance_cost': 45000,
              'fuel_efficiency': 12.5,
            },
            {
              'plate': 'DEF-456-ZW',
              'model': '2021 Toyota Camry',
              'total_trips': 58,
              'earnings': 325000,
              'utilization': 72.3,
              'maintenance_cost': 38000,
              'fuel_efficiency': 13.2,
            },
          ],
          'earnings': {
            'gross_revenue': 5892400.0,
            'commission': 1473100.0,
            'net_earnings': 4419300.0,
            'driver_payouts': 3546180.0,
            'operational_costs': 485200.0,
            'profit_margin': 22.8,
            'growth_rate': 12.5,
          },
        };
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading report: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Fleet Reports'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: _downloadReport,
          ),
          IconButton(icon: const Icon(Icons.share), onPressed: _shareReport),
        ],
      ),
      body: Column(
        children: [
          // Report controls
          Container(
            color: Colors.white,
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Report type selector
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _buildReportTypeChip('Overview', 'overview'),
                      const SizedBox(width: 8),
                      _buildReportTypeChip('Drivers', 'drivers'),
                      const SizedBox(width: 8),
                      _buildReportTypeChip('Vehicles', 'vehicles'),
                      const SizedBox(width: 8),
                      _buildReportTypeChip('Earnings', 'earnings'),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Date range selector
                Row(
                  children: [
                    Expanded(
                      child: InkWell(
                        onTap: _selectStartDate,
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.grey[300]!),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.calendar_today,
                                size: 16,
                                color: Colors.grey[600],
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'From: ${_startDate.day}/${_startDate.month}/${_startDate.year}',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[700],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: InkWell(
                        onTap: _selectEndDate,
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.grey[300]!),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.calendar_today,
                                size: 16,
                                color: Colors.grey[600],
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'To: ${_endDate.day}/${_endDate.month}/${_endDate.year}',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[700],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Report content
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _loadReportData,
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.all(16),
                      child: _buildReportContent(),
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildReportTypeChip(String label, String value) {
    final isSelected = _selectedReportType == value;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        if (selected) {
          setState(() => _selectedReportType = value);
          _loadReportData();
        }
      },
      backgroundColor: Colors.grey[200],
      selectedColor: Colors.orange[100],
      labelStyle: TextStyle(
        color: isSelected ? Colors.orange[600] : Colors.grey[700],
        fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
      ),
    );
  }

  Widget _buildReportContent() {
    switch (_selectedReportType) {
      case 'overview':
        return _buildOverviewReport();
      case 'drivers':
        return _buildDriversReport();
      case 'vehicles':
        return _buildVehiclesReport();
      case 'earnings':
        return _buildEarningsReport();
      default:
        return _buildOverviewReport();
    }
  }

  Widget _buildOverviewReport() {
    final overview = _reportData['overview'] ?? {};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Fleet Overview',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),

        const SizedBox(height: 16),

        // Key metrics grid
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.2,
          children: [
            _buildMetricCard(
              'Total Rides',
              overview['total_rides']?.toString() ?? '0',
              Icons.local_taxi,
              Colors.blue,
            ),
            _buildMetricCard(
              'Total Earnings',
              '₦${overview['total_earnings']?.toStringAsFixed(0) ?? '0'}',
              Icons.monetization_on,
              Colors.green,
            ),
            _buildMetricCard(
              'Active Drivers',
              overview['active_drivers']?.toString() ?? '0',
              Icons.people,
              Colors.orange,
            ),
            _buildMetricCard(
              'Active Vehicles',
              overview['active_vehicles']?.toString() ?? '0',
              Icons.directions_car,
              Colors.purple,
            ),
          ],
        ),

        const SizedBox(height: 24),

        // Performance metrics
        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Performance Metrics',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                _buildPerformanceItem(
                  'Average Rating',
                  '${overview['avg_rating'] ?? 0.0}',
                  Icons.star,
                  Colors.amber,
                ),
                const SizedBox(height: 12),
                _buildPerformanceItem(
                  'Completion Rate',
                  '${overview['completion_rate'] ?? 0.0}%',
                  Icons.check_circle,
                  Colors.green,
                ),
                const SizedBox(height: 12),
                _buildPerformanceItem(
                  'Cancellation Rate',
                  '${overview['cancellation_rate'] ?? 0.0}%',
                  Icons.cancel,
                  Colors.red,
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Insights
        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Insights',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                _buildInsightItem(
                  'Peak Hours',
                  overview['peak_hours'] ?? 'N/A',
                ),
                const SizedBox(height: 12),
                _buildInsightItem(
                  'Busiest Day',
                  overview['busiest_day'] ?? 'N/A',
                ),
                const SizedBox(height: 12),
                _buildInsightItem(
                  'Top Location',
                  overview['top_location'] ?? 'N/A',
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDriversReport() {
    final drivers = _reportData['drivers'] ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Driver Performance Report',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),

        const SizedBox(height: 16),

        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: drivers.length,
          separatorBuilder: (context, index) => const SizedBox(height: 16),
          itemBuilder: (context, index) {
            final driver = drivers[index];
            return _buildDriverReportCard(driver);
          },
        ),
      ],
    );
  }

  Widget _buildVehiclesReport() {
    final vehicles = _reportData['vehicles'] ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Vehicle Performance Report',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),

        const SizedBox(height: 16),

        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: vehicles.length,
          separatorBuilder: (context, index) => const SizedBox(height: 16),
          itemBuilder: (context, index) {
            final vehicle = vehicles[index];
            return _buildVehicleReportCard(vehicle);
          },
        ),
      ],
    );
  }

  Widget _buildEarningsReport() {
    final earnings = _reportData['earnings'] ?? {};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Financial Report',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),

        const SizedBox(height: 16),

        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Revenue Breakdown',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                _buildEarningsRow(
                  'Gross Revenue',
                  '₦${earnings['gross_revenue']?.toStringAsFixed(0) ?? '0'}',
                  Colors.blue,
                ),
                const SizedBox(height: 12),
                _buildEarningsRow(
                  'Commission',
                  '₦${earnings['commission']?.toStringAsFixed(0) ?? '0'}',
                  Colors.orange,
                ),
                const SizedBox(height: 12),
                _buildEarningsRow(
                  'Driver Payouts',
                  '₦${earnings['driver_payouts']?.toStringAsFixed(0) ?? '0'}',
                  Colors.green,
                ),
                const SizedBox(height: 12),
                _buildEarningsRow(
                  'Operational Costs',
                  '₦${earnings['operational_costs']?.toStringAsFixed(0) ?? '0'}',
                  Colors.red,
                ),
                const Divider(),
                _buildEarningsRow(
                  'Net Earnings',
                  '₦${earnings['net_earnings']?.toStringAsFixed(0) ?? '0'}',
                  Colors.green,
                  isTotal: true,
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Performance Indicators',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: _buildKPICard(
                        'Profit Margin',
                        '${earnings['profit_margin'] ?? 0.0}%',
                        Colors.green,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildKPICard(
                        'Growth Rate',
                        '${earnings['growth_rate'] ?? 0.0}%',
                        Colors.blue,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMetricCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: color,
              ),
              textAlign: TextAlign.center,
            ),
            Text(
              title,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 12),
        Text(
          label,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
        ),
        const Spacer(),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildInsightItem(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label:',
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            style: TextStyle(fontSize: 14, color: Colors.grey[700]),
          ),
        ),
      ],
    );
  }

  Widget _buildDriverReportCard(Map<String, dynamic> driver) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              driver['name'] ?? 'Unknown Driver',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildDriverMetric(
                    'Rides',
                    '${driver['total_rides'] ?? 0}',
                  ),
                ),
                Expanded(
                  child: _buildDriverMetric(
                    'Earnings',
                    '₦${driver['earnings'] ?? 0}',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildDriverMetric(
                    'Rating',
                    '${driver['rating'] ?? 0.0}',
                  ),
                ),
                Expanded(
                  child: _buildDriverMetric(
                    'Completion',
                    '${driver['completion_rate'] ?? 0.0}%',
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVehicleReportCard(Map<String, dynamic> vehicle) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              vehicle['plate'] ?? 'Unknown Vehicle',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Text(
              vehicle['model'] ?? '',
              style: TextStyle(fontSize: 14, color: Colors.grey[600]),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildDriverMetric(
                    'Trips',
                    '${vehicle['total_trips'] ?? 0}',
                  ),
                ),
                Expanded(
                  child: _buildDriverMetric(
                    'Earnings',
                    '₦${vehicle['earnings'] ?? 0}',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildDriverMetric(
                    'Utilization',
                    '${vehicle['utilization'] ?? 0.0}%',
                  ),
                ),
                Expanded(
                  child: _buildDriverMetric(
                    'Efficiency',
                    '${vehicle['fuel_efficiency'] ?? 0.0} km/l',
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDriverMetric(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildEarningsRow(
    String label,
    String value,
    Color color, {
    bool isTotal = false,
  }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            fontWeight: isTotal ? FontWeight.bold : FontWeight.w500,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildKPICard(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  void _selectStartDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: _endDate,
    );

    if (date != null) {
      setState(() => _startDate = date);
      _loadReportData();
    }
  }

  void _selectEndDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _endDate,
      firstDate: _startDate,
      lastDate: DateTime.now(),
    );

    if (date != null) {
      setState(() => _endDate = date);
      _loadReportData();
    }
  }

  void _downloadReport() {
    // TODO: Download report as PDF/Excel
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Download report feature coming soon')),
    );
  }

  void _shareReport() {
    // TODO: Share report
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Share report feature coming soon')),
    );
  }
}
