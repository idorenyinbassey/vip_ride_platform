import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../services/auth_provider.dart';
import '../../../widgets/premium_card_section.dart';
import '../../premium/premium_upgrade_screen.dart';

class BlackTierClientApp extends StatefulWidget {
  const BlackTierClientApp({super.key});

  @override
  State<BlackTierClientApp> createState() => _BlackTierClientAppState();
}

class _BlackTierClientAppState extends State<BlackTierClientApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const BlackTierHomeScreen(),
    const BlackTierRidesScreen(),
    const BlackTierConciergeScreen(),
    const BlackTierLifestyleScreen(),
    const BlackTierProfileScreen(),
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
        selectedItemColor: Colors.black,
        backgroundColor: Colors.white,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car),
            label: 'Rides',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.support_agent),
            label: 'Concierge',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.diamond),
            label: 'Lifestyle',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}

class BlackTierHomeScreen extends StatelessWidget {
  const BlackTierHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.diamond, color: Colors.black),
            SizedBox(width: 8),
            Text('Black Tier Elite'),
          ],
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        actions: [
          IconButton(onPressed: () {}, icon: const Icon(Icons.notifications)),
        ],
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.diamond, size: 100, color: Colors.black),
            SizedBox(height: 20),
            Text(
              'Black Tier Elite',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            SizedBox(height: 10),
            Text(
              'Ultra-luxury experience awaits',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const PremiumUpgradeScreen(),
            ),
          );
        },
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.diamond),
        label: const Text('Upgrade Premium'),
      ),
    );
  }
}

class BlackTierRidesScreen extends StatelessWidget {
  const BlackTierRidesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Elite Rides'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 100, color: Colors.black),
            SizedBox(height: 20),
            Text(
              'Elite Ride History',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Your luxury rides with exclusive fleet'),
          ],
        ),
      ),
    );
  }
}

class BlackTierConciergeScreen extends StatelessWidget {
  const BlackTierConciergeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Elite Concierge'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.support_agent, size: 100, color: Colors.black),
            SizedBox(height: 20),
            Text(
              'Personal Concierge Service',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Dedicated personal assistant'),
          ],
        ),
      ),
    );
  }
}

class BlackTierLifestyleScreen extends StatelessWidget {
  const BlackTierLifestyleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lifestyle'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.diamond, size: 100, color: Colors.black),
            SizedBox(height: 20),
            Text(
              'Elite Lifestyle Services',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Exclusive experiences and partnerships'),
          ],
        ),
      ),
    );
  }
}

class BlackTierProfileScreen extends StatelessWidget {
  const BlackTierProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Elite Profile'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
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
                  elevation: 8,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.diamond, color: Colors.black),
                            const SizedBox(width: 8),
                            Text(
                              'Black Tier Elite Profile',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text('Name: ${user?.fullName ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text('Email: ${user?.email ?? 'N/A'}'),
                        const SizedBox(height: 8),
                        Text(
                          'Tier: ${authProvider.getUserTierDisplayName() ?? 'N/A'}',
                        ),
                        const SizedBox(height: 8),
                        Text('User Type: ${user?.userType ?? 'N/A'}'),
                        const SizedBox(height: 16),
                        const Text('Elite Benefits:'),
                        const Text('• Instant ride confirmation'),
                        const Text('• Ultra-luxury vehicle fleet'),
                        const Text('• Personal concierge service'),
                        const Text('• Private airport transfers'),
                        const Text('• Hotel partnerships'),
                        const Text('• VIP event access'),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                const Card(
                  child: Padding(
                    padding: EdgeInsets.all(16.0),
                    child: PremiumCardSection(),
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
