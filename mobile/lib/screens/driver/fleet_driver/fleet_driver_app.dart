import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../services/auth_provider.dart';

class FleetDriverApp extends StatefulWidget {
  const FleetDriverApp({super.key});

  @override
  State<FleetDriverApp> createState() => _FleetDriverAppState();
}

class _FleetDriverAppState extends State<FleetDriverApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const FleetDriverHomeScreen(),
    const FleetDriverRidesScreen(),
    const FleetDriverEarningsScreen(),
    const FleetDriverProfileScreen(),
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
        selectedItemColor: Theme.of(context).primaryColor,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car),
            label: 'Rides',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.attach_money),
            label: 'Earnings',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}

class FleetDriverHomeScreen extends StatelessWidget {
  const FleetDriverHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.group),
            SizedBox(width: 8),
            Text('Fleet Driver'),
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
            Icon(Icons.group, size: 100, color: Colors.teal),
            SizedBox(height: 20),
            Text(
              'Fleet Driver Dashboard',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Working with your fleet team'),
          ],
        ),
      ),
    );
  }
}

class FleetDriverRidesScreen extends StatelessWidget {
  const FleetDriverRidesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Fleet Rides')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 100, color: Colors.teal),
            SizedBox(height: 20),
            Text(
              'Fleet Ride History',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Your rides assigned through fleet'),
          ],
        ),
      ),
    );
  }
}

class FleetDriverEarningsScreen extends StatelessWidget {
  const FleetDriverEarningsScreen({super.key});

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
              'Your Fleet Earnings',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Earnings from fleet assignments'),
          ],
        ),
      ),
    );
  }
}

class FleetDriverProfileScreen extends StatelessWidget {
  const FleetDriverProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fleet Driver Profile'),
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
                            const Icon(Icons.group, color: Colors.teal),
                            const SizedBox(width: 8),
                            Text(
                              'Fleet Driver Profile',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text('Name: ${user?.fullName ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Email: ${user?.email ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Driver Type: Fleet Driver'),
                        const SizedBox(height: 8),
                        Text('Fleet: Company Fleet'),
                        const SizedBox(height: 8),
                        Text('Status: Active'),
                        const SizedBox(height: 16),
                        const Text('Fleet Driver Benefits:'),
                        const Text('• Assigned vehicle provided'),
                        const Text('• Regular income guarantee'),
                        const Text('• Fleet support team'),
                        const Text('• Maintenance handled by fleet'),
                        const Text('• Group insurance coverage'),
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
