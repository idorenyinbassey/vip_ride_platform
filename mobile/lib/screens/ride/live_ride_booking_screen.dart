import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart' as geo;
import 'package:geolocator/geolocator.dart';
import 'package:provider/provider.dart';
import '../../services/ride_service.dart';
import '../../services/auth_provider.dart';
import '../../models/ride_models.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/ride/location_input.dart';
import '../../widgets/ride/vehicle_selector.dart';
import '../../widgets/ride/fare_display.dart';
import '../../widgets/ride/ride_booking_sheet.dart';
import '../../widgets/map/live_map_widget.dart';

class LiveRideBookingScreen extends StatefulWidget {
  const LiveRideBookingScreen({super.key});

  @override
  State<LiveRideBookingScreen> createState() => _LiveRideBookingScreenState();
}

class _LiveRideBookingScreenState extends State<LiveRideBookingScreen> {
  final RideService _rideService = RideService();

  // Location controllers
  final TextEditingController _pickupController = TextEditingController();
  final TextEditingController _destinationController = TextEditingController();

  // Map and location state
  geo.LatLng? _currentLocation;
  geo.LatLng? _pickupLocation;
  geo.LatLng? _destinationLocation;
  LocationData? _pickupData;
  LocationData? _destinationData;

  // Ride state
  String _selectedVehicleType = 'standard';
  String _selectedServiceLevel = 'regular';
  FareEstimate? _fareEstimate;
  bool _isLoadingFare = false;
  bool _isBookingRide = false;

  // Drivers and ride data
  List<Driver> _nearbyDrivers = [];
  Ride? _activeRide;

  @override
  void initState() {
    super.initState();
    _initializeLocation();
    _checkActiveRides();
  }

