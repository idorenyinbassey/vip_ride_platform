import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../services/auth_provider.dart';

class LeasedDriverApp extends StatefulWidget {
  const LeasedDriverApp({super.key});

  @override
  State<LeasedDriverApp> createState() => _LeasedDriverAppState();
}

class _LeasedDriverAppState extends State<LeasedDriverApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const LeasedDriverHomeScreen(),
    const LeasedDriverRidesScreen(),
    const LeasedDriverEarningsScreen(),
    const LeaseDetailsScreen(),
    const LeasedDriverProfileScreen(),
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
          BottomNavigationBarItem(
            icon: Icon(Icons.description),
            label: 'Lease',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}

class LeasedDriverHomeScreen extends StatelessWidget {
  const LeasedDriverHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.car_rental),
            SizedBox(width: 8),
            Text('Leased Driver'),
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
            Icon(Icons.car_rental, size: 100, color: Colors.deepPurple),
            SizedBox(height: 20),
            Text(
              'Leased Driver Dashboard',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Driving with your leased vehicle'),
          ],
        ),
      ),
    );
  }
}

class LeasedDriverRidesScreen extends StatelessWidget {
  const LeasedDriverRidesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Leased Rides')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 100, color: Colors.deepPurple),
            SizedBox(height: 20),
            Text(
              'Leased Vehicle Rides',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Your rides with leased vehicle'),
          ],
        ),
      ),
    );
  }
}

class LeasedDriverEarningsScreen extends StatelessWidget {
  const LeasedDriverEarningsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Leased Earnings')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.attach_money, size: 100, color: Colors.green),
            SizedBox(height: 20),
            Text(
              'Net Earnings After Lease',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Your earnings minus lease payments'),
          ],
        ),
      ),
    );
  }
}

class LeaseDetailsScreen extends StatelessWidget {
  const LeaseDetailsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Lease Details')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.description, size: 100, color: Colors.deepPurple),
            SizedBox(height: 20),
            Text(
              'Vehicle Lease Agreement',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('View your lease terms and payments'),
          ],
        ),
      ),
    );
  }
}

class LeasedDriverProfileScreen extends StatelessWidget {
  const LeasedDriverProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Leased Driver Profile'),
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
                            const Icon(
                              Icons.car_rental,
                              color: Colors.deepPurple,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Leased Driver Profile',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text('Name: ${user?.fullName ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Email: ${user?.email ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Driver Type: Leased'),
                        const SizedBox(height: 8),
                        Text('Lease Status: Active'),
                        const SizedBox(height: 8),
                        Text('Vehicle: Leased Vehicle'),
                        const SizedBox(height: 16),
                        const Text('Leased Driver Benefits:'),
                        const Text('• Access to newer vehicles'),
                        const Text('• Flexible lease terms'),
                        const Text('• Option to purchase'),
                        const Text('• Maintenance support'),
                        const Text('• Insurance included'),
                        const Text('• Build equity over time'),
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
