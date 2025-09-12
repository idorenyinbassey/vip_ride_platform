import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../services/api_service.dart';

class IndependentDriverEarningsScreen extends StatefulWidget {
  const IndependentDriverEarningsScreen({super.key});

  @override
  State<IndependentDriverEarningsScreen> createState() =>
      _IndependentDriverEarningsScreenState();
}

class _IndependentDriverEarningsScreenState
    extends State<IndependentDriverEarningsScreen>
    with TickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  late TabController _tabController;

  // Earnings data
  double _todayEarnings = 0.0;
  double _weeklyEarnings = 0.0;
  double _monthlyEarnings = 0.0;

  // Stats
  int _todayRides = 0;
  int _weeklyRides = 0;
  int _monthlyRides = 0;

  // Chart data
  List<FlSpot> _dailyChartData = [];
  List<FlSpot> _weeklyChartData = [];
  List<FlSpot> _monthlyChartData = [];

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadEarningsData();
  }

  Future<void> _loadEarningsData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real earnings data from API
      // Simulate earnings data for now
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        // Today's data
        _todayEarnings = 15650.0;
        _todayRides = 12;

        // Weekly data
        _weeklyEarnings = 89250.0;
        _weeklyRides = 67;

        // Monthly data
        _monthlyEarnings = 342800.0;
        _monthlyRides = 245;

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
    // Daily chart data (last 24 hours)
    _dailyChartData = List.generate(24, (index) {
      double earnings = (index < 12)
          ? 0
          : (500 + (index * 150) + (index * 50 * (index % 3)));
      return FlSpot(index.toDouble(), earnings);
    });

    // Weekly chart data (last 7 days)
    _weeklyChartData = List.generate(7, (index) {
      double earnings = 8000 + (index * 2500) + (index * 1000 * (index % 3));
      return FlSpot(index.toDouble(), earnings);
    });

    // Monthly chart data (last 30 days)
    _monthlyChartData = List.generate(30, (index) {
      double earnings = 5000 + (index * 800) + (index * 200 * (index % 5));
      return FlSpot(index.toDouble(), earnings);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Earnings'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.green[600],
          unselectedLabelColor: Colors.grey[600],
          indicatorColor: Colors.green[600],
          tabs: const [
            Tab(text: 'Today'),
            Tab(text: 'Weekly'),
            Tab(text: 'Monthly'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildDailyEarnings(),
                _buildWeeklyEarnings(),
                _buildMonthlyEarnings(),
              ],
            ),
    );
  }

  Widget _buildDailyEarnings() {
    return RefreshIndicator(
      onRefresh: _loadEarningsData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Today's summary
            _buildEarningsSummary(
              'Today\'s Earnings',
              _todayEarnings,
              _todayRides,
              Colors.green,
            ),

            const SizedBox(height: 24),

            // Hourly earnings chart
            _buildEarningsChart(
              'Hourly Earnings',
              _dailyChartData,
              Colors.green,
            ),

            const SizedBox(height: 24),

            // Today's breakdown
            _buildTodayBreakdown(),
          ],
        ),
      ),
    );
  }

  Widget _buildWeeklyEarnings() {
    return RefreshIndicator(
      onRefresh: _loadEarningsData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Week's summary
            _buildEarningsSummary(
              'This Week\'s Earnings',
              _weeklyEarnings,
              _weeklyRides,
              Colors.blue,
            ),

            const SizedBox(height: 24),

            // Daily earnings chart
            _buildEarningsChart(
              'Daily Earnings',
              _weeklyChartData,
              Colors.blue,
            ),

            const SizedBox(height: 24),

            // Weekly goals
            _buildWeeklyGoals(),
          ],
        ),
      ),
    );
  }

  Widget _buildMonthlyEarnings() {
    return RefreshIndicator(
      onRefresh: _loadEarningsData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Month's summary
            _buildEarningsSummary(
              'This Month\'s Earnings',
              _monthlyEarnings,
              _monthlyRides,
              Colors.purple,
            ),

            const SizedBox(height: 24),

            // Monthly earnings chart
            _buildEarningsChart(
              'Daily Earnings',
              _monthlyChartData,
              Colors.purple,
            ),

            const SizedBox(height: 24),

            // Monthly stats
            _buildMonthlyStats(),
          ],
        ),
      ),
    );
  }

  Widget _buildEarningsSummary(
    String title,
    double earnings,
    int rides,
    Color color,
  ) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [color.withOpacity(0.1), color.withOpacity(0.05)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[700],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              '₦${earnings.toStringAsFixed(0)}',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildSummaryItem(
                  'Rides',
                  rides.toString(),
                  Icons.directions_car,
                ),
                _buildSummaryItem(
                  'Avg/Ride',
                  '₦${(earnings / (rides > 0 ? rides : 1)).toStringAsFixed(0)}',
                  Icons.attach_money,
                ),
                _buildSummaryItem('Rating', '4.8', Icons.star),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 24, color: Colors.grey[600]),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildEarningsChart(String title, List<FlSpot> data, Color color) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(color: Colors.grey[300]!, strokeWidth: 1);
                    },
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 30,
                        interval: data.length > 20 ? 5 : 1,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            value.toInt().toString(),
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 12,
                            ),
                          );
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        interval: 5000,
                        reservedSize: 60,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            '₦${(value / 1000).toInt()}k',
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 12,
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                  borderData: FlBorderData(show: false),
                  minX: 0,
                  maxX: (data.length - 1).toDouble(),
                  minY: 0,
                  maxY:
                      data.map((e) => e.y).reduce((a, b) => a > b ? a : b) *
                      1.2,
                  lineBarsData: [
                    LineChartBarData(
                      spots: data,
                      isCurved: true,
                      color: color,
                      barWidth: 3,
                      isStrokeCapRound: true,
                      dotData: const FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        color: color.withOpacity(0.2),
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

  Widget _buildTodayBreakdown() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Today\'s Breakdown',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildBreakdownItem('Gross Earnings', '₦15,650', Colors.green),
            _buildBreakdownItem('Platform Fee (20%)', '-₦3,130', Colors.red),
            _buildBreakdownItem('Fuel & Maintenance', '-₦2,000', Colors.orange),
            const Divider(),
            _buildBreakdownItem(
              'Net Earnings',
              '₦10,520',
              Colors.blue,
              isBold: true,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBreakdownItem(
    String label,
    String amount,
    Color color, {
    bool isBold = false,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              color: Colors.grey[700],
            ),
          ),
          Text(
            amount,
            style: TextStyle(
              fontSize: 14,
              fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWeeklyGoals() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Weekly Goals',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildGoalProgress('Earnings Goal', _weeklyEarnings, 100000, '₦'),
            const SizedBox(height: 16),
            _buildGoalProgress('Rides Goal', _weeklyRides.toDouble(), 80, ''),
          ],
        ),
      ),
    );
  }

  Widget _buildGoalProgress(
    String label,
    double current,
    double target,
    String currency,
  ) {
    double progress = current / target;
    if (progress > 1.0) progress = 1.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
            ),
            Text(
              '$currency${current.toStringAsFixed(0)} / $currency${target.toStringAsFixed(0)}',
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
            ),
          ],
        ),
        const SizedBox(height: 8),
        LinearProgressIndicator(
          value: progress,
          backgroundColor: Colors.grey[300],
          valueColor: AlwaysStoppedAnimation<Color>(
            progress >= 1.0 ? Colors.green : Colors.blue,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          '${(progress * 100).toStringAsFixed(1)}% completed',
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }

  Widget _buildMonthlyStats() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Monthly Performance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Best Day',
                    '₦18,500',
                    Icons.trending_up,
                    Colors.green,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard(
                    'Avg Daily',
                    '₦11,426',
                    Icons.analytics,
                    Colors.blue,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Total Hours',
                    '156h',
                    Icons.access_time,
                    Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard(
                    'Efficiency',
                    '95%',
                    Icons.speed,
                    Colors.purple,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
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
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
}
