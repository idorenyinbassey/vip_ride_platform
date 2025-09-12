import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../services/auth_provider.dart';

class IndependentDriverApp extends StatefulWidget {
  const IndependentDriverApp({super.key});

  @override
  State<IndependentDriverApp> createState() => _IndependentDriverAppState();
}

class _IndependentDriverAppState extends State<IndependentDriverApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const IndependentDriverHomeScreen(),
    const IndependentDriverRidesScreen(),
    const IndependentDriverEarningsScreen(),
    const IndependentDriverProfileScreen(),
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

class IndependentDriverHomeScreen extends StatelessWidget {
  const IndependentDriverHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.drive_eta),
            SizedBox(width: 8),
            Text('Driver Dashboard'),
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
            Icon(Icons.drive_eta, size: 100, color: Colors.blue),
            SizedBox(height: 20),
            Text(
              'Independent Driver',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Ready to accept rides'),
          ],
        ),
      ),
    );
  }
}

class IndependentDriverRidesScreen extends StatelessWidget {
  const IndependentDriverRidesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ride Requests')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 100, color: Colors.blue),
            SizedBox(height: 20),
            Text(
              'Ride History',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Your completed and upcoming rides'),
          ],
        ),
      ),
    );
  }
}

class IndependentDriverEarningsScreen extends StatelessWidget {
  const IndependentDriverEarningsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Earnings')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.attach_money, size: 100, color: Colors.green),
            SizedBox(height: 20),
            Text(
              'Your Earnings',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Track your daily, weekly, and monthly earnings'),
          ],
        ),
      ),
    );
  }
}

class IndependentDriverProfileScreen extends StatelessWidget {
  const IndependentDriverProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Profile'),
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
                            const Icon(Icons.drive_eta, color: Colors.blue),
                            const SizedBox(width: 8),
                            Text(
                              'Independent Driver Profile',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text('Name: ${user?.fullName ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Email: ${user?.email ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Driver Type: Independent'),
                        const SizedBox(height: 8),
                        Text('Status: Active'),
                        const SizedBox(height: 16),
                        const Text('Driver Benefits:'),
                        const Text('• Flexible working hours'),
                        const Text('• Own your vehicle'),
                        const Text('• Higher earning percentage'),
                        const Text('• Direct customer relationships'),
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
