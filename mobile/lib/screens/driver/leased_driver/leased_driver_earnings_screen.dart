import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../services/api_service.dart';

class LeasedDriverEarningsScreen extends StatefulWidget {
  const LeasedDriverEarningsScreen({super.key});

  @override
  State<LeasedDriverEarningsScreen> createState() =>
      _LeasedDriverEarningsScreenState();
}

class _LeasedDriverEarningsScreenState extends State<LeasedDriverEarningsScreen>
    with TickerProviderStateMixin {
  final ApiService _apiService = ApiService();

  late TabController _tabController;
  bool _isLoading = false;

  // Earnings data
  Map<String, dynamic> _todayEarnings = {};
  Map<String, dynamic> _weeklyEarnings = {};
  Map<String, dynamic> _monthlyEarnings = {};
  Map<String, dynamic> _leaseDetails = {};
  List<Map<String, dynamic>> _payoutHistory = [];
  List<Map<String, dynamic>> _dailyData = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadEarningsData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadEarningsData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real earnings data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _leaseDetails = {
          'daily_fee': 15000.0,
          'revenue_split': 70.0, // Driver gets 70%
          'lessor_name': 'Elite Vehicle Leasing',
          'payment_status': 'current',
          'lease_end_date': '2024-07-15',
        };

        _todayEarnings = {
          'gross_earnings': 28500.0,
          'rides_completed': 12,
          'driver_share': 19950.0, // 70% of gross
          'daily_fee': 15000.0,
          'net_earnings': 4950.0, // driver_share - daily_fee
          'hours_worked': 8.5,
          'avg_fare': 2375.0,
          'peak_bonus': 850.0,
        };

        _weeklyEarnings = {
          'gross_earnings': 186500.0,
          'rides_completed': 78,
          'driver_share': 130550.0, // 70% of gross
          'daily_fees_paid': 105000.0, // 7 days * 15000
          'net_earnings': 25550.0, // driver_share - daily_fees
          'hours_worked': 58.5,
          'avg_daily_earnings': 3650.0,
          'peak_bonuses': 4800.0,
        };

        _monthlyEarnings = {
          'gross_earnings': 745000.0,
          'rides_completed': 315,
          'driver_share': 521500.0, // 70% of gross
          'daily_fees_paid': 465000.0, // 31 days * 15000
          'net_earnings': 56500.0, // driver_share - daily_fees
          'hours_worked': 248.0,
          'avg_daily_earnings': 1822.6,
          'peak_bonuses': 18200.0,
        };

        _payoutHistory = [
          {
            'date': '2024-03-10',
            'amount': 4950.0,
            'gross_earnings': 28500.0,
            'daily_fee': 15000.0,
            'rides': 12,
            'status': 'completed',
          },
          {
            'date': '2024-03-09',
            'amount': 3200.0,
            'gross_earnings': 25000.0,
            'daily_fee': 15000.0,
            'rides': 10,
            'status': 'completed',
          },
          {
            'date': '2024-03-08',
            'amount': 5800.0,
            'gross_earnings': 32000.0,
            'daily_fee': 15000.0,
            'rides': 14,
            'status': 'completed',
          },
          {
            'date': '2024-03-07',
            'amount': 2100.0,
            'gross_earnings': 21000.0,
            'daily_fee': 15000.0,
            'rides': 8,
            'status': 'completed',
          },
        ];

        _dailyData = [
          {'day': 'Mon', 'gross': 25000.0, 'net': 2500.0},
          {'day': 'Tue', 'gross': 28000.0, 'net': 4600.0},
          {'day': 'Wed', 'gross': 32000.0, 'net': 7400.0},
          {'day': 'Thu', 'gross': 21000.0, 'net': 1700.0},
          {'day': 'Fri', 'gross': 35000.0, 'net': 9500.0},
          {'day': 'Sat', 'gross': 30000.0, 'net': 6000.0},
          {'day': 'Sun', 'gross': 28500.0, 'net': 4950.0},
        ];
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading earnings: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
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
                _buildTodayTab(),
                _buildWeeklyTab(),
                _buildMonthlyTab(),
              ],
            ),
    );
  }

  Widget _buildTodayTab() {
    return RefreshIndicator(
      onRefresh: _loadEarningsData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Lease summary card
            _buildLeaseSummaryCard(),

            const SizedBox(height: 16),

            // Net earnings highlight
            _buildNetEarningsCard('today'),

            const SizedBox(height: 16),

            // Earnings breakdown
            _buildEarningsBreakdownCard('today'),

            const SizedBox(height: 16),

            // Performance metrics
            _buildPerformanceMetricsCard('today'),

            const SizedBox(height: 16),

            // Daily breakdown chart
            _buildDailyChart(),

            const SizedBox(height: 16),

            // Recent payouts
            _buildRecentPayoutsCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildWeeklyTab() {
    return RefreshIndicator(
      onRefresh: _loadEarningsData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Weekly summary
            _buildNetEarningsCard('weekly'),

            const SizedBox(height: 16),

            // Weekly breakdown
            _buildEarningsBreakdownCard('weekly'),

            const SizedBox(height: 16),

            // Weekly performance
            _buildPerformanceMetricsCard('weekly'),

            const SizedBox(height: 16),

            // Weekly chart
            _buildWeeklyChart(),

            const SizedBox(height: 16),

            // Daily averages
            _buildDailyAveragesCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildMonthlyTab() {
    return RefreshIndicator(
      onRefresh: _loadEarningsData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Monthly summary
            _buildNetEarningsCard('monthly'),

            const SizedBox(height: 16),

            // Monthly breakdown
            _buildEarningsBreakdownCard('monthly'),

            const SizedBox(height: 16),

            // Monthly performance
            _buildPerformanceMetricsCard('monthly'),

            const SizedBox(height: 16),

            // Payout schedule
            _buildPayoutScheduleCard(),

            const SizedBox(height: 16),

            // Lease renewal reminder
            _buildLeaseRenewalCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildLeaseSummaryCard() {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.purple[400]!, Colors.purple[600]!],
          ),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.assignment, color: Colors.white, size: 24),
                const SizedBox(width: 8),
                const Text(
                  'Lease Agreement',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _leaseDetails['payment_status']?.toString().toUpperCase() ??
                        'CURRENT',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: _buildLeaseMetric(
                    'Daily Fee',
                    '₦${(_leaseDetails['daily_fee'] ?? 0).toStringAsFixed(0)}',
                    Colors.white,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildLeaseMetric(
                    'Your Share',
                    '${_leaseDetails['revenue_split'] ?? 0}%',
                    Colors.white,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Text(
              'Lessor: ${_leaseDetails['lessor_name'] ?? 'Unknown'}',
              style: const TextStyle(color: Colors.white70, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNetEarningsCard(String period) {
    final earnings = period == 'today'
        ? _todayEarnings
        : period == 'weekly'
        ? _weeklyEarnings
        : _monthlyEarnings;

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.green[400]!, Colors.green[600]!],
          ),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.account_balance_wallet,
                  color: Colors.white,
                  size: 28,
                ),
                const SizedBox(width: 12),
                Text(
                  'Net Earnings ($period)',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            Text(
              '₦${(earnings['net_earnings'] ?? 0).toStringAsFixed(0)}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 8),

            Text(
              'After daily fee deduction',
              style: const TextStyle(color: Colors.white70, fontSize: 14),
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: _buildEarningsQuickStat(
                    'Rides',
                    '${earnings['rides_completed'] ?? 0}',
                    Icons.drive_eta,
                  ),
                ),
                Expanded(
                  child: _buildEarningsQuickStat(
                    'Hours',
                    '${(earnings['hours_worked'] ?? 0).toStringAsFixed(1)}',
                    Icons.access_time,
                  ),
                ),
                Expanded(
                  child: _buildEarningsQuickStat(
                    'Avg/Hour',
                    '₦${((earnings['net_earnings'] ?? 0) / (earnings['hours_worked'] ?? 1)).toStringAsFixed(0)}',
                    Icons.trending_up,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEarningsBreakdownCard(String period) {
    final earnings = period == 'today'
        ? _todayEarnings
        : period == 'weekly'
        ? _weeklyEarnings
        : _monthlyEarnings;

    final dailyFeeKey = period == 'today' ? 'daily_fee' : 'daily_fees_paid';

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Earnings Breakdown',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 16),

            // Gross earnings
            _buildBreakdownItem(
              'Gross Earnings',
              '₦${(earnings['gross_earnings'] ?? 0).toStringAsFixed(0)}',
              Colors.blue[600]!,
              Icons.monetization_on,
              true,
            ),

            const SizedBox(height: 12),

            // Driver share (70%)
            _buildBreakdownItem(
              'Your Share (${_leaseDetails['revenue_split']}%)',
              '₦${(earnings['driver_share'] ?? 0).toStringAsFixed(0)}',
              Colors.purple[600]!,
              Icons.pie_chart,
              false,
            ),

            const SizedBox(height: 12),

            // Daily fee deduction
            _buildBreakdownItem(
              period == 'today' ? 'Daily Fee' : 'Total Daily Fees',
              '-₦${(earnings[dailyFeeKey] ?? 0).toStringAsFixed(0)}',
              Colors.orange[600]!,
              Icons.remove_circle,
              false,
            ),

            const SizedBox(height: 12),

            // Peak bonuses (if any)
            if (earnings['peak_bonus'] != null ||
                earnings['peak_bonuses'] != null)
              _buildBreakdownItem(
                'Peak Bonuses',
                '+₦${((earnings['peak_bonus'] ?? earnings['peak_bonuses']) ?? 0).toStringAsFixed(0)}',
                Colors.amber[600]!,
                Icons.star,
                false,
              ),

            const Divider(height: 24),

            // Net earnings
            _buildBreakdownItem(
              'Net Earnings',
              '₦${(earnings['net_earnings'] ?? 0).toStringAsFixed(0)}',
              Colors.green[600]!,
              Icons.account_balance_wallet,
              true,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceMetricsCard(String period) {
    final earnings = period == 'today'
        ? _todayEarnings
        : period == 'weekly'
        ? _weeklyEarnings
        : _monthlyEarnings;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Performance Metrics',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: _buildMetricCard(
                    'Avg per Ride',
                    '₦${((earnings['gross_earnings'] ?? 0) / (earnings['rides_completed'] ?? 1)).toStringAsFixed(0)}',
                    Icons.directions_car,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildMetricCard(
                    'Hourly Rate',
                    '₦${((earnings['net_earnings'] ?? 0) / (earnings['hours_worked'] ?? 1)).toStringAsFixed(0)}',
                    Icons.access_time,
                    Colors.green,
                  ),
                ),
              ],
            ),

            if (period != 'today') ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      'Daily Average',
                      '₦${(earnings['avg_daily_earnings'] ?? 0).toStringAsFixed(0)}',
                      Icons.calendar_today,
                      Colors.purple,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricCard(
                      'Total Bonuses',
                      '₦${((earnings['peak_bonuses'] ?? earnings['peak_bonus']) ?? 0).toStringAsFixed(0)}',
                      Icons.star,
                      Colors.amber,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDailyChart() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'This Week\'s Performance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 20),

            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY:
                      _dailyData
                          .map((e) => e['gross'] as double)
                          .reduce((a, b) => a > b ? a : b) *
                      1.2,
                  barTouchData: BarTouchData(enabled: true),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          if (value.toInt() < _dailyData.length) {
                            return Text(
                              _dailyData[value.toInt()]['day'],
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            );
                          }
                          return const Text('');
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            '${(value / 1000).toStringAsFixed(0)}k',
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.grey[600],
                            ),
                          );
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  gridData: FlGridData(
                    show: true,
                    horizontalInterval: 5000,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(color: Colors.grey[300], strokeWidth: 1);
                    },
                  ),
                  borderData: FlBorderData(show: false),
                  barGroups: _dailyData.asMap().entries.map((entry) {
                    final index = entry.key;
                    final data = entry.value;
                    return BarChartGroupData(
                      x: index,
                      barRods: [
                        BarChartRodData(
                          toY: data['gross'],
                          color: Colors.blue[400],
                          width: 16,
                          borderRadius: const BorderRadius.only(
                            topLeft: Radius.circular(4),
                            topRight: Radius.circular(4),
                          ),
                        ),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ),

            const SizedBox(height: 12),

            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Row(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: Colors.blue[400],
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Gross Earnings',
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeeklyChart() {
    // Similar to daily chart but with weekly data
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Weekly Trends',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 20),

            Container(
              height: 200,
              child: const Center(
                child: Text(
                  'Weekly trend chart would go here',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentPayoutsCard() {
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
                const Text(
                  'Recent Payouts',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                TextButton(
                  onPressed: _viewAllPayouts,
                  child: const Text('View All'),
                ),
              ],
            ),

            const SizedBox(height: 16),

            ..._payoutHistory.take(3).map((payout) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildPayoutItem(payout),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildDailyAveragesCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Daily Averages This Week',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: _buildAverageMetric(
                    'Rides/Day',
                    '${(_weeklyEarnings['rides_completed'] / 7).toStringAsFixed(1)}',
                    Icons.drive_eta,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildAverageMetric(
                    'Hours/Day',
                    '${(_weeklyEarnings['hours_worked'] / 7).toStringAsFixed(1)}',
                    Icons.access_time,
                    Colors.green,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildAverageMetric(
                    'Gross/Day',
                    '₦${(_weeklyEarnings['gross_earnings'] / 7).toStringAsFixed(0)}',
                    Icons.monetization_on,
                    Colors.purple,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildAverageMetric(
                    'Net/Day',
                    '₦${(_weeklyEarnings['net_earnings'] / 7).toStringAsFixed(0)}',
                    Icons.account_balance_wallet,
                    Colors.orange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPayoutScheduleCard() {
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
                Icon(Icons.schedule, color: Colors.blue[600]),
                const SizedBox(width: 8),
                const Text(
                  'Payout Schedule',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),

            const SizedBox(height: 16),

            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Daily Automatic Payouts',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue[600],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Net earnings are automatically paid out daily after midnight.',
                    style: TextStyle(fontSize: 14, color: Colors.blue[600]),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Icon(
                        Icons.access_time,
                        size: 16,
                        color: Colors.blue[600],
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Next payout: Tomorrow 12:00 AM',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Colors.blue[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLeaseRenewalCard() {
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
                Icon(Icons.warning, color: Colors.orange[600]),
                const SizedBox(width: 8),
                const Text(
                  'Lease Renewal',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),

            const SizedBox(height: 16),

            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange[50],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.orange[300]!),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Lease expires on ${_leaseDetails['lease_end_date']}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: Colors.orange[600],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Contact your lessor to discuss renewal options.',
                    style: TextStyle(fontSize: 12, color: Colors.orange[600]),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: _contactLessor,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange[600],
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Contact Lessor'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Helper widgets
  Widget _buildLeaseMetric(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(color: color.withOpacity(0.8), fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildEarningsQuickStat(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.white70, fontSize: 10),
        ),
      ],
    );
  }

  Widget _buildBreakdownItem(
    String label,
    String value,
    Color color,
    IconData icon,
    bool isHighlight,
  ) {
    return Container(
      padding: EdgeInsets.all(isHighlight ? 16 : 12),
      decoration: BoxDecoration(
        color: isHighlight ? color.withOpacity(0.1) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
        border: isHighlight ? Border.all(color: color.withOpacity(0.3)) : null,
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: isHighlight ? 16 : 14,
                fontWeight: isHighlight ? FontWeight.bold : FontWeight.w600,
                color: isHighlight ? color : Colors.grey[700],
              ),
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: isHighlight ? 18 : 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricCard(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildPayoutItem(Map<String, dynamic> payout) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green[200]!),
      ),
      child: Row(
        children: [
          Icon(Icons.check_circle, color: Colors.green[600], size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  payout['date'],
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  '${payout['rides']} rides completed',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
          Text(
            '₦${payout['amount'].toStringAsFixed(0)}',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.green[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAverageMetric(
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
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
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
                Text(
                  label,
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _viewAllPayouts() {
    // TODO: Navigate to full payout history
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Full payout history feature coming soon')),
    );
  }

  void _contactLessor() {
    // TODO: Contact lessor functionality
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Contacting lessor...')));
  }
}
