import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../services/api_service.dart';

class FleetEarningsScreen extends StatefulWidget {
  const FleetEarningsScreen({super.key});

  @override
  State<FleetEarningsScreen> createState() => _FleetEarningsScreenState();
}

class _FleetEarningsScreenState extends State<FleetEarningsScreen> {
  final ApiService _apiService = ApiService();

  String _selectedPeriod = 'today'; // today, week, month, year
  bool _isLoading = false;

  // Earnings data
  double _totalEarnings = 0.0;
  double _commission = 0.0;
  double _netEarnings = 0.0;
  double _previousPeriodEarnings = 0.0;

  // Breakdown data
  List<Map<String, dynamic>> _earningsBreakdown = [];
  List<Map<String, dynamic>> _driverEarnings = [];
  List<Map<String, dynamic>> _vehicleEarnings = [];

  // Chart data
  List<FlSpot> _earningsChartData = [];
  List<BarChartGroupData> _comparisonData = [];

  @override
  void initState() {
    super.initState();
    _loadEarningsData();
  }

  Future<void> _loadEarningsData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real earnings data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        // Sample data based on selected period
        switch (_selectedPeriod) {
          case 'today':
            _totalEarnings = 245650.0;
            _commission = 61412.5; // 25% commission
            _netEarnings = _totalEarnings - _commission;
            _previousPeriodEarnings = 232150.0;
            break;
          case 'week':
            _totalEarnings = 1624500.0;
            _commission = 406125.0;
            _netEarnings = _totalEarnings - _commission;
            _previousPeriodEarnings = 1548200.0;
            break;
          case 'month':
            _totalEarnings = 5892400.0;
            _commission = 1473100.0;
            _netEarnings = _totalEarnings - _commission;
            _previousPeriodEarnings = 5234800.0;
            break;
          case 'year':
            _totalEarnings = 68250000.0;
            _commission = 17062500.0;
            _netEarnings = _totalEarnings - _commission;
            _previousPeriodEarnings = 62100000.0;
            break;
        }

        _earningsBreakdown = [
          {
            'category': 'Rides',
            'amount': _totalEarnings * 0.85,
            'color': Colors.green,
          },
          {
            'category': 'Premium Rides',
            'amount': _totalEarnings * 0.12,
            'color': Colors.blue,
          },
          {
            'category': 'VIP Rides',
            'amount': _totalEarnings * 0.03,
            'color': Colors.purple,
          },
        ];

        _driverEarnings = [
          {
            'name': 'James Okafor',
            'earnings': 285000,
            'rides': 45,
            'commission': 71250,
          },
          {
            'name': 'Sarah Ahmed',
            'earnings': 262000,
            'rides': 42,
            'commission': 65500,
          },
          {
            'name': 'Peter Eze',
            'earnings': 248000,
            'rides': 38,
            'commission': 62000,
          },
          {
            'name': 'Mary Johnson',
            'earnings': 235000,
            'rides': 35,
            'commission': 58750,
          },
          {
            'name': 'David Wilson',
            'earnings': 220000,
            'rides': 32,
            'commission': 55000,
          },
        ];

        _vehicleEarnings = [
          {
            'plate': 'ABC-123-XY',
            'model': 'Honda Accord',
            'earnings': 350000,
            'trips': 65,
          },
          {
            'plate': 'DEF-456-ZW',
            'model': 'Toyota Camry',
            'earnings': 325000,
            'trips': 58,
          },
          {
            'plate': 'GHI-789-UV',
            'model': 'Hyundai Elantra',
            'earnings': 289000,
            'trips': 52,
          },
          {
            'plate': 'JKL-012-ST',
            'model': 'Nissan Altima',
            'earnings': 275000,
            'trips': 48,
          },
        ];

