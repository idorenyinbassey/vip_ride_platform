import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';

import 'config/theme.dart';
import 'services/api_service.dart';
import 'services/auth_provider.dart';
import 'services/location_service.dart';
import 'screens/shared/splash_screen.dart';
import 'screens/shared/login_screen.dart';
import 'screens/shared/register_screen.dart';
import 'screens/client/unified_client_app.dart';
import 'screens/driver/independent/independent_driver_app.dart';
import 'screens/driver/fleet_owner/fleet_owner_app.dart';
import 'screens/driver/fleet_driver/fleet_driver_app.dart';
import 'screens/driver/leased/leased_driver_app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize API service
  ApiService().initialize();

  // Initialize location service (singleton)
  LocationService();

  // Set preferred orientations (skip for web to avoid issues)
  if (!kIsWeb) {
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
  }

  runApp(const VipRideApp());
}

class VipRideApp extends StatelessWidget {
  const VipRideApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [ChangeNotifierProvider(create: (context) => AuthProvider())],
      child: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return MaterialApp(
            title: 'VIP Ride',
            debugShowCheckedModeBanner: false,
            theme: _getThemeForUser(authProvider),
            home: const AppNavigator(),
            routes: {
              '/login': (context) => const LoginScreen(),
              '/register': (context) => const RegisterScreen(),
            },
          );
        },
      ),
    );
  }

  ThemeData _getThemeForUser(AuthProvider authProvider) {
    if (!authProvider.isLoggedIn) {
      return AppTheme.lightTheme;
    }

    // Return theme based on user tier - Black-Tier includes Premium and VIP
    if (authProvider.isBlackTierClient) {
      // For Black-Tier users (Premium and VIP), use premium theme
      return AppTheme.blackTierTheme;
    }

    return AppTheme.lightTheme;
  }
}

class AppNavigator extends StatelessWidget {
  const AppNavigator({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        // Show splash screen while initializing
        if (!authProvider.isInitialized) {
          return const SplashScreen();
        }

        // Show login screen if not authenticated
        if (!authProvider.isLoggedIn) {
          return const LoginScreen();
        }

        // Navigate based on user type and tier
        return _getHomeScreenForUser(authProvider);
      },
    );
  }

  Widget _getHomeScreenForUser(AuthProvider authProvider) {
    final user = authProvider.user!;

    if (user.isClient) {
      // All clients use the unified client app which routes based on tier
      // Regular users can upgrade via digital card activation
      return const UnifiedClientApp();
    } else if (user.isDriver) {
      // Driver navigation based on driver type
      if (user.isFleetOwner) {
        return const FleetOwnerApp();
      } else if (user.isFleetDriver) {
        return const FleetDriverApp();
      } else if (user.isLeasedDriver) {
        return const LeasedDriverApp();
      } else {
        return const IndependentDriverApp();
      }
    }

    // Fallback to unified client app
    return const UnifiedClientApp();
  }
}