  Future<void> _initializeLocation() async {
    try {
      // Request location permission
      final permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        return;
      }

      // Get current position
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      setState(() {
        _currentLocation = geo.LatLng(position.latitude, position.longitude);
        _pickupLocation = _currentLocation;
      });

      // Set pickup to current location
      await _setPickupFromCurrentLocation();
    } catch (e) {
      debugPrint('❌ Error getting location: $e');
    }
  }

  Future<void> _setPickupFromCurrentLocation() async {
    if (_currentLocation == null) return;

    try {
      // For now, just set the pickup data with coordinates
      // In a real app, you'd reverse geocode to get the address
      _pickupData = LocationData(
        latitude: _currentLocation!.latitude,
        longitude: _currentLocation!.longitude,
        address: 'Current Location',
      );

      _pickupController.text = 'Current Location';

      // Load nearby drivers
      await _loadNearbyDrivers();
    } catch (e) {
      debugPrint('❌ Error setting pickup location: $e');
    }
  }

  Future<void> _loadNearbyDrivers() async {
    if (_pickupLocation == null) return;

    try {
      final drivers = await _rideService.getNearbyDrivers(
        _pickupLocation!.latitude,
        _pickupLocation!.longitude,
        _selectedVehicleType,
      );

      setState(() {
        _nearbyDrivers = drivers;
      });
    } catch (e) {
      debugPrint('❌ Error loading nearby drivers: $e');
    }
  }

  Future<void> _checkActiveRides() async {
    try {
      final activeRides = await _rideService.getActiveRides();
      if (activeRides.isNotEmpty) {
        setState(() {
          _activeRide = activeRides.first;
        });
      }
    } catch (e) {
      debugPrint('❌ Error checking active rides: $e');
    }
  }

  Future<void> _calculateFare() async {
    if (_pickupData == null || _destinationData == null) return;

    setState(() => _isLoadingFare = true);

    try {
      final request = RideRequest(
        pickup: _pickupData!,
        destination: _destinationData!,
        vehicleType: _selectedVehicleType,
        serviceLevel: _selectedServiceLevel,
        paymentMethod: 'card',
      );

      final fareEstimate = await _rideService.getEstimatedFare(request);

      setState(() {
        _fareEstimate = fareEstimate;
        _isLoadingFare = false;
      });
    } catch (e) {
      debugPrint('❌ Error calculating fare: $e');
      setState(() => _isLoadingFare = false);
    }
  }

  Future<void> _bookRide() async {
    if (_pickupData == null || _destinationData == null) return;

    setState(() => _isBookingRide = true);

    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final user = authProvider.user;

      final request = RideRequest(
        pickup: _pickupData!,
        destination: _destinationData!,
        vehicleType: _selectedVehicleType,
        serviceLevel: user?.tier ?? 'regular',
        paymentMethod: 'card',
        encryptedTracking: user?.tier == 'vip' || user?.tier == 'vip_premium',
        vipFeatures: user?.tier == 'vip_premium'
            ? {
                'concierge_support': true,
                'priority_matching': true,
                'discreet_mode': true,
              }
            : null,
        estimatedFare: _fareEstimate?.totalFare,
      );

      final response = await _rideService.bookRide(request);

      if (response.success && response.ride != null) {
        setState(() {
          _activeRide = response.ride;
          _isBookingRide = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response.message),
            backgroundColor: Colors.green,
          ),
        );

        // Start listening for ride updates
        _listenToRideUpdates();
      } else {
        setState(() => _isBookingRide = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response.message),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      setState(() => _isBookingRide = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to book ride: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _listenToRideUpdates() {
    _rideService.rideUpdates.listen((updatedRide) {
      if (updatedRide.id == _activeRide?.id) {
        setState(() {
          _activeRide = updatedRide;
        });
      }
    });
  }

  void _onVehicleTypeChanged(String vehicleType) {
    setState(() {
      _selectedVehicleType = vehicleType;
    });

    _loadNearbyDrivers();
    if (_destinationData != null) {
      _calculateFare();
    }
  }

  void _onDestinationSelected(LocationData destination) {
    setState(() {
      _destinationData = destination;
      _destinationLocation = destination.latLng;
    });

    _destinationController.text = destination.address;
    _calculateFare();
  }

  void _onPickupSelected(LocationData pickup) {
    setState(() {
      _pickupData = pickup;
      _pickupLocation = pickup.latLng;
    });

    _pickupController.text = pickup.address;
    _loadNearbyDrivers();

    if (_destinationData != null) {
      _calculateFare();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: LoadingOverlay(
        isLoading: _isBookingRide,
        child: Column(
          children: [
            // Map Section
            Expanded(
              flex: 3,
              child: Stack(
                children: [
                  LiveMapWidget(
                    currentLocation: _currentLocation,
                    pickupLocation: _pickupLocation,
                    destinationLocation: _destinationLocation,
                    nearbyDrivers: _nearbyDrivers,
                    showNearbyDrivers: true,
                    zoom: 15.0,
                  ),

                  // Back button
                  Positioned(
                    top: 50,
                    left: 16,
                    child: Container(
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black12,
                            blurRadius: 4,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                      child: IconButton(
                        icon: const Icon(Icons.arrow_back),
                        onPressed: () => Navigator.of(context).pop(),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Booking Interface
            Expanded(
              flex: 2,
              child: Container(
                decoration: const BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 8,
                      offset: Offset(0, -2),
                    ),
                  ],
                ),
                child: _activeRide != null
                    ? _buildActiveRideInterface()
                    : _buildBookingInterface(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBookingInterface() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // Handle bar
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 16),

          // Location inputs
          Expanded(
            child: Column(
              children: [
                LocationInput(
                  controller: _pickupController,
                  label: 'Pickup Location',
                  icon: Icons.my_location,
                  onLocationSelected: _onPickupSelected,
                ),
                const SizedBox(height: 12),
                LocationInput(
                  controller: _destinationController,
                  label: 'Where to?',
                  icon: Icons.location_on,
                  onLocationSelected: _onDestinationSelected,
                ),
                const SizedBox(height: 16),

                // Vehicle selector
                VehicleSelector(
                  selectedVehicleType: _selectedVehicleType,
                  onVehicleTypeChanged: _onVehicleTypeChanged,
                  nearbyDrivers: _nearbyDrivers,
                ),
                const SizedBox(height: 16),

                // Fare display
                if (_fareEstimate != null)
                  FareDisplay(
                    fareEstimate: _fareEstimate!,
                    isLoading: _isLoadingFare,
                  ),

                const Spacer(),

                // Book ride button
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _canBookRide() ? _bookRide : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Theme.of(context).primaryColor,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      _getBookButtonText(),
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActiveRideInterface() {
    return RideBookingSheet(
      ride: _activeRide!,
      onCancelRide: () async {
        final confirmed = await _showCancelConfirmation();
        if (confirmed) {
          final success = await _rideService.cancelRide(
            _activeRide!.id,
            'Cancelled by passenger',
          );

          if (success) {
            setState(() => _activeRide = null);
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Ride cancelled successfully'),
                backgroundColor: Colors.orange,
              ),
            );
          }
        }
      },
      onSOSPressed: () async {
        final success = await _rideService.sendSOS(
          _activeRide!.id,
          'Emergency assistance needed',
        );

        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('🚨 SOS sent! Help is on the way'),
              backgroundColor: Colors.red,
            ),
          );
        }
      },
    );
  }

  bool _canBookRide() {
    return _pickupData != null &&
        _destinationData != null &&
        !_isLoadingFare &&
        !_isBookingRide;
  }

  String _getBookButtonText() {
    if (_isBookingRide) return 'Booking Ride...';
    if (_pickupData == null) return 'Select Pickup Location';
    if (_destinationData == null) return 'Select Destination';
    if (_isLoadingFare) return 'Calculating Fare...';
    return 'Book Ride';
  }

  Future<bool> _showCancelConfirmation() async {
    return await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Cancel Ride'),
            content: const Text('Are you sure you want to cancel this ride?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: const Text('No'),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(true),
                child: const Text('Yes, Cancel'),
              ),
            ],
          ),
        ) ??
        false;
  }

  @override
  void dispose() {
    _pickupController.dispose();
    _destinationController.dispose();
    super.dispose();
  }
}
