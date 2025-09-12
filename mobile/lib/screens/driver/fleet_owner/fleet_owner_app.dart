import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../services/auth_provider.dart';
import 'fleet_owner_dashboard_screen.dart';
import 'fleet_vehicles_screen.dart';
import 'fleet_drivers_screen.dart';
import 'fleet_earnings_screen.dart';
import 'fleet_reports_screen.dart';

class FleetOwnerApp extends StatefulWidget {
  const FleetOwnerApp({super.key});

  @override
  State<FleetOwnerApp> createState() => _FleetOwnerAppState();
}

class _FleetOwnerAppState extends State<FleetOwnerApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const FleetOwnerDashboardScreen(),
    const FleetVehiclesScreen(),
    const FleetDriversScreen(),
    const FleetEarningsScreen(),
    const FleetReportsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.orange[600],
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car),
            label: 'Vehicles',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.people), label: 'Drivers'),
          BottomNavigationBarItem(
            icon: Icon(Icons.monetization_on),
            label: 'Earnings',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: 'Reports',
          ),
        ],
      ),
    );
  }
}

class FleetOwnerHomeScreen extends StatelessWidget {
  const FleetOwnerHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.business),
            SizedBox(width: 8),
            Text('Fleet Management'),
          ],
        ),
        actions: [
          IconButton(onPressed: () {}, icon: const Icon(Icons.notifications)),
        ],
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.business, size: 100, color: Colors.orange),
            SizedBox(height: 20),
            Text(
              'Fleet Owner Dashboard',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Manage your fleet operations'),
          ],
        ),
      ),
    );
  }
}

class FleetVehiclesScreen extends StatelessWidget {
  const FleetVehiclesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fleet Vehicles'),
        actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.add))],
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.directions_car, size: 100, color: Colors.orange),
            SizedBox(height: 20),
            Text(
              'Your Vehicle Fleet',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Manage and monitor your vehicles'),
          ],
        ),
      ),
    );
  }
}

class FleetDriversScreen extends StatelessWidget {
  const FleetDriversScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fleet Drivers'),
        actions: [
          IconButton(onPressed: () {}, icon: const Icon(Icons.person_add)),
        ],
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.people, size: 100, color: Colors.orange),
            SizedBox(height: 20),
            Text(
              'Your Driver Team',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Manage your drivers and assignments'),
          ],
        ),
      ),
    );
  }
}

class FleetEarningsScreen extends StatelessWidget {
  const FleetEarningsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Fleet Earnings')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.attach_money, size: 100, color: Colors.green),
            SizedBox(height: 20),
            Text(
              'Fleet Revenue',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Track your fleet earnings and performance'),
          ],
        ),
      ),
    );
  }
}

class FleetOwnerProfileScreen extends StatelessWidget {
  const FleetOwnerProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fleet Owner Profile'),
        actions: [
          Consumer<AuthProvider>(
            builder: (context, authProvider, child) {
              return IconButton(
                onPressed: () async {
                  await authProvider.logout();
                },
                icon: const Icon(Icons.logout),
              );
            },
          ),
        ],
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          final user = authProvider.user;

          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.business, color: Colors.orange),
                            const SizedBox(width: 8),
                            Text(
                              'Fleet Owner Profile',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text('Name: ${user?.fullName ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Email: ${user?.email ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Role: Fleet Owner'),
                        const SizedBox(height: 8),
                        Text('Status: Active'),
                        const SizedBox(height: 16),
                        const Text('Fleet Owner Benefits:'),
                        const Text('• Manage multiple vehicles'),
                        const Text('• Assign drivers to vehicles'),
                        const Text('• Track fleet performance'),
                        const Text('• Revenue sharing control'),
                        const Text('• Fleet analytics dashboard'),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