        // Generate chart data
        _generateChartData();
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading earnings: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _generateChartData() {
    // Line chart data for earnings trend
    _earningsChartData = [
      FlSpot(0, _previousPeriodEarnings * 0.7),
      FlSpot(1, _previousPeriodEarnings * 0.8),
      FlSpot(2, _previousPeriodEarnings * 0.9),
      FlSpot(3, _previousPeriodEarnings * 0.95),
      FlSpot(4, _previousPeriodEarnings),
      FlSpot(5, _totalEarnings * 0.8),
      FlSpot(6, _totalEarnings),
    ];

    // Bar chart data for comparison
    _comparisonData = [
      BarChartGroupData(
        x: 0,
        barRods: [
          BarChartRodData(
            toY: _previousPeriodEarnings / 1000,
            color: Colors.grey[400],
            width: 20,
          ),
        ],
      ),
      BarChartGroupData(
        x: 1,
        barRods: [
          BarChartRodData(
            toY: _totalEarnings / 1000,
            color: Colors.orange[600],
            width: 20,
          ),
        ],
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Fleet Earnings'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: _exportReport,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadEarningsData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Period selector
                    _buildPeriodSelector(),

                    const SizedBox(height: 24),

                    // Earnings overview
                    _buildEarningsOverview(),

                    const SizedBox(height: 24),

                    // Earnings chart
                    _buildEarningsChart(),

                    const SizedBox(height: 24),

                    // Earnings breakdown
                    _buildEarningsBreakdown(),

                    const SizedBox(height: 24),

                    // Top performers
                    _buildTopPerformers(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildPeriodSelector() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Select Period',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildPeriodChip('Today', 'today'),
                  const SizedBox(width: 8),
                  _buildPeriodChip('This Week', 'week'),
                  const SizedBox(width: 8),
                  _buildPeriodChip('This Month', 'month'),
                  const SizedBox(width: 8),
                  _buildPeriodChip('This Year', 'year'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPeriodChip(String label, String value) {
    final isSelected = _selectedPeriod == value;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        if (selected) {
          setState(() => _selectedPeriod = value);
          _loadEarningsData();
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

  Widget _buildEarningsOverview() {
    final growthPercentage = _previousPeriodEarnings > 0
        ? ((_totalEarnings - _previousPeriodEarnings) /
              _previousPeriodEarnings *
              100)
        : 0.0;

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.orange[400]!, Colors.orange[600]!],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Total Earnings',
              style: TextStyle(color: Colors.white70, fontSize: 16),
            ),
            const SizedBox(height: 8),
            Text(
              '₦${_totalEarnings.toStringAsFixed(0)}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Commission',
                      style: TextStyle(color: Colors.white70, fontSize: 14),
                    ),
                    Text(
                      '₦${_commission.toStringAsFixed(0)}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Net Earnings',
                      style: TextStyle(color: Colors.white70, fontSize: 14),
                    ),
                    Text(
                      '₦${_netEarnings.toStringAsFixed(0)}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: growthPercentage >= 0
                    ? Colors.green[400]
                    : Colors.red[400],
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    growthPercentage >= 0
                        ? Icons.trending_up
                        : Icons.trending_down,
                    color: Colors.white,
                    size: 16,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${growthPercentage.abs().toStringAsFixed(1)}% vs last period',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEarningsChart() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Earnings Trend',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(show: false),
                  titlesData: FlTitlesData(show: false),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: _earningsChartData,
                      isCurved: true,
                      color: Colors.orange[600],
                      barWidth: 3,
                      dotData: FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        color: Colors.orange[600]!.withOpacity(0.1),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEarningsBreakdown() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Earnings Breakdown',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _earningsBreakdown.length,
              separatorBuilder: (context, index) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final item = _earningsBreakdown[index];
                final percentage = (item['amount'] / _totalEarnings * 100);

                return Row(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: item['color'],
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        item['category'],
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    Text(
                      '${percentage.toStringAsFixed(1)}%',
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '₦${item['amount'].toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopPerformers() {
    return Column(
      children: [
        // Top Drivers
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Top Earning Drivers',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    TextButton(
                      onPressed: _viewAllDrivers,
                      child: const Text('View All'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _driverEarnings.take(3).length,
                  separatorBuilder: (context, index) =>
                      const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final driver = _driverEarnings[index];
                    return _buildDriverEarningsItem(driver, index + 1);
                  },
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Top Vehicles
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Top Earning Vehicles',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    TextButton(
                      onPressed: _viewAllVehicles,
                      child: const Text('View All'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _vehicleEarnings.take(3).length,
                  separatorBuilder: (context, index) =>
                      const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final vehicle = _vehicleEarnings[index];
                    return _buildVehicleEarningsItem(vehicle, index + 1);
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDriverEarningsItem(Map<String, dynamic> driver, int rank) {
    return Row(
      children: [
        CircleAvatar(
          radius: 16,
          backgroundColor: _getRankColor(rank),
          child: Text(
            rank.toString(),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                driver['name'],
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                '${driver['rides']} rides • Commission: ₦${driver['commission']}',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
        Text(
          '₦${driver['earnings']}',
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
      ],
    );
  }

  Widget _buildVehicleEarningsItem(Map<String, dynamic> vehicle, int rank) {
    return Row(
      children: [
        CircleAvatar(
          radius: 16,
          backgroundColor: _getRankColor(rank),
          child: Text(
            rank.toString(),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                vehicle['plate'],
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                '${vehicle['model']} • ${vehicle['trips']} trips',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
        Text(
          '₦${vehicle['earnings']}',
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
      ],
    );
  }

  Color _getRankColor(int rank) {
    switch (rank) {
      case 1:
        return Colors.amber[600]!;
      case 2:
        return Colors.grey[400]!;
      case 3:
        return Colors.brown[400]!;
      default:
        return Colors.blue[400]!;
    }
  }

  void _exportReport() {
    // TODO: Export earnings report
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Export report feature coming soon')),
    );
  }

  void _viewAllDrivers() {
    // Navigate to drivers tab
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Navigate to drivers screen')));
  }

  void _viewAllVehicles() {
    // Navigate to vehicles tab
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Navigate to vehicles screen')),
    );
  }
}
